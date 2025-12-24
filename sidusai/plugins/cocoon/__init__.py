import sidusai as sai

__required_modules__ = ['requests']
sai.utils.validate_modules(__required_modules__)

import sidusai.core.plugin as _cp
import sidusai.plugins.cocoon.skills as skills
import sidusai.plugins.cocoon.components as components
import sidusai.plugins.cocoon.values as values

__cocoon_agent_name__ = 'cocoon_monitoring_agent'

class CocoonMonitoringPlugin(sai.AgentPlugin):
    def __init__(self, host: str = "localhost", port: int = 12000):
        super().__init__()

        self.host = host
        self.port = port

    def apply_plugin(self, agent: sai.Agent):
        agent.add_component_builder(self._build_cocoon_monitoring)
        agent.add_skill(skills.cocoon_get_detailed_stats_skill)
        agent.add_skill(skills.cocoon_check_worker_skill)
        agent.add_skill(skills.cocoon_get_comprehensive_report_skill)

    def _build_cocoon_monitoring(self) -> components.CocoonMonitoringComponent:
        return components.CocoonMonitoringComponent(
            host = self.host,
            port = self.port
        )

class CocoonStatsTask(sai.CompletedAgentTask): pass
class CocoonHealthTask(sai.CompletedAgentTask): pass
class CocoonReportTask(sai.CompletedAgentTask): pass

class CocoonMonitoringAgent(sai.Agent):
    def __init__(self, host: str = "localhost", port: int = 12000):
        super().__init__(__cocoon_agent_name__)

        cocoon_plugin = CocoonMonitoringPlugin(
            host = host,
            port = port
        )

        cocoon_plugin.apply_plugin(self)

        stats_skill_names = _cp.build_and_register_task_skill_names(
            [skills.cocoon_get_detailed_stats_skill], 
            self
        )
        health_skill_names = _cp.build_and_register_task_skill_names(
            [skills.cocoon_check_worker_skill], 
            self
        )
        report_skill_names = _cp.build_and_register_task_skill_names(
            [skills.cocoon_get_comprehensive_report_skill], 
            self
        )

        self.task_registration(CocoonStatsTask, skill_names=stats_skill_names)
        self.task_registration(CocoonHealthTask, skill_names=health_skill_names)
        self.task_registration(CocoonReportTask, skill_names=report_skill_names)

    def get_stats(self, handler):
        task = CocoonStatsTask(self).data(values.CocoonStatsValue()).then(handler)
        self.task_execute(task)

    def check_health(self, handler):
        task = CocoonHealthTask(self).data(values.CocoonHealthValue()).then(handler)
        self.task_execute(task)

    def get_report(self, handler):
        task = CocoonReportTask(self).data(values.CocoonReportValue()).then(handler)
        self.task_execute(task)
