import time
import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai.plugins.pepe as pepe

def show_handler(value):
    print(f"Handler: {value}")

def stop_handler(value):
    print("Handler: Pepe stopped")

def speed_handler(value):
    print(f"Handler: Speed changed")

def status_handler(value):
    print(f"Handler: Status received")

def list_handler(value):
    print("Handler: Animations list received")

def celebrate_handler(value):
    print("Handler: Celebration started!")

def demo_pepe():
    agent = pepe.PepeAgent()

    print("🤖 Creating Pepe agent...")
    print("🔧 Building application...")
    agent.application_build()

    print("🎄 Starting New Year Pepe animation...")
    agent.show("new_year", show_handler)
    time.sleep(4)

    print("\n✨ Switching to Happy Pepe...")
    agent.show("happy", show_handler)
    time.sleep(3)

    print("\n⚡ Setting speed to fast...")
    agent.set_speed(0.3, speed_handler)
    time.sleep(2)

    print("\n❄️ Showing Snow Pepe...")
    agent.show("snow", show_handler)
    time.sleep(3)

    print("\n🐢 Setting speed to slow...")
    agent.set_speed(1.0, speed_handler)
    time.sleep(2)

    print("\n😉 Showing blinking Pepe...")
    agent.show("blink", show_handler)
    time.sleep(3)

    print("\n🎉 Starting celebration mode!")
    agent.celebrate(celebrate_handler)
    time.sleep(4)

    print("\n📋 Getting animations list...")
    agent.list_animations(list_handler)
    time.sleep(2)

    print("\n📊 Getting status...")
    agent.status(status_handler)
    time.sleep(2)

    print("\n🛑 Stopping animation...")
    agent.stop(stop_handler)


if __name__ == "__main__":
    demo_pepe()
