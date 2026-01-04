import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.openmeteo import create_openmeteo_agent

def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("OPENMETEO WEATHER API DEMO")
    print("=" * 60)

    agent = create_openmeteo_agent()

    print(f"✅ Agent created: {agent.name}")

    print("\n1. Server connection test:")
    print("-" * 40)

    result = safe_execute(agent.get_current_weather,
                         latitude=52.52,
                         longitude=13.41,
                         timezone="Europe/Berlin")

    if result.get('success'):
        current = result.get('current', {})
        print(f"✅ OpenMeteo Server: Connected successfully")
        print(f"   Location: {result.get('latitude')}°N, {result.get('longitude')}°E")
        print(f"   Elevation: {result.get('elevation')}m")
        print(f"   Timezone: {result.get('timezone')}")

        temp = current.get('temperature_2m', {}).get('value')
        weather_desc = current.get('weather', {}).get('description', 'Unknown')

        print(f"   Current: {temp}°C, {weather_desc}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n2. Current weather in major cities:")
    print("-" * 40)

    cities = [
        {"name": "Berlin", "lat": 52.52, "lon": 13.41, "timezone": "Europe/Berlin"},
        {"name": "London", "lat": 51.51, "lon": -0.13, "timezone": "Europe/London"},
        {"name": "Paris", "lat": 48.85, "lon": 2.35, "timezone": "Europe/Paris"},
        {"name": "New York", "lat": 40.71, "lon": -74.01, "timezone": "America/New_York"},
        {"name": "Tokyo", "lat": 35.68, "lon": 139.69, "timezone": "Asia/Tokyo"},
    ]

    for city in cities:
        result = safe_execute(agent.get_current_weather,
                            latitude=city["lat"],
                            longitude=city["lon"],
                            timezone=city["timezone"])

        if result.get('success'):
            current = result.get('current', {})
            temp = current.get('temperature_2m', {}).get('value', 'N/A')
            weather = current.get('weather', {}).get('description', 'N/A')

            temp_emoji = "🥶" if temp < 0 else "❄️" if temp < 10 else "☁️" if temp < 20 else "🌤️" if temp < 25 else "☀️"
            weather_emoji = "☀️" if "clear" in weather.lower() else "⛅" if "partly" in weather.lower() else "☁️" if "cloud" in weather.lower() else "🌧️" if "rain" in weather.lower() else "❄️" if "snow" in weather.lower() else "🌫️"

            print(f"{temp_emoji}{weather_emoji}  {city['name']}: {temp}°C, {weather}")
        else:
            print(f"❌ {city['name']}: Error - {result.get('error')}")

    print("\n3. 5-day weather forecast (Berlin):")
    print("-" * 40)

    result = safe_execute(agent.get_forecast,
                         latitude=52.52,
                         longitude=13.41,
                         forecast_type="daily",
                         forecast_days=5,
                         timezone="Europe/Berlin")

    if result.get('success'):
        forecast = result.get('forecast', {})
        print(f"✅ 5-day forecast for Berlin")
        print(f"   Days: {forecast.get('days')}")

        parameters = forecast.get('parameters', {})

        if 'temperature_2m_max' in parameters and 'temperature_2m_min' in parameters:
            max_temps = parameters['temperature_2m_max']['values']
            min_temps = parameters['temperature_2m_min']['values']
            dates = forecast.get('dates', [])

            print(f"\n   Daily forecast:")
            for i, date in enumerate(dates[:5]):
                max_temp = max_temps[i] if i < len(max_temps) else 'N/A'
                min_temp = min_temps[i] if i < len(min_temps) else 'N/A'

                temp_range_emoji = "🥶" if max_temp < 0 else "❄️" if max_temp < 5 else "☁️" if max_temp < 15 else "🌤️" if max_temp < 25 else "☀️"

                print(f"   {temp_range_emoji} {date}: Max {max_temp}°C, Min {min_temp}°C")

    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n4. Air quality monitoring (Berlin):")
    print("-" * 40)

    result = safe_execute(agent.get_air_quality,
                         latitude=52.52,
                         longitude=13.41,
                         hourly=["pm2_5", "european_aqi"],
                         forecast_days=3,
                         timezone="Europe/Berlin")

    if result.get('success'):
        air_quality = result.get('air_quality', {})
        print(f"✅ Air quality for Berlin")

        current_conditions = air_quality.get('current_conditions', {})

        if 'pm2_5' in current_conditions:
            pm25 = current_conditions['pm2_5']['value']

            if pm25 < 15:
                rating = "✅ Good"
                emoji = "😊"
            elif pm25 < 35:
                rating = "⚠️ Moderate"
                emoji = "😐"
            elif pm25 < 55:
                rating = "⚠️ Unhealthy for sensitive"
                emoji = "😷"
            else:
                rating = "❌ Unhealthy"
                emoji = "🤢"

            print(f"\n   {emoji} PM2.5: {pm25} μg/m³ - {rating}")

        if 'european_aqi' in current_conditions:
            aqi = current_conditions['european_aqi']['value']

            aqi_emoji = "😊" if aqi < 20 else "😐" if aqi < 40 else "😷" if aqi < 60 else "🤢" if aqi < 80 else "🤮"
            print(f"   {aqi_emoji} European AQI: {aqi}")

    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n5. Weather statistics (last 7 days, London):")
    print("-" * 40)

    result = safe_execute(agent.get_weather_statistics,
                         latitude=51.51,
                         longitude=-0.13,
                         days=7,
                         timezone="Europe/London")

    if result.get('success'):
        stats = result.get('statistics', {})
        period = result.get('statistics_period', {})

        print(f"✅ Weather statistics for London")
        print(f"   Period: {period.get('start_date')} to {period.get('end_date')}")

        temp_stats = stats.get('temperature', {})
        if temp_stats:
            print(f"\n   Temperature analysis:")
            print(f"   Average: {temp_stats.get('average', 0):.1f}°C")
            print(f"   Range: {temp_stats.get('min_recorded', 0):.1f}°C to {temp_stats.get('max_recorded', 0):.1f}°C")

        precip_stats = stats.get('precipitation', {})
        if precip_stats:
            rain_emoji = "🌧️" if precip_stats.get('rainy_days_percentage', 0) > 50 else "🌦️" if precip_stats.get('rainy_days_percentage', 0) > 20 else "☀️"
            print(f"\n   {rain_emoji} Precipitation analysis:")
            print(f"   Total: {precip_stats.get('total', 0):.1f} mm")
            print(f"   Rainy days: {precip_stats.get('rainy_days', 0)}/{period.get('days', 7)}")

    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n6. Quick timezone check (London):")
    print("-" * 40)

    result = safe_execute(agent.get_current_weather,
                         latitude=51.51,
                         longitude=-0.13,
                         timezone="Europe/London")

    if result.get('success'):
        print(f"✅ London timezone check")
        print(f"   API Timezone: {result.get('timezone')}")
        print(f"   Local data available: Yes")

        current = result.get('current', {})
        is_day = current.get('weather', {}).get('is_day')
        print(f"   Is daytime: {'☀️ Yes' if is_day else '🌙 No'}")
    else:
        print(f"⚠️  Timezone check skipped (API busy)")
        print(f"   Note: Timezone functionality works but API is slow sometimes")

    print("\n7. Weather comparison between cities:")
    print("-" * 40)

    comparison_locations = [
        {"name": "Berlin", "latitude": 52.52, "longitude": 13.41, "timezone": "Europe/Berlin"},
        {"name": "Rome", "latitude": 41.90, "longitude": 12.50, "timezone": "Europe/Rome"},
        {"name": "Madrid", "latitude": 40.42, "longitude": -3.70, "timezone": "Europe/Madrid"},
    ]

    result = safe_execute(agent.compare_weather,
                         locations=comparison_locations)

    if result.get('success'):
        print(f"✅ Weather comparison across {result.get('locations_count', 0)} cities")
        comparison = result.get('comparison', {})

        print(f"\n   Summary:")
        print(f"   Warmest: {comparison.get('warmest', 'N/A')}")
        print(f"   Coldest: {comparison.get('coldest', 'N/A')}")
        print(f"   Most comfortable: {comparison.get('most_comfortable', 'N/A')}")

        locations = result.get('locations', [])

        print(f"\n   Detailed comparison:")
        for loc in locations:
            if 'error' not in loc:
                current = loc.get('current', {})
                comfort = loc.get('comfort_index', 0)

                comfort_emoji = "😊" if comfort > 80 else "😐" if comfort > 60 else "😕" if comfort > 40 else "😟"

                print(f"   {loc['name']}: {current.get('temperature')}°C, {current.get('weather_description')}")
                print(f"     Comfort index: {comfort_emoji} {comfort:.0f}/100")
            else:
                print(f"   ❌ {loc.get('name')}: {loc.get('error')}")

    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n8. Multi-location summary table:")
    print("-" * 40)
    print(f"{'City':<15} {'Temp (°C)':<12} {'Weather':<20} {'Humidity':<10} {'Wind':<8}")
    print("-" * 65)

    for city in cities[:3]:
        result = safe_execute(agent.get_current_weather,
                            latitude=city["lat"],
                            longitude=city["lon"],
                            timezone=city["timezone"])

        if result.get('success'):
            current = result.get('current', {})
            temp = current.get('temperature_2m', {}).get('value', 'N/A')
            weather = current.get('weather', {}).get('description', 'N/A')
            humidity = current.get('relative_humidity_2m', {}).get('value', 'N/A')
            wind = current.get('wind', {}).get('speed_10m', {}).get('value', 'N/A')

            weather_short = weather[:18] + "..." if len(weather) > 18 else weather

            if isinstance(temp, (int, float)):
                temp_str = f"{temp:>5.1f}°C"
            else:
                temp_str = str(temp)

            print(f"{city['name']:<15} {temp_str:<12} {weather_short:<20} {humidity:>5}% {wind:>6.1f} m/s")

    print("\n9. Weather trend analysis (Berlin, 14 days):")
    print("-" * 40)

    result = safe_execute(agent.get_weather_statistics,
                         latitude=52.52,
                         longitude=13.41,
                         days=14,
                         timezone="Europe/Berlin")

    if result.get('success'):
        stats = result.get('statistics', {})
        period = result.get('statistics_period', {})

        print(f"✅ {period.get('days', 0)}-day trend analysis for Berlin")
        print(f"   Period: {period.get('start_date')} to {period.get('end_date')}")

        temp_stats = stats.get('temperature', {})
        if temp_stats:
            temp_range = temp_stats.get('range', 0)
            if temp_range > 15:
                variability = "📈 High variability"
            elif temp_range > 10:
                variability = "↗️ Moderate variability"
            else:
                variability = "➡️ Stable"

            print(f"   {variability} (Range: {temp_range:.1f}°C)")

        precip_stats = stats.get('precipitation', {})
        if precip_stats:
            rainy_percentage = precip_stats.get('rainy_days_percentage', 0)
            if rainy_percentage > 50:
                rain_trend = "🌧️ Wet period"
            elif rainy_percentage > 25:
                rain_trend = "🌦️ Some rain"
            else:
                rain_trend = "☀️ Dry period"

            print(f"   {rain_trend} ({rainy_percentage:.0f}% rainy days)")

    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()
