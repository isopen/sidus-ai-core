import requests
import time
from typing import Optional, Dict, Any, List, Union

class NominatimClientComponent:
    def __init__(self, user_agent: str = "sidus-ai-nominatim/1.0", 
                 email: Optional[str] = None,
                 base_url: str = "https://nominatim.openstreetmap.org"):
        self.base_url = base_url
        self.user_agent = user_agent
        self.email = email
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_delay = 1.0

        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/json'
        })

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            else:
                response = self.session.post(url, json=params, timeout=30)

            response.raise_for_status()

            try:
                return response.json()
            except:
                return {"error": "Failed to parse JSON response", "text": response.text}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 2
                time.sleep(wait_time)
                return self._request(method, endpoint, params)
            else:
                error_msg = e.response.text[:200] if e.response.text else str(e)
                raise Exception(f"HTTP error {e.response.status_code}: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def test_connection(self) -> bool:
        try:
            response = self._request("GET", "/search", {"q": "London", "format": "json", "limit": 1})
            return isinstance(response, list) or "error" not in response
        except Exception:
            return False

    def search(self, query: str, 
               limit: int = 10,
               format: str = "json",
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

        params = {
            "q": query,
            "format": format,
            "limit": limit,
            "addressdetails": addressdetails,
            "namedetails": namedetails,
            "bounded": bounded,
            "polygon": polygon,
            "extratags": extratags,
            "dedupe": dedupe,
            "debug": debug
        }

        if countrycodes:
            if isinstance(countrycodes, list):
                params["countrycodes"] = ",".join(countrycodes)
            else:
                params["countrycodes"] = countrycodes

        if viewbox:
            params["viewbox"] = viewbox

        if polygon_kml:
            params["polygon_kml"] = polygon_kml
        if polygon_svg:
            params["polygon_svg"] = polygon_svg
        if polygon_geojson:
            params["polygon_geojson"] = polygon_geojson
        if polygon_text:
            params["polygon_text"] = polygon_text

        if exclude_place_ids:
            if isinstance(exclude_place_ids, list):
                params["exclude_place_ids"] = ",".join(str(pid) for pid in exclude_place_ids)
            else:
                params["exclude_place_ids"] = exclude_place_ids

        if addresstype:
            params["addresstype"] = addresstype

        if accept_language:
            params["accept-language"] = accept_language

        if layer:
            params["layer"] = layer

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/search", params=params)

    def reverse(self, lat: float, lon: float,
                format: str = "json",
                zoom: int = 18,
                addressdetails: int = 1,
                namedetails: int = 0,
                extratags: int = 0,
                polygon: int = 0,
                polygon_kml: int = 0,
                polygon_svg: int = 0,
                polygon_geojson: int = 0,
                polygon_text: int = 0,
                accept_language: Optional[str] = None) -> Dict[str, Any]:

        params = {
            "lat": lat,
            "lon": lon,
            "format": format,
            "zoom": zoom,
            "addressdetails": addressdetails,
            "namedetails": namedetails,
            "extratags": extratags,
            "polygon": polygon
        }

        if polygon_kml:
            params["polygon_kml"] = polygon_kml
        if polygon_svg:
            params["polygon_svg"] = polygon_svg
        if polygon_geojson:
            params["polygon_geojson"] = polygon_geojson
        if polygon_text:
            params["polygon_text"] = polygon_text

        if accept_language:
            params["accept-language"] = accept_language

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/reverse", params=params)

    def lookup(self, osm_ids: List[str],
               format: str = "json",
               addressdetails: int = 1,
               namedetails: int = 0,
               extratags: int = 0,
               accept_language: Optional[str] = None) -> Dict[str, Any]:

        params = {
            "osm_ids": ",".join(osm_ids),
            "format": format,
            "addressdetails": addressdetails,
            "namedetails": namedetails,
            "extratags": extratags
        }

        if accept_language:
            params["accept-language"] = accept_language

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/lookup", params=params)

    def details(self, place_id: Optional[int] = None,
                osmtype: Optional[str] = None,
                osmid: Optional[int] = None,
                format: str = "json",
                entrances: int = 0,
                linkedplaces: int = 0,
                hierarchy: int = 0) -> Dict[str, Any]:

        params = {
            "format": format,
            "entrances": entrances,
            "linkedplaces": linkedplaces,
            "hierarchy": hierarchy
        }

        if place_id:
            params["place_id"] = place_id
        elif osmtype and osmid:
            params["osmtype"] = osmtype
            params["osmid"] = osmid

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/details", params=params)

    def status(self, format: str = "json") -> Dict[str, Any]:
        params = {"format": format}

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/status", params=params)

    def deletable(self, format: str = "json") -> Dict[str, Any]:
        params = {"format": format}

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/deletable", params=params)

    def polygons(self, format: str = "json") -> Dict[str, Any]:
        params = {"format": format}

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/polygons", params=params)

    def details_with_entrances(self, place_id: int,
                              format: str = "json") -> Dict[str, Any]:

        params = {
            "place_id": place_id,
            "format": format,
            "entrances": 1
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/details", params=params)

    def search_with_polygon(self, query: str,
                           polygon_format: str = "kml",
                           limit: int = 10,
                           format_type: str = "xml") -> Dict[str, Any]:

        params = {
            "q": query,
            "format": format_type,
            "limit": limit,
            "addressdetails": 1
        }

        if polygon_format == "kml":
            params["polygon_kml"] = 1
        elif polygon_format == "svg":
            params["polygon_svg"] = 1
        elif polygon_format == "geojson":
            params["polygon_geojson"] = 1
        elif polygon_format == "text":
            params["polygon_text"] = 1

        if self.email:
            params["email"] = self.email

        response = self._request("GET", "/search", params=params)

        return response

    def reverse_with_polygon(self, lat: float, lon: float,
                            polygon_format: str = "kml",
                            format: str = "xml") -> Dict[str, Any]:

        params = {
            "lat": lat,
            "lon": lon,
            "format": format,
            "addressdetails": 1
        }

        if polygon_format == "kml":
            params["polygon_kml"] = 1
        elif polygon_format == "svg":
            params["polygon_svg"] = 1
        elif polygon_format == "geojson":
            params["polygon_geojson"] = 1
        elif polygon_format == "text":
            params["polygon_text"] = 1

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/reverse", params=params)

    def search_geojson(self, query: str,
                      limit: int = 10) -> Dict[str, Any]:

        params = {
            "q": query,
            "format": "geojson",
            "limit": limit,
            "addressdetails": 1
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/search", params=params)

    def reverse_geojson(self, lat: float, lon: float,
                       zoom: int = 18) -> Dict[str, Any]:

        params = {
            "lat": lat,
            "lon": lon,
            "format": "geojson",
            "zoom": zoom,
            "addressdetails": 1
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/reverse", params=params)

    def search_geocodejson(self, query: str,
                          limit: int = 10) -> Dict[str, Any]:

        params = {
            "q": query,
            "format": "geocodejson",
            "limit": limit,
            "addressdetails": 1
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/search", params=params)

    def reverse_geocodejson(self, lat: float, lon: float,
                           zoom: int = 18) -> Dict[str, Any]:

        params = {
            "lat": lat,
            "lon": lon,
            "format": "geocodejson",
            "zoom": zoom,
            "addressdetails": 1
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/reverse", params=params)

    def search_jsonv2(self, query: str,
                     limit: int = 10,
                     addressdetails: int = 1) -> Dict[str, Any]:

        params = {
            "q": query,
            "format": "jsonv2",
            "limit": limit,
            "addressdetails": addressdetails
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/search", params=params)

    def reverse_jsonv2(self, lat: float, lon: float,
                      zoom: int = 18,
                      addressdetails: int = 1) -> Dict[str, Any]:

        params = {
            "lat": lat,
            "lon": lon,
            "format": "jsonv2",
            "zoom": zoom,
            "addressdetails": addressdetails
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/reverse", params=params)

    def search_xml(self, query: str,
                  limit: int = 10) -> Dict[str, Any]:

        params = {
            "q": query,
            "format": "xml",
            "limit": limit,
            "addressdetails": 1
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/search", params=params)

    def reverse_xml(self, lat: float, lon: float,
                   zoom: int = 18) -> Dict[str, Any]:

        params = {
            "lat": lat,
            "lon": lon,
            "format": "xml",
            "zoom": zoom,
            "addressdetails": 1
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/reverse", params=params)

    def lookup_with_extratags(self, osm_ids: List[str]) -> Dict[str, Any]:

        params = {
            "osm_ids": ",".join(osm_ids),
            "format": "json",
            "extratags": 1,
            "addressdetails": 1
        }

        if self.email:
            params["email"] = self.email

        return self._request("GET", "/lookup", params=params)
