from sidusai.core.plugin import ChatAgentValue, AgentValue
from typing import Dict, Any
from datetime import datetime

class CryptoCurrencyValue(AgentValue):
    """Value class for cryptocurrency data"""
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class CurrencyRatesValue(AgentValue):
    """Value class for currency rates data"""
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class CurrencyConversionValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

def get_crypto_price_skill(context: Dict[str, Any]) -> CryptoCurrencyValue:
    print("🔧 Starting get_crypto_price_skill...")

    crypto_id = context.get('crypto_id')
    vs_currency = context.get('vs_currency', 'usd')

    if not crypto_id:
        result = {"error": "No cryptocurrency ID provided"}
        return CryptoCurrencyValue(result)

    try:
        coingecko_component = context.get('coingecko_component')
        if not coingecko_component:
            result = {"error": "Coingecko component not available"}
            return CryptoCurrencyValue(result)

        print(f"💰 Getting price for {crypto_id.upper()} in {vs_currency.upper()}")

        api_result = coingecko_component.get_crypto_price(crypto_id, vs_currency)

        if not api_result:
            result = {"error": "API request failed"}
            return CryptoCurrencyValue(result)

        if crypto_id not in api_result:
            result = {"error": f"Cryptocurrency {crypto_id} not found"}
            return CryptoCurrencyValue(result)

        crypto_data = api_result[crypto_id]

        result = {
            "success": True,
            "crypto_id": crypto_id,
            "vs_currency": vs_currency,
            "price": crypto_data.get(vs_currency, 0),
            "market_cap": crypto_data.get(f"{vs_currency}_market_cap", 0),
            "volume_24h": crypto_data.get(f"{vs_currency}_24h_vol", 0),
            "change_24h": crypto_data.get(f"{vs_currency}_24h_change", 0),
            "last_updated": crypto_data.get("last_updated_at", 0),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ {crypto_id.upper()} price: {result['price']} {vs_currency.upper()}")
        return CryptoCurrencyValue(result)

    except Exception as e:
        print(f"❌ Error in get_crypto_price_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get crypto price: {str(e)}"}
        return CryptoCurrencyValue(result)

def get_crypto_market_data_skill(context: Dict[str, Any]) -> CryptoCurrencyValue:
    print("🔧 Starting get_crypto_market_data_skill...")

    vs_currency = context.get('vs_currency', 'usd')
    limit = context.get('limit', 20)

    try:
        coingecko_component = context.get('coingecko_component')
        if not coingecko_component:
            result = {"error": "Coingecko component not available"}
            return CryptoCurrencyValue(result)

        print(f"📈 Getting market data for top {limit} cryptocurrencies")

        cryptocurrencies = coingecko_component.get_crypto_market_data(vs_currency, limit)

        if not cryptocurrencies:
            result = {"error": "Failed to get market data"}
            return CryptoCurrencyValue(result)

        formatted_cryptos = []
        for crypto in cryptocurrencies:
            formatted_cryptos.append({
                "id": crypto.id,
                "symbol": crypto.symbol,
                "name": crypto.name,
                "current_price": crypto.current_price,
                "market_cap": crypto.market_cap,
                "market_cap_rank": crypto.market_cap_rank,
                "price_change_24h": crypto.price_change_24h,
                "price_change_percentage_24h": crypto.price_change_percentage_24h,
                "circulating_supply": crypto.circulating_supply,
                "total_supply": crypto.total_supply,
                "last_updated": crypto.last_updated.isoformat() if crypto.last_updated else None,
                "image": crypto.image
            })

        result = {
            "success": True,
            "vs_currency": vs_currency,
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
    from_currency = context.get('from_currency')
    to_currency = context.get('to_currency')

    if not amount or not from_currency or not to_currency:
        result = {"error": "Missing required parameters: amount, from_currency, to_currency"}
        return CurrencyConversionValue(result)

    try:
        amount = float(amount)

        coingecko_component = context.get('coingecko_component')
        if not coingecko_component:
            result = {"error": "Coingecko component not available"}
            return CurrencyConversionValue(result)

        print(f"🔄 Converting {amount} {from_currency} to {to_currency}")

        conversion_result = coingecko_component.convert_currency(amount, from_currency, to_currency)

        if not conversion_result or not conversion_result.get('success'):
            result = {"error": f"Failed to convert {from_currency} to {to_currency}"}
            return CurrencyConversionValue(result)

        result = {
            "success": True,
            "conversion": conversion_result,
            "timestamp": datetime.now().isoformat()
        }

        converted_amount = conversion_result.get('converted_amount', 0)
        print(f"✅ Converted: {amount} {from_currency} = {converted_amount:.4f} {to_currency}")
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
        coingecko_component = context.get('coingecko_component')
        if not coingecko_component:
            result = {"error": "Coingecko component not available"}
            return CryptoCurrencyValue(result)

        print("📈 Getting trending cryptocurrencies")

        trending_cryptos = coingecko_component.get_trending_cryptos()

        if not trending_cryptos:
            result = {"error": "Failed to get trending cryptocurrencies"}
            return CryptoCurrencyValue(result)

        formatted_trending = []
        for i, crypto in enumerate(trending_cryptos[:10], 1):
            coin_data = crypto.get('item', {})
            formatted_trending.append({
                "rank": i,
                "id": coin_data.get('id', ''),
                "name": coin_data.get('name', ''),
                "symbol": coin_data.get('symbol', '').upper(),
                "market_cap_rank": coin_data.get('market_cap_rank', 0),
                "score": crypto.get('score', 0)
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

    crypto_id = context.get('crypto_id')
    vs_currency = context.get('vs_currency', 'usd')
    days = context.get('days', 7)

    if not crypto_id:
        result = {"error": "No cryptocurrency ID provided"}
        return CryptoCurrencyValue(result)

    try:
        days = int(days)

        coingecko_component = context.get('coingecko_component')
        if not coingecko_component:
            result = {"error": "Coingecko component not available"}
            return CryptoCurrencyValue(result)

        print(f"📊 Getting {days}-day historical data for {crypto_id.upper()}")

        historical_data = coingecko_component.get_historical_data(crypto_id, vs_currency, days)

        if not historical_data:
            result = {"error": f"Failed to get historical data for {crypto_id}"}
            return CryptoCurrencyValue(result)

        prices = historical_data.get('prices', [])
        market_caps = historical_data.get('market_caps', [])
        volumes = historical_data.get('total_volumes', [])

        formatted_prices = []
        for price_data in prices[-10:]:
            if len(price_data) >= 2:
                timestamp = datetime.fromtimestamp(price_data[0] / 1000)
                formatted_prices.append({
                    "timestamp": timestamp.isoformat(),
                    "price": price_data[1]
                })

        if prices:
            price_values = [p[1] for p in prices if len(p) >= 2]
            if price_values:
                current_price = price_values[-1]
                min_price = min(price_values)
                max_price = max(price_values)
                avg_price = sum(price_values) / len(price_values)

                if len(price_values) > 1:
                    change_percentage = ((current_price - price_values[0]) / price_values[0]) * 100
                else:
                    change_percentage = 0
            else:
                current_price = min_price = max_price = avg_price = change_percentage = 0
        else:
            current_price = min_price = max_price = avg_price = change_percentage = 0

        result = {
            "success": True,
            "crypto_id": crypto_id,
            "vs_currency": vs_currency,
            "days": days,
            "current_price": current_price,
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "change_percentage": change_percentage,
            "sample_data": formatted_prices,
            "total_data_points": len(prices),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Historical data retrieved for {crypto_id.upper()}")
        return CryptoCurrencyValue(result)

    except Exception as e:
        print(f"❌ Error in get_historical_data_skill: {e}")
        result = {"error": f"Failed to get historical data: {str(e)}"}
        return CryptoCurrencyValue(result)

def get_currency_info_skill(context: Dict[str, Any]) -> CryptoCurrencyValue:
    print("🔧 Starting get_currency_info_skill...")

    crypto_id = context.get('crypto_id')

    if not crypto_id:
        result = {"error": "No cryptocurrency ID provided"}
        return CryptoCurrencyValue(result)

    try:
        coingecko_component = context.get('coingecko_component')
        if not coingecko_component:
            result = {"error": "Coingecko component not available"}
            return CryptoCurrencyValue(result)

        print(f"📋 Getting information for {crypto_id.upper()}")

        currency_info = coingecko_component.get_currency_info(crypto_id)

        if not currency_info:
            result = {"error": f"Failed to get information for {crypto_id}"}
            return CryptoCurrencyValue(result)

        market_data = currency_info.get('market_data', {})

        result = {
            "success": True,
            "crypto_id": crypto_id,
            "info": {
                "id": currency_info.get('id', ''),
                "symbol": currency_info.get('symbol', '').upper(),
                "name": currency_info.get('name', ''),
                "description": currency_info.get('description', {}).get('en', ''),
                "homepage": currency_info.get('links', {}).get('homepage', [''])[0],
                "genesis_date": currency_info.get('genesis_date', ''),
                "market_cap_rank": currency_info.get('market_cap_rank', 0),
                "current_price": market_data.get('current_price', {}).get('usd', 0),
                "market_cap": market_data.get('market_cap', {}).get('usd', 0),
                "total_volume": market_data.get('total_volume', {}).get('usd', 0),
                "circulating_supply": market_data.get('circulating_supply', 0),
                "total_supply": market_data.get('total_supply', 0),
                "max_supply": market_data.get('max_supply', 0),
                "ath": market_data.get('ath', {}).get('usd', 0),
                "ath_change_percentage": market_data.get('ath_change_percentage', {}).get('usd', 0),
                "atl": market_data.get('atl', {}).get('usd', 0),
                "atl_change_percentage": market_data.get('atl_change_percentage', {}).get('usd', 0),
            },
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Information retrieved for {crypto_id.upper()}")
        return CryptoCurrencyValue(result)

    except Exception as e:
        print(f"❌ Error in get_currency_info_skill: {e}")
        result = {"error": f"Failed to get currency info: {str(e)}"}
        return CryptoCurrencyValue(result)

def coingecko_chat_skill(chat: ChatAgentValue) -> ChatAgentValue:
    print("🔧 Starting coingecko_chat_skill...")

    try:
        if not chat.messages:
            chat.append_assistant(
                "💰 **Coingecko - Cryptocurrency Monitor**\n\n"
                "I provide real-time cryptocurrency data and monitoring.\n\n"
                "**Available Commands:**\n"
                "• `price <crypto>` - Get cryptocurrency price (e.g., price bitcoin)\n"
                "• `market [limit]` - Get top cryptocurrencies (e.g., market 10)\n"
                "• `trending` - Get trending cryptocurrencies\n"
                "• `convert <amount> <from> <to>` - Convert cryptocurrency (e.g., convert 1 btc eth)\n"
                "• `history <crypto> [days]` - Get historical data (e.g., history bitcoin 30)\n"
                "• `info <crypto>` - Get cryptocurrency information\n"
                "• `search <query>` - Search for cryptocurrencies\n"
                "• `help` - Show this help message\n\n"
                "**Examples:**\n"
                "• price bitcoin\n"
                "• market 20\n"
                "• trending\n"
                "• convert 1 btc eth\n"
                "• history ethereum 7\n"
                "• info cardano\n"
                "• search doge"
            )
            return chat

        last_message = chat.messages[-1]['content'].strip().lower()

        coingecko_component = chat.context.get('coingecko_component') if hasattr(chat, 'context') else None

        if not coingecko_component:
            chat.append_assistant("❌ Coingecko API component not available")
            return chat

        if last_message.startswith('price '):
            crypto_id = last_message.replace('price ', '').strip()
            context = {
                'crypto_id': crypto_id,
                'coingecko_component': coingecko_component
            }

            result = get_crypto_price_skill(context)
            data = result.value

            if data.get('success'):
                change_emoji = "📈" if data['change_24h'] >= 0 else "📉"
                response = [
                    f"💰 **{crypto_id.upper()} Price**",
                    f"**Price:** ${data['price']:,.2f} USD",
                    f"**24h Change:** {change_emoji} {data['change_24h']:+.2f}%",
                    f"**Market Cap:** ${data['market_cap']:,.0f}",
                    f"**24h Volume:** ${data['volume_24h']:,.0f}",
                    f"**Last Updated:** {datetime.fromtimestamp(data['last_updated']).strftime('%Y-%m-%d %H:%M:%S')}"
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
                'vs_currency': 'usd',
                'limit': limit,
                'coingecko_component': coingecko_component
            }

            result = get_crypto_market_data_skill(context)
            data = result.value

            if data.get('success'):
                cryptos = data['cryptocurrencies']

                response = [
                    f"📈 **Top {len(cryptos)} Cryptocurrencies**",
                    f"*Sorted by market cap*",
                    ""
                ]

                for i, crypto in enumerate(cryptos[:5], 1):
                    change_emoji = "📈" if crypto['price_change_percentage_24h'] >= 0 else "📉"
                    response.extend([
                        f"**#{i} {crypto['name']} ({crypto['symbol']})**",
                        f"• Price: ${crypto['current_price']:,.2f}",
                        f"• 24h Change: {change_emoji} {crypto['price_change_percentage_24h']:+.2f}%",
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
                'coingecko_component': coingecko_component
            }

            result = get_trending_cryptos_skill(context)
            data = result.value

            if data.get('success'):
                trending = data['trending_cryptos']

                response = [
                    f"🔥 **Trending Cryptocurrencies**",
                    f"*Currently trending in the crypto community*",
                    ""
                ]

                for i, crypto in enumerate(trending[:5], 1):
                    response.extend([
                        f"**#{i} {crypto['name']} ({crypto['symbol']})**",
                        f"• Rank: #{crypto['market_cap_rank'] if crypto['market_cap_rank'] > 0 else 'N/A'}",
                        f"• Trending Score: {crypto['score']:.2f}",
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
                    from_currency = parts[1].lower()
                    to_currency = parts[2].lower()

                    context = {
                        'amount': amount,
                        'from_currency': from_currency,
                        'to_currency': to_currency,
                        'coingecko_component': coingecko_component
                    }

                    result = convert_currency_skill(context)
                    data = result.value

                    if data.get('success'):
                        conversion = data['conversion']
                        response = [
                            f"🔄 **Cryptocurrency Conversion**",
                            f"**{amount:,.6f} {from_currency.upper()} = {conversion['converted_amount']:.6f} {to_currency.upper()}**",
                            f"**Exchange Rate:** 1 {from_currency.upper()} = {conversion['rate']:.6f} {to_currency.upper()}",
                            f"*Rate updated: {conversion['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}*"
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
                crypto_id = parts[0]
                days = int(parts[1]) if len(parts) > 1 else 7

                if days > 365:
                    chat.append_assistant("❌ Maximum history period is 365 days")
                    return chat

                context = {
                    'crypto_id': crypto_id,
                    'days': days,
                    'coingecko_component': coingecko_component
                }

                result = get_historical_data_skill(context)
                data = result.value

                if data.get('success'):
                    change_emoji = "📈" if data['change_percentage'] >= 0 else "📉"
                    response = [
                        f"📊 **{crypto_id.upper()} - {days} Day History**",
                        f"**Current Price:** ${data['current_price']:,.2f}",
                        f"**Period Change:** {change_emoji} {data['change_percentage']:+.2f}%",
                        f"**High:** ${data['max_price']:,.2f}",
                        f"**Low:** ${data['min_price']:,.2f}",
                        f"**Average:** ${data['avg_price']:,.2f}",
                        f"**Data Points:** {data['total_data_points']}",
                        ""
                    ]

                    if data.get('sample_data'):
                        response.append("**Recent Prices:**")
                        for sample in data['sample_data'][-3:]:
                            date = datetime.fromisoformat(sample['timestamp']).strftime('%m/%d %H:%M')
                            response.append(f"• {date}: ${sample['price']:,.2f}")

                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"❌ Failed to get history: {data.get('error', 'Unknown error')}")
            else:
                chat.append_assistant("❌ Invalid format. Usage: history <crypto> [days]")

        elif last_message.startswith('info '):
            crypto_id = last_message.replace('info ', '').strip()
            context = {
                'crypto_id': crypto_id,
                'coingecko_component': coingecko_component
            }

            result = get_currency_info_skill(context)
            data = result.value

            if data.get('success'):
                info = data['info']

                response = [
                    f"📋 **{crypto_id.upper()} Information**",
                    f"**Name:** {info['name']} ({info['symbol']})",
                    f"**Rank:** #{info['market_cap_rank']}",
                    ""
                ]

                if info['description']:
                    desc = info['description'][:200] + "..." if len(info['description']) > 200 else info['description']
                    response.append(f"**Description:** {desc}")
                    response.append("")

                response.extend([
                    f"**Price:** ${info['current_price']:,.2f}",
                    f"**Market Cap:** ${info['market_cap']:,.0f}",
                    f"**24h Volume:** ${info['total_volume']:,.0f}",
                    ""
                ])

                if info['circulating_supply']:
                    response.append(f"**Circulating Supply:** {info['circulating_supply']:,.0f}")

                if info['total_supply']:
                    response.append(f"**Total Supply:** {info['total_supply']:,.0f}")

                if info['max_supply']:
                    response.append(f"**Max Supply:** {info['max_supply']:,.0f}")

                response.append("")
                response.append(f"**ATH:** ${info['ath']:,.2f}")
                response.append(f"**ATL:** ${info['atl']:,.2f}")

                if info['homepage']:
                    response.append(f"**Website:** {info['homepage']}")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get info: {data.get('error', 'Unknown error')}")

        elif last_message.startswith('search '):
            query = last_message.replace('search ', '').strip()

            if len(query) < 2:
                chat.append_assistant("❌ Search query too short. Minimum 2 characters")
                return chat

            try:
                all_cryptos = coingecko_component.get_supported_cryptocurrencies()
                if not all_cryptos:
                    chat.append_assistant("❌ Failed to get cryptocurrency list")
                    return chat

                search_results = []
                for crypto in all_cryptos:
                    if query.lower() in crypto.get('id', '').lower() or query.lower() in crypto.get('name', '').lower() or query.lower() in crypto.get('symbol', '').lower():
                        search_results.append(crypto)

                if search_results:
                    response = [
                        f"🔍 **Search Results for '{query}'**",
                        f"Found: {len(search_results)} cryptocurrencies",
                        ""
                    ]

                    for i, result in enumerate(search_results[:5], 1):
                        response.extend([
                            f"**#{i} {result.get('name', 'Unknown')} ({result.get('symbol', '').upper()})**",
                            f"• ID: {result.get('id', 'N/A')}",
                            ""
                        ])

                    response.append("💡 Use `price <id>` to get current price")
                    response.append("💡 Use `info <id>` to get detailed information")
                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"🔍 No cryptocurrencies found for '{query}'")
            except Exception as e:
                print(f"❌ Search error: {e}")
                chat.append_assistant(f"❌ Search failed: {str(e)}")

        elif last_message == 'help':
            chat.append_assistant(
                "💰 **Coingecko - Cryptocurrency Monitor**\n\n"
                "**Available Commands:**\n"
                "• `price <crypto>` - Get cryptocurrency price\n"
                "• `market [limit]` - Get top cryptocurrencies\n"
                "• `trending` - Get trending cryptocurrencies\n"
                "• `convert <amount> <from> <to>` - Convert cryptocurrency\n"
                "• `history <crypto> [days]` - Get historical data\n"
                "• `info <crypto>` - Get cryptocurrency information\n"
                "• `search <query>` - Search for cryptocurrencies\n"
                "• `help` - Show this help message\n\n"
                "**Examples:**\n"
                "• price bitcoin\n"
                "• market 20\n"
                "• trending\n"
                "• convert 1 btc eth\n"
                "• history ethereum 7\n"
                "• info cardano\n"
                "• search doge"
            )

        else:
            chat.append_assistant(
                "🤔 I didn't understand that command.\n\n"
                "**Available commands:**\n"
                "• `price <crypto>` - Get cryptocurrency price\n"
                "• `market [limit]` - Get market data\n"
                "• `trending` - Get trending cryptos\n"
                "• `convert <amount> <from> <to>` - Convert cryptocurrency\n"
                "• `history <crypto> [days]` - Get historical data\n"
                "• `info <crypto>` - Get cryptocurrency info\n"
                "• `search <query>` - Search cryptos\n"
                "• `help` - Show help\n\n"
                "Type `help` for more information."
            )

    except Exception as e:
        print(f"❌ Error in coingecko_chat_skill: {e}")
        import traceback
        traceback.print_exc()
        chat.append_assistant("❌ An error occurred while processing your request")

    return chat
