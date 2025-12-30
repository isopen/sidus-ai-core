import sidusai as sai
import sidusai.core.plugin as _cp
import sidusai.plugins.pepe.skills as skills
import sidusai.plugins.pepe.components as components
import sidusai.plugins.pepe.values as values

__pepe_agent_name__ = 'pepe_agent'

class PepePlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()

    def apply_plugin(self, agent: sai.Agent):
        agent.add_component_builder(self._build_pepe)
        agent.add_skill(skills.pepe_execute_skill)

    def _build_pepe(self) -> components.PepeComponent:
        return components.PepeComponent()

class PepeTask(sai.CompletedAgentTask): pass

class PepeAgent(sai.Agent):
    def __init__(self):
        super().__init__(__pepe_agent_name__)

        self.command_data = {}
        self.pepe = components.PepeComponent()

        pepe_plugin = PepePlugin()
        pepe_plugin.apply_plugin(self)

        task_skills = [skills.pepe_execute_skill]
        task_skill_names = _cp.build_and_register_task_skill_names(task_skills, self)
        self.task_registration(PepeTask, skill_names=task_skill_names)

    def show(self, animation_type="new_year", handler=None):
        self.command_data = {'command': 'show', 'kwargs': {'type': animation_type}}
        self.pepe.show(animation_type)
        task = PepeTask(self).data(values.PepeResultValue()).then(handler)
        self.task_execute(task)

    def stop(self, handler=None):
        self.command_data = {'command': 'stop', 'kwargs': {}}
        self.pepe.stop()
        task = PepeTask(self).data(values.PepeResultValue()).then(handler)
        self.task_execute(task)

    def set_speed(self, speed, handler=None):
        self.command_data = {'command': 'set_speed', 'kwargs': {'speed': speed}}
        self.pepe.set_speed(speed)
        task = PepeTask(self).data(values.PepeResultValue()).then(handler)
        self.task_execute(task)

    def list_animations(self, handler=None):
        self.command_data = {'command': 'list_animations', 'kwargs': {}}
        task = PepeTask(self).data(values.PepeResultValue()).then(handler)
        self.task_execute(task)

    def status(self, handler=None):
        self.command_data = {'command': 'status', 'kwargs': {}}
        task = PepeTask(self).data(values.PepeResultValue()).then(handler)
        self.task_execute(task)

    def celebrate(self, handler=None):
        self.command_data = {'command': 'celebrate', 'kwargs': {}}
        self.pepe.celebrate()
        task = PepeTask(self).data(values.PepeResultValue()).then(handler)
        self.task_execute(task)
