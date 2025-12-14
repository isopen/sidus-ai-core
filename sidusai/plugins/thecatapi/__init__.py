import sidusai as sai
from typing import Dict, Any

from .components import CatAPIClient
from .skills import (
    get_all_breeds_skill,
    get_random_cat_skill,
    get_breed_images_skill,
    get_categories_skill,
    search_breeds_skill,
    get_favourites_skill,
    add_favourite_skill,
    delete_favourite_skill,
    get_votes_skill,
    add_vote_skill,
    delete_vote_skill,
    get_facts_skill,
    get_breed_facts_skill,
    upload_image_skill,
    delete_image_skill,
    get_user_images_skill,
    get_image_analysis_skill,
    catapi_chat_skill,
    CatAPIDataValue
)

__thecatapi_agent_name__ = 'thecatapi_agent'

class TheCatAPIPlugin(sai.AgentPlugin):
    def __init__(self, api_key: str):
        super().__init__()
        if not api_key:
            raise ValueError("API key is required for The Cat API plugin")
        self.cat_client = None
        self.api_key = api_key

    def apply_plugin(self, agent: sai.Agent):
        try:
            self.cat_client = CatAPIClient(api_key=self.api_key)

            if not self.cat_client.test_connection():
                raise ConnectionError("Failed to connect to The Cat API. Please check your API key.")

            self.skills = {}

            def all_breeds_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_all_breeds_skill(context)
                return CatAPIDataValue(result.value)

            def random_cat_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_random_cat_skill(context)
                return CatAPIDataValue(result.value)

            def breed_images_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_breed_images_skill(context)
                return CatAPIDataValue(result.value)

            def categories_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_categories_skill(context)
                return CatAPIDataValue(result.value)

            def search_breeds_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = search_breeds_skill(context)
                return CatAPIDataValue(result.value)

            def get_favourites_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_favourites_skill(context)
                return CatAPIDataValue(result.value)

            def add_favourite_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = add_favourite_skill(context)
                return CatAPIDataValue(result.value)

            def delete_favourite_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = delete_favourite_skill(context)
                return CatAPIDataValue(result.value)

            def get_votes_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_votes_skill(context)
                return CatAPIDataValue(result.value)

            def add_vote_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = add_vote_skill(context)
                return CatAPIDataValue(result.value)

            def delete_vote_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = delete_vote_skill(context)
                return CatAPIDataValue(result.value)

            def get_facts_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_facts_skill(context)
                return CatAPIDataValue(result.value)

            def get_breed_facts_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_breed_facts_skill(context)
                return CatAPIDataValue(result.value)

            def upload_image_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = upload_image_skill(context)
                return CatAPIDataValue(result.value)

            def delete_image_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = delete_image_skill(context)
                return CatAPIDataValue(result.value)

            def get_user_images_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_user_images_skill(context)
                return CatAPIDataValue(result.value)

            def get_image_analysis_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['cat_component'] = self.cat_client
                result = get_image_analysis_skill(context)
                return CatAPIDataValue(result.value)

            def thecatapi_chat_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value

                if isinstance(context, dict) and 'messages' in context:
                    chat_data = type('ChatData', (), {
                        'messages': context['messages'],
                        'context': {'cat_component': self.cat_client}
                    })
                    result = catapi_chat_skill(chat_data)

                    if isinstance(result, dict) and 'messages' in result:
                        return CatAPIDataValue({'messages': result['messages']})
                    elif isinstance(result, dict):
                        return CatAPIDataValue(result)
                    else:
                        return CatAPIDataValue({'error': 'Invalid chat response'})
                else:
                    return CatAPIDataValue({'error': 'No messages provided'})

            self.skills = {
                'get_all_breeds': all_breeds_wrapper,
                'get_random_cat': random_cat_wrapper,
                'get_breed_images': breed_images_wrapper,
                'get_categories': categories_wrapper,
                'search_breeds': search_breeds_wrapper,
                'get_favourites': get_favourites_wrapper,
                'add_favourite': add_favourite_wrapper,
                'delete_favourite': delete_favourite_wrapper,
                'get_votes': get_votes_wrapper,
                'add_vote': add_vote_wrapper,
                'delete_vote': delete_vote_wrapper,
                'get_facts': get_facts_wrapper,
                'get_breed_facts': get_breed_facts_wrapper,
                'upload_image': upload_image_wrapper,
                'delete_image': delete_image_wrapper,
                'get_user_images': get_user_images_wrapper,
                'get_image_analysis': get_image_analysis_wrapper,
                'thecatapi_chat': thecatapi_chat_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.cat_client = self.cat_client
            agent.thecatapi_skills = self.skills

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

class TheCatAPIAgent(sai.Agent):
    def __init__(self, api_key: str, name: str = __thecatapi_agent_name__):
        super().__init__()
        if not api_key:
            raise ValueError("API key is required for TheCatAPIAgent")

        self._name = name
        self.api_key = api_key

        self.plugin = TheCatAPIPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            return sai.AgentValue(value=context)
        except TypeError:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value

    def get_random_cat(self, size: str = None, mime_types: str = None, 
                      has_breeds: bool = None, limit: int = 1) -> Dict[str, Any]:
        context = {
            'size': size,
            'mime_types': mime_types,
            'has_breeds': has_breeds,
            'limit': limit
        }

        if 'get_random_cat' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_random_cat'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_breed_images(self, breed_id: str, limit: int = 10) -> Dict[str, Any]:
        context = {
            'breed_id': breed_id,
            'limit': limit
        }

        if 'get_breed_images' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_breed_images'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def upload_image(self, file_path: str, sub_id: str = None, breed_ids: str = None) -> Dict[str, Any]:
        context = {
            'file_path': file_path,
            'sub_id': sub_id,
            'breed_ids': breed_ids
        }

        if 'upload_image' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['upload_image'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_image(self, image_id: str) -> Dict[str, Any]:
        context = {'image_id': image_id}

        if 'delete_image' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_image'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_user_images(self, limit: int = 10, page: int = 0, order: str = "DESC") -> Dict[str, Any]:
        context = {
            'limit': limit,
            'page': page,
            'order': order
        }

        if 'get_user_images' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_user_images'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_image_analysis(self, image_id: str) -> Dict[str, Any]:
        context = {'image_id': image_id}

        if 'get_image_analysis' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_image_analysis'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_all_breeds(self, limit: int = 10, page: int = 0) -> Dict[str, Any]:
        context = {
            'limit': limit,
            'page': page
        }

        if 'get_all_breeds' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_all_breeds'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_breeds(self, query: str, attach_image: int = 1) -> Dict[str, Any]:
        context = {
            'query': query,
            'attach_image': attach_image
        }

        if 'search_breeds' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_breeds'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_favourites(self) -> Dict[str, Any]:
        context = {}

        if 'get_favourites' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_favourites'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def add_favourite(self, image_id: str, sub_id: str = None) -> Dict[str, Any]:
        context = {
            'image_id': image_id,
            'sub_id': sub_id
        }

        if 'add_favourite' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['add_favourite'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_favourite(self, favourite_id: int) -> Dict[str, Any]:
        context = {'favourite_id': favourite_id}

        if 'delete_favourite' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_favourite'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_votes(self) -> Dict[str, Any]:
        context = {}

        if 'get_votes' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_votes'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def add_vote(self, image_id: str, value: int, sub_id: str = None) -> Dict[str, Any]:
        context = {
            'image_id': image_id,
            'value': value,
            'sub_id': sub_id
        }

        if 'add_vote' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['add_vote'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_vote(self, vote_id: int) -> Dict[str, Any]:
        context = {'vote_id': vote_id}

        if 'delete_vote' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_vote'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_facts(self, limit: int = 1) -> Dict[str, Any]:
        context = {'limit': limit}

        if 'get_facts' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_facts'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_breed_facts(self, breed_id: str, limit: int = 5, page: int = 0, order: str = "ASC") -> Dict[str, Any]:
        context = {
            'breed_id': breed_id,
            'limit': limit,
            'page': page,
            'order': order
        }

        if 'get_breed_facts' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_breed_facts'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_categories(self) -> Dict[str, Any]:
        context = {}

        if 'get_categories' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_categories'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def chat(self, message: str) -> str:
        if 'thecatapi_chat' not in self.plugin.skills:
            return "Chat skill not available"

        try:
            context = {
                'messages': [
                    {
                        'role': 'user',
                        'content': message
                    }
                ]
            }

            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['thecatapi_chat'](agent_value)

            result_dict = result.value if hasattr(result, 'value') else result

            if isinstance(result_dict, dict):
                if 'messages' in result_dict:
                    messages = result_dict['messages']
                    if messages and len(messages) > 1:
                        last_message = messages[-1]
                        if isinstance(last_message, dict) and 'content' in last_message:
                            return last_message['content']

                if 'content' in result_dict:
                    return result_dict['content']

                if 'error' in result_dict:
                    return f"Error: {result_dict['error']}"

            return "No valid response"

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"

def create_thecatapi_agent(api_key: str) -> TheCatAPIAgent:
    return TheCatAPIAgent(api_key=api_key)

class SimpleCatAPIClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required for SimpleCatAPIClient")
        from .components import CatAPIClient
        self.client = CatAPIClient(api_key=api_key)

    def get_random_cat(self, **kwargs) -> Dict[str, Any]:
        return self.client.get_random_cat(**kwargs)

    def get_breed_images(self, breed_id: str, limit: int = 10) -> Dict[str, Any]:
        return self.client.get_breed_images(breed_id, limit)

    def upload_image(self, file_path: str, **kwargs) -> Dict[str, Any]:
        return self.client.upload_image(file_path, **kwargs)

    def delete_image(self, image_id: str) -> Dict[str, Any]:
        return self.client.delete_image(image_id)

    def get_user_images(self, **kwargs) -> Dict[str, Any]:
        return self.client.get_user_images(**kwargs)

    def get_all_breeds(self, **kwargs) -> Dict[str, Any]:
        return self.client.get_all_breeds(**kwargs)

    def search_breeds(self, query: str, **kwargs) -> Dict[str, Any]:
        return self.client.search_breeds(query, **kwargs)

    def get_favourites(self) -> Dict[str, Any]:
        return self.client.get_favourites()

    def add_favourite(self, image_id: str, **kwargs) -> Dict[str, Any]:
        return self.client.add_favourite(image_id, **kwargs)

    def delete_favourite(self, favourite_id: int) -> Dict[str, Any]:
        return self.client.delete_favourite(favourite_id)

    def get_votes(self) -> Dict[str, Any]:
        return self.client.get_votes()

    def add_vote(self, image_id: str, value: int, **kwargs) -> Dict[str, Any]:
        return self.client.add_vote(image_id, value, **kwargs)

    def delete_vote(self, vote_id: int) -> Dict[str, Any]:
        return self.client.delete_vote(vote_id)

    def get_facts(self, limit: int = 1) -> Dict[str, Any]:
        return self.client.get_facts(limit)

    def get_breed_facts(self, breed_id: str, **kwargs) -> Dict[str, Any]:
        return self.client.get_breed_facts(breed_id, **kwargs)

    def get_categories(self) -> Dict[str, Any]:
        return self.client.get_categories()

    def test_connection(self) -> bool:
        return self.client.test_connection()

__all__ = [
    'TheCatAPIPlugin',
    'TheCatAPIAgent',
    'SimpleCatAPIClient',
    'create_thecatapi_agent',
]
