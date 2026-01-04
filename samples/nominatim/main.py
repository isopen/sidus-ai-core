import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.nominatim import create_nominatim_agent

def main():
    print("NOMINATIM GEOCODING API")
    print("=" * 50)

    agent = create_nominatim_agent(
        user_agent="sidus-ai-test/1.0",
        email="test@example.com"
    )

    print("\n1. Server status check:")
    print("-" * 30)

    result = agent.get_server_status(format_type='json')
    if result.get('success'):
        server_info = result.get('server_info', {})
        print(f"✅ Nominatim Server Status: {server_info.get('message', 'Unknown')}")
        print(f"   Software Version: {server_info.get('software_version', 'Not Available')}")
        print(f"   Database Version: {server_info.get('database_version', 'Not Available')}")
        print(f"   Data Updated: {server_info.get('data_updated', 'Not Available')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n2. Search for location (Berlin) with advanced options:")
    print("-" * 30)

    result = agent.search_location(
        query="Berlin, Germany",
        limit=5,
        addressdetails=1,
        extratags=1,
        format_type='jsonv2',
        namedetails=1
    )

    if result.get('success'):
        print(f"✅ Found {result.get('places_count')} places")
        print(f"   Format: JSONv2")

        places = result.get('places', [])
        print(f"\n   All results:")
        for i, place in enumerate(places):
            print(f"   {i + 1}. {place['display_name']}")
            print(f"      Type: {place['type']}, Importance: {place['importance']:.3f}")
            if 'extratags' in place:
                print(f"      Extratags: {len(place['extratags'])} items")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n3. Reverse geocoding (Berlin coordinates) with polygon:")
    print("-" * 30)

    result = agent.reverse_geocode(
        lat=52.5200,
        lon=13.4050,
        zoom=18,
        addressdetails=1,
        extratags=1,
        polygon=1,
        polygon_kml=1
    )

    if result.get('success'):
        place = result.get('place', {})
        print(f"✅ Reverse geocode successful")
        print(f"   Location: {place.get('display_name', 'Unknown')}")
        print(f"   Type: {place.get('type', 'Unknown')}")
        print(f"   Has polygon data: {'✅ Yes' if 'polygonpoints' in place else '❌ No'}")

        address_analysis = result.get('address_analysis', {})
        print(f"   Address components: {address_analysis.get('components_count', 0)}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n4. OSM lookup (Berlin landmarks) with extratags:")
    print("-" * 30)

    result = agent.lookup_with_extratags(
        osm_ids=["R62422", "W25917947", "N240109189"]
    )

    if result.get('success'):
        print(f"✅ Found {result.get('places_count')} places")
        print(f"   Places with extratags: {result.get('places_with_extratags', 0)}")

        places_sample = result.get('places_sample', [])
        if places_sample:
            print(f"\n   All results with extratags:")
            for i, place in enumerate(places_sample):
                print(f"   {i + 1}. {place.get('display_name', 'Unknown')}")
                if place.get('extratags'):
                    all_extratags = list(place['extratags'].keys())
                    print(f"      All Extratags: {', '.join(all_extratags)}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n5. Search with GeoJSON format:")
    print("-" * 30)

    result = agent.search_geojson(
        query="Brandenburg Gate Berlin",
        limit=3
    )

    if result.get('success'):
        print(f"✅ GeoJSON search successful")
        print(f"   Features count: {result.get('features_count', 0)}")
        print(f"   Format: {result.get('format')}")

        metadata = result.get('metadata', {})
        print(f"   Licence: {metadata.get('licence', 'Not Available')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n6. Search with country filter and viewbox:")
    print("-" * 30)

    result = agent.search_location(
        query="restaurant",
        countrycodes=["FR"],
        viewbox="2.25,48.85,2.42,48.90",
        bounded=1,
        limit=5,
        addressdetails=1,
        addresstype="amenity"
    )

    if result.get('success'):
        print(f"✅ Found {result.get('places_count')} places in Paris viewbox")
        places = result.get('places', [])
        print(f"\n   All results:")
        for i, place in enumerate(places):
            print(f"   {i + 1}. {place['display_name']}")
            print(f"      Coordinates: {place['lat']}, {place['lon']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n7. Get details with entrances and hierarchy:")
    print("-" * 30)

    result = agent.get_details(
        place_id=25917947,
        format_type='json',
        entrances=1,
        hierarchy=1,
        linkedplaces=1
    )

    if result.get('success'):
        metadata = result.get('metadata', {})
        print(f"✅ Details retrieved for place: {metadata.get('localname', 'Unknown')}")
        print(f"   Type: {metadata.get('type', 'Unknown')}")
        print(f"   Importance: {metadata.get('importance', 0):.3f}")

        additional = result.get('additional_info', {})
        print(f"\n   Additional info:")
        print(f"   Has names: {'✅ Yes' if additional.get('has_names') else '❌ No'}")
        print(f"   Has extratags: {'✅ Yes' if additional.get('has_extratags') else '❌ No'}")
        print(f"   Has entrances: {'✅ Yes' if additional.get('has_entrances') else '❌ No'}")
        print(f"   Has hierarchy: {'✅ Yes' if additional.get('has_hierarchy') else '❌ No'}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n8. Search with multiple polygon formats:")
    print("-" * 30)

    result = agent.search_with_polygon(
        query="135 pilkington avenue, birmingham",
        polygon_format="kml",
        limit=3,
        format_type="xml"
    )

    if result.get('success'):
        print(f"✅ Search with polygon successful")
        print(f"   Polygon format: {result.get('polygon_format')}")
        print(f"   Response format: {result.get('response_format')}")
        print(f"   Places count: {result.get('places_count', 0)}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n9. Reverse with multiple polygon formats:")
    print("-" * 30)

    result = agent.reverse_with_polygon(
        lat=52.5487429714954,
        lon=-1.81602098644987,
        polygon_format="svg",
        format_type="xml"
    )

    if result.get('success'):
        print(f"✅ Reverse with polygon successful")
        print(f"   Polygon format: {result.get('polygon_format')}")
        print(f"   Response format: {result.get('response_format')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n10. Search with accept-language parameter:")
    print("-" * 30)

    queries = [
        {"query": "London", "language": "en", "expected_country": "United Kingdom"},
        {"query": "Londres", "language": "es", "expected_country": "Reino Unido"},
        {"query": "Londres", "language": "fr", "expected_country": "Royaume-Uni"},
    ]

    for test in queries:
        print(f"\nSearch for '{test['query']}' with language {test['language']}:")

        result = agent.search_location(
            query=test['query'],
            limit=2,
            addressdetails=1,
            accept_language=test['language'],
            format_type='jsonv2'
        )

        if result.get('success'):
            places = result.get('places', [])
            if places:
                first_place = places[0]
                address = first_place.get('address', {})
                country = address.get('country', 'Not defined')

                print(f"   ✅ Found: {len(places)} places")
                print(f"   Country (in locale {test['language']}): {country}")
                print(f"   Expected: {test['expected_country']}")
                print(f"   Match: {'✅ Yes' if country == test['expected_country'] else '❌ No'}")

                print(f"   Full name: {first_place['display_name']}")
        else:
            print(f"   ❌ Error: {result.get('error')}")

    print("\n11. Search without layer filtering:")
    print("-" * 30)

    result = agent.search_location(
        query="bakery in berlin",
        limit=3,
        addressdetails=1,
        format_type='jsonv2'
    )

    if result.get('success'):
        print(f"✅ Search for bakeries in Berlin")
        print(f"   Found {result.get('places_count')} places")

        places = result.get('places', [])
        print(f"\n   All bakery results:")
        for i, place in enumerate(places):
            print(f"   {i + 1}. {place.get('display_name', 'Unknown')}")
            address = place.get('address', {})
            if 'shop' in address:
                print(f"      Shop type: {address['shop']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n12. Get deletable items:")
    print("-" * 30)

    result = agent.get_deletable(format_type='json')

    if result.get('success'):
        print(f"✅ Deletable items check")
        summary = result.get('summary', {})
        print(f"   Deletable items: {result.get('deletable_count', 0)}")
        print(f"   OSM types: {summary.get('osm_types', {})}")
        if summary.get('reasons'):
            print(f"   Reasons: {summary.get('reasons', {})}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n13. Get broken polygons:")
    print("-" * 30)

    result = agent.get_polygons(format_type='json')

    if result.get('success'):
        print(f"✅ Broken polygons check")
        summary = result.get('summary', {})
        print(f"   Broken polygons: {result.get('broken_polygons_count', 0)}")
        print(f"   Error types: {summary.get('error_types', {})}")
        print(f"   Countries: {len(summary.get('countries', {}))}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n14. Search with address type filtering:")
    print("-" * 30)

    result = agent.search_location(
        query="street in london",
        limit=3,
        addressdetails=1,
        addresstype="road",
        format_type='jsonv2'
    )

    if result.get('success'):
        print(f"✅ Search with address type filter (road)")
        print(f"   Found {result.get('places_count')} places")

        places = result.get('places', [])
        print(f"\n   All road results:")
        for i, place in enumerate(places):
            print(f"   {i + 1}. {place.get('display_name', 'Unknown')}")
            if 'addresstype' in place:
                print(f"      Address type: {place['addresstype']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n15. Complex search:")
    print("-" * 30)

    result = agent.search_geocodejson(
        query="museum berlin",
        limit=3
    )

    if result.get('success'):
        print(f"✅ GeocodeJSON search successful")
        print(f"   Format: {result.get('format')}")
        print(f"   Features count: {result.get('features_count', 0)}")
        print(f"   Response type: {result.get('type', 'Unknown')}")

        geocoding_info = result.get('geocoding_info', {})
        if geocoding_info:
            print(f"   Attribution: {geocoding_info.get('attribution', 'Not Available')}")
            print(f"   Licence: {geocoding_info.get('licence', 'Not Available')}")

        features_sample = result.get('features_sample', [])
        if features_sample:
            print(f"\n   All sample features:")
            for i, feature in enumerate(features_sample):
                if isinstance(feature, dict):
                    props = feature.get('properties', {})
                    geocoding_props = props.get('geocoding', {})
                    label = geocoding_props.get('label', 'No label')
                    print(f"   {i + 1}. {label}")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()
