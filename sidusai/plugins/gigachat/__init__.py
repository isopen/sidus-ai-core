import sidusai as sai

__required_modules__ = ['requests']
sai.utils.validate_modules(__required_modules__)

import sidusai.core.plugin as _cp
import sidusai.plugins.gigachat.skills as skills
import sidusai.plugins.gigachat.components as components

__gigachat_agent_name__ = 'gc_ai_agent_name'


class GigaChatPlugin(sai.AgentPlugin):

    def __init__(self, client_id: str, client_secret: str, scope: str = "GIGACHAT_API_PERS", 
                 temperature: float = 0.7, top_p: float = 0.9,
                 max_tokens: int = 1024, model_name: str = None):
        super().__init__()

        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.model_name = model_name

    def apply_plugin(self, agent: sai.Agent):
        agent.add_component_builder(self._build_gigachat_connection)
        agent.add_skill(skills.gc_chat_transform_skill)

    def _build_gigachat_connection(self) -> components.GigaChatClientComponent:
        return components.GigaChatClientComponent(
            client_id = self.client_id,
            client_secret = self.client_secret,
            scope = self.scope,
            temperature = self.temperature,
            top_p = self.top_p,
            max_tokens = self.max_tokens,
            model_name = self.model_name
        )


class GigaChatChatTask(sai.CompletedAgentTask): pass

class GigaChatSingleChatAgent(sai.Agent):

    def __init__(self, client_id: str, client_secret: str, system_prompt: str = None, 
                 prepare_task_skills: list = None, scope: str = "GIGACHAT_API_PERS",
                 temperature: float = 0.7, top_p: float = 0.9,
                 max_tokens: int = 1024, model_name: str = None):
        super().__init__(__gigachat_agent_name__)

        self.system_prompt = system_prompt
        self.chat = sai.ChatAgentValue([])

        gc_plugin = GigaChatPlugin(
            client_id = client_id,
            client_secret = client_secret,
            scope = scope,
            temperature = temperature,
            top_p = top_p,
            max_tokens = max_tokens,
            model_name = model_name
        )

        gc_plugin.apply_plugin(self)
        if system_prompt is not None:
            self.chat.append_system(system_prompt)

        task_skills = prepare_task_skills if prepare_task_skills is not None else []
        task_skills.append(skills.gc_chat_transform_skill)

        task_skill_names = _cp.build_and_register_task_skill_names(task_skills, self)
        self.task_registration(GigaChatChatTask, skill_names=task_skill_names)

    def send_to_chat(self, message: str, handler):
        if message is None:
            raise ValueError('Message can not be None')

        self.chat.append_user(message)
        task = GigaChatChatTask(self).data(self.chat).then(handler)
        self.task_execute(task)