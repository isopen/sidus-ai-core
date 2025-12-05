from typing import Dict, Any, Optional
from .components import CocoonMonitoringAgent

class CocoonMonitoringSkills:
    def __init__(self, agent: Optional[CocoonMonitoringAgent] = None):
        self.agent = agent or CocoonMonitoringAgent()

    async def skill_get_detailed_stats(self) -> Dict[str, Any]:
        result = await self.agent.get_json_stats()
        return result

    async def skill_check_worker_available(self) -> Dict[str, Any]:
        result = await self.agent.check_worker_status()

        if result.get("available"):
            return {
                "status": "available",
                "message": "Cocoon worker is responding",
                "details": result
            }
        else:
            return {
                "status": "unavailable",
                "message": "Cocoon worker is not responding",
                "details": result
            }

    async def skill_get_full_status_report(self) -> Dict[str, Any]:
        return await self.agent.get_comprehensive_stats()