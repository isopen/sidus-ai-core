from typing import Dict, Any
from datetime import datetime, timedelta

class OpenMeteoDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def get_current_weather_skill(context: Dict[str, Any]) -> OpenMeteoDataValue:
    try:
        client = context.get('openmeteo_client')

        if not client:
            return OpenMeteoDataValue({"success": False, "error": "OpenMeteo client not available"})

        latitude = context.get('latitude')
        longitude = context.get('longitude')

        if not latitude or not longitude:
            return OpenMeteoDataValue({"success": False, "error": "Latitude and longitude are required"})

        current_params = [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "is_day", "precipitation", "rain", "showers", "snowfall",
            "weather_code", "cloud_cover", "pressure_msl", "surface_pressure",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
        ]

        response = client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            current=current_params,
            timezone=context.get('timezone', 'auto'),
            forecast_days=context.get('forecast_days', 1)
        )

        if 'current' not in response:
            return OpenMeteoDataValue({"success": False, "error": "No current weather data available"})

        current_data = response.get('current', {})
        current_units = response.get('current_units', {})

        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }

        weather_code = current_data.get('weather_code', 0)
        weather_description = weather_codes.get(weather_code, "Unknown")

        analysis_result = {
            "success": True,
            "latitude": response.get('latitude'),
            "longitude": response.get('longitude'),
            "elevation": response.get('elevation'),
            "timezone": response.get('timezone'),
            "current": {
                "time": current_data.get('time'),
                "temperature_2m": {
                    "value": current_data.get('temperature_2m'),
                    "unit": current_units.get('temperature_2m')
                },
                "relative_humidity_2m": {
                    "value": current_data.get('relative_humidity_2m'),
                    "unit": current_units.get('relative_humidity_2m')
                },
                "apparent_temperature": {
                    "value": current_data.get('apparent_temperature'),
                    "unit": current_units.get('apparent_temperature')
                },
                "weather": {
                    "code": weather_code,
                    "description": weather_description,
                    "is_day": current_data.get('is_day')
                },
                "precipitation": {
                    "total": current_data.get('precipitation'),
                    "rain": current_data.get('rain'),
                    "showers": current_data.get('showers'),
                    "snowfall": current_data.get('snowfall'),
                    "units": {
                        "precipitation": current_units.get('precipitation'),
                        "rain": current_units.get('rain'),
                        "showers": current_units.get('showers'),
                        "snowfall": current_units.get('snowfall')
                    }
                },
                "cloud_cover": {
                    "value": current_data.get('cloud_cover'),
                    "unit": current_units.get('cloud_cover')
                },
                "pressure": {
                    "msl": {
                        "value": current_data.get('pressure_msl'),
                        "unit": current_units.get('pressure_msl')
                    },
                    "surface": {
                        "value": current_data.get('surface_pressure'),
                        "unit": current_units.get('surface_pressure')
                    }
                },
                "wind": {
                    "speed_10m": {
                        "value": current_data.get('wind_speed_10m'),
                        "unit": current_units.get('wind_speed_10m')
                    },
                    "direction_10m": {
                        "value": current_data.get('wind_direction_10m'),
                        "unit": current_units.get('wind_direction_10m')
                    },
                    "gusts_10m": {
                        "value": current_data.get('wind_gusts_10m'),
                        "unit": current_units.get('wind_gusts_10m')
                    }
                }
            },
            "summary": {
                "conditions": weather_description,
                "temperature_feeling": "Cold" if current_data.get('apparent_temperature', 0) < 10 else 
                                      "Cool" if current_data.get('apparent_temperature', 0) < 20 else 
                                      "Warm" if current_data.get('apparent_temperature', 0) < 30 else "Hot",
                "precipitation_type": "Snow" if current_data.get('snowfall', 0) > 0 else 
                                     "Rain" if current_data.get('rain', 0) > 0 else "None"
            },
            "timestamp": datetime.now().isoformat()
        }

        return OpenMeteoDataValue(analysis_result)

    except Exception as e:
        return OpenMeteoDataValue({"success": False, "error": f"Failed to get current weather: {str(e)}"})

def get_forecast_skill(context: Dict[str, Any]) -> OpenMeteoDataValue:
    try:
        client = context.get('openmeteo_client')

        if not client:
            return OpenMeteoDataValue({"success": False, "error": "OpenMeteo client not available"})

        latitude = context.get('latitude')
        longitude = context.get('longitude')
        forecast_type = context.get('forecast_type', 'daily')

        if not latitude or not longitude:
            return OpenMeteoDataValue({"success": False, "error": "Latitude and longitude are required"})

        if forecast_type == 'hourly':
            hourly_params = [
                "temperature_2m", "relative_humidity_2m", "dew_point_2m",
                "apparent_temperature", "precipitation_probability",
                "precipitation", "rain", "showers", "snowfall",
                "snow_depth", "weather_code", "pressure_msl",
                "surface_pressure", "cloud_cover", "cloud_cover_low",
                "cloud_cover_mid", "cloud_cover_high",
                "visibility", "evapotranspiration", "et0_fao_evapotranspiration",
                "vapour_pressure_deficit", "wind_speed_10m",
                "wind_speed_80m", "wind_speed_120m", "wind_speed_180m",
                "wind_direction_10m", "wind_direction_80m",
                "wind_direction_120m", "wind_direction_180m",
                "wind_gusts_10m", "temperature_80m", "temperature_120m",
                "temperature_180m", "soil_temperature_0cm",
                "soil_temperature_6cm", "soil_temperature_18cm",
                "soil_temperature_54cm", "soil_moisture_0_1cm",
                "soil_moisture_1_3cm", "soil_moisture_3_9cm",
                "soil_moisture_9_27cm", "soil_moisture_27_81cm"
            ]

            daily_params = None
        else:
            hourly_params = None
            daily_params = [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "apparent_temperature_max", "apparent_temperature_min",
                "sunrise", "sunset", "daylight_duration", "sunshine_duration",
                "uv_index_max", "uv_index_clear_sky_max",
                "precipitation_sum", "rain_sum", "showers_sum", "snowfall_sum",
                "precipitation_hours", "precipitation_probability_max",
                "wind_speed_10m_max", "wind_gusts_10m_max",
                "wind_direction_10m_dominant", "shortwave_radiation_sum",
                "et0_fao_evapotranspiration"
            ]

        response = client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            hourly=hourly_params,
            daily=daily_params,
            timezone=context.get('timezone', 'auto'),
            forecast_days=context.get('forecast_days', 5),
            past_days=context.get('past_days', 0),
            start_date=context.get('start_date'),
            end_date=context.get('end_date')
        )

        forecast_data = {}

        if forecast_type == 'hourly' and 'hourly' in response:
            times = response['hourly'].get('time', [])
            forecast_data = {
                "forecast_type": "hourly",
                "timestamps": times,
                "data_points": len(times),
                "parameters": {}
            }

            for param in hourly_params:
                if param in response['hourly']:
                    forecast_data["parameters"][param] = {
                        "values": response['hourly'][param],
                        "unit": response.get('hourly_units', {}).get(param, '')
                    }

        elif forecast_type == 'daily' and 'daily' in response:
            times = response['daily'].get('time', [])
            forecast_data = {
                "forecast_type": "daily",
                "dates": times,
                "days": len(times),
                "parameters": {}
            }

            for param in daily_params:
                if param in response['daily']:
                    forecast_data["parameters"][param] = {
                        "values": response['daily'][param],
                        "unit": response.get('daily_units', {}).get(param, '')
                    }

        analysis_result = {
            "success": True,
            "latitude": response.get('latitude'),
            "longitude": response.get('longitude'),
            "elevation": response.get('elevation'),
            "timezone": response.get('timezone'),
            "forecast": forecast_data,
            "generation_time_ms": response.get('generationtime_ms'),
            "timestamp": datetime.now().isoformat()
        }

        return OpenMeteoDataValue(analysis_result)

    except Exception as e:
        return OpenMeteoDataValue({"success": False, "error": f"Failed to get forecast: {str(e)}"})

def get_air_quality_skill(context: Dict[str, Any]) -> OpenMeteoDataValue:
    try:
        client = context.get('openmeteo_client')

        if not client:
            return OpenMeteoDataValue({"success": False, "error": "OpenMeteo client not available"})

        latitude = context.get('latitude')
        longitude = context.get('longitude')

        if not latitude or not longitude:
            return OpenMeteoDataValue({"success": False, "error": "Latitude and longitude are required"})

        hourly_params = context.get('hourly', [
            "pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide",
            "sulphur_dioxide", "ozone", "european_aqi", "us_aqi"
        ])

        domains = context.get('domains', 'auto')
        forecast_days = context.get('forecast_days', 5)

        response = client.get_air_quality(
            latitude=latitude,
            longitude=longitude,
            hourly=hourly_params,
            domains=domains,
            timezone=context.get('timezone', 'auto'),
            past_days=context.get('past_days', 0),
            forecast_days=forecast_days
        )

        if 'hourly' not in response:
            return OpenMeteoDataValue({"success": False, "error": "No air quality data available"})

        times = response['hourly'].get('time', [])

        aqi_categories = {
            "european_aqi": {
                (0, 20): "Good",
                (20, 40): "Fair",
                (40, 60): "Moderate",
                (60, 80): "Poor",
                (80, 100): "Very Poor",
                (100, float('inf')): "Extremely Poor"
            },
            "us_aqi": {
                (0, 50): "Good",
                (51, 100): "Moderate",
                (101, 150): "Unhealthy for Sensitive Groups",
                (151, 200): "Unhealthy",
                (201, 300): "Very Unhealthy",
                (301, 500): "Hazardous"
            }
        }

        analysis_result = {
            "success": True,
            "latitude": response.get('latitude'),
            "longitude": response.get('longitude'),
            "elevation": response.get('elevation'),
            "timezone": response.get('timezone'),
            "domain": response.get('domain', domains),
            "air_quality": {
                "timestamps": times,
                "data_points": len(times),
                "parameters": {},
                "current_conditions": {}
            },
            "timestamp": datetime.now().isoformat()
        }

        for param in hourly_params:
            if param in response['hourly']:
                values = response['hourly'][param]
                current_value = values[0] if values else None

                param_data = {
                    "values": values,
                    "unit": response.get('hourly_units', {}).get(param, ''),
                    "current": current_value
                }

                if param in aqi_categories:
                    if current_value is not None:
                        for (low, high), category in aqi_categories[param].items():
                            if low <= current_value < high:
                                param_data["category"] = category
                                break

                analysis_result["air_quality"]["parameters"][param] = param_data

                if current_value is not None:
                    analysis_result["air_quality"]["current_conditions"][param] = {
                        "value": current_value,
                        "unit": response.get('hourly_units', {}).get(param, '')
                    }

        return OpenMeteoDataValue(analysis_result)

    except Exception as e:
        return OpenMeteoDataValue({"success": False, "error": f"Failed to get air quality data: {str(e)}"})

def get_previous_runs_skill(context: Dict[str, Any]) -> OpenMeteoDataValue:
    try:
        client = context.get('openmeteo_client')

        if not client:
            return OpenMeteoDataValue({"success": False, "error": "OpenMeteo client not available"})

        latitude = context.get('latitude')
        longitude = context.get('longitude')

        if not latitude or not longitude:
            return OpenMeteoDataValue({"success": False, "error": "Latitude and longitude are required"})

        hourly_params = context.get('hourly', [
            "temperature_2m",
            "temperature_2m_previous_day1",
            "temperature_2m_previous_day2",
            "temperature_2m_previous_day3",
            "temperature_2m_previous_day4",
            "temperature_2m_previous_day5"
        ])

        response = client.get_previous_runs(
            latitude=latitude,
            longitude=longitude,
            hourly=hourly_params,
            timezone=context.get('timezone', 'auto')
        )

        if 'hourly' not in response:
            return OpenMeteoDataValue({"success": False, "error": "No previous runs data available"})

        times = response['hourly'].get('time', [])

        analysis_result = {
            "success": True,
            "latitude": response.get('latitude'),
            "longitude": response.get('longitude'),
            "elevation": response.get('elevation'),
            "timezone": response.get('timezone'),
            "previous_runs": {
                "timestamps": times,
                "data_points": len(times),
                "parameters": {}
            },
            "comparison": {},
            "timestamp": datetime.now().isoformat()
        }

        temperature_data = {}
        for param in hourly_params:
            if param in response['hourly']:
                values = response['hourly'][param]
                unit = response.get('hourly_units', {}).get(param, '')

                analysis_result["previous_runs"]["parameters"][param] = {
                    "values": values,
                    "unit": unit,
                    "statistics": {
                        "min": min(values) if values else None,
                        "max": max(values) if values else None,
                        "avg": sum(values)/len(values) if values else None
                    }
                }

                if 'temperature_2m' in param:
                    if param == 'temperature_2m':
                        temperature_data['current'] = values
                    else:
                        day_num = param.replace('temperature_2m_previous_day', '')
                        temperature_data[f'day_{day_num}'] = values

        if temperature_data.get('current') and len(temperature_data) > 1:
            current_avg = sum(temperature_data['current'])/len(temperature_data['current'])
            comparison = {}

            for key, values in temperature_data.items():
                if key != 'current':
                    day_avg = sum(values)/len(values)
                    diff = current_avg - day_avg
                    comparison[key] = {
                        "average": day_avg,
                        "difference_from_current": diff,
                        "difference_percentage": (diff / day_avg * 100) if day_avg != 0 else 0
                    }

            analysis_result["comparison"] = comparison

        return OpenMeteoDataValue(analysis_result)

    except Exception as e:
        return OpenMeteoDataValue({"success": False, "error": f"Failed to get previous runs: {str(e)}"})

def get_weather_statistics_skill(context: Dict[str, Any]) -> OpenMeteoDataValue:
    try:
        client = context.get('openmeteo_client')

        if not client:
            return OpenMeteoDataValue({"success": False, "error": "OpenMeteo client not available"})

        latitude = context.get('latitude')
        longitude = context.get('longitude')

        if not latitude or not longitude:
            return OpenMeteoDataValue({"success": False, "error": "Latitude and longitude are required"})

        days = context.get('days', 7)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days-1)).strftime('%Y-%m-%d')

        response = client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            daily=[
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "weather_code"
            ],
            start_date=start_date,
            end_date=end_date,
            timezone=context.get('timezone', 'auto')
        )

        if 'daily' not in response:
            return OpenMeteoDataValue({"success": False, "error": "No weather statistics available"})

        dates = response['daily'].get('time', [])

        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }

        analysis_result = {
            "success": True,
            "latitude": response.get('latitude'),
            "longitude": response.get('longitude'),
            "statistics_period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": len(dates)
            },
            "statistics": {
                "temperature": {},
                "precipitation": {},
                "weather_conditions": {}
            },
            "timestamp": datetime.now().isoformat()
        }

        max_temps = response['daily'].get('temperature_2m_max', [])
        min_temps = response['daily'].get('temperature_2m_min', [])
        precip = response['daily'].get('precipitation_sum', [])
        weather_codes_list = response['daily'].get('weather_code', [])

        if max_temps and min_temps:
            avg_max = sum(max_temps) / len(max_temps) if max_temps else 0
            avg_min = sum(min_temps) / len(min_temps) if min_temps else 0
            avg_temp = (avg_max + avg_min) / 2 if max_temps and min_temps else 0

            analysis_result["statistics"]["temperature"] = {
                "average_max": avg_max,
                "average_min": avg_min,
                "average": avg_temp,
                "max_recorded": max(max_temps) if max_temps else 0,
                "min_recorded": min(min_temps) if min_temps else 0,
                "range": (max(max_temps) - min(min_temps)) if max_temps and min_temps else 0,
                "unit": response.get('daily_units', {}).get('temperature_2m_max', '°C')
            }

        if precip:
            total_precip = sum(precip) if precip else 0
            rainy_days = sum(1 for p in precip if p > 0) if precip else 0
            max_daily = max(precip) if precip else 0

            analysis_result["statistics"]["precipitation"] = {
                "total": total_precip,
                "average_daily": total_precip / len(precip) if precip else 0,
                "rainy_days": rainy_days,
                "rainy_days_percentage": (rainy_days / len(precip) * 100) if precip else 0,
                "max_daily": max_daily,
                "unit": response.get('daily_units', {}).get('precipitation_sum', 'mm')
            }

        if weather_codes_list:
            weather_counts = {}
            for code in weather_codes_list:
                condition = weather_codes.get(code, f"Unknown ({code})")
                weather_counts[condition] = weather_counts.get(condition, 0) + 1

            most_common = max(weather_counts.items(), key=lambda x: x[1]) if weather_counts else ("Unknown", 0)

            analysis_result["statistics"]["weather_conditions"] = {
                "distribution": weather_counts,
                "most_common": {
                    "condition": most_common[0],
                    "days": most_common[1],
                    "percentage": (most_common[1] / len(weather_codes_list) * 100) if weather_codes_list else 0
                },
                "clear_days": weather_counts.get("Clear sky", 0) + weather_counts.get("Mainly clear", 0),
                "precipitation_days": sum(count for condition, count in weather_counts.items() 
                                        if condition and ("rain" in condition.lower() or "snow" in condition.lower() 
                                        or "drizzle" in condition.lower() or "showers" in condition.lower()))
            }

        return OpenMeteoDataValue(analysis_result)

    except Exception as e:
        return OpenMeteoDataValue({"success": False, "error": f"Failed to get weather statistics: {str(e)}"})

def get_timezone_data_skill(context: Dict[str, Any]) -> OpenMeteoDataValue:
    try:
        client = context.get('openmeteo_client')

        if not client:
            return OpenMeteoDataValue({"success": False, "error": "OpenMeteo client not available"})

        latitude = context.get('latitude')
        longitude = context.get('longitude')

        if not latitude or not longitude:
            return OpenMeteoDataValue({"success": False, "error": "Latitude and longitude are required"})

        try:
            response = client.get_forecast(
                latitude=latitude,
                longitude=longitude,
                current=[],
                timezone="auto",
                forecast_days=0
            )

            if 'timezone' not in response:
                raise Exception("No timezone in response")

        except Exception:
            hour_offset = int(longitude / 15)

            timezone_name = f"UTC{'+' if hour_offset >= 0 else ''}{hour_offset}"
            utc_offset = hour_offset * 3600

            from datetime import datetime, timezone as tz, timedelta
            utc_now = datetime.now(tz.utc)
            local_time = utc_now + timedelta(seconds=utc_offset)

            hour = local_time.hour
            is_daytime = 6 <= hour < 18

            timezone_info = {
                "name": timezone_name,
                "abbreviation": timezone_name,
                "utc_offset_seconds": utc_offset,
                "utc_offset_formatted": f"UTC{'+' if hour_offset >= 0 else ''}{hour_offset:02d}:00",
                "current_utc": utc_now.isoformat(),
                "current_local": local_time.isoformat(),
                "current_time_formatted": local_time.strftime('%Y-%m-%d %H:%M:%S'),
                "is_daytime": is_daytime,
                "day_night_status": "Daytime" if is_daytime else "Nighttime",
                "time_of_day": "Morning" if 6 <= hour < 12 else "Afternoon" if 12 <= hour < 18 else "Evening" if 18 <= hour < 22 else "Night",
                "hour": hour,
                "source": "estimated from longitude"
            }

            analysis_result = {
                "success": True,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_data": timezone_info,
                "timestamp": datetime.now().isoformat(),
                "note": "Used estimated timezone (approximate)"
            }

            return OpenMeteoDataValue(analysis_result)
        else:
            utc_offset = response.get('utc_offset_seconds', 0)
            timezone_name = response.get('timezone', 'Unknown')
            timezone_abbr = response.get('timezone_abbreviation', 'Unknown')

            from datetime import datetime, timezone as tz, timedelta
            utc_now = datetime.now(tz.utc)
            local_time = utc_now + timedelta(seconds=utc_offset)

            is_day = response.get('current', {}).get('is_day', 0)
            hour = local_time.hour

            timezone_info = {
                "name": timezone_name,
                "abbreviation": timezone_abbr,
                "utc_offset_seconds": utc_offset,
                "utc_offset_formatted": f"UTC{'+' if utc_offset >= 0 else ''}{utc_offset//3600:02d}:{abs(utc_offset%3600)//60:02d}",
                "current_utc": utc_now.isoformat(),
                "current_local": local_time.isoformat(),
                "current_time_formatted": local_time.strftime('%Y-%m-%d %H:%M:%S'),
                "is_daytime": bool(is_day),
                "day_night_status": "Daytime" if is_day else "Nighttime",
                "time_of_day": "Morning" if 6 <= hour < 12 else "Afternoon" if 12 <= hour < 18 else "Evening" if 18 <= hour < 22 else "Night",
                "hour": hour,
                "source": "OpenMeteo API"
            }

            analysis_result = {
                "success": True,
                "latitude": response.get('latitude'),
                "longitude": response.get('longitude'),
                "timezone_data": timezone_info,
                "timestamp": datetime.now().isoformat()
            }

            return OpenMeteoDataValue(analysis_result)

    except Exception as e:
        return OpenMeteoDataValue({"success": False, "error": f"Failed to get timezone data: {str(e)}"})

def get_weather_comparison_skill(context: Dict[str, Any]) -> OpenMeteoDataValue:
    try:
        client = context.get('openmeteo_client')

        if not client:
            return OpenMeteoDataValue({"success": False, "error": "OpenMeteo client not available"})

        locations = context.get('locations')

        if not locations or not isinstance(locations, list):
            return OpenMeteoDataValue({"success": False, "error": "Locations list is required"})

        if len(locations) > 5:
            return OpenMeteoDataValue({"success": False, "error": "Maximum 5 locations allowed"})

        comparison_data = []

        for loc in locations:
            try:
                result = client.get_forecast(
                    latitude=loc.get('latitude'),
                    longitude=loc.get('longitude'),
                    current=["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
                    timezone=loc.get('timezone', 'auto')
                )

                if 'current' in result:
                    current = result['current']

                    weather_codes = {
                        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                        45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
                        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
                    }

                    weather_code = current.get('weather_code', 0)

                    location_data = {
                        "name": loc.get('name', f"{loc['latitude']},{loc['longitude']}"),
                        "latitude": result.get('latitude'),
                        "longitude": result.get('longitude'),
                        "elevation": result.get('elevation'),
                        "timezone": result.get('timezone'),
                        "current": {
                            "temperature": current.get('temperature_2m'),
                            "temperature_unit": result.get('current_units', {}).get('temperature_2m', '°C'),
                            "humidity": current.get('relative_humidity_2m'),
                            "humidity_unit": result.get('current_units', {}).get('relative_humidity_2m', '%'),
                            "weather_code": weather_code,
                            "weather_description": weather_codes.get(weather_code, "Unknown"),
                            "wind_speed": current.get('wind_speed_10m'),
                            "wind_speed_unit": result.get('current_units', {}).get('wind_speed_10m', 'm/s'),
                            "is_day": current.get('is_day')
                        },
                        "comfort_index": 0
                    }

                    temp = current.get('temperature_2m', 20)
                    humidity = current.get('relative_humidity_2m', 50)
                    wind = current.get('wind_speed_10m', 5)

                    comfort_score = 100
                    comfort_score -= abs(temp - 22) * 2
                    comfort_score -= abs(humidity - 50) * 0.5
                    comfort_score += min(wind, 10)

                    if "rain" in location_data["current"]["weather_description"].lower():
                        comfort_score -= 20
                    if "snow" in location_data["current"]["weather_description"].lower():
                        comfort_score -= 30
                    if "thunderstorm" in location_data["current"]["weather_description"].lower():
                        comfort_score -= 40

                    location_data["comfort_index"] = max(0, min(100, comfort_score))

                    comparison_data.append(location_data)

            except Exception as e:
                comparison_data.append({
                    "name": loc.get('name', f"{loc.get('latitude')},{loc.get('longitude')}"),
                    "error": str(e)
                })

        if not comparison_data:
            return OpenMeteoDataValue({"success": False, "error": "No comparison data available"})

        sorted_by_temp = sorted([d for d in comparison_data if 'current' in d], 
                               key=lambda x: x['current']['temperature'], reverse=True)
        sorted_by_comfort = sorted([d for d in comparison_data if 'comfort_index' in d], 
                                  key=lambda x: x['comfort_index'], reverse=True)

        analysis_result = {
            "success": True,
            "locations_count": len(comparison_data),
            "locations": comparison_data,
            "comparison": {
                "warmest": sorted_by_temp[0]['name'] if sorted_by_temp else None,
                "coldest": sorted_by_temp[-1]['name'] if sorted_by_temp else None,
                "most_comfortable": sorted_by_comfort[0]['name'] if sorted_by_comfort else None,
                "least_comfortable": sorted_by_comfort[-1]['name'] if sorted_by_comfort else None,
                "temperature_range": f"{sorted_by_temp[-1]['current']['temperature']} to {sorted_by_temp[0]['current']['temperature']} °C" if sorted_by_temp else None
            },
            "timestamp": datetime.now().isoformat()
        }

        return OpenMeteoDataValue(analysis_result)

    except Exception as e:
        return OpenMeteoDataValue({"success": False, "error": f"Failed to compare weather: {str(e)}"})
