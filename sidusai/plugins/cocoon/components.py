import requests
from datetime import datetime
from typing import Dict, Any

class CocoonMonitoringComponent:
    def __init__(self, host: str = "localhost", port: int = 12000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = 10
        self.session = requests.Session()

    def get_json_stats(self) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/jsonstats"
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error accessing {endpoint}: HTTP {response.status_code}")
                return {
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code,
                    "endpoint": endpoint,
                    "timestamp": datetime.now().isoformat()
                }
        except requests.exceptions.RequestException as e:
            print(f"HTTP error accessing {endpoint}: {e}")
            return {
                "error": f"Connection failed: {str(e)}",
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat(),
                "status": "connection_error"
            }
        except Exception as e:
            print(f"Unexpected error accessing {endpoint}: {e}")
            return {
                "error": f"Unexpected error: {str(e)}",
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }

    def check_worker_status(self) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/stats"
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            return {
                "available": response.status_code == 200,
                "http_status": response.status_code,
                "raw_response": response.text.strip(),
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            print(f"HTTP error accessing {endpoint}: {e}")
            return {
                "available": False,
                "error": f"Connection failed: {str(e)}",
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Unexpected error accessing {endpoint}: {e}")
            return {
                "available": False,
                "error": f"Unexpected error: {str(e)}",
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat()
            }

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        json_stats = self.get_json_stats()
        worker_status = self.check_worker_status()

        return {
            "detailed_stats": json_stats,
            "worker_available": worker_status.get("available", False),
            "worker_status": worker_status,
            "timestamp": datetime.now().isoformat()
        }
