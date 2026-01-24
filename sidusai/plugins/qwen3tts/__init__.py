import sidusai as sai
import torch
from typing import Optional, Dict, Any

from .components import QwenTTSProcessor
from .skills import (
    generate_voice_skill,
    generate_voice_clone_skill,
    process_audio_skill,
    analyze_audio_skill
)

__qwen_tts_agent_name__ = 'qwen_tts_agent'

class QwenTTSPlugin(sai.AgentPlugin):
    def __init__(self, device: str = "cpu", dtype: torch.dtype = torch.float32):
        super().__init__()
        self.tts_processor = None
        self.device = device
        self.dtype = dtype
        print(f"QwenTTS Plugin initialized (device={device}, dtype={dtype})")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying QwenTTS plugin to agent...")

        try:
            self.tts_processor = QwenTTSProcessor(
                device=self.device,
                dtype=self.dtype
            )
            print("QwenTTS processor created")

            self.skills = {}

            def generate_voice_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['tts_processor'] = self.tts_processor
                    result = generate_voice_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def generate_voice_clone_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['tts_processor'] = self.tts_processor
                    result = generate_voice_clone_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def process_audio_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['tts_processor'] = self.tts_processor
                    result = process_audio_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def analyze_audio_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['tts_processor'] = self.tts_processor
                    result = analyze_audio_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'generate_voice': generate_voice_wrapper,
                'generate_voice_clone': generate_voice_clone_wrapper,
                'process_audio': process_audio_wrapper,
                'analyze_audio': analyze_audio_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.tts_processor = self.tts_processor
            agent.tts_skills = self.skills

            print("QwenTTS plugin applied successfully")

        except Exception as e:
            print(f"Error applying QwenTTS plugin: {e}")
            import traceback
            traceback.print_exc()

class QwenTTSAgent(sai.Agent):
    def __init__(self, name: str = __qwen_tts_agent_name__, 
                 device: str = "cpu", dtype: torch.dtype = torch.float32):
        super().__init__()
        self._name = name

        print(f"Creating QwenTTS Agent '{name}'...")
        self.plugin = QwenTTSPlugin(device=device, dtype=dtype)
        self.plugin.apply_plugin(self)
        print(f"QwenTTS Agent '{name}' created successfully")

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value
        except Exception as e:
            print(f"Error creating AgentValue: {e}")
            agent_value = sai.AgentValue()
            setattr(agent_value, 'value', context)
            return agent_value

    def generate_voice(self,
                      text: str,
                      language: str = "english",
                      speaker: str = "ryan",
                      max_new_tokens: int = 512,
                      top_p: float = 0.9,
                      temperature: float = 0.8) -> Dict[str, Any]:

        context = {
            'text': text,
            'language': language,
            'speaker': speaker,
            'max_new_tokens': max_new_tokens,
            'top_p': top_p,
            'temperature': temperature,
            'mode': 'standard'
        }

        if 'generate_voice' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['generate_voice'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def generate_voice_clone(self,
                           text: str,
                           ref_audio_path: str,
                           ref_text: Optional[str] = None,
                           language: str = "english",
                           x_vector_only_mode: bool = False,
                           max_new_tokens: int = 512,
                           top_p: float = 0.9,
                           temperature: float = 0.8) -> Dict[str, Any]:

        context = {
            'text': text,
            'ref_audio_path': ref_audio_path,
            'ref_text': ref_text,
            'language': language,
            'x_vector_only_mode': x_vector_only_mode,
            'max_new_tokens': max_new_tokens,
            'top_p': top_p,
            'temperature': temperature,
            'mode': 'clone'
        }

        if 'generate_voice_clone' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['generate_voice_clone'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def process_audio(self,
                     audio_path: str,
                     target_dbfs: float = -16.0,
                     apply_compression: bool = True) -> Dict[str, Any]:

        context = {
            'audio_path': audio_path,
            'target_dbfs': target_dbfs,
            'apply_compression': apply_compression,
            'mode': 'process'
        }

        if 'process_audio' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['process_audio'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        context = {
            'audio_path': audio_path,
            'mode': 'analyze'
        }

        if 'analyze_audio' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['analyze_audio'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def test_voice_cloning(self,
                          ref_audio_path: str,
                          ref_text: str,
                          test_texts: Optional[list] = None) -> Dict[str, Any]:

        if test_texts is None:
            test_texts = [
                "Hello. Tanya, how are you? I cloned your voice.",
                "This is a test message for checking speech synthesis quality.",
                "As you can see, the TTS system can reproduce different phrases."
            ]

        context = {
            'ref_audio_path': ref_audio_path,
            'ref_text': ref_text,
            'test_texts': test_texts,
            'mode': 'test_cloning'
        }

        if 'generate_voice_clone' in self.plugin.skills:
            results = []
            for i, text in enumerate(test_texts):
                test_context = context.copy()
                test_context['text'] = text
                agent_value = self._create_agent_value(test_context)
                result = self.plugin.skills['generate_voice_clone'](agent_value)
                results.append(getattr(result, 'value', result) if hasattr(result, 'value') else result)

            return {
                "success": True,
                "test_count": len(test_texts),
                "results": results,
                "summary": {
                    "successful": sum(1 for r in results if r.get('success', False)),
                    "failed": sum(1 for r in results if not r.get('success', True))
                }
            }
        else:
            return {"success": False, "error": "Skill not available"}

def create_qwen_tts_agent(device: str = "cpu", dtype: torch.dtype = torch.float32) -> QwenTTSAgent:
    return QwenTTSAgent(device=device, dtype=dtype)

class SimpleQwenTTSClient:
    def __init__(self, device: str = "cpu", dtype: torch.dtype = torch.float32):
        from .components import QwenTTSProcessor
        self.processor = QwenTTSProcessor(device=device, dtype=dtype)

    def test_connection(self) -> bool:
        try:
            return self.processor.load_base_model()
        except:
            return False

    def generate_simple_voice(self, text: str, language: str = "english") -> Dict[str, Any]:
        return self.processor.generate_voice(text=text, language=language)

    def quick_test(self) -> Dict[str, Any]:
        result = self.generate_simple_voice("Hello, this is a TTS system test.", "english")
        return {
            "success": result.get("success", False),
            "model_loaded": self.processor.base_model is not None,
            "audio_generated": result.get("success", False)
        }

__all__ = [
    'QwenTTSPlugin',
    'QwenTTSAgent',
    'SimpleQwenTTSClient',
    'create_qwen_tts_agent',
    'QwenTTSProcessor',
]
