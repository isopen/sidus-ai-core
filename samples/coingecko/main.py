import sys
import time
import os

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
from sidusai.plugins.coingecko import CoingeckoPlugin

def agent_creation():
    try:
        print("🤖 Creating Sidus AI agent...")
        agent = sai.Agent()
        print("✅ Sidus AI agent created")

        print("🔧 Creating Coingecko plugin...")
        plugin = CoingeckoPlugin()
        print("✅ Coingecko plugin created")

        print("🔧 Applying Coingecko plugin to agent...")
        plugin.apply_plugin(agent)
        print("✅ Coingecko plugin applied")

        return agent, plugin

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def interactive():
    try:
        agent, plugin = agent_creation()

        if not agent or not plugin:
            print("❌ Failed to create agent or plugin")
            return

        if hasattr(plugin, 'coingecko_client'):
            print("🔗 Testing CoinGecko API connection...")
            if plugin.coingecko_client.test_connection():
                print("✅ CoinGecko API connection successful")
            else:
                print("⚠️ CoinGecko API connection issues")

        while True:
            try:
                print("\n" + "-"*50)
                print("Commands:")
                print("1. price <crypto>       - Get cryptocurrency price")
                print("2. market [limit]       - Get top cryptocurrencies")
                print("3. convert              - Convert cryptocurrency")
                print("4. trending             - Get trending cryptocurrencies")
                print("5. history              - Get historical data")
                print("6. info                 - Get cryptocurrency information")
                print("7. search               - Search cryptocurrencies")
                print("8. exit                 - Exit")
                print("-"*50)

                choice = input("\n🔧 Enter command number (1-8): ").strip()

                if choice == '1':
                    crypto_id = input("Enter cryptocurrency ID (e.g., bitcoin): ").strip()
                    vs_currency = input("Currency (USD, EUR, etc., default USD): ").strip().lower()
                    vs_currency = vs_currency if vs_currency else "usd"

                    if crypto_id:
                        print(f"\n💰 Getting price for {crypto_id.upper()}...")
                        result = plugin.coingecko_client.get_crypto_price(crypto_id, vs_currency)

                        if result and crypto_id in result:
                            data = result[crypto_id]
                            price = data.get(vs_currency, 0)
                            market_cap = data.get(f"{vs_currency}_market_cap", 0)
                            volume = data.get(f"{vs_currency}_24h_vol", 0)
                            change = data.get(f"{vs_currency}_24h_change", 0)
                            last_updated = data.get("last_updated_at", 0)

                            print(f"Price: {price:,.2f} {vs_currency.upper()}")
                            print(f"24h Change: {change:+.2f}%")
                            print(f"Market Cap: {market_cap:,.0f} {vs_currency.upper()}")
                            print(f"24h Volume: {volume:,.0f} {vs_currency.upper()}")

                            if last_updated:
                                from datetime import datetime
                                dt = datetime.fromtimestamp(last_updated)
                                print(f"Last Updated: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            print(f"❌ Failed to get {crypto_id} price")
                    else:
                        print("❌ Please enter cryptocurrency ID")

                elif choice == '2':
                    limit = input("How many cryptocurrencies to show (default 10): ").strip()
                    limit = int(limit) if limit.isdigit() else 10

                    vs_currency = input("Currency (USD, EUR, etc., default USD): ").strip().lower()
                    vs_currency = vs_currency if vs_currency else "usd"

                    if limit > 50:
                        print("⚠️ Maximum limit is 50, using 50")
                        limit = 50

                    print(f"\n📈 Getting top {limit} cryptocurrencies...")
                    result = plugin.coingecko_client.get_crypto_market_data(vs_currency, limit)

                    if result:
                        print(f"\nTop {len(result)} Cryptocurrencies by Market Cap:")
                        for i, crypto in enumerate(result[:10], 1):
                            change_emoji = "📈" if crypto.price_change_percentage_24h >= 0 else "📉"
                            print(f"\n#{i} {crypto.name} ({crypto.symbol})")
                            print(f"  Price: {crypto.current_price:,.2f} {vs_currency.upper()}")
                            print(f"  24h Change: {change_emoji} {crypto.price_change_percentage_24h:+.2f}%")
                            print(f"  Market Cap: {crypto.market_cap:,.0f} {vs_currency.upper()}")
                            print(f"  Rank: #{crypto.market_cap_rank}")
                    else:
                        print("❌ Failed to get market data")

                elif choice == '3':
                    try:
                        amount = float(input("Amount to convert: ").strip())
                        from_curr = input("From cryptocurrency ID (e.g., bitcoin): ").strip().lower()
                        to_curr = input("To cryptocurrency ID (e.g., ethereum): ").strip().lower()

                        print(f"\n🔄 Converting {amount} {from_curr} to {to_curr}...")
                        result = plugin.coingecko_client.convert_currency(amount, from_curr, to_curr)

                        if result and result.get('success'):
                            print(f"Conversion Result:")
                            print(f"{result['amount']} {result['from_currency']} = {result['converted_amount']:.6f} {result['to_currency']}")
                            print(f"Rate: 1 {result['from_currency']} = {result['rate']:.6f} {result['to_currency']}")

                            from datetime import datetime
                            if isinstance(result['timestamp'], datetime):
                                print(f"Rate updated: {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            print("❌ Failed to convert cryptocurrency")
                    except ValueError:
                        print("❌ Invalid amount")
                    except Exception as e:
                        print(f"❌ Error: {e}")

                elif choice == '4':
                    print(f"\n🔥 Getting trending cryptocurrencies...")
                    result = plugin.coingecko_client.get_trending_cryptos()

                    if result:
                        print(f"Trending Cryptocurrencies:")
                        for i, crypto in enumerate(result[:5], 1):
                            coin = crypto.get('item', {})
                            name = coin.get('name', 'Unknown')
                            symbol = coin.get('symbol', '').upper()
                            rank = coin.get('market_cap_rank', 'N/A')
                            score = crypto.get('score', 0)

                            print(f"\n#{i} {name} ({symbol})")
                            print(f"  Rank: #{rank}")
                            print(f"  Trending Score: {score:.2f}")

                            coin_id = coin.get('id', '')
                            if coin_id:
                                price_result = plugin.coingecko_client.get_crypto_price(coin_id)
                                if price_result and coin_id in price_result:
                                    price_data = price_result[coin_id]
                                    price = price_data.get('usd', 0)
                                    change = price_data.get('usd_24h_change', 0)
                                    print(f"  Price: ${price:,.2f}")
                                    print(f"  24h Change: {change:+.2f}%")
                    else:
                        print("❌ Failed to get trending cryptos")

                elif choice == '5':
                    crypto_id = input("Enter cryptocurrency ID (e.g., bitcoin): ").strip()
                    days = input("Number of days (1-90, default 7): ").strip()
                    days = int(days) if days.isdigit() else 7

                    vs_currency = input("Currency (USD, EUR, etc., default USD): ").strip().lower()
                    vs_currency = vs_currency if vs_currency else "usd"

                    if days > 90:
                        print("⚠️ Maximum 90 days, using 90 days")
                        days = 90

                    if crypto_id:
                        print(f"\n📊 Getting {days}-day historical data for {crypto_id.upper()}...")
                        result = plugin.coingecko_client.get_historical_data(crypto_id, vs_currency, days)

                        if result:
                            prices = result.get('prices', [])
                            if prices:
                                print(f"Historical Data:")
                                print(f"Data Points: {len(prices)}")

                                current_result = plugin.coingecko_client.get_crypto_price(crypto_id, vs_currency)
                                if current_result and crypto_id in current_result:
                                    current_price = current_result[crypto_id].get(vs_currency, 0)
                                    print(f"Current Price: {current_price:,.2f} {vs_currency.upper()}")

                                price_values = [p[1] for p in prices if len(p) > 1]
                                if price_values:
                                    first_price = price_values[0]
                                    last_price = price_values[-1]
                                    min_price = min(price_values)
                                    max_price = max(price_values)

                                    if first_price > 0:
                                        change = ((last_price - first_price) / first_price) * 100
                                        print(f"Period Change: {change:+.2f}%")

                                    print(f"High: {max_price:,.2f} {vs_currency.upper()}")
                                    print(f"Low: {min_price:,.2f} {vs_currency.upper()}")
                                    print(f"Range: {max_price - min_price:,.2f} {vs_currency.upper()}")
                            else:
                                print("❌ No price data available")
                        else:
                            print(f"❌ Failed to get historical data")
                    else:
                        print("❌ Please enter cryptocurrency ID")

                elif choice == '6':
                    crypto_id = input("Enter cryptocurrency ID (e.g., ethereum): ").strip()

                    if crypto_id:
                        print(f"\n📋 Getting information for {crypto_id.upper()}...")
                        result = plugin.coingecko_client.get_currency_info(crypto_id)

                        if result:
                            print(f"Basic Information:")
                            print(f"Name: {result.get('name', 'N/A')}")
                            print(f"Symbol: {result.get('symbol', '').upper()}")
                            print(f"Rank: #{result.get('market_cap_rank', 'N/A')}")

                            description = result.get('description', {}).get('en', '')
                            if description:
                                desc = description[:200] + "..." if len(description) > 200 else description
                                print(f"Description: {desc}")

                            market_data = result.get('market_data', {})
                            if market_data:
                                print(f"\nMarket Data:")

                                current_price = market_data.get('current_price', {}).get('usd', 0)
                                market_cap = market_data.get('market_cap', {}).get('usd', 0)
                                volume = market_data.get('total_volume', {}).get('usd', 0)

                                print(f"Current Price: ${current_price:,.2f}")
                                print(f"Market Cap: ${market_cap:,.0f}")
                                print(f"24h Volume: ${volume:,.0f}")

                                price_change_24h = market_data.get('price_change_24h', 0)
                                price_change_percentage_24h = market_data.get('price_change_percentage_24h', 0)

                                print(f"24h Price Change: ${price_change_24h:,.2f}")
                                print(f"24h Price Change %: {price_change_percentage_24h:+.2f}%")

                                ath = market_data.get('ath', {}).get('usd', 0)
                                ath_change_percentage = market_data.get('ath_change_percentage', {}).get('usd', 0)
                                ath_date = market_data.get('ath_date', {}).get('usd', '')

                                atl = market_data.get('atl', {}).get('usd', 0)
                                atl_change_percentage = market_data.get('atl_change_percentage', {}).get('usd', 0)
                                atl_date = market_data.get('atl_date', {}).get('usd', '')

                                print(f"\nAll Time High: ${ath:,.2f}")
                                print(f"ATH Change: {ath_change_percentage:+.2f}%")
                                if ath_date:
                                    print(f"ATH Date: {ath_date[:10]}")

                                print(f"\nAll Time Low: ${atl:,.2f}")
                                print(f"ATL Change: {atl_change_percentage:+.2f}%")
                                if atl_date:
                                    print(f"ATL Date: {atl_date[:10]}")

                                print(f"\nSupply Information:")
                                circulating = market_data.get('circulating_supply', 0)
                                total = market_data.get('total_supply', 0)
                                max_supply = market_data.get('max_supply', 0)

                                if circulating:
                                    print(f"Circulating Supply: {circulating:,.0f}")
                                if total:
                                    print(f"Total Supply: {total:,.0f}")
                                if max_supply:
                                    print(f"Max Supply: {max_supply:,.0f}")
                        else:
                            print(f"❌ Failed to get currency info")
                    else:
                        print("❌ Please enter cryptocurrency ID")

                elif choice == '7':
                    query = input("Search query: ").strip()

                    if len(query) >= 2:
                        print(f"\n🔍 Searching for '{query}'...")
                        result = plugin.coingecko_client.get_supported_cryptocurrencies()

                        if result:
                            search_results = []
                            for crypto in result:
                                if (query.lower() in crypto.get('id', '').lower() or 
                                    query.lower() in crypto.get('name', '').lower() or 
                                    query.lower() in crypto.get('symbol', '').lower()):
                                    search_results.append(crypto)

                            if search_results:
                                print(f"Found {len(search_results)} cryptocurrencies:")
                                print("Showing first 10 results:")

                                for i, crypto in enumerate(search_results[:10], 1):
                                    name = crypto.get('name', 'Unknown')
                                    symbol = crypto.get('symbol', '').upper()
                                    crypto_id = crypto.get('id', 'N/A')

                                    print(f"\n#{i} {name} ({symbol})")
                                    print(f"  ID: {crypto_id}")
                            else:
                                print(f"🔍 No cryptocurrencies found for '{query}'")
                        else:
                            print("❌ Failed to get cryptocurrency list")
                    else:
                        print("❌ Search query too short (minimum 2 characters)")

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
                continue

    except Exception as e:
        print(f"\n❌ Fatal error in interactive demo: {e}")


def main():
    interactive()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
