import sidusai as sai
import datetime
from typing import Optional, Dict, Any, List, Union

from .components import NominatimClientComponent
from .skills import (
    search_location_skill,
    reverse_geocode_skill,
    lookup_osm_skill,
    get_server_status_skill,
    get_details_skill,
    get_deletable_skill,
    get_polygons_skill,
    search_with_polygon_skill,
    reverse_with_polygon_skill,
    search_geojson_skill,
    reverse_geojson_skill,
    search_geocodejson_skill,
    reverse_geocodejson_skill,
    search_jsonv2_skill,
    reverse_jsonv2_skill,
    search_xml_skill,
    reverse_xml_skill,
    lookup_with_extratags_skill
)

__nominatim_agent_name__ = 'nominatim_geocoding_agent'

class NominatimPlugin(sai.AgentPlugin):
    def __init__(self, user_agent: str = "sidus-ai-nominatim/1.0", email: Optional[str] = None):
        super().__init__()
        self.nominatim_client = None
        self.user_agent = user_agent
        self.email = email
        print(f"Nominatim Plugin initialized with user agent: {user_agent}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Nominatim plugin to agent...")

        try:
            self.nominatim_client = NominatimClientComponent(
                user_agent=self.user_agent,
                email=self.email
            )
            print("Nominatim client component created")

            self.skills = {}

            def create_wrapper(skill_func):
                def wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                    try:
                        context = {}
                        if hasattr(agent_value, 'value'):
                            context = agent_value.value
                        elif isinstance(agent_value, dict):
                            context = agent_value

                        context['nominatim_client'] = self.nominatim_client
                        result = skill_func(context)
                        return_value = sai.AgentValue()
                        return_value.value = result.value
                        return return_value
                    except Exception as e:
                        error_value = sai.AgentValue()
                        error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                        return error_value
                return wrapper

            skill_mapping = {
                'search_location': search_location_skill,
                'reverse_geocode': reverse_geocode_skill,
                'lookup_osm': lookup_osm_skill,
                'get_server_status': get_server_status_skill,
                'get_details': get_details_skill,
                'get_deletable': get_deletable_skill,
                'get_polygons': get_polygons_skill,
                'search_with_polygon': search_with_polygon_skill,
                'reverse_with_polygon': reverse_with_polygon_skill,
                'search_geojson': search_geojson_skill,
                'reverse_geojson': reverse_geojson_skill,
                'search_geocodejson': search_geocodejson_skill,
                'reverse_geocodejson': reverse_geocodejson_skill,
                'search_jsonv2': search_jsonv2_skill,
                'reverse_jsonv2': reverse_jsonv2_skill,
                'search_xml': search_xml_skill,
                'reverse_xml': reverse_xml_skill,
                'lookup_with_extratags': lookup_with_extratags_skill
            }

            for skill_name, skill_func in skill_mapping.items():
                self.skills[skill_name] = create_wrapper(skill_func)
                agent.add_skill(self.skills[skill_name], name=skill_name)

            agent.nominatim_client = self.nominatim_client
            agent.nominatim_skills = self.skills

            print(f"Nominatim plugin applied successfully with {len(self.skills)} skills")

        except Exception as e:
            print(f"Error applying Nominatim plugin: {e}")
            import traceback
            traceback.print_exc()

class NominatimAgent(sai.Agent):
    def __init__(self, name: str = __nominatim_agent_name__, 
                 user_agent: str = "sidus-ai-nominatim/1.0",
                 email: Optional[str] = None):
        super().__init__()
        self._name = name

        print(f"Creating Nominatim Agent '{name}'...")
        self.plugin = NominatimPlugin(user_agent=user_agent, email=email)
        self.plugin.apply_plugin(self)
        print(f"Nominatim Agent '{name}' created successfully")

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

    def search_location(self,
                       query: str,
                       limit: int = 10,
                       format_type: str = "json",
                       addressdetails: int = 1,
                       namedetails: int = 0,
                       countrycodes: Optional[Union[str, List[str]]] = None,
                       viewbox: Optional[str] = None,
                       bounded: int = 0,
                       polygon: int = 0,
                       polygon_kml: int = 0,
                       polygon_svg: int = 0,
                       polygon_geojson: int = 0,
                       polygon_text: int = 0,
                       extratags: int = 0,
                       exclude_place_ids: Optional[Union[str, List[int]]] = None,
                       dedupe: int = 1,
                       debug: int = 0,
                       addresstype: Optional[str] = None,
                       accept_language: Optional[str] = None,
                       layer: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'query': query,
            'limit': limit,
            'format': format_type,
            'addressdetails': addressdetails,
            'namedetails': namedetails,
            'bounded': bounded,
            'polygon': polygon,
            'polygon_kml': polygon_kml,
            'polygon_svg': polygon_svg,
            'polygon_geojson': polygon_geojson,
            'polygon_text': polygon_text,
            'extratags': extratags,
            'dedupe': dedupe,
            'debug': debug
        }

        if countrycodes:
            context['countrycodes'] = countrycodes
        if viewbox:
            context['viewbox'] = viewbox
        if exclude_place_ids:
            context['exclude_place_ids'] = exclude_place_ids
        if addresstype:
            context['addresstype'] = addresstype
        if accept_language:
            context['accept_language'] = accept_language
        if layer:
            context['layer'] = layer

        if 'search_location' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_location'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def reverse_geocode(self,
                       lat: float,
                       lon: float,
                       zoom: int = 18,
                       format_type: str = "json",
                       addressdetails: int = 1,
                       namedetails: int = 0,
                       extratags: int = 0,
                       polygon: int = 0,
                       polygon_kml: int = 0,
                       polygon_svg: int = 0,
                       polygon_geojson: int = 0,
                       polygon_text: int = 0,
                       accept_language: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'lat': lat,
            'lon': lon,
            'zoom': zoom,
            'format': format_type,
            'addressdetails': addressdetails,
            'namedetails': namedetails,
            'extratags': extratags,
            'polygon': polygon,
            'polygon_kml': polygon_kml,
            'polygon_svg': polygon_svg,
            'polygon_geojson': polygon_geojson,
            'polygon_text': polygon_text
        }

        if accept_language:
            context['accept_language'] = accept_language

        if 'reverse_geocode' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['reverse_geocode'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def lookup_osm(self,
                  osm_ids: List[str],
                  format_type: str = "json",
                  addressdetails: int = 1,
                  namedetails: int = 0,
                  extratags: int = 0,
                  accept_language: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'osm_ids': osm_ids,
            'format': format_type,
            'addressdetails': addressdetails,
            'namedetails': namedetails,
            'extratags': extratags
        }

        if accept_language:
            context['accept_language'] = accept_language

        if 'lookup_osm' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['lookup_osm'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_server_status(self, format_type: str = 'json') -> Dict[str, Any]:
        context = {
            'format': format_type
        }

        if 'get_server_status' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_server_status'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_details(self,
                   place_id: Optional[int] = None,
                   osm_type: Optional[str] = None,
                   osm_id: Optional[int] = None,
                   format_type: str = 'json',
                   entrances: int = 0,
                   linkedplaces: int = 0,
                   hierarchy: int = 0) -> Dict[str, Any]:

        context = {
            'place_id': place_id,
            'osm_type': osm_type,
            'osm_id': osm_id,
            'format': format_type,
            'entrances': entrances,
            'linkedplaces': linkedplaces,
            'hierarchy': hierarchy
        }

        if 'get_details' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_details'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_with_polygon(self,
                       query: str,
                       polygon_format: str = "kml",
                       limit: int = 10,
                       format_type: str = "xml") -> Dict[str, Any]:

        context = {
            'query': query,
            'polygon_format': polygon_format,
            'limit': limit,
            'format': format_type
        }

        if 'search_with_polygon' in self.plugin.skills:
            try:
                agent_value = self._create_agent_value(context)
                result = self.plugin.skills['search_with_polygon'](agent_value)
                return getattr(result, 'value', result) if hasattr(result, 'value') else result
            except Exception as e:
                return {"success": False, "error": f"Agent skill error: {str(e)}"}
        else:
            return {"success": False, "error": "Skill not available"}

    def reverse_with_polygon(self,
                            lat: float,
                            lon: float,
                            polygon_format: str = "kml",
                            format_type: str = "xml") -> Dict[str, Any]:

        context = {
            'lat': lat,
            'lon': lon,
            'polygon_format': polygon_format,
            'format': format_type
        }

        if 'reverse_with_polygon' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['reverse_with_polygon'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_geojson(self,
                      query: str,
                      limit: int = 10) -> Dict[str, Any]:

        context = {
            'query': query,
            'limit': limit,
            'format': 'geojson'
        }

        if 'search_geojson' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_geojson'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def reverse_geojson(self,
                       lat: float,
                       lon: float,
                       zoom: int = 18) -> Dict[str, Any]:

        context = {
            'lat': lat,
            'lon': lon,
            'zoom': zoom,
            'format': 'geojson'
        }

        if 'reverse_geojson' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['reverse_geojson'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_geocodejson(self,
                          query: str,
                          limit: int = 10) -> Dict[str, Any]:

        context = {
            'query': query,
            'limit': limit,
            'format': 'geocodejson'
        }

        if 'search_geocodejson' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_geocodejson'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def reverse_geocodejson(self,
                           lat: float,
                           lon: float,
                           zoom: int = 18) -> Dict[str, Any]:

        context = {
            'lat': lat,
            'lon': lon,
            'zoom': zoom,
            'format': 'geocodejson'
        }

        if 'reverse_geocodejson' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['reverse_geocodejson'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_jsonv2(self,
                     query: str,
                     limit: int = 10,
                     addressdetails: int = 1) -> Dict[str, Any]:

        context = {
            'query': query,
            'limit': limit,
            'format': 'jsonv2',
            'addressdetails': addressdetails
        }

        if 'search_jsonv2' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_jsonv2'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def reverse_jsonv2(self,
                      lat: float,
                      lon: float,
                      zoom: int = 18,
                      addressdetails: int = 1) -> Dict[str, Any]:

        context = {
            'lat': lat,
            'lon': lon,
            'zoom': zoom,
            'format': 'jsonv2',
            'addressdetails': addressdetails
        }

        if 'reverse_jsonv2' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['reverse_jsonv2'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_xml(self,
                  query: str,
                  limit: int = 10) -> Dict[str, Any]:

        context = {
            'query': query,
            'limit': limit,
            'format': 'xml'
        }

        if 'search_xml' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_xml'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def reverse_xml(self,
                   lat: float,
                   lon: float,
                   zoom: int = 18) -> Dict[str, Any]:

        context = {
            'lat': lat,
            'lon': lon,
            'zoom': zoom,
            'format': 'xml'
        }

        if 'reverse_xml' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['reverse_xml'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def lookup_with_extratags(self,
                             osm_ids: List[str]) -> Dict[str, Any]:

        context = {
            'osm_ids': osm_ids,
            'format': 'json',
            'extratags': 1
        }

        if 'lookup_with_extratags' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['lookup_with_extratags'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_deletable(self,
                     format_type: str = 'json') -> Dict[str, Any]:

        context = {
            'format': format_type
        }

        if 'get_deletable' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_deletable'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_polygons(self,
                    format_type: str = 'json') -> Dict[str, Any]:

        context = {
            'format': format_type
        }

        if 'get_polygons' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_polygons'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_nominatim_agent(user_agent: str = "sidus-ai-nominatim/1.0",
                          email: Optional[str] = None) -> NominatimAgent:
    return NominatimAgent(user_agent=user_agent, email=email)

def test_parameters(self) -> Dict[str, Any]:
        """Test various parameter combinations to see what works"""
        tests = []

        test_cases = [
            {"name": "Basic search", "query": "London", "limit": 1},
            {"name": "Search with country", "query": "Paris", "countrycodes": "FR", "limit": 1},
            {"name": "Search with extratags", "query": "Berlin", "extratags": 1, "limit": 1},
            {"name": "Search with namedetails", "query": "Rome", "namedetails": 1, "limit": 1},
        ]

        for test in test_cases:
            try:
                result = self.search_location(**{k: v for k, v in test.items() if k != 'name'})
                tests.append({
                    "name": test['name'],
                    "success": result.get('success', False),
                    "places_count": result.get('places_count', 0)
                })
            except Exception as e:
                tests.append({
                    "name": test['name'],
                    "success": False,
                    "error": str(e)
                })

        return {"success": True, "tests": tests, "timestamp": datetime.now().isoformat()}

class SimpleNominatimClient:
    def __init__(self, user_agent: str = "sidus-ai-nominatim/1.0", email: Optional[str] = None):
        from .components import NominatimClientComponent
        self.client = NominatimClientComponent(user_agent=user_agent, email=email)

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def search_city(self, city_name: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        return self.client.search(
            query=city_name,
            countrycodes=country_code,
            limit=5
        )

    def reverse_city(self, lat: float, lon: float) -> Dict[str, Any]:
        return self.client.reverse(lat=lat, lon=lon)

__all__ = [
    'NominatimPlugin',
    'NominatimAgent',
    'SimpleNominatimClient',
    'create_nominatim_agent',
    'NominatimClientComponent',
]
