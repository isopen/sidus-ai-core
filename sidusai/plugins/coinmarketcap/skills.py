from sidusai.core.plugin import ChatAgentValue, AgentValue
from typing import Dict, Any
from datetime import datetime

class CryptoCurrencyValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class CurrencyConversionValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class GlobalMetricsValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

def get_crypto_price_skill(context: Dict[str, Any]) -> CryptoCurrencyValue:
    print("🔧 Starting get_crypto_price_skill...")

    symbol = context.get('symbol')
    convert = context.get('convert', 'USD')

    if not symbol:
        result = {"error": "No cryptocurrency symbol provided"}
        return CryptoCurrencyValue(result)

    try:
        coinmarketcap_component = context.get('coinmarketcap_component')
        if not coinmarketcap_component:
            result = {"error": "CoinMarketCap component not available"}
            return CryptoCurrencyValue(result)

        print(f"💰 Getting price for {symbol.upper()} in {convert.upper()}...")

        api_result = coinmarketcap_component.get_crypto_price(symbol, convert)

        if not api_result:
            result = {"error": f"Failed to get price for {symbol.upper()}"}
            return CryptoCurrencyValue(result)

        result = {
            "success": True,
            "symbol": symbol.upper(),
            "convert": convert.upper(),
            "data": api_result,
            "timestamp": datetime.now().isoformat()
        }

        price = api_result.get('price', 0)
        return CryptoCurrencyValue(result)

    except Exception as e:
        print(f"❌ Error in get_crypto_price_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get crypto price: {str(e)}"}
        return CryptoCurrencyValue(result)

def get_crypto_market_data_skill(context: Dict[str, Any]) -> CryptoCurrencyValue:
    print("🔧 Starting get_crypto_market_data_skill...")

    limit = context.get('limit', 20)
    convert = context.get('convert', 'USD')

    try:
        coinmarketcap_component = context.get('coinmarketcap_component')
        if not coinmarketcap_component:
            result = {"error": "CoinMarketCap component not available"}
            return CryptoCurrencyValue(result)

        print(f"📈 Getting market data for top {limit} cryptocurrencies")

        cryptocurrencies = coinmarketcap_component.get_crypto_market_data(limit, convert)

        if not cryptocurrencies:
            result = {"error": "Failed to get market data"}
            return CryptoCurrencyValue(result)

        formatted_cryptos = []
        for crypto in cryptocurrencies:
            formatted_cryptos.append({
                "id": crypto.id,
                "name": crypto.name,
                "symbol": crypto.symbol,
                "cmc_rank": crypto.cmc_rank,
                "price": crypto.price,
                "market_cap": crypto.market_cap,
                "volume_24h": crypto.volume_24h,
                "percent_change_1h": crypto.percent_change_1h,
                "percent_change_24h": crypto.percent_change_24h,
                "percent_change_7d": crypto.percent_change_7d,
                "circulating_supply": crypto.circulating_supply,
                "total_supply": crypto.total_supply,
                "max_supply": crypto.max_supply,
                "last_updated": crypto.last_updated.isoformat() if crypto.last_updated else None,
                "tags": crypto.tags[:3] if crypto.tags else []
            })

        result = {
            "success": True,
            "convert": convert,
            "cryptocurrencies": formatted_cryptos,
            "count": len(formatted_cryptos),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(formatted_cryptos)} cryptocurrencies")
        return CryptoCurrencyValue(result)

    except Exception as e:
        print(f"❌ Error in get_crypto_market_data_skill: {e}")
        result = {"error": f"Failed to get market data: {str(e)}"}
        return CryptoCurrencyValue(result)

def convert_currency_skill(context: Dict[str, Any]) -> CurrencyConversionValue:
    print("🔧 Starting convert_currency_skill...")

    amount = context.get('amount')
    symbol = context.get('symbol')
    convert = context.get('convert')

    if not amount or not symbol or not convert:
        result = {"error": "Missing required parameters: amount, symbol, convert"}
        return CurrencyConversionValue(result)

    try:
        amount = float(amount)

        coinmarketcap_component = context.get('coinmarketcap_component')
        if not coinmarketcap_component:
            result = {"error": "CoinMarketCap component not available"}
            return CurrencyConversionValue(result)

        print(f"🔄 Converting {amount} {symbol.upper()} to {convert.upper()}")

        conversion_result = coinmarketcap_component.convert_currency(amount, symbol, convert)

        if not conversion_result or not conversion_result.get('success'):
            result = {"error": f"Failed to convert {symbol.upper()} to {convert.upper()}"}
            return CurrencyConversionValue(result)

        result = {
            "success": True,
            "conversion": conversion_result,
            "timestamp": datetime.now().isoformat()
        }

        converted_amount = conversion_result.get('converted_amount', 0)
        print(f"✅ Converted: {amount} {symbol.upper()} = {converted_amount:.4f} {convert.upper()}")
        return CurrencyConversionValue(result)

    except ValueError:
        result = {"error": "Invalid amount value"}
        return CurrencyConversionValue(result)
    except Exception as e:
        print(f"❌ Error in convert_currency_skill: {e}")
        result = {"error": f"Failed to convert currency: {str(e)}"}
        return CurrencyConversionValue(result)

def get_trending_cryptos_skill(context: Dict[str, Any]) -> CryptoCurrencyValue:
    print("🔧 Starting get_trending_cryptos_skill...")

    try:
        coinmarketcap_component = context.get('coinmarketcap_component')
        if not coinmarketcap_component:
            result = {"error": "CoinMarketCap component not available"}
            return CryptoCurrencyValue(result)

        print("📈 Getting trending cryptocurrencies")

        trending_cryptos = coinmarketcap_component.get_trending_cryptos()

        if not trending_cryptos:
            result = {"error": "Failed to get trending cryptocurrencies"}
            return CryptoCurrencyValue(result)

        formatted_trending = []
        for i, crypto in enumerate(trending_cryptos[:10], 1):
            formatted_trending.append({
                "rank": i,
                "id": crypto.get('id', ''),
                "name": crypto.get('name', ''),
                "symbol": crypto.get('symbol', '').upper(),
                "cmc_rank": crypto.get('cmc_rank', 0),
                "trend_score": crypto.get('trend_score', 0)
            })

        result = {
            "success": True,
            "trending_cryptos": formatted_trending,
            "count": len(formatted_trending),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Found {len(formatted_trending)} trending cryptocurrencies")
        return CryptoCurrencyValue(result)

    except Exception as e:
        print(f"❌ Error in get_trending_cryptos_skill: {e}")
        result = {"error": f"Failed to get trending cryptos: {str(e)}"}
        return CryptoCurrencyValue(result)

def get_historical_data_skill(context: Dict[str, Any]) -> CryptoCurrencyValue:
    print("🔧 Starting get_historical_data_skill...")

    symbol = context.get('symbol')
    time_period = context.get('time_period', '7d')
    convert = context.get('convert', 'USD')

    if not symbol:
        result = {"error": "No cryptocurrency symbol provided"}
        return CryptoCurrencyValue(result)

    try:
        coinmarketcap_component = context.get('coinmarketcap_component')
        if not coinmarketcap_component:
            result = {"error": "CoinMarketCap component not available"}
            return CryptoCurrencyValue(result)

        print(f"📊 Getting {time_period} historical data for {symbol.upper()}")

        historical_data = coinmarketcap_component.get_historical_data(symbol, time_period, convert)

        if not historical_data:
            result = {"error": f"Failed to get historical data for {symbol.upper()}"}
            return CryptoCurrencyValue(result)

        prices = historical_data.get('prices', [])

        sample_data = []
        if len(prices) > 0:
            for i, price in enumerate(prices[-5:], 1):
                sample_data.append({
                    "day": i,
                    "price": price
                })

        result = {
            "success": True,
            "symbol": symbol.upper(),
            "time_period": time_period,
            "convert": convert.upper(),
            "current_price": historical_data.get('current_price', 0),
            "min_price": historical_data.get('min_price', 0),
            "max_price": historical_data.get('max_price', 0),
            "avg_price": historical_data.get('avg_price', 0),
            "change_percentage": historical_data.get('change_percentage', 0),
            "data_points": historical_data.get('data_points', 0),
            "sample_data": sample_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Historical data retrieved for {symbol.upper()}")
        return CryptoCurrencyValue(result)

    except Exception as e:
        print(f"❌ Error in get_historical_data_skill: {e}")
        result = {"error": f"Failed to get historical data: {str(e)}"}
        return CryptoCurrencyValue(result)

def get_currency_info_skill(context: Dict[str, Any]) -> CryptoCurrencyValue:
    print("🔧 Starting get_currency_info_skill...")

    symbol = context.get('symbol')

    if not symbol:
        result = {"error": "No cryptocurrency symbol provided"}
        return CryptoCurrencyValue(result)

    try:
        coinmarketcap_component = context.get('coinmarketcap_component')
        if not coinmarketcap_component:
            result = {"error": "CoinMarketCap component not available"}
            return CryptoCurrencyValue(result)

        print(f"📋 Getting information for {symbol.upper()}")

        currency_info = coinmarketcap_component.get_currency_info(symbol)

        if not currency_info:
            result = {"error": f"Failed to get information for {symbol.upper()}"}
            return CryptoCurrencyValue(result)

        result = {
            "success": True,
            "symbol": symbol.upper(),
            "info": currency_info,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Information retrieved for {symbol.upper()}")
        return CryptoCurrencyValue(result)

    except Exception as e:
        print(f"❌ Error in get_currency_info_skill: {e}")
        result = {"error": f"Failed to get currency info: {str(e)}"}
        return CryptoCurrencyValue(result)

def get_global_metrics_skill(context: Dict[str, Any]) -> GlobalMetricsValue:
    print("🔧 Starting get_global_metrics_skill...")

    convert = context.get('convert', 'USD')

    try:
        coinmarketcap_component = context.get('coinmarketcap_component')
        if not coinmarketcap_component:
            result = {"error": "CoinMarketCap component not available"}
            return GlobalMetricsValue(result)

        print("🌍 Getting global cryptocurrency metrics")

        global_metrics = coinmarketcap_component.get_global_metrics(convert)

        if not global_metrics:
            result = {"error": "Failed to get global metrics"}
            return GlobalMetricsValue(result)

        result = {
            "success": True,
            "convert": convert.upper(),
            "metrics": global_metrics,
            "timestamp": datetime.now().isoformat()
        }

        print("✅ Global metrics retrieved")
        return GlobalMetricsValue(result)

    except Exception as e:
        print(f"❌ Error in get_global_metrics_skill: {e}")
        result = {"error": f"Failed to get global metrics: {str(e)}"}
        return GlobalMetricsValue(result)

def coinmarketcap_chat_skill(chat: ChatAgentValue) -> ChatAgentValue:
    print("🔧 Starting coinmarketcap_chat_skill...")

    try:
        if not chat.messages:
            chat.append_assistant(
                "💰 CoinMarketCap - Professional Crypto Data\n\n"
                "I provide real-time cryptocurrency data from CoinMarketCap API.\n\n"
                "Available Commands:\n"
                "• price <symbol> - Get cryptocurrency price (e.g., price BTC)\n"
                "• market [limit] - Get top cryptocurrencies (e.g., market 10)\n"
                "• trending - Get trending cryptocurrencies\n"
                "• convert <amount> <from> <to> - Convert cryptocurrency (e.g., convert 1 BTC ETH)\n"
                "• history <symbol> [period] - Get historical data (e.g., history BTC 30d)\n"
                "• info <symbol> - Get cryptocurrency information\n"
                "• global - Get global market metrics\n"
                "• search <query> - Search for cryptocurrencies\n"
                "• help - Show this help message\n\n"
                "Examples:\n"
                "• price BTC\n"
                "• market 20\n"
                "• trending\n"
                "• convert 1 BTC ETH\n"
                "• history ETH 30d\n"
                "• info ADA\n"
                "• global\n"
                "• search doge"
            )
            return chat

        last_message = chat.messages[-1]['content'].strip().lower()

        coinmarketcap_component = chat.context.get('coinmarketcap_component') if hasattr(chat, 'context') else None

        if not coinmarketcap_component:
            chat.append_assistant("❌ CoinMarketCap API component not available")
            return chat

        if last_message.startswith('price '):
            symbol = last_message.replace('price ', '').strip().upper()
            context = {
                'symbol': symbol,
                'coinmarketcap_component': coinmarketcap_component
            }

            result = get_crypto_price_skill(context)
            data = result.value

            if data.get('success'):
                crypto_data = data['data']
                change_emoji = "📈" if crypto_data['percent_change_24h'] >= 0 else "📉"
                response = [
                    f"💰 {symbol} Price",
                    f"Name: {crypto_data['name']}",
                    f"Price: ${crypto_data['price']:,.2f} USD",
                    f"24h Change: {change_emoji} {crypto_data['percent_change_24h']:+.2f}%",
                    f"1h Change: {crypto_data['percent_change_1h']:+.2f}%",
                    f"7d Change: {crypto_data['percent_change_7d']:+.2f}%",
                    f"Market Cap: ${crypto_data['market_cap']:,.0f}",
                    f"24h Volume: ${crypto_data['volume_24h']:,.0f}",
                    f"Circulating Supply: {crypto_data['circulating_supply']:,.0f}",
                    f"Last Updated: {datetime.fromisoformat(crypto_data['last_updated'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')}"
                ]
                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get price: {data.get('error', 'Unknown error')}")

        elif last_message.startswith('market'):
            parts = last_message.split()
            limit = 10
            if len(parts) > 1:
                try:
                    limit = int(parts[1])
                except ValueError:
                    limit = 10

            context = {
                'limit': limit,
                'coinmarketcap_component': coinmarketcap_component
            }

            result = get_crypto_market_data_skill(context)
            data = result.value

            if data.get('success'):
                cryptos = data['cryptocurrencies']

                response = [
                    f"📈 Top {len(cryptos)} Cryptocurrencies",
                    f"Sorted by market cap",
                    ""
                ]

                for i, crypto in enumerate(cryptos[:5], 1):
                    change_emoji = "📈" if crypto['percent_change_24h'] >= 0 else "📉"
                    response.extend([
                        f"#{i} {crypto['name']} ({crypto['symbol']})",
                        f"• Rank: #{crypto['cmc_rank']}",
                        f"• Price: ${crypto['price']:,.2f}",
                        f"• 24h Change: {change_emoji} {crypto['percent_change_24h']:+.2f}%",
                        f"• Market Cap: ${crypto['market_cap']:,.0f}",
                        ""
                    ])

                if len(cryptos) > 5:
                    response.append(f"... and {len(cryptos) - 5} more cryptocurrencies")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get market data: {data.get('error', 'Unknown error')}")

        elif last_message == 'trending':
            context = {
                'coinmarketcap_component': coinmarketcap_component
            }

            result = get_trending_cryptos_skill(context)
            data = result.value

            if data.get('success'):
                trending = data['trending_cryptos']

                response = [
                    f"🔥 Trending Cryptocurrencies",
                    f"Based on CoinMarketCap trending data",
                    ""
                ]

                for i, crypto in enumerate(trending[:5], 1):
                    response.extend([
                        f"#{i} {crypto['name']} ({crypto['symbol']})",
                        f"• Overall Rank: #{crypto['cmc_rank'] if crypto['cmc_rank'] > 0 else 'N/A'}",
                        f"• Trend Score: {crypto['trend_score']:.2f}",
                        ""
                    ])

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get trending cryptos: {data.get('error', 'Unknown error')}")

        elif last_message.startswith('convert '):
            parts = last_message.replace('convert ', '').strip().split()
            if len(parts) == 3:
                try:
                    amount = float(parts[0])
                    from_symbol = parts[1].upper()
                    to_symbol = parts[2].upper()

                    context = {
                        'amount': amount,
                        'symbol': from_symbol,
                        'convert': to_symbol,
                        'coinmarketcap_component': coinmarketcap_component
                    }

                    result = convert_currency_skill(context)
                    data = result.value

                    if data.get('success'):
                        conversion = data['conversion']
                        response = [
                            f"🔄 Cryptocurrency Conversion",
                            f"{amount:,.6f} {from_symbol} = {conversion['converted_amount']:.6f} {to_symbol}",
                            f"Exchange Rate: 1 {from_symbol} = {conversion['rate']:.6f} {to_symbol}",
                            f"Rate updated: {conversion['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
                        ]
                        chat.append_assistant("\n".join(response))
                    else:
                        chat.append_assistant(f"❌ Failed to convert: {data.get('error', 'Unknown error')}")
                except ValueError:
                    chat.append_assistant("❌ Invalid amount. Usage: convert <amount> <from> <to>")
            else:
                chat.append_assistant("❌ Invalid format. Usage: convert <amount> <from> <to>")

        elif last_message.startswith('history '):
            parts = last_message.replace('history ', '').strip().split()
            if len(parts) >= 1:
                symbol = parts[0].upper()
                time_period = parts[1] if len(parts) > 1 else "7d"

                allowed_periods = ["1d", "7d", "30d", "90d", "365d"]
                if time_period not in allowed_periods:
                    time_period = "7d"

                context = {
                    'symbol': symbol,
                    'time_period': time_period,
                    'coinmarketcap_component': coinmarketcap_component
                }

                result = get_historical_data_skill(context)
                data = result.value

                if data.get('success'):
                    change_emoji = "📈" if data['change_percentage'] >= 0 else "📉"
                    response = [
                        f"📊 {symbol} - {time_period} History",
                        f"Current Price: ${data['current_price']:,.2f}",
                        f"Period Change: {change_emoji} {data['change_percentage']:+.2f}%",
                        f"High: ${data['max_price']:,.2f}",
                        f"Low: ${data['min_price']:,.2f}",
                        f"Average: ${data['avg_price']:,.2f}",
                        f"Data Points: {data['data_points']}",
                        ""
                    ]

                    if data.get('sample_data'):
                        response.append("Recent Prices:")
                        for sample in data['sample_data']:
                            response.append(f"• Day {sample['day']}: ${sample['price']:,.2f}")

                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"❌ Failed to get history: {data.get('error', 'Unknown error')}")
            else:
                chat.append_assistant("❌ Invalid format. Usage: history <symbol> [period]")

        elif last_message.startswith('info '):
            symbol = last_message.replace('info ', '').strip().upper()
            context = {
                'symbol': symbol,
                'coinmarketcap_component': coinmarketcap_component
            }

            result = get_currency_info_skill(context)
            data = result.value

            if data.get('success'):
                info = data['info']

                response = [
                    f"📋 {symbol} Information",
                    f"Name: {info['name']}",
                    f"Symbol: {info['symbol']}",
                    f"Category: {info.get('category', 'Cryptocurrency')}",
                    ""
                ]

                if info.get('description'):
                    desc = info['description'][:200] + "..." if len(info['description']) > 200 else info['description']
                    response.append(f"Description: {desc}")
                    response.append("")

                if info.get('urls'):
                    urls = info['urls']
                    if urls.get('website'):
                        response.append(f"Website: {urls['website'][0] if urls['website'] else 'N/A'}")
                    if urls.get('twitter'):
                        response.append(f"Twitter: {urls['twitter'][0] if urls['twitter'] else 'N/A'}")
                    response.append("")

                if info.get('tags'):
                    tags = ', '.join(info['tags'][:5])
                    response.append(f"Tags: {tags}")

                if info.get('date_added'):
                    response.append(f"Date Added: {info['date_added']}")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get info: {data.get('error', 'Unknown error')}")

        elif last_message == 'global':
            context = {
                'coinmarketcap_component': coinmarketcap_component
            }

            result = get_global_metrics_skill(context)
            data = result.value

            if data.get('success'):
                metrics = data['metrics']

                btc_dominance = metrics['btc_dominance']
                eth_dominance = metrics['eth_dominance']
                total_share = btc_dominance + eth_dominance
                other_dominance = 100 - total_share

                response = [
                    f"🌍 Global Cryptocurrency Market",
                    f"Total Market Cap: ${metrics['total_market_cap']:,.0f}",
                    f"24h Volume: ${metrics['total_volume_24h']:,.0f}",
                    f"Active Cryptocurrencies: {metrics['active_cryptocurrencies']:,}",
                    f"Total Cryptocurrencies: {metrics['total_cryptocurrencies']:,}",
                    "",
                    f"Market Dominance:",
                    f"• Bitcoin: {btc_dominance:.1f}%",
                    f"• Ethereum: {eth_dominance:.1f}%",
                    f"• Others: {other_dominance:.1f}%"
                ]

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get global metrics: {data.get('error', 'Unknown error')}")

        elif last_message.startswith('search '):
            query = last_message.replace('search ', '').strip().lower()

            if len(query) < 2:
                chat.append_assistant("❌ Search query too short. Minimum 2 characters")
                return chat

            try:
                crypto_map = coinmarketcap_component.get_crypto_map()
                if not crypto_map:
                    chat.append_assistant("❌ Failed to get cryptocurrency list")
                    return chat

                search_results = []
                for crypto in crypto_map:
                    if (query in crypto.get('name', '').lower() or 
                        query in crypto.get('symbol', '').lower() or
                        query in crypto.get('slug', '').lower()):
                        search_results.append(crypto)

                if search_results:
                    response = [
                        f"🔍 Search Results for '{query}'",
                        f"Found: {len(search_results)} cryptocurrencies",
                        ""
                    ]

                    for i, result in enumerate(search_results[:5], 1):
                        response.extend([
                            f"#{i} {result.get('name', 'Unknown')} ({result.get('symbol', '').upper()})",
                            f"• ID: {result.get('id', 'N/A')}",
                            f"• Slug: {result.get('slug', 'N/A')}",
                            ""
                        ])

                    response.append("💡 Use price <symbol> to get current price")
                    response.append("💡 Use info <symbol> to get detailed information")
                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"🔍 No cryptocurrencies found for '{query}'")
            except Exception as e:
                print(f"❌ Search error: {e}")
                chat.append_assistant(f"❌ Search failed: {str(e)}")

        elif last_message == 'help':
            chat.append_assistant(
                "💰 CoinMarketCap - Professional Crypto Data\n\n"
                "Available Commands:\n"
                "• price <symbol> - Get cryptocurrency price\n"
                "• market [limit] - Get top cryptocurrencies\n"
                "• trending - Get trending cryptocurrencies\n"
                "• convert <amount> <from> <to> - Convert cryptocurrency\n"
                "• history <symbol> [period] - Get historical data\n"
                "• info <symbol> - Get cryptocurrency information\n"
                "• global - Get global market metrics\n"
                "• search <query> - Search for cryptocurrencies\n"
                "• help - Show this help message\n\n"
                "Examples:\n"
                "• price BTC\n"
                "• market 20\n"
                "• trending\n"
                "• convert 1 BTC ETH\n"
                "• history ETH 30d\n"
                "• info ADA\n"
                "• global\n"
                "• search doge"
            )

        else:
            chat.append_assistant(
                "🤔 I didn't understand that command.\n\n"
                "Available commands:\n"
                "• price <symbol> - Get cryptocurrency price\n"
                "• market [limit] - Get market data\n"
                "• trending - Get trending cryptos\n"
                "• convert <amount> <from> <to> - Convert cryptocurrency\n"
                "• history <symbol> [period] - Get historical data\n"
                "• info <symbol> - Get cryptocurrency info\n"
                "• global - Get global market metrics\n"
                "• search <query> - Search cryptos\n"
                "• help - Show help\n\n"
                "Type help for more information."
            )

    except Exception as e:
        print(f"❌ Error in coinmarketcap_chat_skill: {e}")
        import traceback
        traceback.print_exc()
        chat.append_assistant("❌ An error occurred while processing your request")

    return chat