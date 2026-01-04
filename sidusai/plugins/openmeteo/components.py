import requests
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta

class OpenMeteoClientComponent:
    API_VERSIONS = {
        'forecast': 'v1',
        'historical': 'v1',
        'previous_runs': 'v1',
        'air_quality': 'v1',
        'satellite': 'v1',
        'geocoding': 'v1',
        'flood': 'v1'
    }

    BASE_URLS = {
        'forecast': 'https://api.open-meteo.com',
        'historical': 'https://historical-forecast-api.open-meteo.com',
        'previous_runs': 'https://previous-runs-api.open-meteo.com',
        'air_quality': 'https://air-quality-api.open-meteo.com',
        'satellite': 'https://satellite-api.open-meteo.com',
        'geocoding': 'https://geocoding-api.open-meteo.com',
        'flood': 'https://flood-api.open-meteo.com'
    }

    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_delay = 0.5

        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OpenMeteo-SidusAI/1.0'
        })

    def _request(self, api_type: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        base_url = self.BASE_URLS.get(api_type, 'https://api.open-meteo.com')
        api_version = self.API_VERSIONS.get(api_type, 'v1')

        url = f"{base_url}/{api_version}{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            processed_params = {}
            if params:
                for key, value in params.items():
                    if value is not None:
                        if isinstance(value, list):
                            processed_params[key] = ','.join(str(v) for v in value)
                        elif isinstance(value, bool):
                            processed_params[key] = str(value).lower()
                        elif isinstance(value, (date, datetime)):
                            processed_params[key] = value.isoformat()
                        else:
                            processed_params[key] = str(value)

            response = self.session.get(url, params=processed_params, timeout=45)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 10
                time.sleep(wait_time)
                return self._request(api_type, endpoint, params)
            else:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('reason', error_data.get('error', str(e)))
                except:
                    error_msg = e.response.text[:200] if e.response.text else str(e)
                raise Exception(f"HTTP error {e.response.status_code}: {error_msg}")
        except requests.exceptions.Timeout:
            raise Exception("Request timeout. The server took too long to respond.")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def test_connection(self) -> bool:
        try:
            response = self._request('forecast', "/forecast", {
                "latitude": 52.52,
                "longitude": 13.41,
                "current": "temperature_2m"
            })
            return "current" in response
        except Exception:
            return False

    def get_forecast(self, 
                    latitude: float,
                    longitude: float,
                    current: Optional[List[str]] = None,
                    hourly: Optional[List[str]] = None,
                    daily: Optional[List[str]] = None,
                    timezone: str = "auto",
                    forecast_days: Optional[int] = None,
                    past_days: int = 0,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "past_days": past_days
        }

        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date
            if forecast_days:
                del params["forecast_days"]
        elif forecast_days is not None:
            params["forecast_days"] = forecast_days

        if current:
            params["current"] = current
        if hourly:
            params["hourly"] = hourly
        if daily:
            params["daily"] = daily

        return self._request('forecast', "/forecast", params)

    def get_previous_runs(self,
                         latitude: float,
                         longitude: float,
                         hourly: Optional[List[str]] = None,
                         timezone: str = "auto") -> Dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone
        }

        if hourly:
            params["hourly"] = hourly

        try:
            return self._request('previous_runs', "/forecast", params)
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
                return self.get_forecast(
                    latitude=latitude,
                    longitude=longitude,
                    hourly=["temperature_2m"],
                    start_date=start_date,
                    end_date=end_date,
                    timezone=timezone
                )
            else:
                raise

    def get_air_quality(self,
                       latitude: float,
                       longitude: float,
                       hourly: Optional[List[str]] = None,
                       current: Optional[List[str]] = None,
                       domains: str = "auto",
                       timezone: str = "auto",
                       past_days: int = 0,
                       forecast_days: int = 5) -> Dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "domains": domains,
            "timezone": timezone,
            "past_days": past_days,
            "forecast_days": forecast_days
        }

        if hourly:
            params["hourly"] = hourly
        if current:
            params["current"] = current

        return self._request('air_quality', "/air-quality", params)

    def search_locations(self,
                        name: str,
                        count: int = 10,
                        language: str = "en",
                        country_code: Optional[str] = None,
                        format: str = "json") -> Dict[str, Any]:

        params = {
            "name": name,
            "count": count,
            "language": language,
            "format": format
        }

        if country_code:
            params["country_code"] = country_code

        return self._request('geocoding', "/search", params)

    def get_flood_data(self,
                      latitude: float,
                      longitude: float,
                      daily: Optional[List[str]] = None,
                      past_days: int = 0,
                      forecast_days: int = 92,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      ensemble: bool = False) -> Dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "past_days": past_days,
            "forecast_days": forecast_days
        }

        if daily:
            params["daily"] = daily
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if ensemble:
            params["ensemble"] = ensemble

        return self._request('flood', "/flood", params)

    def get_satellite_data(self,
                          latitude: float,
                          longitude: float,
                          hourly: Optional[List[str]] = None,
                          models: Optional[str] = None,
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> Dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude
        }

        if hourly:
            params["hourly"] = hourly
        if models:
            params["models"] = models
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        return self._request('satellite', "/archive", params)

    def get_marine_forecast(self,
                           latitude: float,
                           longitude: float,
                           hourly: Optional[List[str]] = None,
                           daily: Optional[List[str]] = None,
                           timezone: str = "auto") -> Dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone
        }

        if hourly:
            params["hourly"] = hourly
        if daily:
            params["daily"] = daily

        return self._request('forecast', "/marine", params)

    def get_climate_data(self,
                        latitude: float,
                        longitude: float,
                        start_date: str,
                        end_date: str,
                        models: Optional[str] = None,
                        daily: Optional[List[str]] = None) -> Dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date
        }

        if models:
            params["models"] = models
        if daily:
            params["daily"] = daily

        return self._request('forecast', "/climate", params)
