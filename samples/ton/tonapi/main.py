import sys
import time
import os
from datetime import datetime

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
from sidusai.plugins.ton.tonapi import TONAPIPlugin

def agent_creation():
    try:
        print("🤖 Creating Sidus AI agent...")
        agent = sai.Agent()
        print("✅ Sidus AI agent created")

        print("🔧 Creating TON API plugin...")
        api_key = os.environ.get('TONAPI_API_KEY', '')
        plugin = TONAPIPlugin(api_key=api_key)
        print("✅ TON API plugin created")

        print("🔧 Applying TON API plugin to agent...")
        plugin.apply_plugin(agent)
        print("✅ TON API plugin applied")

        return agent, plugin

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def interactive():
    try:
        agent, plugin = agent_creation()

        if not agent or not plugin:
            print("❌ Failed to create agent or plugin")
            return

        if hasattr(plugin, 'tonapi_client'):
            print("🔗 Testing TON API connection...")
            if plugin.tonapi_client.test_connection():
                print("✅ TON API connection successful")
            else:
                print("⚠️ TON API connection issues")
                print("ℹ️ Make sure you have a valid API key from https://tonconsole.com/")

        while True:
            try:
                print("\n" + "-"*50)
                print("Commands:")
                print("1. price [currencies]   - Get TON price (USD,EUR,RUB)")
                print("2. balance <address>    - Get wallet balance")
                print("3. transactions <addr>  - Get wallet transactions")
                print("4. token <address>      - Get token information")
                print("5. holders <address>    - Get jetton holders")
                print("6. nftcollection <addr> - Get NFT collection info")
                print("7. nftitem <address>    - Get NFT item info")
                print("8. exit                - Exit")
                print("-"*50)

                choice = input("\n🔧 Enter command number (1-8): ").strip()

                if choice == '1':
                    currencies_input = input("Currencies (comma-separated, default USD,EUR,RUB): ").strip()
                    currencies = [c.strip().upper() for c in currencies_input.split(',')] if currencies_input else ["USD", "EUR", "RUB"]

                    print(f"\n💰 Getting TON price in {currencies}...")
                    result = plugin.tonapi_client.get_ton_price(currencies)

                    if result:
                        prices = result.get('prices', {})
                        diff_24h = result.get('diff_24h', {})
                        diff_7d = result.get('diff_7d', {})
                        diff_30d = result.get('diff_30d', {})

                        print(f"TON Price:")
                        for currency in currencies:
                            price = prices.get(currency, 0)
                            change_24h = diff_24h.get(currency, '0%')
                            print(f"{currency}: {price:.4f} ({change_24h})")

                        print(f"\n7d Change:")
                        for currency in currencies[:3]:
                            change_7d = diff_7d.get(currency, '0%')
                            print(f"{currency}: {change_7d}")

                        print(f"\n30d Change:")
                        for currency in currencies[:3]:
                            change_30d = diff_30d.get(currency, '0%')
                            print(f"{currency}: {change_30d}")

                        print(f"\nSource: {result.get('source', 'TON API')}")
                        print(f"Timestamp: {result.get('timestamp', '')}")
                    else:
                        print(f"❌ Failed to get TON price")

                elif choice == '2':
                    wallet_address = input("Enter wallet address: ").strip()

                    if wallet_address:
                        print(f"\n💰 Getting balance for wallet...")
                        result = plugin.tonapi_client.get_wallet_balance(wallet_address)

                        if result:
                            balance_ton = result.get('balance_ton', 0)
                            is_scam = result.get('is_scam', False)
                            is_wallet = result.get('is_wallet', False)
                            status = result.get('status', 'unknown')
                            last_activity = result.get('last_activity', '')

                            print(f"Wallet: {wallet_address}")
                            print(f"Balance: {balance_ton:.2f} TON")
                            print(f"Status: {status.upper()}")

                            if is_scam:
                                print("WARNING: This address is marked as SCAM!")
                            elif is_wallet:
                                print("Verified: This is a wallet address")

                            if last_activity:
                                if isinstance(last_activity, (int, float)):
                                    try:
                                        dt = datetime.fromtimestamp(last_activity)
                                        print(f"Last Activity: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                                    except:
                                        print(f"Last Activity timestamp: {last_activity}")
                                elif isinstance(last_activity, str):
                                    print(f"Last Activity: {last_activity[:10]}")
                        else:
                            print(f"❌ Failed to get wallet balance")
                    else:
                        print("❌ Please enter wallet address")

                elif choice == '3':
                    wallet_address = input("Enter wallet address: ").strip()
                    limit_input = input("Limit (default 10): ").strip()
                    limit = int(limit_input) if limit_input.isdigit() else 10

                    if wallet_address:
                        print(f"\n📊 Getting transactions for wallet...")
                        result = plugin.tonapi_client.get_wallet_transactions(wallet_address, limit)

                        if result:
                            print(f"Found {len(result)} transactions:")

                            for i, tx in enumerate(result[:limit], 1):
                                print(f"\nFrom: {tx.from_address}")
                                print(f"To: {tx.to_address}")
                                print(f"Amount: {tx.value:.6f} TON")
                                print(f"Fee: {tx.fee:.6f} TON")

                                if tx.message:
                                    print(f"Message: {tx.message[:50]}")

                                if tx.timestamp:
                                    if isinstance(tx.timestamp, datetime):
                                        print(f"Time: {tx.timestamp.strftime('%Y-%m-%d %H:%M')}")
                                    else:
                                        try:
                                            dt = datetime.fromtimestamp(tx.timestamp)
                                            print(f"Time: {dt.strftime('%Y-%m-%d %H:%M')}")
                                        except:
                                            print(f"Time: {tx.timestamp}")

                            if len(result) > limit:
                                print(f"\n... and {len(result) - limit} more transactions")
                        else:
                            print(f"❌ Failed to get transactions or no transactions found")
                    else:
                        print("❌ Please enter wallet address")

                elif choice == '4':
                    token_address = input("Enter token address: ").strip()

                    if token_address:
                        print(f"\n🎯 Getting token information...")
                        result = plugin.tonapi_client.get_token_info(token_address)

                        if result:
                            name = result.get('name', 'Unknown')
                            symbol = result.get('symbol', 'UNKNOWN')
                            is_verified = result.get('is_verified', False)
                            is_scam = result.get('is_scam', False)
                            holders_count = result.get('holders_count', 0)
                            total_supply = result.get('total_supply', 0)
                            description = result.get('description', '')

                            print(f"Token: {name} ({symbol})")
                            print(f"Address: {token_address[:15]}...")

                            if is_verified:
                                print("Verified Token")
                            elif is_scam:
                                print("WARNING: Scam Token")
                            else:
                                print("Unverified Token")

                            if isinstance(total_supply, (int, float)):
                                print(f"Total Supply: {total_supply:,}")
                            elif isinstance(total_supply, str):
                                try:
                                    clean_supply = total_supply.replace(',', '').replace(' ', '')
                                    if '.' in clean_supply:
                                        supply_num = float(clean_supply)
                                    else:
                                        supply_num = int(clean_supply)
                                    print(f"Total Supply: {supply_num:,}")
                                except (ValueError, TypeError):
                                    print(f"Total Supply: {total_supply}")
                            else:
                                print(f"Total Supply: {total_supply}")

                            if isinstance(holders_count, (int, float)):
                                print(f"Holders: {holders_count:,}")
                            elif isinstance(holders_count, str):
                                try:
                                    clean_holders = holders_count.replace(',', '').replace(' ', '')
                                    holders_num = int(clean_holders)
                                    print(f"Holders: {holders_num:,}")
                                except (ValueError, TypeError):
                                    print(f"Holders: {holders_count}")
                            else:
                                print(f"Holders: {holders_count}")

                            print(f"Decimals: {result.get('decimals', 9)}")

                            if description:
                                desc = description[:200] + "..." if len(description) > 200 else description
                                print(f"Description: {desc}")

                            social_links = result.get('social_links', [])
                            if social_links:
                                print(f"Social Links: {', '.join(social_links[:3])}")
                        else:
                            print(f"❌ Failed to get token info")
                    else:
                        print("❌ Please enter token address")

                elif choice == '5':
                    jetton_address = input("Enter jetton address: ").strip()
                    limit_input = input("Limit (default 10): ").strip()
                    limit = int(limit_input) if limit_input.isdigit() else 10

                    if jetton_address:
                        print(f"\n👥 Getting jetton holders...")
                        result = plugin.tonapi_client.get_jetton_holders(jetton_address, limit)

                        if result:
                            print(f"Found {len(result)} holders:")

                            for i, holder in enumerate(result, 1):
                                address = holder.get('address', '')
                                owner_name = holder.get('owner_name', '')
                                owner_address = holder.get('owner_address', '')
                                balance = holder.get('balance', 0)
                                is_scam = holder.get('is_scam', False)
                                is_wallet = holder.get('is_wallet', False)
                                balance_str = holder.get('balance_str', '0')

                                display_name = owner_name if owner_name else (owner_address if owner_address else 'Unknown')

                                status = "SCAM" if is_scam else "Valid"
                                print(f"\n#{i} {status}")
                                print(f"Holder: {display_name}")
                                print(f"Address: {address}")

                                try:
                                    if isinstance(balance, (int, float)):
                                        balance_formatted = balance / 1_000_000_000
                                        print(f"Balance: {balance_formatted:,.6f}")
                                    elif isinstance(balance_str, str):
                                        try:
                                            balance_num = int(balance_str)
                                            balance_formatted = balance_num / 1_000_000_000
                                            print(f"Balance: {balance_formatted:,.6f}")
                                        except ValueError:
                                            print(f"Balance: {balance_str}")
                                    else:
                                        print(f"Balance: {balance}")
                                except Exception:
                                    print(f"Balance: {balance_str}")

                                if owner_name and not is_wallet:
                                    print(f"Type: {owner_name}")
                                elif is_wallet:
                                    print(f"Type: Wallet")

                            if len(result) > 5:
                                print(f"\n... and {len(result) - 5} more holders")
                            try:
                                total_holders = plugin.tonapi_client._make_request(
                                    f"jettons/{jetton_address}/holders", 
                                    {'limit': 1}
                                ).get('total', 0)
                                if total_holders:
                                    print(f"\nTotal holders: {total_holders:,}")
                            except:
                                pass
                        else:
                            print(f"❌ Failed to get holders or no holders found")
                    else:
                        print("❌ Please enter jetton address")

                elif choice == '6':
                    collection_address = input("Enter NFT collection address: ").strip()

                    if collection_address:
                        print(f"\n🖼️  Getting NFT collection information...")
                        result = plugin.tonapi_client.get_nft_collection(collection_address)

                        if result:
                            name = result.get('name', 'Unknown')
                            is_verified = result.get('is_verified', False)
                            is_scam = result.get('is_scam', False)
                            description = result.get('description', '')
                            external_link = result.get('external_link', '')
                            marketplaces = result.get('marketplaces', [])
                            owner = result.get('owner_address', '')

                            print(f"Collection: {name}")
                            print(f"Address: {collection_address}")

                            if is_verified:
                                print("Verified Collection")
                            elif is_scam:
                                print("WARNING: Scam Collection")
                            else:
                                print("Unverified Collection")

                            if description:
                                desc = description[:200] + "..." if len(description) > 200 else description
                                print(f"Description: {desc}")

                            if external_link:
                                print(f"External Link: {external_link}")

                            if marketplaces:
                                print(f"Marketplaces: {', '.join(marketplaces[:3])}")

                            if owner:
                                print(f"Owner: {owner}")
                        else:
                            print(f"❌ Failed to get NFT collection")
                    else:
                        print("❌ Please enter collection address")

                elif choice == '7':
                    nft_address = input("Enter NFT item address: ").strip()

                    if nft_address:
                        print(f"\n🖼️  Getting NFT item information...")
                        result = plugin.tonapi_client.get_nft_item(nft_address)

                        if result:
                            name = result.get('name', 'Unknown')
                            collection_name = result.get('collection_name', '')
                            is_for_sale = result.get('is_for_sale', False)
                            price = result.get('price', 0)
                            price_token = result.get('price_token', 'TON')
                            owner = result.get('owner_address', '')
                            description = result.get('description', '')
                            attributes = result.get('attributes', [])

                            print(f"NFT: {name}")
                            print(f"Address: {nft_address}")

                            if collection_name:
                                print(f"Collection: {collection_name}")

                            if is_for_sale:
                                print(f"Sale: {price:.2f} {price_token}")
                            else:
                                print("Not for Sale")

                            if owner:
                                print(f"Owner: {owner}")

                            if description:
                                desc = description[:200] + "..." if len(description) > 200 else description
                                print(f"Description: {desc}")

                            if attributes:
                                print(f"Attributes:")
                                for attr in attributes[:3]:
                                    trait = attr.get('trait_type', '')
                                    value = attr.get('value', '')
                                    if trait and value:
                                        print(f"• {trait}: {value}")
                        else:
                            print(f"❌ Failed to get NFT item")
                    else:
                        print("❌ Please enter NFT address")

                elif choice == '8':
                    print("\n👋 Goodbye!")
                    break

                else:
                    print("❌ Invalid choice. Please enter 1-8.")

                time.sleep(1)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                continue

    except Exception as e:
        print(f"\n❌ Fatal error in interactive demo: {e}")
        import traceback
        traceback.print_exc()

def main():
    interactive()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)