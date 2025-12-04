import sidusai as sai
from typing import Optional, Dict, Any, List, Union
import os

from .components import OpenLibraryClient, Book, Author, Work, SearchResult
from .skills import (
    search_books_skill,
    search_authors_skill,
    get_book_details_skill,
    get_author_info_skill,
    get_work_details_skill,
    get_books_by_subject_skill,
    get_work_editions_skill,
    openlibrary_chat_skill,
    BookValue,
    AuthorValue,
    SearchResultValue,
    WorkValue
)

__openlibrary_agent_name__ = 'openlibrary_agent'

class OpenLibraryPlugin(sai.AgentPlugin):
    def __init__(self, rate_limit_delay: float = 0.2):
        super().__init__()
        self.rate_limit_delay = rate_limit_delay
        self.openlibrary_client = None
        print(f"🔧 OpenLibrary Plugin initialized")

    def apply_plugin(self, agent: sai.Agent):
        print("🔧 Applying OpenLibrary plugin to agent...")

        try:
            self.openlibrary_client = OpenLibraryClient(rate_limit_delay=self.rate_limit_delay)

            if self.openlibrary_client.test_connection():
                print("✅ OpenLibrary API connection successful")
            else:
                print("⚠️ OpenLibrary API connection issues - some features may not work")

            self.skills = {}

            def search_books_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openlibrary_component'] = self.openlibrary_client
                result = search_books_skill(context)
                return SearchResultValue(result.value)

            def search_authors_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openlibrary_component'] = self.openlibrary_client
                result = search_authors_skill(context)
                return AuthorValue(result.value)

            def get_book_details_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openlibrary_component'] = self.openlibrary_client
                result = get_book_details_skill(context)
                return BookValue(result.value)

            def get_author_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openlibrary_component'] = self.openlibrary_client
                result = get_author_info_skill(context)
                return AuthorValue(result.value)

            def get_work_details_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openlibrary_component'] = self.openlibrary_client
                result = get_work_details_skill(context)
                return WorkValue(result.value)

            def get_books_by_subject_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openlibrary_component'] = self.openlibrary_client
                result = get_books_by_subject_skill(context)
                return SearchResultValue(result.value)

            def get_work_editions_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openlibrary_component'] = self.openlibrary_client
                result = get_work_editions_skill(context)
                return BookValue(result.value)

            def openlibrary_chat_wrapper(chat_value: sai.ChatAgentValue) -> sai.ChatAgentValue:
                chat_value.context = {'openlibrary_component': self.openlibrary_client}
                return openlibrary_chat_skill(chat_value)

            self.skills = {
                'search_books': search_books_wrapper,
                'search_authors': search_authors_wrapper,
                'get_book_details': get_book_details_wrapper,
                'get_author_info': get_author_info_wrapper,
                'get_work_details': get_work_details_wrapper,
                'get_books_by_subject': get_books_by_subject_wrapper,
                'get_work_editions': get_work_editions_wrapper,
                'openlibrary_chat': openlibrary_chat_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.openlibrary_client = self.openlibrary_client
            agent.openlibrary_skills = self.skills

            print("✅ OpenLibrary plugin applied successfully")

        except Exception as e:
            print(f"❌ Error applying OpenLibrary plugin: {e}")
            import traceback
            traceback.print_exc()


class OpenLibraryAgent(sai.Agent):
    def __init__(self, rate_limit_delay: float = 0.2, name: str = __openlibrary_agent_name__):
        super().__init__()
        self._name = name

        print(f"🤖 Creating OpenLibrary Agent '{name}'...")
        self.plugin = OpenLibraryPlugin(rate_limit_delay=rate_limit_delay)
        self.plugin.apply_plugin(self)

        print(f"✅ OpenLibrary Agent '{name}' created successfully")

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

    def search_books(self, query: str, limit: int = 10, page: int = 1) -> Dict[str, Any]:
        context = {
            'query': query,
            'limit': limit,
            'page': page
        }

        if 'search_books' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_books'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available", "success": False}

    def search_authors(self, query: str, limit: int = 10) -> Dict[str, Any]:
        context = {
            'query': query,
            'limit': limit
        }

        if 'search_authors' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_authors'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available", "success": False}

    def get_book_details(self, book_key: str) -> Dict[str, Any]:
        context = {
            'book_key': book_key
        }

        if 'get_book_details' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_book_details'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available", "success": False}

    def get_author_info(self, author_key: str) -> Dict[str, Any]:
        context = {
            'author_key': author_key
        }

        if 'get_author_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_author_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available", "success": False}

    def get_work_details(self, work_key: str) -> Dict[str, Any]:
        context = {
            'work_key': work_key
        }

        if 'get_work_details' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_work_details'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available", "success": False}

    def get_books_by_subject(self, subject: str, limit: int = 20) -> Dict[str, Any]:
        context = {
            'subject': subject,
            'limit': limit
        }

        if 'get_books_by_subject' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_books_by_subject'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available", "success": False}

    def get_work_editions(self, work_key: str, limit: int = 20) -> Dict[str, Any]:
        context = {
            'work_key': work_key,
            'limit': limit
        }

        if 'get_work_editions' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_work_editions'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available", "success": False}

    def chat(self, message: str) -> str:
        from sidusai.core.plugin import ChatAgentValue

        if 'openlibrary_chat' not in self.plugin.skills:
            return "Chat skill not available"

        try:
            chat = ChatAgentValue(messages=[])
        except TypeError:
            try:
                chat = ChatAgentValue()
                chat.messages = []
            except:
                class SimpleChat:
                    def __init__(self):
                        self.messages = []
                        self.context = {}

                    def append_user(self, message):
                        self.messages.append({'role': 'user', 'content': message})

                    def append_assistant(self, message):
                        self.messages.append({'role': 'assistant', 'content': message})

                chat = SimpleChat()

        chat.append_user(message)
        chat.context = {'openlibrary_component': self.plugin.openlibrary_client}

        result = self.plugin.skills['openlibrary_chat'](chat)

        if isinstance(result, ChatAgentValue) and result.messages:
            for msg in reversed(result.messages):
                if msg['role'] == 'assistant':
                    return msg['content']
        elif hasattr(result, 'messages') and result.messages:
            for msg in reversed(result.messages):
                if msg['role'] == 'assistant':
                    return msg['content']

        return "No response from agent"


def create_openlibrary_agent(rate_limit_delay: float = 0.2) -> OpenLibraryAgent:
    return OpenLibraryAgent(rate_limit_delay=rate_limit_delay)


class SimpleOpenLibraryClient:
    def __init__(self, rate_limit_delay: float = 0.2):
        from .components import OpenLibraryClient
        self.client = OpenLibraryClient(rate_limit_delay=rate_limit_delay)

    def search_books(self, query: str, limit: int = 10, page: int = 1) -> List[SearchResult]:
        return self.client.search_books(query, limit, page)

    def search_authors(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.client.search_authors(query, limit)

    def get_book(self, key: str) -> Optional[Book]:
        return self.client.get_book(key)

    def get_author(self, key: str) -> Optional[Author]:
        return self.client.get_author(key)

    def get_work(self, key: str) -> Optional[Work]:
        return self.client.get_work(key)

    def get_subject_books(self, subject: str, limit: int = 20) -> List[Dict[str, Any]]:
        return self.client.get_subject_books(subject, limit)

    def get_work_editions(self, work_key: str, limit: int = 50) -> List[Dict[str, Any]]:
        return self.client.get_work_editions(work_key, limit)

    def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.client.get_book_by_isbn(isbn)

    def get_author_by_name(self, name: str) -> Optional[Author]:
        return self.client.get_author_by_name(name)

    def get_book_cover(self, cover_id: int, size: str = "M") -> Optional[str]:
        return self.client.get_book_cover(cover_id, size)

    def get_author_photo(self, photo_id: int, size: str = "M") -> Optional[str]:
        return self.client.get_author_photo(photo_id, size)

    def test_connection(self) -> bool:
        return self.client.test_connection()

    def get_api_status(self) -> Dict[str, Any]:
        return self.client.get_api_status()

__all__ = [
    'OpenLibraryPlugin',
    'OpenLibraryAgent',
    'SimpleOpenLibraryClient',
    'OpenLibraryClient',
    'Book',
    'Author',
    'Work',
    'SearchResult',
    'create_openlibrary_agent',
    'BookValue',
    'AuthorValue',
    'SearchResultValue',
    'WorkValue',
]
