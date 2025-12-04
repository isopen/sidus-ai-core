from sidusai.core.plugin import ChatAgentValue, AgentValue
from typing import Dict, Any, List
from datetime import datetime

class TONDataValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class TONWalletValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class TONTokenValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

def get_ton_price_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_ton_price_skill...")

    currencies = context.get('currencies', ["USD", "EUR", "RUB"])

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting TON price in {currencies}")

        price_data = tonapi_component.get_ton_price(currencies)

        if not price_data:
            result = {"error": "Failed to get TON price"}
            return TONDataValue(result)

        result = {
            "success": True,
            "currencies": currencies,
            "prices": price_data.get('prices', {}),
            "timestamp": price_data.get('timestamp', datetime.now().isoformat()),
            "source": "TON API"
        }

        print(f"✅ TON price retrieved")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_ton_price_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get TON price: {str(e)}"}
        return TONDataValue(result)

def get_wallet_balance_skill(context: Dict[str, Any]) -> TONWalletValue:
    print("🔧 Starting get_wallet_balance_skill...")

    wallet_address = context.get('wallet_address')

    if not wallet_address:
        result = {"error": "No wallet address provided"}
        return TONWalletValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONWalletValue(result)

        print(f"💰 Getting balance for wallet: {wallet_address[:10]}...")

        balance_data = tonapi_component.get_wallet_balance(wallet_address)

        if not balance_data:
            result = {"error": f"Failed to get balance for wallet {wallet_address}"}
            return TONWalletValue(result)

        result = {
            "success": True,
            "wallet_address": wallet_address,
            "data": balance_data,
            "timestamp": datetime.now().isoformat()
        }

        balance_ton = balance_data.get('balance_ton', 0)
        print(f"✅ Wallet balance: {balance_ton:.2f} TON")
        return TONWalletValue(result)

    except Exception as e:
        print(f"❌ Error in get_wallet_balance_skill: {e}")
        result = {"error": f"Failed to get wallet balance: {str(e)}"}
        return TONWalletValue(result)

def get_wallet_transactions_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_wallet_transactions_skill...")

    wallet_address = context.get('wallet_address')
    limit = context.get('limit', 10)

    if not wallet_address:
        result = {"error": "No wallet address provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting transactions for wallet: {wallet_address[:10]}...")

        transactions = tonapi_component.get_wallet_transactions(wallet_address, limit)

        if not transactions:
            result = {"error": f"Failed to get transactions for wallet {wallet_address}"}
            return TONDataValue(result)

        formatted_transactions = []
        total_sent = 0
        total_received = 0

        for tx in transactions:
            from_addr = tx.from_address.lower() if tx.from_address else ''
            to_addr = tx.to_address.lower() if tx.to_address else ''
            wallet_addr = wallet_address.lower()

            is_sent = from_addr == wallet_addr
            is_received = to_addr == wallet_addr

            formatted_tx = {
                "hash": tx.hash[:10] + "..." if tx.hash and len(tx.hash) > 10 else tx.hash or "",
                "from": from_addr[:10] + "..." if from_addr and len(from_addr) > 10 else from_addr or "",
                "to": to_addr[:10] + "..." if to_addr and len(to_addr) > 10 else to_addr or "",
                "value": tx.value,
                "fee": tx.fee,
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "message": tx.message[:50] + "..." if tx.message and len(tx.message) > 50 else tx.message,
                "operation": tx.operation,
                "direction": "sent" if is_sent else "received" if is_received else "unknown"
            }

            formatted_transactions.append(formatted_tx)

            if is_sent:
                total_sent += tx.value + tx.fee
            elif is_received:
                total_received += tx.value

        result = {
            "success": True,
            "wallet_address": wallet_address,
            "transactions": formatted_transactions,
            "total_sent": total_sent,
            "total_received": total_received,
            "net_flow": total_received - total_sent,
            "count": len(formatted_transactions),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(formatted_transactions)} transactions")
        print(f"   Sent: {total_sent:.6f} TON, Received: {total_received:.6f} TON")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_wallet_transactions_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get wallet transactions: {str(e)}"}
        return TONDataValue(result)

def get_token_info_skill(context: Dict[str, Any]) -> TONTokenValue:
    print("🔧 Starting get_token_info_skill...")

    token_address = context.get('token_address')

    if not token_address:
        result = {"error": "No token address provided"}
        return TONTokenValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONTokenValue(result)

        print(f"💰 Getting info for token: {token_address[:10]}...")

        token_info = tonapi_component.get_token_info(token_address)

        if not token_info:
            result = {"error": f"Failed to get info for token {token_address}"}
            return TONTokenValue(result)

        result = {
            "success": True,
            "token_address": token_address,
            "info": token_info,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Token info retrieved for {token_info.get('name', 'Unknown')}")
        return TONTokenValue(result)

    except Exception as e:
        print(f"❌ Error in get_token_info_skill: {e}")
        result = {"error": f"Failed to get token info: {str(e)}"}
        return TONTokenValue(result)

def get_jetton_holders_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_jetton_holders_skill...")

    jetton_address = context.get('jetton_address')
    limit = context.get('limit', 10)

    if not jetton_address:
        result = {"error": "No jetton address provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting holders for jetton: {jetton_address[:10]}...")

        holders = tonapi_component.get_jetton_holders(jetton_address, limit)

        if not holders:
            result = {"error": f"Failed to get holders for jetton {jetton_address}"}
            return TONDataValue(result)

        formatted_holders = []
        total_percentage = 0

        for holder in holders:
            formatted_holders.append({
                "address": holder.get('address', ''),
                "balance": holder.get('balance', 0),
                "percentage": holder.get('percentage', 0),
                "is_scam": holder.get('is_scam', False),
                "is_wallet": holder.get('is_wallet', False)
            })
            total_percentage += holder.get('percentage', 0)

        result = {
            "success": True,
            "jetton_address": jetton_address,
            "holders": formatted_holders,
            "total_holders": len(formatted_holders),
            "top_holders_percentage": total_percentage,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(formatted_holders)} holders")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_jetton_holders_skill: {e}")
        result = {"error": f"Failed to get jetton holders: {str(e)}"}
        return TONDataValue(result)

def get_nft_collection_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_nft_collection_skill...")

    collection_address = context.get('collection_address')

    if not collection_address:
        result = {"error": "No NFT collection address provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting NFT collection: {collection_address[:10]}...")

        collection_info = tonapi_component.get_nft_collection(collection_address)

        if not collection_info:
            result = {"error": f"Failed to get NFT collection {collection_address}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "collection_address": collection_address,
            "info": collection_info,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ NFT collection info retrieved for {collection_info.get('name', 'Unknown')}")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_nft_collection_skill: {e}")
        result = {"error": f"Failed to get NFT collection: {str(e)}"}
        return TONDataValue(result)

def get_nft_item_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_nft_item_skill...")

    nft_address = context.get('nft_address')

    if not nft_address:
        result = {"error": "No NFT address provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting NFT item: {nft_address[:10]}...")

        nft_info = tonapi_component.get_nft_item(nft_address)

        if not nft_info:
            result = {"error": f"Failed to get NFT item {nft_address}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "nft_address": nft_address,
            "info": nft_info,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ NFT item info retrieved for {nft_info.get('name', 'Unknown')}")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_nft_item_skill: {e}")
        result = {"error": f"Failed to get NFT item: {str(e)}"}
        return TONDataValue(result)

def tonapi_chat_skill(chat: ChatAgentValue) -> ChatAgentValue:
    print("🔧 Starting tonapi_chat_skill...")

    try:
        if not chat.messages:
            chat.append_assistant(
                "⚡ **TON API - The Open Network**\n\n"
                "I provide data and analytics for The Open Network (TON) blockchain.\n\n"
                "**Available Commands:**\n"
                "• `price [currencies]` - Get TON price (e.g., price USD,EUR,RUB)\n"
                "• `balance <address>` - Get wallet balance\n"
                "• `transactions <address> [limit]` - Get wallet transactions\n"
                "• `token <address>` - Get token information\n"
                "• `holders <address> [limit]` - Get jetton holders\n"
                "• `nftcollection <address>` - Get NFT collection info\n"
                "• `nftitem <address>` - Get NFT item info\n"
                "• `marketplace [name]` - Get marketplace stats\n"
                "• `help` - Show this help message\n\n"
                "**Examples:**\n"
                "• price USD,EUR,RUB\n"
                "• balance EQDR4ne9zGk9dM...\n"
                "• transactions EQDR4ne9zGk9dM... 20\n"
                "• token EQB-MPw...\n"
                "• holders EQB-MPw... 15\n"
                "• nftcollection EQB-MPw...\n"
                "• nftitem EQB-MPw...\n"
                "• marketplace getgems\n"
                "• help"
            )
            return chat

        last_message = chat.messages[-1]['content'].strip().lower()

        tonapi_component = chat.context.get('tonapi_component') if hasattr(chat, 'context') else None

        if not tonapi_component:
            chat.append_assistant("❌ TON API component not available")
            return chat

        if last_message.startswith('price'):
            parts = last_message.replace('price', '').strip()
            currencies = ["USD", "EUR", "RUB"]
            if parts:
                currencies = [c.strip().upper() for c in parts.split(',') if c.strip()]

            context = {
                'currencies': currencies,
                'tonapi_component': tonapi_component
            }

            result = get_ton_price_skill(context)
            data = result.value

            if data.get('success'):
                prices = data.get('prices', {})
                response = [
                    f"💰 **TON Price**",
                    f"*Current exchange rates*",
                    ""
                ]

                for currency, price in prices.items():
                    response.append(f"**1 TON = {price:.2f} {currency}**")

                response.append(f"\n*Source: {data.get('source', 'TON API')}*")
                response.append(f"*Updated: {data.get('timestamp', '')}*")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get TON price: {data.get('error', 'Unknown error')}")

        elif last_message.startswith('balance '):
            wallet_address = last_message.replace('balance ', '').strip()
            context = {
                'wallet_address': wallet_address,
                'tonapi_component': tonapi_component
            }

            result = get_wallet_balance_skill(context)
            data = result.value

            if data.get('success'):
                wallet_data = data['data']
                balance_ton = wallet_data.get('balance_ton', 0)
                is_scam = wallet_data.get('is_scam', False)
                is_wallet = wallet_data.get('is_wallet', False)
                status = wallet_data.get('status', 'unknown')

                response = [
                    f"💰 **Wallet Balance**",
                    f"**Address:** `{wallet_address[:15]}...`",
                    f"**Balance:** {balance_ton:.2f} TON",
                    f"**Status:** {status.upper()}"
                ]

                if is_scam:
                    response.append("⚠️ **WARNING:** This address is marked as SCAM!")
                elif is_wallet:
                    response.append("✅ **Verified:** This is a wallet address")

                last_activity = wallet_data.get('last_activity', '')
                if last_activity:
                    response.append(f"**Last Activity:** {last_activity[:10]}")

                response.append(f"\n*Data provided by TON API*")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get wallet balance: {data.get('error', 'Unknown error')}")

        elif last_message.startswith('transactions '):
            parts = last_message.replace('transactions ', '').strip().split()
            if len(parts) >= 1:
                wallet_address = parts[0]
                limit = int(parts[1]) if len(parts) > 1 else 10

                context = {
                    'wallet_address': wallet_address,
                    'limit': limit,
                    'tonapi_component': tonapi_component
                }

                result = get_wallet_transactions_skill(context)
                data = result.value

                if data.get('success'):
                    transactions = data.get('transactions', [])
                    total_sent = data.get('total_sent', 0)
                    total_received = data.get('total_received', 0)

                    response = [
                        f"📊 **Wallet Transactions**",
                        f"**Address:** `{wallet_address[:15]}...`",
                        f"**Total Transactions:** {len(transactions)}",
                        f"**Total Sent:** {total_sent:.2f} TON",
                        f"**Total Received:** {total_received:.2f} TON",
                        f"**Net Flow:** {total_received - total_sent:.2f} TON",
                        ""
                    ]

                    if transactions:
                        response.append("**Recent Transactions:**")
                        for i, tx in enumerate(transactions[:5], 1):
                            direction = "⬆️ Sent" if tx['from'] == wallet_address[:10] + "..." else "⬇️ Received"
                            response.append(f"\n**#{i} {direction}**")
                            response.append(f"• Amount: {tx['value']:.2f} TON")
                            response.append(f"• Fee: {tx['fee']:.6f} TON")
                            if tx['message']:
                                response.append(f"• Message: {tx['message']}")
                            if tx['timestamp']:
                                response.append(f"• Time: {tx['timestamp'][:10]}")

                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"❌ Failed to get transactions: {data.get('error', 'Unknown error')}")
            else:
                chat.append_assistant("❌ Invalid format. Usage: transactions <address> [limit]")

        elif last_message.startswith('token '):
            token_address = last_message.replace('token ', '').strip()
            context = {
                'token_address': token_address,
                'tonapi_component': tonapi_component
            }

            result = get_token_info_skill(context)
            data = result.value

            if data.get('success'):
                token_info = data['info']
                name = token_info.get('name', 'Unknown')
                symbol = token_info.get('symbol', 'UNKNOWN')
                is_verified = token_info.get('is_verified', False)
                is_scam = token_info.get('is_scam', False)
                holders_count = token_info.get('holders_count', 0)
                total_supply = token_info.get('total_supply', 0)

                response = [
                    f"🎯 **Token Information**",
                    f"**Name:** {name}",
                    f"**Symbol:** {symbol}",
                    f"**Address:** `{token_address[:15]}...`"
                ]

                if is_verified:
                    response.append("✅ **Verified Token**")
                elif is_scam:
                    response.append("⚠️ **WARNING: Scam Token**")
                else:
                    response.append("⚠️ **Unverified Token**")

                response.append(f"**Total Supply:** {total_supply:,}")
                response.append(f"**Holders:** {holders_count:,}")
                response.append(f"**Decimals:** {token_info.get('decimals', 9)}")

                description = token_info.get('description', '')
                if description:
                    desc = description[:200] + "..." if len(description) > 200 else description
                    response.append(f"\n**Description:** {desc}")

                social_links = token_info.get('social_links', [])
                if social_links:
                    response.append(f"\n**Social Links:**")
                    for link in social_links[:3]:
                        response.append(f"• {link}")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get token info: {data.get('error', 'Unknown error')}")

        elif last_message.startswith('holders '):
            parts = last_message.replace('holders ', '').strip().split()
            if len(parts) >= 1:
                jetton_address = parts[0]
                limit = int(parts[1]) if len(parts) > 1 else 10

                context = {
                    'jetton_address': jetton_address,
                    'limit': limit,
                    'tonapi_component': tonapi_component
                }

                result = get_jetton_holders_skill(context)
                data = result.value

                if data.get('success'):
                    holders = data.get('holders', [])
                    top_percentage = data.get('top_holders_percentage', 0)

                    response = [
                        f"👥 **Jetton Holders**",
                        f"**Token Address:** `{jetton_address[:15]}...`",
                        f"**Total Holders:** {data.get('total_holders', 0)}",
                        f"**Top {len(holders)} Holders Control:** {top_percentage:.1f}%",
                        ""
                    ]

                    if holders:
                        response.append("**Top Holders:**")
                        for i, holder in enumerate(holders[:5], 1):
                            address = holder.get('address', '')
                            percentage = holder.get('percentage', 0)
                            is_scam = holder.get('is_scam', False)
                            status = "⚠️ SCAM" if is_scam else "✅ Valid"
                            response.append(f"\n**#{i} {status}**")
                            response.append(f"• Address: `{address[:15]}...`")
                            response.append(f"• Share: {percentage:.2f}%")

                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"❌ Failed to get holders: {data.get('error', 'Unknown error')}")
            else:
                chat.append_assistant("❌ Invalid format. Usage: holders <address> [limit]")

        elif last_message.startswith('nftcollection '):
            collection_address = last_message.replace('nftcollection ', '').strip()
            context = {
                'collection_address': collection_address,
                'tonapi_component': tonapi_component
            }

            result = get_nft_collection_skill(context)
            data = result.value

            if data.get('success'):
                collection_info = data['info']
                name = collection_info.get('name', 'Unknown')
                items_count = collection_info.get('items_count', 0)
                is_verified = collection_info.get('is_verified', False)
                is_scam = collection_info.get('is_scam', False)

                response = [
                    f"🖼️ **NFT Collection**",
                    f"**Name:** {name}",
                    f"**Address:** `{collection_address[:15]}...`",
                    f"**Items:** {items_count:,} NFTs"
                ]

                if is_verified:
                    response.append("✅ **Verified Collection**")
                elif is_scam:
                    response.append("⚠️ **WARNING: Scam Collection**")
                else:
                    response.append("⚠️ **Unverified Collection**")

                description = collection_info.get('description', '')
                if description:
                    desc = description[:200] + "..." if len(description) > 200 else description
                    response.append(f"\n**Description:** {desc}")

                marketplace = collection_info.get('marketplace', '')
                if marketplace:
                    response.append(f"**Marketplace:** {marketplace}")

                royalty = collection_info.get('royalty', 0)
                if royalty > 0:
                    response.append(f"**Royalty:** {royalty}%")

                owner = collection_info.get('owner_address', '')
                if owner:
                    response.append(f"**Owner:** `{owner[:15]}...`")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get NFT collection: {data.get('error', 'Unknown error')}")

        elif last_message.startswith('nftitem '):
            nft_address = last_message.replace('nftitem ', '').strip()
            context = {
                'nft_address': nft_address,
                'tonapi_component': tonapi_component
            }

            result = get_nft_item_skill(context)
            data = result.value

            if data.get('success'):
                nft_info = data['info']
                name = nft_info.get('name', 'Unknown')
                collection_name = nft_info.get('collection_name', '')
                is_for_sale = nft_info.get('is_for_sale', False)
                price = nft_info.get('price', 0)
                price_token = nft_info.get('price_token', 'TON')

                response = [
                    f"🖼️ **NFT Item**",
                    f"**Name:** {name}",
                    f"**Address:** `{nft_address[:15]}...`"
                ]

                if collection_name:
                    response.append(f"**Collection:** {collection_name}")

                if is_for_sale:
                    response.append(f"💰 **For Sale:** {price:.2f} {price_token}")
                else:
                    response.append("📭 **Not for Sale**")

                owner = nft_info.get('owner_address', '')
                if owner:
                    response.append(f"**Owner:** `{owner[:15]}...`")

                description = nft_info.get('description', '')
                if description:
                    desc = description[:200] + "..." if len(description) > 200 else description
                    response.append(f"\n**Description:** {desc}")

                attributes = nft_info.get('attributes', [])
                if attributes:
                    response.append(f"\n**Attributes:**")
                    for attr in attributes[:3]:
                        trait = attr.get('trait_type', '')
                        value = attr.get('value', '')
                        if trait and value:
                            response.append(f"• {trait}: {value}")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed to get NFT item: {data.get('error', 'Unknown error')}")

        elif last_message == 'help':
            chat.append_assistant(
                "⚡ **TON API - The Open Network**\n\n"
                "**Available Commands:**\n"
                "• `price [currencies]` - Get TON price\n"
                "• `balance <address>` - Get wallet balance\n"
                "• `transactions <address> [limit]` - Get wallet transactions\n"
                "• `token <address>` - Get token information\n"
                "• `holders <address> [limit]` - Get jetton holders\n"
                "• `nftcollection <address>` - Get NFT collection info\n"
                "• `nftitem <address>` - Get NFT item info\n"
                "• `marketplace [name]` - Get marketplace stats\n"
                "• `help` - Show this help message\n\n"
                "**Examples:**\n"
                "• price USD,EUR,RUB\n"
                "• balance EQDR4ne9zGk9dM...\n"
                "• transactions EQDR4ne9zGk9dM... 20\n"
                "• token EQB-MPw...\n"
                "• holders EQB-MPw... 15\n"
                "• nftcollection EQB-MPw...\n"
                "• nftitem EQB-MPw...\n"
                "• marketplace getgems\n"
                "• help"
            )

        else:
            chat.append_assistant(
                "🤔 I didn't understand that command.\n\n"
                "**Available commands:**\n"
                "• `price [currencies]` - Get TON price\n"
                "• `balance <address>` - Get wallet balance\n"
                "• `transactions <address> [limit]` - Get wallet transactions\n"
                "• `token <address>` - Get token information\n"
                "• `holders <address> [limit]` - Get jetton holders\n"
                "• `nftcollection <address>` - Get NFT collection info\n"
                "• `nftitem <address>` - Get NFT item info\n"
                "• `marketplace [name]` - Get marketplace stats\n"
                "• `help` - Show help\n\n"
                "Type `help` for more information."
            )

    except Exception as e:
        print(f"❌ Error in tonapi_chat_skill: {e}")
        import traceback
        traceback.print_exc()
        chat.append_assistant("❌ An error occurred while processing your request")

    return chat
