import sidusai as sai

__required_modules__ = ['requests']
sai.utils.validate_modules(__required_modules__)

import sidusai.core.plugin as _cp
import sidusai.plugins.mistral.skills as skills
import sidusai.plugins.mistral.components as components

__mistral_agent_name__ = 'mistral_ai_agent_name'

class MistralPlugin(sai.AgentPlugin):
    def __init__(self, api_key: str,
                 temperature: float = 0.7, top_p: float = 0.9,
                 max_tokens: int = 1024, model_name: str = "open-mistral-7b",
                 base_url: str = "https://api.mistral.ai/v1"):
        super().__init__()

        self.api_key = api_key
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.model_name = model_name
        self.base_url = base_url

    def apply_plugin(self, agent: sai.Agent):
        agent.add_component_builder(self._build_mistral_connection)
        agent.add_skill(skills.mistral_chat_transform_skill)

    def _build_mistral_connection(self) -> components.MistralClientComponent:
        return components.MistralClientComponent(
            api_key = self.api_key,
            temperature = self.temperature,
            top_p = self.top_p,
            max_tokens = self.max_tokens,
            model_name = self.model_name,
            base_url = self.base_url
        )


class MistralChatTask(sai.CompletedAgentTask): pass

class MistralSingleChatAgent(sai.Agent):
    def __init__(self, api_key: str, system_prompt: str = None,
                 prepare_task_skills: list = None,
                 temperature: float = 0.7, top_p: float = 0.9,
                 max_tokens: int = 1024, model_name: str = "open-mistral-7b",
                 base_url: str = "https://api.mistral.ai/v1"):
        super().__init__(__mistral_agent_name__)

        self.system_prompt = system_prompt
        self.chat = sai.ChatAgentValue([])

        mistral_plugin = MistralPlugin(
            api_key = api_key,
            temperature = temperature,
            top_p = top_p,
            max_tokens = max_tokens,
            model_name = model_name,
            base_url = base_url
        )

        mistral_plugin.apply_plugin(self)
        if system_prompt is not None:
            self.chat.append_system(system_prompt)

        task_skills = prepare_task_skills if prepare_task_skills is not None else []
        task_skills.append(skills.mistral_chat_transform_skill)

        task_skill_names = _cp.build_and_register_task_skill_names(task_skills, self)
        self.task_registration(MistralChatTask, skill_names=task_skill_names)

    def send_to_chat(self, message: str, handler):
        if message is None:
            raise ValueError('Message can not be None')

        self.chat.append_user(message)
        task = MistralChatTask(self).data(self.chat).then(handler)
        self.task_execute(task)
