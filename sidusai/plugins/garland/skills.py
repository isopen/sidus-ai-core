from .components import Garland

class GarlandSkill:
    def __init__(self):
        self.garland = Garland()
        self.modes = [
            "wave", "async", "async_random", "pulse_waves", 
            "chaos", "breathing", "fireflies", "chase", 
            "bounce", "rainbow", "blink"
        ]

    def execute(self, command: str, **kwargs):
        if command == "start":
            self.garland.start()
            return {"success": True, "message": "Garland started"}

        elif command == "stop":
            self.garland.stop()
            return {"success": True, "message": "Garland stopped"}

        elif command == "set_mode":
            mode = kwargs.get("mode", "wave")
            if mode in self.modes:
                self.garland.set_mode(mode)
                return {"success": True, "message": f"Mode: {mode}"}
            return {"success": False, "error": f"Unknown mode. Available: {', '.join(self.modes)}"}

        elif command == "set_speed":
            speed = float(kwargs.get("speed", 0.15))
            self.garland.set_speed(speed)
            return {"success": True, "message": f"Speed: {speed}"}

        elif command == "status":
            return {"success": True, "data": self.garland.get_status()}

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
            return {"success": True, "data": {
                "modes": self.modes,
                "descriptions": mode_descriptions
            }}

        else:
            return {"success": False, "error": "Unknown command"}
