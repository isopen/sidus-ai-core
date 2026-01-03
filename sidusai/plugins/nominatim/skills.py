from typing import Dict, Any
from datetime import datetime

class NominatimDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def search_location_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting search_location_skill...")

    query = context.get('query', '')
    limit = context.get('limit', 10)
    format_type = context.get('format', 'json')
    addressdetails = context.get('addressdetails', 1)
    namedetails = context.get('namedetails', 0)
    countrycodes = context.get('countrycodes')
    viewbox = context.get('viewbox')
    bounded = context.get('bounded', 0)
    polygon = context.get('polygon', 0)
    polygon_kml = context.get('polygon_kml', 0)
    polygon_svg = context.get('polygon_svg', 0)
    polygon_geojson = context.get('polygon_geojson', 0)
    polygon_text = context.get('polygon_text', 0)
    extratags = context.get('extratags', 0)
    exclude_place_ids = context.get('exclude_place_ids')
    dedupe = context.get('dedupe', 1)
    debug = context.get('debug', 0)
    addresstype = context.get('addresstype')
    accept_language = context.get('accept_language')
    layer = context.get('layer')

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.search(
                query=query,
                limit=limit,
                format=format_type,
                addressdetails=addressdetails,
                namedetails=namedetails,
                countrycodes=countrycodes,
                viewbox=viewbox,
                bounded=bounded,
                polygon=polygon,
                polygon_kml=polygon_kml,
                polygon_svg=polygon_svg,
                polygon_geojson=polygon_geojson,
                polygon_text=polygon_text,
                extratags=extratags,
                exclude_place_ids=exclude_place_ids,
                dedupe=dedupe,
                debug=debug,
                addresstype=addresstype,
                accept_language=accept_language,
                layer=layer
            )

            if isinstance(response, list):
                places = response

                analysis_result = {
                    "success": True,
                    "places_count": len(places),
                    "places": [],
                    "summary": {
                        "countries": {},
                        "place_types": {},
                        "bbox_present": 0,
                        "osm_types": {},
                        "formats_supported": {
                            "geojson": 0,
                            "geocodejson": 0,
                            "xml": 0,
                            "jsonv2": 0
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }

                for place in places:
                    place_type = place.get('type', 'unknown')
                    osm_type = place.get('osm_type', 'unknown')
                    display_name = place.get('display_name', '')
                    address = place.get('address', {})
                    country = address.get('country', 'Unknown')

                    analysis_result["summary"]["countries"][country] = analysis_result["summary"]["countries"].get(country, 0) + 1
                    analysis_result["summary"]["place_types"][place_type] = analysis_result["summary"]["place_types"].get(place_type, 0) + 1
                    analysis_result["summary"]["osm_types"][osm_type] = analysis_result["summary"]["osm_types"].get(osm_type, 0) + 1

                    if place.get('boundingbox'):
                        analysis_result["summary"]["bbox_present"] += 1

                    if place.get('geojson'):
                        analysis_result["summary"]["formats_supported"]["geojson"] += 1
                    if place.get('geocodejson'):
                        analysis_result["summary"]["formats_supported"]["geocodejson"] += 1
                    if place.get('xml'):
                        analysis_result["summary"]["formats_supported"]["xml"] += 1
                    if place.get('jsonv2'):
                        analysis_result["summary"]["formats_supported"]["jsonv2"] += 1

                    place_data = {
                        "place_id": place.get('place_id'),
                        "osm_id": place.get('osm_id'),
                        "osm_type": osm_type,
                        "type": place_type,
                        "display_name": display_name,
                        "lat": place.get('lat'),
                        "lon": place.get('lon'),
                        "importance": place.get('importance', 0),
                        "icon": place.get('icon'),
                        "class": place.get('class'),
                        "address": address,
                        "boundingbox": place.get('boundingbox'),
                        "licence": place.get('licence')
                    }

                    if place.get('extratags'):
                        place_data["extratags"] = place.get('extratags')
                    if place.get('namedetails'):
                        place_data["namedetails"] = place.get('namedetails')
                    if place.get('polygonpoints'):
                        place_data["polygonpoints"] = place.get('polygonpoints')
                    if place.get('svg'):
                        place_data["svg"] = place.get('svg')

                    analysis_result["places"].append(place_data)

                analysis_result["places"].sort(key=lambda x: x.get('importance', 0), reverse=True)

                print(f"✅ Location search: Found {len(places)} places for query '{query}'")
                print(f"   Format: {format_type}")
                print(f"   Countries: {len(analysis_result['summary']['countries'])}")

                if analysis_result["places"]:
                    print(f"\nAll results:")
                    for i, place in enumerate(analysis_result["places"]):
                        print(f"   {i+1}. {place['display_name']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid response format",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid response format")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error searching location: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to search location: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_location_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def reverse_geocode_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting reverse_geocode_skill...")

    lat = context.get('lat')
    lon = context.get('lon')
    zoom = context.get('zoom', 18)
    format_type = context.get('format', 'json')
    addressdetails = context.get('addressdetails', 1)
    namedetails = context.get('namedetails', 0)
    extratags = context.get('extratags', 0)
    polygon = context.get('polygon', 0)
    polygon_kml = context.get('polygon_kml', 0)
    polygon_svg = context.get('polygon_svg', 0)
    polygon_geojson = context.get('polygon_geojson', 0)
    polygon_text = context.get('polygon_text', 0)
    accept_language = context.get('accept_language')

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if lat is None or lon is None:
            result = {"success": False, "error": "Latitude and longitude are required"}
            return NominatimDataValue(result)

        try:
            response = client.reverse(
                lat=lat,
                lon=lon,
                zoom=zoom,
                format=format_type,
                addressdetails=addressdetails,
                namedetails=namedetails,
                extratags=extratags,
                polygon=polygon,
                polygon_kml=polygon_kml,
                polygon_svg=polygon_svg,
                polygon_geojson=polygon_geojson,
                polygon_text=polygon_text,
                accept_language=accept_language
            )

            if isinstance(response, dict) or (isinstance(response, list) and len(response) > 0):
                if isinstance(response, list):
                    place = response[0] if response else {}
                else:
                    place = response

                analysis_result = {
                    "success": True,
                    "coordinates": {
                        "lat": lat,
                        "lon": lon,
                        "zoom": zoom
                    },
                    "place": {},
                    "address_analysis": {
                        "components_count": 0,
                        "address_hierarchy": [],
                        "country_code": ""
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if place:
                    address = place.get('address', {})
                    address_components = []

                    for key, value in address.items():
                        if value:
                            address_components.append({
                                "type": key,
                                "value": value
                            })

                    analysis_result["address_analysis"]["components_count"] = len(address_components)
                    analysis_result["address_analysis"]["country_code"] = address.get('country_code', '')

                    analysis_result["place"] = {
                        "place_id": place.get('place_id'),
                        "osm_id": place.get('osm_id'),
                        "osm_type": place.get('osm_type'),
                        "type": place.get('type'),
                        "category": place.get('category'),
                        "display_name": place.get('display_name'),
                        "lat": place.get('lat'),
                        "lon": place.get('lon'),
                        "importance": place.get('importance', 0),
                        "address": address,
                        "boundingbox": place.get('boundingbox'),
                        "licence": place.get('licence')
                    }

                    if place.get('extratags'):
                        analysis_result["place"]["extratags"] = place.get('extratags')
                    if place.get('namedetails'):
                        analysis_result["place"]["namedetails"] = place.get('namedetails')

                    print(f"✅ Reverse geocode: Found location for coordinates ({lat}, {lon})")
                    print(f"   Format: {format_type}")
                    print(f"   Display name: {analysis_result['place']['display_name']}")

                else:
                    analysis_result = {
                        "success": False,
                        "error": "No location found for these coordinates",
                        "coordinates": {"lat": lat, "lon": lon},
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"❌ No location found for coordinates ({lat}, {lon})")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid response format",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid response format")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error reverse geocoding: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to reverse geocode: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in reverse_geocode_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def lookup_osm_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting lookup_osm_skill...")

    osm_ids = context.get('osm_ids', [])
    format_type = context.get('format', 'json')
    addressdetails = context.get('addressdetails', 1)
    namedetails = context.get('namedetails', 0)
    extratags = context.get('extratags', 0)
    accept_language = context.get('accept_language')

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if not osm_ids:
            result = {"success": False, "error": "OSM IDs are required"}
            return NominatimDataValue(result)

        try:
            response = client.lookup(
                osm_ids=osm_ids,
                format=format_type,
                addressdetails=addressdetails,
                namedetails=namedetails,
                extratags=extratags,
                accept_language=accept_language
            )

            if isinstance(response, list):
                places = response

                analysis_result = {
                    "success": True,
                    "osm_ids_requested": osm_ids,
                    "places_found": len(places),
                    "places": [],
                    "summary": {
                        "osm_types": {},
                        "categories": {},
                        "countries": {},
                        "extratags_present": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                for place in places:
                    osm_type = place.get('osm_type', 'unknown')
                    category = place.get('class', 'unknown')
                    address = place.get('address', {})
                    country = address.get('country', 'Unknown')

                    analysis_result["summary"]["osm_types"][osm_type] = analysis_result["summary"]["osm_types"].get(osm_type, 0) + 1
                    analysis_result["summary"]["categories"][category] = analysis_result["summary"]["categories"].get(category, 0) + 1
                    analysis_result["summary"]["countries"][country] = analysis_result["summary"]["countries"].get(country, 0) + 1

                    if place.get('extratags'):
                        analysis_result["summary"]["extratags_present"] += 1

                    place_data = {
                        "osm_id": place.get('osm_id'),
                        "osm_type": osm_type,
                        "category": category,
                        "type": place.get('type'),
                        "display_name": place.get('display_name'),
                        "lat": place.get('lat'),
                        "lon": place.get('lon'),
                        "importance": place.get('importance', 0),
                        "address": address,
                        "boundingbox": place.get('boundingbox'),
                        "licence": place.get('licence')
                    }

                    if place.get('extratags'):
                        place_data["extratags"] = place.get('extratags')
                    if place.get('namedetails'):
                        place_data["namedetails"] = place.get('namedetails')

                    analysis_result["places"].append(place_data)

                print(f"✅ OSM lookup: Found {len(places)} places for {len(osm_ids)} OSM IDs")
                print(f"   Format: {format_type}")

                if analysis_result["places"]:
                    print(f"\nAll lookup results:")
                    for i, place in enumerate(analysis_result["places"]):
                        print(f"   {i+1}. {place['display_name']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid response format",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid response format")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error looking up OSM objects: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to lookup OSM objects: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in lookup_osm_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def get_server_status_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting get_server_status_skill...")

    format_type = context.get('format', 'json')

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.status(format=format_type)

            if format_type == 'json':
                if isinstance(response, dict):
                    analysis_result = {
                        "success": True,
                        "status": "online",
                        "details": response,
                        "server_info": {
                            "status_code": response.get('status', 0),
                            "message": response.get('message', ''),
                            "data_updated": response.get('data_updated'),
                            "software_version": response.get('software_version'),
                            "database_version": response.get('database_version')
                        },
                        "timestamp": datetime.now().isoformat()
                    }

                    status_msg = response.get('message', 'Unknown')
                    print(f"✅ Server status: {status_msg}")
                    if response.get('software_version'):
                        print(f"   Software version: {response['software_version']}")

                else:
                    analysis_result = {
                        "success": False,
                        "error": "Invalid JSON response",
                        "response": response,
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"❌ Invalid JSON response")

            else:
                analysis_result = {
                    "success": True,
                    "status": "online",
                    "response_raw": str(response),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"✅ Server status (text format)")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting server status: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get server status: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_server_status_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def get_details_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting get_details_skill...")

    place_id = context.get('place_id')
    osm_type = context.get('osm_type')
    osm_id = context.get('osm_id')
    format_type = context.get('format', 'json')
    entrances = context.get('entrances', 0)
    linkedplaces = context.get('linkedplaces', 0)
    hierarchy = context.get('hierarchy', 0)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if not place_id and not (osm_type and osm_id):
            result = {"success": False, "error": "Either place_id or (osm_type and osm_id) are required"}
            return NominatimDataValue(result)

        try:
            response = client.details(
                place_id=place_id,
                osmtype=osm_type,
                osmid=osm_id,
                format=format_type,
                entrances=entrances,
                linkedplaces=linkedplaces,
                hierarchy=hierarchy
            )

            if isinstance(response, dict):
                analysis_result = {
                    "success": True,
                    "details": response,
                    "metadata": {
                        "place_id": response.get('place_id'),
                        "osm_type": response.get('osm_type'),
                        "osm_id": response.get('osm_id'),
                        "category": response.get('category'),
                        "type": response.get('type'),
                        "localname": response.get('localname'),
                        "importance": response.get('importance', 0),
                        "calculated_importance": response.get('calculated_importance', 0),
                        "rank_address": response.get('rank_address'),
                        "rank_search": response.get('rank_search'),
                        "isarea": response.get('isarea', False)
                    },
                    "additional_info": {
                        "has_names": bool(response.get('names')),
                        "has_extratags": bool(response.get('extratags')),
                        "has_geometry": bool(response.get('geometry')),
                        "has_centroid": bool(response.get('centroid')),
                        "has_entrances": bool(response.get('entrances') and len(response.get('entrances', [])) > 0),
                        "has_linkedplaces": bool(response.get('linkedplaces') and len(response.get('linkedplaces', [])) > 0),
                        "has_hierarchy": bool(response.get('hierarchy') and len(response.get('hierarchy', [])) > 0)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if response.get('names'):
                    analysis_result["names"] = response['names']
                if response.get('extratags'):
                    analysis_result["extratags"] = response['extratags']
                if response.get('geometry'):
                    analysis_result["geometry"] = response['geometry']
                if response.get('centroid'):
                    analysis_result["centroid"] = response['centroid']
                if response.get('entrances'):
                    analysis_result["entrances"] = response['entrances']
                if response.get('linkedplaces'):
                    analysis_result["linkedplaces"] = response['linkedplaces']
                if response.get('hierarchy'):
                    analysis_result["hierarchy"] = response['hierarchy']

                print(f"✅ Details retrieved successfully")
                print(f"   Format: {format_type}")
                if response.get('localname'):
                    print(f"   Place: {response.get('localname')}")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid response format",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid response format")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting details: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get details: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_details_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def get_deletable_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting get_deletable_skill...")

    format_type = context.get('format', 'json')

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.deletable(format=format_type)

            if isinstance(response, list):
                deletable_items = response

                analysis_result = {
                    "success": True,
                    "deletable_count": len(deletable_items),
                    "deletable_items": deletable_items,
                    "summary": {
                        "osm_types": {},
                        "reasons": {},
                        "oldest_timestamp": None,
                        "newest_timestamp": None
                    },
                    "timestamp": datetime.now().isoformat()
                }

                timestamps = []

                for item in deletable_items:
                    osm_type = item.get('osm_type', 'unknown')
                    reason = item.get('reason', 'unknown')
                    timestamp = item.get('timestamp')

                    analysis_result["summary"]["osm_types"][osm_type] = analysis_result["summary"]["osm_types"].get(osm_type, 0) + 1
                    analysis_result["summary"]["reasons"][reason] = analysis_result["summary"]["reasons"].get(reason, 0) + 1

                    if timestamp:
                        timestamps.append(timestamp)

                if timestamps:
                    analysis_result["summary"]["oldest_timestamp"] = min(timestamps)
                    analysis_result["summary"]["newest_timestamp"] = max(timestamps)

                print(f"✅ Deletable items: Found {len(deletable_items)} items")
                print(f"   Format: {format_type}")

            else:
                analysis_result = {
                    "success": True,
                    "message": "No deletable items or empty list",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"✅ No deletable items found")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting deletable items: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get deletable items: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_deletable_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def get_polygons_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting get_polygons_skill...")

    format_type = context.get('format', 'json')

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.polygons(format=format_type)

            if isinstance(response, list):
                polygons = response

                analysis_result = {
                    "success": True,
                    "broken_polygons_count": len(polygons),
                    "polygons": polygons,
                    "summary": {
                        "osm_types": {},
                        "error_types": {},
                        "countries": {}
                    },
                    "timestamp": datetime.now().isoformat()
                }

                for polygon in polygons:
                    osm_type = polygon.get('osm_type', 'unknown')
                    error = polygon.get('error', 'unknown')
                    country_code = polygon.get('country_code', 'unknown')

                    analysis_result["summary"]["osm_types"][osm_type] = analysis_result["summary"]["osm_types"].get(osm_type, 0) + 1
                    analysis_result["summary"]["error_types"][error] = analysis_result["summary"]["error_types"].get(error, 0) + 1
                    analysis_result["summary"]["countries"][country_code] = analysis_result["summary"]["countries"].get(country_code, 0) + 1

                print(f"✅ Broken polygons: Found {len(polygons)} polygons")
                print(f"   Format: {format_type}")

            else:
                analysis_result = {
                    "success": True,
                    "message": "No broken polygons or empty list",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"✅ No broken polygons found")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting polygons: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get polygons: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_polygons_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def search_with_polygon_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting search_with_polygon_skill...")

    query = context.get('query', '')
    polygon_format = context.get('polygon_format', 'kml')
    limit = context.get('limit', 10)
    format_type = context.get('format', 'xml')

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.search_with_polygon(
                query=query,
                polygon_format=polygon_format,
                limit=limit,
                format_type=format_type
            )

            if isinstance(response, str) or (isinstance(response, dict) and response.get('error')):
                analysis_result = {
                    "success": True,
                    "polygon_format": polygon_format,
                    "response_format": format_type,
                    "has_polygon_data": True,
                    "response_length": len(str(response)),
                    "timestamp": datetime.now().isoformat()
                }

                print(f"✅ Search with polygon: Raw XML/KML response")
                print(f"   Polygon format: {polygon_format}")
                print(f"   Response format: {format_type}")

            elif isinstance(response, list):
                analysis_result = {
                    "success": True,
                    "polygon_format": polygon_format,
                    "response_format": format_type,
                    "places_count": len(response),
                    "has_polygon_data": any('polygonpoints' in p or 'svg' in p for p in response),
                    "timestamp": datetime.now().isoformat()
                }

                print(f"✅ Search with polygon: Found {len(response)} places")
                print(f"   Polygon format: {polygon_format}")

            else:
                analysis_result = {
                    "success": True,
                    "polygon_format": polygon_format,
                    "response_format": format_type,
                    "response_type": type(response).__name__,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"✅ Search with polygon: Response type: {type(response).__name__}")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error searching with polygon: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to search with polygon: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_with_polygon_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def reverse_with_polygon_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting reverse_with_polygon_skill...")

    lat = context.get('lat')
    lon = context.get('lon')
    polygon_format = context.get('polygon_format', 'kml')
    format_type = context.get('format', 'xml')

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if lat is None or lon is None:
            result = {"success": False, "error": "Latitude and longitude are required"}
            return NominatimDataValue(result)

        try:
            response = client.reverse_with_polygon(
                lat=lat,
                lon=lon,
                polygon_format=polygon_format,
                format=format_type
            )

            analysis_result = {
                "success": True,
                "coordinates": {"lat": lat, "lon": lon},
                "polygon_format": polygon_format,
                "response_format": format_type,
                "response_sample": str(response),
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Reverse with polygon: Processed coordinates ({lat}, {lon})")
            print(f"   Polygon format: {polygon_format}")
            print(f"   Response format: {format_type}")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error reversing with polygon: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to reverse with polygon: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in reverse_with_polygon_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def search_geojson_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting search_geojson_skill...")

    query = context.get('query', '')
    limit = context.get('limit', 10)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.search_geojson(
                query=query,
                limit=limit
            )

            analysis_result = {
                "success": True,
                "format": "geojson",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }

            if isinstance(response, dict):
                features = response.get('features', [])

                analysis_result.update({
                    "features_count": len(features),
                    "features_sample": features,
                    "type": response.get('type', 'Unknown'),
                    "licence": response.get('licence', 'Unknown')
                })

                print(f"✅ GeoJSON search: Found {len(features)} features for query '{query}'")
                print(f"   Format: GeoJSON")

                if features:
                    print(f"\nAll features:")
                    for i, feature in enumerate(features):
                        props = feature.get('properties', {})
                        print(f"   {i+1}. {props.get('display_name', 'Unknown')}")

            elif isinstance(response, list):
                analysis_result.update({
                    "features_count": len(response),
                    "features_sample": response,
                    "response_type": "list"
                })

                print(f"✅ GeoJSON search: Found {len(response)} items (list format)")

            else:
                analysis_result.update({
                    "response_raw": str(response),
                    "response_type": type(response).__name__
                })

                print(f"✅ GeoJSON search: Raw response (type: {type(response).__name__})")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error searching GeoJSON: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to search GeoJSON: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_geojson_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def reverse_geojson_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting reverse_geojson_skill...")

    lat = context.get('lat')
    lon = context.get('lon')
    zoom = context.get('zoom', 18)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if lat is None or lon is None:
            result = {"success": False, "error": "Latitude and longitude are required"}
            return NominatimDataValue(result)

        try:
            response = client.reverse_geojson(
                lat=lat,
                lon=lon,
                zoom=zoom
            )

            if isinstance(response, dict) and response.get('type') == 'FeatureCollection':
                features = response.get('features', [])

                analysis_result = {
                    "success": True,
                    "format": "geojson",
                    "coordinates": {"lat": lat, "lon": lon, "zoom": zoom},
                    "features_count": len(features),
                    "features_sample": features,
                    "metadata": {
                        "licence": response.get('licence')
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"✅ GeoJSON reverse: Found {len(features)} features for coordinates ({lat}, {lon})")
                print(f"   Format: GeoJSON")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid GeoJSON response",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid GeoJSON response")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error reversing GeoJSON: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to reverse GeoJSON: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in reverse_geojson_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def search_geocodejson_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting search_geocodejson_skill...")

    query = context.get('query', '')
    limit = context.get('limit', 10)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.search_geocodejson(
                query=query,
                limit=limit
            )

            analysis_result = {
                "success": True,
                "format": "geocodejson",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }

            if isinstance(response, dict):
                features = response.get('features', [])
                geocoding = response.get('geocoding', {})

                analysis_result.update({
                    "features_count": len(features),
                    "features_sample": features,
                    "geocoding_info": geocoding,
                    "type": response.get('type', 'Unknown'),
                    "licence": response.get('licence', 'Unknown')
                })

                print(f"✅ GeocodeJSON search: Found {len(features)} features for query '{query}'")
                print(f"   Format: GeocodeJSON")
                print(f"   Response type: {response.get('type', 'Unknown')}")

                if features:
                    print(f"\nAll features:")
                    for i, feature in enumerate(features):
                        props = feature.get('properties', {})
                        geocoding_props = props.get('geocoding', {})
                        print(f"   {i+1}. {geocoding_props.get('label', 'Unknown')}")

            elif isinstance(response, list):
                analysis_result.update({
                    "features_count": len(response),
                    "features_sample": response,
                    "response_type": "list"
                })

                print(f"✅ GeocodeJSON search: Found {len(response)} items (list format)")
                print(f"   Format: GeocodeJSON")

            else:
                analysis_result.update({
                    "response_raw": str(response),
                    "response_type": type(response).__name__
                })

                print(f"✅ GeocodeJSON search: Raw response (type: {type(response).__name__})")
                print(f"   Format: GeocodeJSON")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error searching GeocodeJSON: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to search GeocodeJSON: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_geocodejson_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def reverse_geocodejson_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting reverse_geocodejson_skill...")

    lat = context.get('lat')
    lon = context.get('lon')
    zoom = context.get('zoom', 18)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if lat is None or lon is None:
            result = {"success": False, "error": "Latitude and longitude are required"}
            return NominatimDataValue(result)

        try:
            response = client.reverse_geocodejson(
                lat=lat,
                lon=lon,
                zoom=zoom
            )

            if isinstance(response, dict):
                analysis_result = {
                    "success": True,
                    "format": "geocodejson",
                    "coordinates": {"lat": lat, "lon": lon, "zoom": zoom},
                    "response_data": response,
                    "geocoding_info": response.get('geocoding', {}),
                    "timestamp": datetime.now().isoformat()
                }

                print(f"✅ GeocodeJSON reverse: Processed coordinates ({lat}, {lon})")
                print(f"   Format: GeocodeJSON")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid GeocodeJSON response",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid GeocodeJSON response")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error reversing GeocodeJSON: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to reverse GeocodeJSON: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in reverse_geocodejson_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def search_jsonv2_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting search_jsonv2_skill...")

    query = context.get('query', '')
    limit = context.get('limit', 10)
    addressdetails = context.get('addressdetails', 1)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.search_jsonv2(
                query=query,
                limit=limit,
                addressdetails=addressdetails
            )

            if isinstance(response, list):
                places = response

                analysis_result = {
                    "success": True,
                    "format": "jsonv2",
                    "places_count": len(places),
                    "places_sample": places,
                    "summary": {
                        "addresstypes": {},
                        "categories": {}
                    },
                    "timestamp": datetime.now().isoformat()
                }

                for place in places:
                    addresstype = place.get('addresstype', 'unknown')
                    category = place.get('category', 'unknown')

                    analysis_result["summary"]["addresstypes"][addresstype] = analysis_result["summary"]["addresstypes"].get(addresstype, 0) + 1
                    analysis_result["summary"]["categories"][category] = analysis_result["summary"]["categories"].get(category, 0) + 1

                print(f"✅ JSONv2 search: Found {len(places)} places for query '{query}'")
                print(f"   Format: JSONv2")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid JSONv2 response",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid JSONv2 response")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error searching JSONv2: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to search JSONv2: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_jsonv2_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def reverse_jsonv2_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting reverse_jsonv2_skill...")

    lat = context.get('lat')
    lon = context.get('lon')
    zoom = context.get('zoom', 18)
    addressdetails = context.get('addressdetails', 1)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if lat is None or lon is None:
            result = {"success": False, "error": "Latitude and longitude are required"}
            return NominatimDataValue(result)

        try:
            response = client.reverse_jsonv2(
                lat=lat,
                lon=lon,
                zoom=zoom,
                addressdetails=addressdetails
            )

            if isinstance(response, dict):
                analysis_result = {
                    "success": True,
                    "format": "jsonv2",
                    "coordinates": {"lat": lat, "lon": lon, "zoom": zoom},
                    "place_data": response,
                    "address_info": response.get('address', {}),
                    "timestamp": datetime.now().isoformat()
                }

                print(f"✅ JSONv2 reverse: Processed coordinates ({lat}, {lon})")
                print(f"   Format: JSONv2")
                if response.get('display_name'):
                    print(f"   Display name: {response['display_name']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid JSONv2 response",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid JSONv2 response")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error reversing JSONv2: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to reverse JSONv2: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in reverse_jsonv2_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def search_xml_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting search_xml_skill...")

    query = context.get('query', '')
    limit = context.get('limit', 10)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        try:
            response = client.search_xml(
                query=query,
                limit=limit
            )

            analysis_result = {
                "success": True,
                "format": "xml",
                "query": query,
                "response_sample": str(response),
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ XML search: Processed query '{query}'")
            print(f"   Format: XML")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error searching XML: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to search XML: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_xml_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def reverse_xml_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting reverse_xml_skill...")

    lat = context.get('lat')
    lon = context.get('lon')
    zoom = context.get('zoom', 18)

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if lat is None or lon is None:
            result = {"success": False, "error": "Latitude and longitude are required"}
            return NominatimDataValue(result)

        try:
            response = client.reverse_xml(
                lat=lat,
                lon=lon,
                zoom=zoom
            )

            analysis_result = {
                "success": True,
                "format": "xml",
                "coordinates": {"lat": lat, "lon": lon, "zoom": zoom},
                "response_sample": str(response),
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ XML reverse: Processed coordinates ({lat}, {lon})")
            print(f"   Format: XML")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error reversing XML: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to reverse XML: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in reverse_xml_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)

def lookup_with_extratags_skill(context: Dict[str, Any]) -> NominatimDataValue:
    print("Starting lookup_with_extratags_skill...")

    osm_ids = context.get('osm_ids', [])

    try:
        client = context.get('nominatim_client')

        if not client:
            result = {"success": False, "error": "Nominatim client not available"}
            return NominatimDataValue(result)

        if not osm_ids:
            result = {"success": False, "error": "OSM IDs are required"}
            return NominatimDataValue(result)

        try:
            response = client.lookup_with_extratags(
                osm_ids=osm_ids
            )

            if isinstance(response, list):
                places = response

                analysis_result = {
                    "success": True,
                    "format": "json",
                    "extratags_enabled": True,
                    "places_count": len(places),
                    "places_with_extratags": 0,
                    "places_sample": places,
                    "timestamp": datetime.now().isoformat()
                }

                for place in places:
                    if place.get('extratags'):
                        analysis_result["places_with_extratags"] += 1

                print(f"✅ Lookup with extratags: Found {len(places)} places")
                print(f"   Places with extratags: {analysis_result['places_with_extratags']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": "Invalid response",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Invalid response")

            return NominatimDataValue(analysis_result)

        except Exception as e:
            print(f"Error looking up with extratags: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to lookup with extratags: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return NominatimDataValue(analysis_result)

    except Exception as e:
        print(f"Error in lookup_with_extratags_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return NominatimDataValue(result)
