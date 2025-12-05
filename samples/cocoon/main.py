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

    print("1. Checking worker availability:")
    availability = await skills.skill_check_worker_available()
    print(json.dumps(availability, indent=2))

    print("\n2. Getting detailed JSON statistics:")
    stats = await skills.skill_get_detailed_stats()
    print(json.dumps(stats, indent=2))

    print("\n3. Getting full status report:")
    full_report = await skills.skill_get_full_status_report()
    print(json.dumps(full_report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
