from sidusai.core.plugin import AgentValue
from typing import Dict, Any
from datetime import datetime

class NFTCollectionValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class NFTItemsValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class NFTItemValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

def get_nfts_on_sale_skill(context: Dict[str, Any]) -> NFTItemsValue:
    """
    GET /public-api/v1/nfts/on-sale/{collectionAddress}
    """
    print("🔧 Starting get_nfts_on_sale_skill...")

    collection_address = context.get('collection_address')
    if not collection_address:
        result = {"error": "No collection address provided"}
        return NFTItemsValue(result)

    limit = context.get('limit', 20)
    cursor = context.get('cursor')

    try:
        getgems_component = context.get('getgems_component')
        if not getgems_component:
            result = {"error": "Getgems component not available"}
            return NFTItemsValue(result)

        print(f"📥 Getting NFTs on sale for collection: {collection_address}")

        api_result = getgems_component.get_nfts_on_sale(collection_address, limit, cursor)

        if not api_result.get("success"):
            error = api_result.get("error", "API request failed")
            result = {"error": error}
            return NFTItemsValue(result)

        data = api_result["data"]
        response_data = data.get("response", {})

        items = response_data.get("items", [])
        formatted_items = []

        for item in items:
            sale = item.get("sale", {})
            price_ton = None

            if sale.get("minBid"):
                price_nano = int(sale["minBid"])
                price_ton = price_nano / 1e9
            elif sale.get("lastBidAmount"):
                price_nano = int(sale["lastBidAmount"])
                price_ton = price_nano / 1e9

            formatted_items.append({
                "address": item.get("address", ""),
                "name": item.get("name", "Unnamed NFT"),
                "description": item.get("description", ""),
                "image": item.get("image", ""),
                "owner_address": item.get("ownerAddress", ""),
                "price": price_ton,
                "currency": sale.get("currency", "TON"),
                "attributes": item.get("attributes", []),
                "collection_address": item.get("collectionAddress", ""),
                "sale": sale
            })

        result = {
            "success": True,
            "collection_address": collection_address,
            "items": formatted_items,
            "total_count": len(formatted_items),
            "cursor": response_data.get("cursor"),
            "has_more": bool(response_data.get("cursor")),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Found {len(formatted_items)} NFTs on sale")
        return NFTItemsValue(result)

    except Exception as e:
        print(f"❌ Error in get_nfts_on_sale_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get NFTs on sale: {str(e)}"}
        return NFTItemsValue(result)

def get_collection_nfts_skill(context: Dict[str, Any]) -> NFTItemsValue:
    """
    GET /public-api/v1/nfts/collection/{collectionAddress}
    """
    print("🔧 Starting get_collection_nfts_skill...")

    collection_address = context.get('collection_address')
    if not collection_address:
        result = {"error": "No collection address provided"}
        return NFTItemsValue(result)

    limit = context.get('limit', 20)
    cursor = context.get('cursor')

    try:
        getgems_component = context.get('getgems_component')
        if not getgems_component:
            result = {"error": "Getgems component not available"}
            return NFTItemsValue(result)

        print(f"📥 Getting all NFTs for collection: {collection_address}")

        api_result = getgems_component.get_collection_nfts(collection_address, limit, cursor)

        if not api_result.get("success"):
            error = api_result.get("error", "API request failed")
            result = {"error": error}
            return NFTItemsValue(result)

        data = api_result["data"]
        response_data = data.get("response", {})

        items = response_data.get("items", [])
        formatted_items = []

        for item in items:
            sale = item.get("sale", {})
            price_ton = None

            if sale.get("minBid"):
                price_nano = int(sale["minBid"])
                price_ton = price_nano / 1e9
            elif sale.get("lastBidAmount"):
                price_nano = int(sale["lastBidAmount"])
                price_ton = price_nano / 1e9

            formatted_items.append({
                "address": item.get("address", ""),
                "name": item.get("name", "Unnamed NFT"),
                "description": item.get("description", ""),
                "image": item.get("image", ""),
                "owner_address": item.get("ownerAddress", ""),
                "price": price_ton,
                "currency": sale.get("currency", "TON"),
                "attributes": item.get("attributes", []),
                "collection_address": item.get("collectionAddress", ""),
                "sale": sale
            })

        result = {
            "success": True,
            "collection_address": collection_address,
            "items": formatted_items,
            "total_count": len(formatted_items),
            "cursor": response_data.get("cursor"),
            "has_more": bool(response_data.get("cursor")),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Found {len(formatted_items)} NFTs in collection")
        return NFTItemsValue(result)

    except Exception as e:
        print(f"❌ Error in get_collection_nfts_skill: {e}")
        result = {"error": f"Failed to get collection NFTs: {str(e)}"}
        return NFTItemsValue(result)


def get_nft_by_address_skill(context: Dict[str, Any]) -> NFTItemValue:
    """
    GET /public-api/v1/nft/{address}
    """
    print("🔧 Starting get_nft_by_address_skill...")

    nft_address = context.get('nft_address')
    if not nft_address:
        result = {"error": "No NFT address provided"}
        return NFTItemValue(result)

    try:
        getgems_component = context.get('getgems_component')
        if not getgems_component:
            result = {"error": "Getgems component not available"}
            return NFTItemValue(result)

        print(f"📄 Getting NFT: {nft_address}")

        api_result = getgems_component.get_nft_by_address(nft_address)

        if not api_result.get("success"):
            error = api_result.get("error", "API request failed")
            result = {"error": error}
            return NFTItemValue(result)

        data = api_result["data"]
        response_data = data.get("response", {})

        sale = response_data.get("sale", {})
        price_ton = None

        if sale.get("minBid"):
            price_nano = int(sale["minBid"])
            price_ton = price_nano / 1e9
        elif sale.get("lastBidAmount"):
            price_nano = int(sale["lastBidAmount"])
            price_ton = price_nano / 1e9

        result = {
            "success": True,
            "nft": {
                "address": response_data.get("address", nft_address),
                "name": response_data.get("name", "Unnamed NFT"),
                "description": response_data.get("description", ""),
                "image": response_data.get("image", ""),
                "owner_address": response_data.get("ownerAddress", ""),
                "price": price_ton,
                "currency": sale.get("currency", "TON"),
                "attributes": response_data.get("attributes", []),
                "collection_address": response_data.get("collectionAddress", ""),
                "sale": sale,
                "created_at": sale.get("createdAt")
            },
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Found NFT: {result['nft']['name']}")
        return NFTItemValue(result)

    except Exception as e:
        print(f"❌ Error in get_nft_by_address_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get NFT: {str(e)}"}
        return NFTItemValue(result)

def get_collection_stats_skill(context: Dict[str, Any]) -> NFTCollectionValue:
    """
    GET /public-api/v1/collection/stats/{collectionAddress}
    """
    print("🔧 Starting get_collection_stats_api_skill...")

    collection_address = context.get('collection_address')
    if not collection_address:
        result = {"error": "No collection address provided"}
        return NFTCollectionValue(result)

    try:
        getgems_component = context.get('getgems_component')
        if not getgems_component:
            result = {"error": "Getgems component not available"}
            return NFTCollectionValue(result)

        print(f"📊 Getting collection stats for: {collection_address}")

        api_result = getgems_component.get_collection_stats_api(collection_address)

        if not api_result.get("success"):
            error = api_result.get("error", "API request failed")
            result = {"error": error}
            return NFTCollectionValue(result)

        data = api_result["data"]
        response_data = data.get("response", {})

        floor_price_nano = response_data.get("floorPriceNano", "0")
        total_volume_nano = response_data.get("totalVolumeSoldNano", "0")

        try:
            floor_price_ton = int(floor_price_nano) / 1e9 if floor_price_nano != "string" else 0
        except (ValueError, TypeError):
            floor_price_ton = 0

        try:
            total_volume_ton = int(total_volume_nano) / 1e9 if total_volume_nano != "string" else 0
        except (ValueError, TypeError):
            total_volume_ton = 0

        result = {
            "success": True,
            "collection_address": collection_address,
            "stats": {
                "floor_price": floor_price_ton,
                "floor_price_nano": floor_price_nano,
                "items_count": response_data.get("itemsCount", 0),
                "total_volume_sold": total_volume_ton,
                "total_volume_sold_nano": total_volume_nano,
                "holders": response_data.get("holders", 0),
                "raw_response": response_data
            },
            "api_success": data.get("success", False),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Collection stats retrieved")
        return NFTCollectionValue(result)

    except Exception as e:
        print(f"❌ Error in get_collection_stats_api_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get collection stats: {str(e)}"}
        return NFTCollectionValue(result)

def get_collection_info_skill(context: Dict[str, Any]) -> NFTCollectionValue:
    """
    GET /public-api/v1/collection/{collectionAddress}
    """
    print("🔧 Starting get_collection_info_skill...")

    collection_address = context.get('collection_address')
    if not collection_address:
        result = {"error": "No collection address provided"}
        return NFTCollectionValue(result)

    try:
        getgems_component = context.get('getgems_component')
        if not getgems_component:
            result = {"error": "Getgems component not available"}
            return NFTCollectionValue(result)

        print(f"📄 Getting collection info for: {collection_address}")

        api_result = getgems_component.get_collection_info(collection_address)

        if not api_result.get("success"):
            error = api_result.get("error", "API request failed")
            result = {"error": error}
            return NFTCollectionValue(result)

        data = api_result["data"]
        response_data = data.get("response", {})

        result = {
            "success": True,
            "collection_address": collection_address,
            "collection_info": {
                "address": response_data.get("address", collection_address),
                "owner_address": response_data.get("ownerAddress", ""),
                "name": response_data.get("name", "Unknown Collection"),
                "description": response_data.get("description", ""),
                "image": response_data.get("image", ""),
                "verified": response_data.get("verified", False),
                "social_links": response_data.get("socialLinks", {}),
                "external_url": response_data.get("externalUrl", "")
            },
            "api_success": data.get("success", False),
            "timestamp": datetime.now().isoformat(),
            "raw_response": response_data  # Для отладки
        }

        print(f"✅ Collection info retrieved: {result['collection_info']['name']}")
        return NFTCollectionValue(result)

    except Exception as e:
        print(f"❌ Error in get_collection_info_skill: {e}")
        result = {"error": f"Failed to get collection info: {str(e)}"}
        return NFTCollectionValue(result)
