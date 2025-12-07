import json
import os
import sys
from ctypes import CDLL, CFUNCTYPE, c_char_p, c_double, c_int
from typing import Any, Dict

class TDLibManager:    
    def __init__(self, api_id: int, api_hash: str, database_directory: str = "./tdlib_data", tdlib_directory: str = "./"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.database_directory = os.path.abspath(database_directory)
        self.tdlib_directory = tdlib_directory

        print(f"TDLibManager initialized with API ID: {api_id}")

        os.makedirs(self.database_directory, exist_ok=True)

        self._load_library()
        self._setup_functions()
        self._setup_logging()

        self.client_id = self._td_create_client_id()

        print(f"TDLibManager: Created client ID {self.client_id}")

    def _load_library(self):
        tdjson_path = self.tdlib_directory
        if tdjson_path is None:
            if os.name == "nt":
                tdjson_path = os.path.join(os.path.dirname(__file__), "tdjson.dll")
            else:
                sys.exit("Error: Can't find 'tdjson' library.")

        try:
            self.tdjson = CDLL(tdjson_path)
            print(f"Loaded TDLib from: {tdjson_path}")
        except Exception as e:
            sys.exit(f"Error loading TDLib: {e}")

    def _setup_functions(self):
        self._td_create_client_id = self.tdjson.td_create_client_id
        self._td_create_client_id.restype = c_int
        self._td_create_client_id.argtypes = []

        self._td_receive = self.tdjson.td_receive
        self._td_receive.restype = c_char_p
        self._td_receive.argtypes = [c_double]

        self._td_send = self.tdjson.td_send
        self._td_send.restype = None
        self._td_send.argtypes = [c_int, c_char_p]

        self._td_execute = self.tdjson.td_execute
        self._td_execute.restype = c_char_p
        self._td_execute.argtypes = [c_char_p]

        self.log_message_callback_type = CFUNCTYPE(None, c_int, c_char_p)
        self._td_set_log_message_callback = self.tdjson.td_set_log_message_callback
        self._td_set_log_message_callback.restype = None
        self._td_set_log_message_callback.argtypes = [
            c_int,
            self.log_message_callback_type,
        ]

    def _setup_logging(self, verbosity_level: int = 1):
        @self.log_message_callback_type
        def on_log_message_callback(verbosity_level, message):
            if verbosity_level == 0:
                sys.exit(f"TDLib fatal error: {message.decode('utf-8')}")

        self._td_set_log_message_callback(2, on_log_message_callback)
        self.execute({"@type": "setLogVerbosityLevel", "new_verbosity_level": verbosity_level})

    def set_tdlib_parameters(self, client_id: int):
        params = {
            "@type": "setTdlibParameters",
            "database_directory": self.database_directory,
            "use_message_database": True,
            "use_secret_chats": True,
            "api_id": self.api_id,
            "api_hash": self.api_hash,
            "system_language_code": "en",
            "device_model": "Python TDLib Client",
            "application_version": "1.1",
        }
        print(f"Setting TDLib parameters...")
        self.send(params)

    def execute(self, query: Dict[str, Any]):
        query_json = json.dumps(query).encode("utf-8")
        result = self._td_execute(query_json)
        if result:
            return json.loads(result.decode("utf-8"))
        return None

    def send(self, query: Dict[str, Any]):
        query_json = json.dumps(query).encode("utf-8")
        self._td_send(self.client_id, query_json)

    def receive(self, timeout: float = 1.0):
        result = self._td_receive(timeout)
        if result:
            return json.loads(result.decode("utf-8"))
        return None

    def close(self):
        print("Closing TDLib manager")
