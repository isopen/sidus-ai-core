import sys
import time
import os

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
from sidusai.plugins.ton.getgems import GetgemsPlugin

def agent_creation():
    try:
        print("🤖 Creating Sidus AI agent...")
        agent = sai.Agent()
        print("✅ Sidus AI agent created")

        print("🔧 Creating Getgems plugin...")
        plugin = GetgemsPlugin()
        print("✅ Getgems plugin created")

        print("🔧 Applying Getgems plugin to agent...")
        plugin.apply_plugin(agent)
        print("✅ Getgems plugin applied")

        return agent, plugin

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def interactive_demo():
    try:
        agent, plugin = agent_creation()

        if not agent or not plugin:
            print("❌ Failed to create agent or plugin")
            return

        if hasattr(plugin, 'getgems_client'):
            print("🔗 Testing Getgems API connection...")
            if plugin.getgems_client.test_connection():
                print("✅ Getgems API connection successful")
            else:
                print("⚠️ Getgems API connection issues")

        while True:
            try:
                print("\n" + "-"*50)
                print("Commands:")
                print("1. stats <address>      - Estimated collection stats")
                print("2. info <address>       - Collection information")
                print("3. nfts <address>       - NFTs on sale")
                print("4. nft <address>        - NFT information")
                print("5. exit                 - Exit")
                print("-"*50)

                choice = input("\n🔧 Enter command number (1-9): ").strip()

                if choice == '1':
                    address = input("Enter collection address (starts with EQ): ").strip()
                    if address.startswith('EQ'):
                        print(f"\n📊 Getting stats for: {address[:20]}...")
                        result = plugin.getgems_client.get_collection_stats(address)

                        if result.get('success'):
                            data = result.get('data', {})
                            response = data.get('response', {})

                            if response.get('floorPrice') is not None:
                                print(f"Floor Price: {response.get('floorPrice', 0):.2f} TON")

                            print(f"Items Count: {response.get('itemsCount', 0):,}")
                            print(f"Holders: {response.get('holders', 0):,}")

                            if response.get('floorPriceNano') and response['floorPriceNano'] != "string":
                                print(f"Floor Price (nano): {response['floorPriceNano']}")

                            if response.get('totalVolumeSoldNano') and response['totalVolumeSoldNano'] != "string":
                                print(f"Total Volume (nano): {response['totalVolumeSoldNano']}")
                        else:
                            print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    else:
                        print("❌ Invalid address. Should start with 'EQ'")

                elif choice == '2':
                    address = input("Enter collection address (starts with EQ): ").strip()
                    if address.startswith('EQ'):
                        print(f"\n📋 Getting collection info for: {address[:20]}...")
                        result = plugin.getgems_client.get_collection_info(address)

                        if result.get('success'):
                            data = result.get('data', {})
                            response = data.get('response', {})

                            print(f"Address: {response.get('address', address)}")

                            name = response.get('name', 'Unknown Collection')
                            if name != "string":
                                print(f"Name: {name}")

                            description = response.get('description', '')
                            if description and description != "string":
                                desc = description[:150] + "..." if len(description) > 150 else description
                                print(f"Description: {desc}")
                            else:
                                print(f"Description: No description available")

                            if response.get('ownerAddress'):
                                print(f"Owner: {response['ownerAddress'][:20]}...")

                            image = response.get('image', '')
                            if image and image != "string":
                                print(f"Image: Available")

                            if response.get('verified'):
                                print(f"Verified: ✅")

                            if response.get('externalUrl'):
                                print(f"Website: {response['externalUrl']}")

                            if response.get('socialLinks'):
                                socials = response['socialLinks']
                                if socials and isinstance(socials, dict):
                                    print(f"Social Links:")
                                    for platform, url in socials.items():
                                        if url and url != "string":
                                            print(f"  • {platform}: {url}")
                        else:
                            print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    else:
                        print("❌ Invalid address. Should start with 'EQ'")

                elif choice == '3':
                    address = input("Enter collection address (starts with EQ): ").strip()
                    limit = input("How many NFTs to show (default 5): ").strip()
                    limit = int(limit) if limit.isdigit() else 5

                    if address.startswith('EQ'):
                        print(f"\n🛒 Getting NFTs on sale for: {address[:20]}...")
                        result = plugin.getgems_client.get_nfts_on_sale(address, limit=limit)

                        if result.get('success'):
                            data = result.get('data', {})
                            response = data.get('response', {})
                            items = response.get('items', [])

                            if items:
                                for i, item in enumerate(items[:5], 1):
                                    print(f"\n{i}. {item.get('name', 'Unnamed NFT')}")

                                    sale = item.get('sale', {})
                                    price_ton = None

                                    if sale.get('minBid'):
                                        price_nano = int(sale['minBid'])
                                        price_ton = price_nano / 1e9
                                        print(f"   Price: {price_ton:.2f} {sale.get('currency', 'TON')}")
                                    elif sale.get('lastBidAmount'):
                                        price_nano = int(sale['lastBidAmount'])
                                        price_ton = price_nano / 1e9
                                        print(f"   Price: {price_ton:.2f} {sale.get('currency', 'TON')}")
                                    else:
                                        print(f"   Price: Not for sale")

                                    if item.get('ownerAddress'):
                                        owner = item['ownerAddress']
                                        if len(owner) > 20:
                                            owner = owner[:20] + "..."
                                        print(f"   Owner: {owner}")

                                    if item.get('attributes'):
                                        print(f"   Attributes: {len(item['attributes'])}")

                                    if i < min(5, len(items)):
                                        print(f"   {'-'*40}")
                            else:
                                print("No NFTs found for sale in this collection")
                        else:
                            print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    else:
                        print("❌ Invalid address. Should start with 'EQ'")

                elif choice == '4':
                    address = input("Enter NFT address (starts with EQ): ").strip()
                    if address.startswith('EQ'):
                        print(f"\n📄 Getting NFT info for: {address[:20]}...")
                        result = plugin.getgems_client.get_nft_by_address(address)

                        if result.get('success'):
                            data = result.get('data', {})
                            nft = data.get('response', {})

                            print(f"Name: {nft.get('name', 'Unknown NFT')}")

                            description = nft.get('description', '')
                            if description:
                                desc = description[:150] + "..." if len(description) > 150 else description
                                print(f"Description: {desc}")

                            if nft.get('ownerAddress'):
                                print(f"Owner: {nft['ownerAddress'][:20]}...")

                            if nft.get('collectionAddress'):
                                print(f"Collection: {nft['collectionAddress'][:20]}...")

                            sale = nft.get('sale', {})
                            if sale.get('minBid'):
                                price_nano = int(sale['minBid'])
                                price_ton = price_nano / 1e9
                                print(f"Price: {price_ton:.2f} {sale.get('currency', 'TON')}")

                            attributes = nft.get('attributes', [])
                            print(f"Attributes: {len(attributes)}")

                            if attributes:
                                print(f"Key Attributes:")
                                for attr in attributes[:3]:
                                    value = attr.get('value', 'Unknown')
                                    print(f"  - {value}")
                        else:
                            print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    else:
                        print("❌ Invalid address. Should start with 'EQ'")

                elif choice == '5':
                    print("\n👋 Goodbye!")
                    break

                else:
                    print("❌ Invalid choice. Please enter 1-9.")

                time.sleep(1)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue

    except Exception as e:
        print(f"\n❌ Fatal error in interactive demo: {e}")

def main():
    interactive_demo()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
