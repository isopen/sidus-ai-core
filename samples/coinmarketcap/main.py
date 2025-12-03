import sys
import time
import os

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
from sidusai.plugins.coinmarketcap import CoinMarketCapPlugin

def agent_creation():
    try:
        print("🤖 Creating Sidus AI agent...")
        agent = sai.Agent()
        print("✅ Sidus AI agent created")

        print("🔧 Creating CoinMarketCap plugin...")
        api_key = os.environ.get('COINMARKETCAP_API_KEY')
        plugin = CoinMarketCapPlugin(api_key=api_key)
        print("✅ CoinMarketCap plugin created")

        print("🔧 Applying CoinMarketCap plugin to agent...")
        plugin.apply_plugin(agent)
        print("✅ CoinMarketCap plugin applied")

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

        if hasattr(plugin, 'coinmarketcap_client'):
            print("🔗 Testing CoinMarketCap API connection...")
            if plugin.coinmarketcap_client.test_connection():
                print("✅ CoinMarketCap API connection successful")
            else:
                print("⚠️ CoinMarketCap API connection issues")
                print("ℹ️ Make sure you have a valid API key from https://coinmarketcap.com/api/")

        while True:
            try:
                print("\n" + "-"*50)
                print("Commands:")
                print("1. price <symbol>       - Get cryptocurrency price")
                print("2. market [limit]       - Get top cryptocurrencies")
                print("3. convert              - Convert cryptocurrency")
                print("4. trending             - Get trending cryptocurrencies")
                print("5. history              - Get historical data")
                print("6. info                 - Get cryptocurrency information")
                print("7. global               - Get global market metrics")
                print("8. search               - Search cryptocurrencies")
                print("9. exit                 - Exit")
                print("-"*50)

                choice = input("\n🔧 Enter command number (1-9): ").strip()

                if choice == '1':
                    symbol = input("Enter cryptocurrency symbol (e.g., BTC, ETH): ").strip().upper()
                    convert = input("Currency (USD, EUR, etc., default USD): ").strip().upper()
                    convert = convert if convert else "USD"

                    if symbol:
                        print(f"\n💰 Getting price for {symbol}...")
                        result = plugin.coinmarketcap_client.get_crypto_price(symbol, convert)

                        if result:
                            print(f"Name: {result.get('name', 'N/A')}")
                            print(f"Symbol: {result.get('symbol', 'N/A')}")
                            print(f"Price: ${result.get('price', 0):,.2f} {convert}")
                            print(f"1h Change: {result.get('percent_change_1h', 0):+.2f}%")
                            print(f"24h Change: {result.get('percent_change_24h', 0):+.2f}%")
                            print(f"7d Change: {result.get('percent_change_7d', 0):+.2f}%")
                            print(f"Market Cap: ${result.get('market_cap', 0):,.0f}")
                            print(f"24h Volume: ${result.get('volume_24h', 0):,.0f}")

                            circulating = result.get('circulating_supply')
                            if circulating:
                                print(f"Circulating Supply: {circulating:,.0f}")

                            last_updated = result.get('last_updated', '')
                            if last_updated:
                                print(f"Last Updated: {last_updated}")
                        else:
                            print(f"❌ Failed to get {symbol} price")
                    else:
                        print("❌ Please enter cryptocurrency symbol")

                elif choice == '2':
                    limit = input("How many cryptocurrencies to show (default 10): ").strip()
                    limit = int(limit) if limit.isdigit() else 10

                    convert = input("Currency (USD, EUR, etc., default USD): ").strip().upper()
                    convert = convert if convert else "USD"

                    if limit > 100:
                        print("⚠️ Maximum limit is 100, using 100")
                        limit = 100

                    print(f"\n📈 Getting top {limit} cryptocurrencies...")
                    result = plugin.coinmarketcap_client.get_crypto_market_data(limit, convert)

                    if result:
                        print(f"\nTop {len(result)} Cryptocurrencies by Market Cap:")
                        for i, crypto in enumerate(result[:10], 1):
                            change_emoji = "📈" if crypto.percent_change_24h >= 0 else "📉"
                            print(f"\n#{i} {crypto.name} ({crypto.symbol})")
                            print(f"  Price: ${crypto.price:,.2f}")
                            print(f"  24h Change: {change_emoji} {crypto.percent_change_24h:+.2f}%")
                            print(f"  Market Cap: ${crypto.market_cap:,.0f}")
                            print(f"  Rank: #{crypto.cmc_rank}")

                            if i <= 5:
                                print(f"  1h Change: {crypto.percent_change_1h:+.2f}%")
                                print(f"  7d Change: {crypto.percent_change_7d:+.2f}%")
                                print(f"  Volume 24h: ${crypto.volume_24h:,.0f}")
                    else:
                        print("❌ Failed to get market data")

                elif choice == '3':
                    try:
                        amount = float(input("Amount to convert: ").strip())
                        from_symbol = input("From cryptocurrency symbol (e.g., BTC): ").strip().upper()
                        to_symbol = input("To cryptocurrency symbol (e.g., ETH): ").strip().upper()

                        print(f"\n🔄 Converting {amount} {from_symbol} to {to_symbol}...")
                        result = plugin.coinmarketcap_client.convert_currency(amount, from_symbol, to_symbol)

                        if result and result.get('success'):
                            print(f"Conversion Result:")
                            print(f"{result['amount']} {result['symbol_from']} = {result['converted_amount']:.6f} {result['symbol_to']}")
                            print(f"Rate: 1 {result['symbol_from']} = {result['rate']:.6f} {result['symbol_to']}")

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
                    result = plugin.coinmarketcap_client.get_trending_cryptos()

                    if result:
                        print(f"Trending Cryptocurrencies:")
                        for i, crypto in enumerate(result[:5], 1):
                            name = crypto.get('name', 'Unknown')
                            symbol = crypto.get('symbol', '').upper()
                            rank = crypto.get('cmc_rank', 'N/A')
                            trend_score = crypto.get('trend_score', 0)

                            print(f"\n#{i} {name} ({symbol})")
                            print(f"  Rank: #{rank}")
                            print(f"  Trend Score: {trend_score:.2f}")

                            price_result = plugin.coinmarketcap_client.get_crypto_price(symbol)
                            if price_result:
                                print(f"  Price: ${price_result.get('price', 0):,.2f}")
                                print(f"  24h Change: {price_result.get('percent_change_24h', 0):+.2f}%")
                    else:
                        print("❌ Failed to get trending cryptos")

                elif choice == '5':
                    symbol = input("Enter cryptocurrency symbol (e.g., BTC, ETH): ").strip().upper()
                    time_period = input("Time period (1d, 7d, 30d, 90d, 365d, default 7d): ").strip().lower()
                    time_period = time_period if time_period in ['1d', '7d', '30d', '90d', '365d'] else '7d'

                    convert = input("Currency (USD, EUR, etc., default USD): ").strip().upper()
                    convert = convert if convert else "USD"

                    if symbol:
                        print(f"\n📊 Getting {time_period} historical data for {symbol}...")
                        result = plugin.coinmarketcap_client.get_historical_data(symbol, time_period, convert)

                        if result:
                            prices = result.get('prices', [])
                            if prices:
                                print(f"Historical Data:")
                                print(f"Data Points: {len(prices)}")
                                print(f"Time Period: {time_period}")

                                current_price = result.get('current_price', 0)
                                min_price = result.get('min_price', 0)
                                max_price = result.get('max_price', 0)
                                avg_price = result.get('avg_price', 0)
                                change_percentage = result.get('change_percentage', 0)

                                print(f"Current Price: ${current_price:,.2f}")
                                print(f"Period Change: {change_percentage:+.2f}%")
                                print(f"High: ${max_price:,.2f}")
                                print(f"Low: ${min_price:,.2f}")
                                print(f"Average: ${avg_price:,.2f}")
                                print(f"Range: ${max_price - min_price:,.2f}")

                                if len(prices) > 5:
                                    print(f"\nLast 5 prices:")
                                    for i, price in enumerate(prices[-5:], 1):
                                        print(f"  Day -{6-i}: ${price:,.2f}")
                            else:
                                print("❌ No price data available")
                        else:
                            print(f"❌ Failed to get historical data")
                    else:
                        print("❌ Please enter cryptocurrency symbol")

                elif choice == '6':
                    symbol = input("Enter cryptocurrency symbol (e.g., BTC, ETH): ").strip().upper()

                    if symbol:
                        print(f"\n📋 Getting information for {symbol}...")
                        result = plugin.coinmarketcap_client.get_currency_info(symbol)

                        if result:
                            print(f"Basic Information:")
                            print(f"Name: {result.get('name', 'N/A')}")
                            print(f"Symbol: {result.get('symbol', 'N/A')}")
                            print(f"Category: {result.get('category', 'Cryptocurrency')}")

                            description = result.get('description', '')
                            if description:
                                desc = description[:200] + "..." if len(description) > 200 else description
                                print(f"Description: {desc}")

                            print(f"Slug: {result.get('slug', 'N/A')}")
                            print(f"Date Added: {result.get('date_added', 'N/A')}")

                            urls = result.get('urls', {})
                            if urls:
                                print(f"\nURLs:")
                                if urls.get('website'):
                                    print(f"  Website: {urls['website'][0]}")
                                if urls.get('twitter'):
                                    print(f"  Twitter: {urls['twitter'][0]}")
                                if urls.get('reddit'):
                                    print(f"  Reddit: {urls['reddit'][0]}")

                            tags = result.get('tags', [])
                            if tags:
                                tags_str = ', '.join(tags[:5])
                                print(f"Tags: {tags_str}")
                                if len(tags) > 5:
                                    print(f"  + {len(tags) - 5} more tags")

                            platform = result.get('platform')
                            if platform:
                                print(f"Platform: {platform.get('name', 'N/A')}")
                                print(f"Platform Token: {platform.get('token_address', 'N/A')}")
                        else:
                            print(f"❌ Failed to get currency info")
                    else:
                        print("❌ Please enter cryptocurrency symbol")

                elif choice == '7':
                    convert = input("Currency (USD, EUR, etc., default USD): ").strip().upper()
                    convert = convert if convert else "USD"

                    print(f"\n🌍 Getting global cryptocurrency market metrics...")
                    result = plugin.coinmarketcap_client.get_global_metrics(convert)

                    if result:
                        print(f"Global Cryptocurrency Market:")
                        print(f"Total Market Cap: ${result.get('total_market_cap', 0):,.0f}")
                        print(f"24h Volume: ${result.get('total_volume_24h', 0):,.0f}")
                        print(f"Bitcoin Dominance: {result.get('btc_dominance', 0):.1f}%")
                        print(f"Ethereum Dominance: {result.get('eth_dominance', 0):.1f}%")
                        print(f"Active Cryptocurrencies: {result.get('active_cryptocurrencies', 0):,}")
                        print(f"Total Cryptocurrencies: {result.get('total_cryptocurrencies', 0):,}")

                        btc_dominance = result.get('btc_dominance', 0)
                        eth_dominance = result.get('eth_dominance', 0)
                        other_dominance = 100 - btc_dominance - eth_dominance

                        print(f"\nMarket Dominance Breakdown:")
                        print(f"  Bitcoin: {btc_dominance:.1f}%")
                        print(f"  Ethereum: {eth_dominance:.1f}%")
                        print(f"  Others: {other_dominance:.1f}%")
                    else:
                        print("❌ Failed to get global metrics")

                elif choice == '8':
                    query = input("Search query: ").strip()

                    if len(query) >= 2:
                        print(f"\n🔍 Searching for '{query}'...")
                        result = plugin.coinmarketcap_client.get_crypto_map()

                        if result:
                            search_results = []
                            for crypto in result:
                                if (query.lower() in crypto.get('name', '').lower() or 
                                    query.lower() in crypto.get('symbol', '').lower() or 
                                    query.lower() in crypto.get('slug', '').lower()):
                                    search_results.append(crypto)

                            if search_results:
                                print(f"Found {len(search_results)} cryptocurrencies:")
                                print("Showing first 10 results:")

                                for i, crypto in enumerate(search_results[:10], 1):
                                    name = crypto.get('name', 'Unknown')
                                    symbol = crypto.get('symbol', '').upper()
                                    crypto_id = crypto.get('id', 'N/A')
                                    slug = crypto.get('slug', 'N/A')

                                    print(f"\n#{i} {name} ({symbol})")
                                    print(f"  ID: {crypto_id}")
                                    print(f"  Slug: {slug}")

                                    if i <= 5:
                                        price_result = plugin.coinmarketcap_client.get_crypto_price(symbol)
                                        if price_result:
                                            print(f"  Price: ${price_result.get('price', 0):,.2f}")
                                            print(f"  24h Change: {price_result.get('percent_change_24h', 0):+.2f}%")
                            else:
                                print(f"🔍 No cryptocurrencies found for '{query}'")
                        else:
                            print("❌ Failed to get cryptocurrency list")
                    else:
                        print("❌ Search query too short (minimum 2 characters)")

                elif choice == '9':
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