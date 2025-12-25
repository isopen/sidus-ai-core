import sidusai as sai
import sidusai.core.plugin as _cp
import sidusai.plugins.garland.skills as skills
import sidusai.plugins.garland.components as components
import sidusai.plugins.garland.values as values

__garland_agent_name__ = 'garland_agent'

class GarlandPlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()

    def apply_plugin(self, agent: sai.Agent):
        agent.add_component_builder(self._build_garland)
        agent.add_skill(skills.garland_execute_skill)

    def _build_garland(self) -> components.GarlandComponent:
        return components.GarlandComponent()

class GarlandTask(sai.CompletedAgentTask): pass

class GarlandAgent(sai.Agent):
    def __init__(self):
        super().__init__(__garland_agent_name__)

        self.command_data = {}
        self.garland = components.GarlandComponent()

        garland_plugin = GarlandPlugin()
        garland_plugin.apply_plugin(self)

        task_skills = [skills.garland_execute_skill]
        task_skill_names = _cp.build_and_register_task_skill_names(task_skills, self)
        self.task_registration(GarlandTask, skill_names=task_skill_names)

    def start(self, handler):
        self.command_data = {'command': 'start', 'kwargs': {}}
        self.garland.start()
        task = GarlandTask(self).data(values.GarlandResultValue()).then(handler)
        self.task_execute(task)

    def stop(self, handler):
        self.command_data = {'command': 'stop', 'kwargs': {}}
        self.garland.stop()
        task = GarlandTask(self).data(values.GarlandResultValue()).then(handler)
        self.task_execute(task)

    def set_mode(self, mode, handler):
        self.command_data = {'command': 'set_mode', 'kwargs': {'mode': mode}}
        self.garland.set_mode(mode)
        task = GarlandTask(self).data(values.GarlandResultValue()).then(handler)
        self.task_execute(task)

    def set_speed(self, speed, handler):
        self.command_data = {'command': 'set_speed', 'kwargs': {'speed': speed}}
        self.garland.set_speed(speed)
        task = GarlandTask(self).data(values.GarlandResultValue()).then(handler)
        self.task_execute(task)

    def status(self, handler):
        self.command_data = {'command': 'status', 'kwargs': {}}
        task = GarlandTask(self).data(values.GarlandResultValue()).then(handler)
        self.task_execute(task)

    def modes(self, handler):
        self.command_data = {'command': 'modes', 'kwargs': {}}
        task = GarlandTask(self).data(values.GarlandResultValue()).then(handler)
        self.task_execute(task)
