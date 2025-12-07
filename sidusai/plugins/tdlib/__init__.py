import sidusai as sai
import json
import time
from typing import Any, Dict, Optional, Callable
from .components import TDLibManager

__default_database_directory__ = "./tdlib_data"
__default_tdlib_directory__ = "./"

class TDLibAiAgent(sai.Agent):
    def __init__(self, api_id: int, api_hash: str, system_prompt: str = "",
                 database_directory: str = __default_database_directory__, tdlib_directory: str = __default_tdlib_directory__):
        super().__init__("tdlib_ai_agent")

        self.api_id = api_id
        self.api_hash = api_hash
        self.database_directory = database_directory
        self.system_prompt = system_prompt,
        self.tdlib_directory = tdlib_directory

        print(f"Initializing TDLib agent...")

        self.tdlib_manager = TDLibManager(
            api_id=api_id,
            api_hash=api_hash,
            database_directory=database_directory,
            tdlib_directory=tdlib_directory
        )

        self.on_auth_required: Optional[Callable] = None

        print("Setting TDLib parameters...")
        self.tdlib_manager.set_tdlib_parameters(self.tdlib_manager.client_id)

        self.add_loop_method(self._tdlib_polling_loop)

        print("✓ TDLib AiAgent initialized")

    def _tdlib_polling_loop(self):
        try:
            event = self.tdlib_manager.receive(0.1)
            if event:
                self._process_event(event)
        except Exception as e:
            print(f"Error in polling loop: {e}")
            time.sleep(0.1)

    def _process_event(self, event: Dict[str, Any]):
        event_type = event.get("@type", "")

        if event_type != "updateAuthorizationState":
            print(f"Receive: {json.dumps(event, indent=2)}")

        if event_type == "updateAuthorizationState":
            self._handle_auth_state(event)

        elif event_type == "updateNewMessage":
            self._handle_new_message(event)

    def _handle_auth_state(self, event: Dict[str, Any]):
        auth_state = event.get("authorization_state", {})
        auth_type = auth_state.get("@type", "")

        print(f"Authorization state: {auth_type}")

        if auth_type == "authorizationStateWaitTdlibParameters":
            pass

        elif auth_type == "authorizationStateWaitPhoneNumber":
            if self.on_auth_required:
                self.on_auth_required(self.tdlib_manager.client_id, 'phone')
            else:
                print("Phone number required (set on_auth_required callback)")

        elif auth_type == "authorizationStateWaitCode":
            if self.on_auth_required:
                self.on_auth_required(self.tdlib_manager.client_id, 'code')

        elif auth_type == "authorizationStateWaitPassword":
            if self.on_auth_required:
                self.on_auth_required(self.tdlib_manager.client_id, 'password')

        elif auth_type == "authorizationStateReady":
            print("✓ Authorization complete! You are now logged in.")

    def _handle_new_message(self, event: Dict[str, Any]):
        message = event.get('message', {})
        content = message.get('content', {})

        if content.get('@type') == 'messageText':
            text = content.get('text', {}).get('text', '')
            chat_id = message.get('chat_id', 0)

            print(f"New message in chat {chat_id}: {text[:100]}")

            if text and chat_id:
                self.send_message(f"Echo: {text}", chat_id)

    def send(self, query: Dict[str, Any]) -> None:
        self.tdlib_manager.send(query)

    def send_message(self, text: str, chat_id: int):
        message = {
            "@type": "sendMessage",
            "chat_id": chat_id,
            "input_message_content": {
                "@type": "inputMessageText",
                "text": {
                    "@type": "formattedText",
                    "text": text
                }
            }
        }

        self.send(message)
        print(f"Sent to chat {chat_id}: {text[:50]}...")

    def execute(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.tdlib_manager.execute(query)

    def receive(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        return self.tdlib_manager.receive(timeout)

    def close(self):
        print("Closing TDLib agent")
        self.tdlib_manager.close()
