import time
import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import time
from sidusai.plugins.garland import GarlandSkill

def demo_async():
    skill = GarlandSkill()

    skill.execute("start")

    async_modes = ["async", "async_random", "pulse_waves", "chaos", "breathing", "fireflies"]

    for mode in async_modes:
        skill.execute("set_mode", mode=mode)
        time.sleep(4)

    skill.execute("set_speed", speed=0.08)

    for mode in ["async", "chaos", "fireflies"]:
        skill.execute("set_mode", mode=mode)
        time.sleep(3)

    skill.execute("set_speed", speed=0.3)
    skill.execute("set_mode", mode="breathing")
    time.sleep(5)

    print("\nStopping...")
    skill.execute("stop")

    result = skill.execute("modes")
    if result["success"]:
        print("\nAvailable modes:")
        for mode in result["data"]["modes"]:
            desc = result["data"]["descriptions"].get(mode, "")
            print(f"  - {mode}: {desc}")

if __name__ == "__main__":
    demo_async()
