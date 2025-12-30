from sidusai.plugins.pepe.components import PepeComponent
from sidusai.plugins.pepe.values import PepeResultValue

def pepe_execute_skill(value: PepeResultValue, client: PepeComponent) -> PepeResultValue:
    agent = value._agent

    animations = ["new_year", "happy", "blink", "snow", "celebration"]

    if hasattr(agent, 'command_data'):
        command = agent.command_data.get('command', '')
        kwargs = agent.command_data.get('kwargs', {})

        if command == "show":
            animation_type = kwargs.get("type", "new_year")
            if animation_type in animations:
                client.show(animation_type)
                result = {"success": True, "message": f"Showing Pepe: {animation_type}"}
            else:
                result = {"success": False, "error": f"Unknown animation. Available: {', '.join(animations)}"}

        elif command == "stop":
            if client.active:
                client.stop()
                result = {"success": True, "message": "Pepe animation stopped"}
            else:
                result = {"success": False, "message": "Pepe not active"}

        elif command == "set_speed":
            speed = float(kwargs.get("speed", 0.5))
            client.set_speed(speed)
            result = {"success": True, "message": f"Animation speed: {speed}"}

        elif command == "list_animations":
            result = {"success": True, "data": {
                "animations": animations,
                "descriptions": {
                    "new_year": "New Year Pepe with blinking eyes and hat",
                    "happy": "Happy Pepe with Christmas tree",
                    "blink": "Simple blinking Pepe",
                    "snow": "Pepe with snow animation",
                    "celebration": "Festive celebration with fireworks"
                }
            }}

        elif command == "status":
            result = {"success": True, "data": client.get_status()}

        elif command == "celebrate":
            client.celebrate()
            result = {"success": True, "message": "Pepe celebration started!"}

        else:
            result = {"success": False, "error": "Unknown command"}

        print(f"Pepe: {result}")

    return value
