import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import OpenMeteoClientComponent
from .skills import (
    get_current_weather_skill,
    get_forecast_skill,
    get_previous_runs_skill,
    get_air_quality_skill,
    get_weather_statistics_skill,
    get_timezone_data_skill,
    get_weather_comparison_skill
)

__openmeteo_agent_name__ = 'openmeteo_weather_agent'

class OpenMeteoPlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()
        self.openmeteo_client = None

    def apply_plugin(self, agent: sai.Agent):
        try:
            self.openmeteo_client = OpenMeteoClientComponent()

            self.skills = {}

            skill_wrappers = {
                'get_current_weather': get_current_weather_skill,
                'get_forecast': get_forecast_skill,
                'get_previous_runs': get_previous_runs_skill,
                'get_air_quality': get_air_quality_skill,
                'get_weather_statistics': get_weather_statistics_skill,
                'get_timezone_data': get_timezone_data_skill,
                'get_weather_comparison': get_weather_comparison_skill
            }

            for skill_name, skill_func in skill_wrappers.items():
                def create_wrapper(func):
                    def wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                        try:
                            context = {}
                            if hasattr(agent_value, 'value'):
                                context = agent_value.value
                            elif isinstance(agent_value, dict):
                                context = agent_value

                            context['openmeteo_client'] = self.openmeteo_client
                            result = func(context)
                            return_value = sai.AgentValue()
                            return_value.value = result.value
                            return return_value
                        except Exception as e:
                            error_value = sai.AgentValue()
                            error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                            return error_value
                    return wrapper

                self.skills[skill_name] = create_wrapper(skill_func)

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.openmeteo_client = self.openmeteo_client
            agent.openmeteo_skills = self.skills

        except Exception as e:
            import traceback
            traceback.print_exc()

class OpenMeteoAgent(sai.Agent):
    def __init__(self, name: str = __openmeteo_agent_name__):
        super().__init__()
        self._name = name

        self.plugin = OpenMeteoPlugin()
        self.plugin.apply_plugin(self)

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value
        except Exception as e:
            agent_value = sai.AgentValue()
            setattr(agent_value, 'value', context)
            return agent_value

    def get_current_weather(self,
                           latitude: float,
                           longitude: float,
                           timezone: str = "auto") -> Dict[str, Any]:

        context = {
            'latitude': latitude,
            'longitude': longitude,
            'timezone': timezone
        }

        if 'get_current_weather' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_current_weather'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_forecast(self,
                    latitude: float,
                    longitude: float,
                    forecast_type: str = "daily",
                    timezone: str = "auto",
                    forecast_days: int = 5,
                    past_days: int = 0,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'latitude': latitude,
            'longitude': longitude,
            'forecast_type': forecast_type,
            'timezone': timezone,
            'forecast_days': forecast_days,
            'past_days': past_days,
            'start_date': start_date,
            'end_date': end_date
        }

        if 'get_forecast' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_forecast'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_previous_runs(self,
                         latitude: float,
                         longitude: float,
                         hourly: Optional[List[str]] = None,
                         timezone: str = "auto") -> Dict[str, Any]:

        context = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': hourly,
            'timezone': timezone
        }

        if 'get_previous_runs' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_previous_runs'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_air_quality(self,
                       latitude: float,
                       longitude: float,
                       hourly: Optional[List[str]] = None,
                       domains: str = "auto",
                       timezone: str = "auto",
                       past_days: int = 0,
                       forecast_days: int = 5) -> Dict[str, Any]:

        context = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': hourly,
            'domains': domains,
            'timezone': timezone,
            'past_days': past_days,
            'forecast_days': forecast_days
        }

        if 'get_air_quality' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_air_quality'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_weather_statistics(self,
                              latitude: float,
                              longitude: float,
                              days: int = 7,
                              timezone: str = "auto") -> Dict[str, Any]:

        context = {
            'latitude': latitude,
            'longitude': longitude,
            'days': days,
            'timezone': timezone
        }

        if 'get_weather_statistics' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_weather_statistics'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_timezone_data(self,
                         latitude: float,
                         longitude: float) -> Dict[str, Any]:

        context = {
            'latitude': latitude,
            'longitude': longitude
        }

        if 'get_timezone_data' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_timezone_data'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def compare_weather(self,
                       locations: List[Dict[str, Any]]) -> Dict[str, Any]:

        context = {
            'locations': locations
        }

        if 'get_weather_comparison' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_weather_comparison'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_openmeteo_agent() -> OpenMeteoAgent:
    return OpenMeteoAgent()

class SimpleOpenMeteoClient:
    def __init__(self):
        from .components import OpenMeteoClientComponent
        self.client = OpenMeteoClientComponent()

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        return self.client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            current=["temperature_2m", "weather_code"]
        )

__all__ = [
    'OpenMeteoPlugin',
    'OpenMeteoAgent',
    'SimpleOpenMeteoClient',
    'create_openmeteo_agent',
    'OpenMeteoClientComponent',
]
