from typing import Dict, Any, Optional
from .components import CocoonMonitoringAgent

class CocoonMonitoringSkills:
    def __init__(self, agent: Optional[CocoonMonitoringAgent] = None):
        self.agent = agent or CocoonMonitoringAgent()

    async def skill_get_detailed_stats(self) -> Dict[str, Any]:
        return await self.agent.get_json_stats()

    async def skill_check_worker_running(self) -> Dict[str, Any]:
        return await self.agent.check_worker_status()

    async def skill_get_health_report(self) -> Dict[str, Any]:
        return await self.agent.get_comprehensive_stats()

    async def skill_check_service_health(self) -> Dict[str, Any]:
        result = await self.agent.get_comprehensive_stats()
        is_healthy = result.get("service_healthy", False)

        if is_healthy:
            return {
                "status": "healthy",
                "message": "Cocoon service is running normally",
                "details": result
            }
        else:
            return {
                "status": "unhealthy",
                "message": "Cocoon service has issues",
                "details": result
            }
