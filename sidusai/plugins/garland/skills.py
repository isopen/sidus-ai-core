from sidusai.plugins.garland.components import GarlandComponent
from sidusai.plugins.garland.values import GarlandResultValue

def garland_execute_skill(value: GarlandResultValue, client: GarlandComponent) -> GarlandResultValue:
    agent = value._agent

    modes = [
        "wave", "async", "async_random", "pulse_waves", 
        "chaos", "breathing", "fireflies", "chase", 
        "bounce", "rainbow", "blink"
    ]

    if hasattr(agent, 'command_data'):
        command = agent.command_data.get('command', '')
        kwargs = agent.command_data.get('kwargs', {})

        if command == "start":
            if not client.active:
                client.start()
                result = {"success": True, "message": "Garland started"}
            else:
                result = {"success": False, "message": "Garland already running"}

        elif command == "stop":
            if client.active:
                client.stop()
                result = {"success": True, "message": "Garland stopped"}
            else:
                result = {"success": False, "message": "Garland not running"}

        elif command == "set_mode":
            mode = kwargs.get("mode", "wave")
            if mode in modes:
                client.set_mode(mode)
                result = {"success": True, "message": f"Mode: {mode}"}
            else:
                result = {"success": False, "error": f"Unknown mode. Available: {', '.join(modes)}"}

        elif command == "set_speed":
            speed = float(kwargs.get("speed", 0.15))
            client.set_speed(speed)
            result = {"success": True, "message": f"Speed: {speed}"}

        elif command == "status":
            result = {"success": True, "data": client.get_status()}

        elif command == "modes":
            mode_descriptions = {
                "wave": "Single running light",
                "async": "Async blinking with phases",
                "async_random": "Random async blinking",
                "pulse_waves": "Pulsating waves",
                "chaos": "Chaotic async pattern",
                "breathing": "Breathing effect",
                "fireflies": "Fireflies random appear",
                "chase": "Chasing lights",
                "bounce": "Bouncing light",
                "rainbow": "Rainbow colors",
                "blink": "All blink together"
            }
            result = {"success": True, "data": {
                "modes": modes,
                "descriptions": mode_descriptions
            }}

        else:
            result = {"success": False, "error": "Unknown command"}

        print(f"Garland: {result}")

    return value
