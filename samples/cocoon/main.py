import asyncio
import json
import sys
import os

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.cocoon import CocoonMonitoringAgent
from sidusai.plugins.cocoon.skills import CocoonMonitoringSkills

async def main():
    agent = CocoonMonitoringAgent()
    skills = CocoonMonitoringSkills(agent)

    print("Testing Cocoon Monitoring Plugin...")
    print("-" * 50)

    print("1. Checking worker status:")
    status = await skills.skill_check_worker_running()
    print(json.dumps(status, indent=2))

    print("\n2. Getting detailed statistics:")
    stats = await skills.skill_get_detailed_stats()
    print(json.dumps(stats, indent=2))

    print("\n3. Getting health report:")
    health = await skills.skill_get_health_report()
    print(json.dumps(health, indent=2))

    print("\n4. Service health check:")
    service_health = await skills.skill_check_service_health()
    print(json.dumps(service_health, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
