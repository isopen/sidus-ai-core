import sidusai as sai

__required_modules__ = ['requests']
sai.utils.validate_modules(__required_modules__)

import sidusai.core.plugin as _cp
import sidusai.plugins.aliceai.components as components
from sidusai.plugins.aliceai.skills import create_aliceai_skill

__aliceai_agent_name__ = 'aliceai_agent_name'

class AliceAIChatTask(sai.CompletedAgentTask): pass

class AliceAISingleChatAgent(sai.Agent):
    def __init__(self, api_key: str, folder_id: str, system_prompt: str = None,
                 prepare_task_skills: list = None, temperature: float = 0.7,
                 max_tokens: int = 1024, model_name: str = None):
        super().__init__(__aliceai_agent_name__)

        self.system_prompt = system_prompt
        self.chat = sai.ChatAgentValue([])

        print("🔧 Creating Alice AI component...")
        self.component = components.AliceAIClientComponent(
            api_key=api_key,
            folder_id=folder_id,
            temperature=temperature,
            max_tokens=max_tokens,
            model_name=model_name
        )

        print("🔧 Creating Alice AI skill...")
        aliceai_skill = create_aliceai_skill(self.component)

        def component_builder() -> components.AliceAIClientComponent:
            return self.component

        self.add_component_builder(component_builder)
        self.add_skill(aliceai_skill)

        if system_prompt is not None:
            self.chat.append_system(system_prompt)

        task_skills = prepare_task_skills if prepare_task_skills is not None else []
        task_skills.append(aliceai_skill)

        task_skill_names = _cp.build_and_register_task_skill_names(task_skills, self)
        self.task_registration(AliceAIChatTask, skill_names=task_skill_names)

        print("✅ Alice AI agent created successfully")

    def send_to_chat(self, message: str, handler):
        if message is None:
            raise ValueError('Message can not be None')

        self.chat.append_user(message)
        task = AliceAIChatTask(self).data(self.chat).then(handler)
        self.task_execute(task)

class AliceAIPlugin(sai.AgentPlugin):
    def __init__(self, api_key: str, folder_id: str,
                 temperature: float = 0.7, max_tokens: int = 1024,
                 model_name: str = None):
        super().__init__()

        self.api_key = api_key
        self.folder_id = folder_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model_name = model_name
        self.component = None
        print(f"🔧 AliceAIPlugin initialized")

    def apply_plugin(self, agent: sai.Agent):
        print(f"🔧 Applying Alice AI plugin to agent...")

        self.component = components.AliceAIClientComponent(
            api_key=self.api_key,
            folder_id=self.folder_id,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            model_name=self.model_name
        )

        aliceai_skill = create_aliceai_skill(self.component)

        def component_builder() -> components.AliceAIClientComponent:
            return self.component

        agent.add_component_builder(component_builder)
        agent.add_skill(aliceai_skill)

        print(f"🔧 Plugin applied successfully")

__all__ = [
    'AliceAISingleChatAgent',
    'AliceAIChatTask',
    'AliceAIClientComponent',
    'AliceAIPlugin',
    'create_aliceai_skill'
]
