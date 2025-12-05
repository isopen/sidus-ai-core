import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CocoonMonitoringAgent:
    def __init__(self, host: str = "localhost", port: int = 12000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = aiohttp.ClientTimeout(total=10)

    async def get_json_stats(self) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/jsonstats"
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {
                            "error": f"HTTP {response.status}",
                            "status_code": response.status,
                            "endpoint": endpoint,
                            "timestamp": datetime.now().isoformat()
                        }
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error accessing {endpoint}: {e}")
            return {
                "error": f"Connection failed: {str(e)}",
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat(),
                "status": "connection_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error accessing {endpoint}: {e}")
            return {
                "error": f"Unexpected error: {str(e)}",
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }

    async def check_worker_status(self) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/stats"
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(endpoint) as response:
                    response_text = await response.text()

                    return {
                        "available": response.status == 200,
                        "http_status": response.status,
                        "raw_response": response_text.strip(),
                        "endpoint": endpoint,
                        "timestamp": datetime.now().isoformat()
                    }
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error accessing {endpoint}: {e}")
            return {
                "available": False,
                "error": f"Connection failed: {str(e)}",
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error accessing {endpoint}: {e}")
            return {
                "available": False,
                "error": f"Unexpected error: {str(e)}",
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat()
            }

    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        json_stats, worker_status = await asyncio.gather(
            self.get_json_stats(),
            self.check_worker_status()
        )

        return {
            "detailed_stats": json_stats,
            "worker_available": worker_status.get("available", False),
            "worker_status": worker_status,
            "timestamp": datetime.now().isoformat()
        }