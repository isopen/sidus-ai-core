import time
import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai.plugins.garland as garland

def start_handler(value):
    print("Handler: Garland started")

def stop_handler(value):
    print("Handler: Garland stopped")

def mode_handler(value):
    print("Handler: Mode changed")

def speed_handler(value):
    print("Handler: Speed changed")

def demo_async():
    agent = garland.GarlandAgent()

    print("🤖 Creating Garland agent...")
    print("🔧 Building application...")
    agent.application_build()

    print("🎄 Starting garland...")
    agent.start(start_handler)

    time.sleep(2)

    async_modes = ["async", "async_random", "pulse_waves", "chaos", "breathing", "fireflies"]

    for mode in async_modes:
        print(f"\n🎄 Setting mode: {mode}")
        agent.set_mode(mode, mode_handler)
        time.sleep(3)

    print("\n⚡ Setting speed to fast")
    agent.set_speed(0.08, speed_handler)

    for mode in ["async", "chaos", "fireflies"]:
        print(f"\n🎄 Setting mode: {mode}")
        agent.set_mode(mode, mode_handler)
        time.sleep(3)

    print("\n🐢 Setting speed to slow")
    agent.set_speed(0.3, speed_handler)
    agent.set_mode("breathing", mode_handler)

    time.sleep(5)

    print("\n🛑 Stopping...")
    agent.stop(stop_handler)

    time.sleep(1)

    print("\n✅ Demo completed!")

if __name__ == "__main__":
    demo_async()
