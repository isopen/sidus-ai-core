import sidusai as sai
from typing import Optional, Dict, Any
import os

from .components import GetgemsClient, NFTItem, CollectionInfo
from .skills import (
    get_nfts_on_sale_skill,
    get_collection_nfts_skill,
    get_nft_by_address_skill,
    get_collection_stats_skill,
    get_collection_info_skill,
    NFTCollectionValue,
    NFTItemsValue,
    NFTItemValue
)

__getgems_agent_name__ = 'getgems_nft_agent'

class GetgemsPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv('GETGEMS_API_KEY')
        self.getgems_client = None
        print(f"🔧 Getgems Plugin initialized")

    def apply_plugin(self, agent: sai.Agent):
        print("🔧 Applying Getgems plugin to agent...")

        try:
            self.getgems_client = GetgemsClient(api_key = self.api_key)

            if self.getgems_client.test_connection():
                print("✅ Getgems API connection successful")
            else:
                print("⚠️ Getgems API connection issues - some features may not work")

            self.skills = {}

            def nfts_on_sale_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value if hasattr(agent_value, 'value') else agent_value
                if isinstance(context, dict):
                    context['getgems_component'] = self.getgems_client
                result = get_nfts_on_sale_skill(context)
                return NFTItemsValue(result.value)

            def collection_nfts_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value if hasattr(agent_value, 'value') else agent_value
                if isinstance(context, dict):
                    context['getgems_component'] = self.getgems_client
                result = get_collection_nfts_skill(context)
                return NFTItemsValue(result.value)

            def nft_by_address_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value if hasattr(agent_value, 'value') else agent_value
                if isinstance(context, dict):
                    context['getgems_component'] = self.getgems_client
                result = get_nft_by_address_skill(context)
                return NFTItemValue(result.value)

            def collection_stats_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value if hasattr(agent_value, 'value') else agent_value
                if isinstance(context, dict):
                    context['getgems_component'] = self.getgems_client
                result = get_collection_stats_skill(context)
                return NFTCollectionValue(result.value)

            def collection_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value if hasattr(agent_value, 'value') else agent_value
                if isinstance(context, dict):
                    context['getgems_component'] = self.getgems_client
                result = get_collection_info_skill(context)
                return NFTCollectionValue(result.value)

            self.skills = {
                'get_nfts_on_sale': nfts_on_sale_wrapper,
                'get_collection_nfts': collection_nfts_wrapper,
                'get_nft_by_address': nft_by_address_wrapper,
                'get_collection_stats': collection_stats_wrapper,
                'get_collection_info': collection_info_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.getgems_client = self.getgems_client
            agent.getgems_skills = self.skills

            print("✅ Getgems plugin applied successfully")

        except Exception as e:
            print(f"❌ Error applying Getgems plugin: {e}")

class GetgemsNFTAnalyzer(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __getgems_agent_name__):
        super().__init__(name)

        print("🤖 Creating Getgems NFT Agent...")

        self.plugin = GetgemsPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

        print("✅ Getgems NFT Agent created successfully")

    def get_nfts_on_sale(self, collection_address: str, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        from sidusai.core.plugin import AgentValue

        context = {
            'collection_address': collection_address,
            'limit': limit,
            'cursor': cursor
        }

        if 'get_nfts_on_sale' in self.plugin.skills:
            agent_value = AgentValue(context)
            result = self.plugin.skills['get_nfts_on_sale'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_collection_nfts(self, collection_address: str, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        from sidusai.core.plugin import AgentValue

        context = {
            'collection_address': collection_address,
            'limit': limit,
            'cursor': cursor
        }

        if 'get_collection_nfts' in self.plugin.skills:
            agent_value = AgentValue(context)
            result = self.plugin.skills['get_collection_nfts'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_nft_by_address(self, nft_address: str) -> Dict[str, Any]:
        from sidusai.core.plugin import AgentValue

        context = {'nft_address': nft_address}

        if 'get_nft_by_address' in self.plugin.skills:
            agent_value = AgentValue(context)
            result = self.plugin.skills['get_nft_by_address'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_collection_stats(self, collection_address: str) -> Dict[str, Any]:
        from sidusai.core.plugin import AgentValue

        context = {'collection_address': collection_address}

        if 'get_collection_stats' in self.plugin.skills:
            agent_value = AgentValue(context)
            result = self.plugin.skills['get_collection_stats'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_collection_stats_api(self, collection_address: str) -> Dict[str, Any]:
        from sidusai.core.plugin import AgentValue

        context = {'collection_address': collection_address}

        if 'get_collection_stats_api' in self.plugin.skills:
            agent_value = AgentValue(context)
            result = self.plugin.skills['get_collection_stats_api'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_collection_info(self, collection_address: str) -> Dict[str, Any]:
        from sidusai.core.plugin import AgentValue

        context = {'collection_address': collection_address}

        if 'get_collection_info' in self.plugin.skills:
            agent_value = AgentValue(context)
            result = self.plugin.skills['get_collection_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}


def create_getgems_analyzer(api_key: Optional[str] = None) -> GetgemsNFTAnalyzer:
    return GetgemsNFTAnalyzer(api_key = api_key)

class SimpleGetgemsClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import GetgemsClient
        self.client = GetgemsClient(api_key=api_key)

    def get_nfts_on_sale(self, collection_address: str, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        return self.client.get_nfts_on_sale(collection_address, limit, cursor)

    def get_collection_nfts(self, collection_address: str, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        return self.client.get_collection_nfts(collection_address, limit, cursor)

    def get_nft_by_address(self, nft_address: str) -> Dict[str, Any]:
        return self.client.get_nft_by_address(nft_address)

    def get_collection_stats(self, collection_address: str) -> Dict[str, Any]:
        return self.client.get_collection_stats(collection_address)

    def get_collection_info(self, collection_address: str) -> Dict[str, Any]:
        return self.client.get_collection_info(collection_address)

    def test_connection(self) -> bool:
        return self.client.test_connection()

__all__ = [
    'GetgemsPlugin',
    'GetgemsNFTAnalyzer',
    'SimpleGetgemsClient',
    'create_getgems_analyzer',
    'GetgemsClient',
    'NFTItem',
    'CollectionInfo',
]
