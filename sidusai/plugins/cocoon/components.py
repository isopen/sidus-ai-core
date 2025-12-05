from typing import Dict, Any
import aiohttp
import asyncio
from datetime import datetime

class CocoonMonitoringAgent:
    def __init__(self, host: str = "localhost", port: int = 12000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"

    async def get_json_stats(self) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/jsonstats") as response:
                    return await response.json()
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def check_worker_status(self) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/stats") as response:
                    status_text = await response.text()
                    return {
                        "status": "running" if "running" in status_text.lower() else "unknown",
                        "response": status_text.strip(),
                        "http_status": response.status,
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            return {"error": str(e), "status": "unreachable", "timestamp": datetime.now().isoformat()}

    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        json_stats, worker_status = await asyncio.gather(
            self.get_json_stats(),
            self.check_worker_status()
        )

        return {
            "detailed_stats": json_stats,
            "worker_status": worker_status,
            "service_healthy": worker_status.get("status") == "running",
            "timestamp": datetime.now().isoformat()
        }
