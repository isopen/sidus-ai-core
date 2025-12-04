from sidusai.core.plugin import AgentValue
from typing import Dict, Any
from datetime import datetime

class EthereumDataValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class EthereumWalletValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class EthereumTokenValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

def get_eth_price_skill(context: Dict[str, Any]) -> EthereumDataValue:
    print("🔧 Starting get_eth_price_skill...")

    try:
        etherscan_component = context.get('etherscan_component')
        if not etherscan_component:
            result = {"error": "Etherscan component not available"}
            return EthereumDataValue(result)

        print("💰 Getting ETH price")

        price_data = etherscan_component.get_eth_price()

        if not price_data:
            result = {"error": "Failed to get ETH price"}
            return EthereumDataValue(result)

        result = {
            "success": True,
            "price_data": price_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ ETH price: ${price_data.get('ethusd', 0):.2f}")
        return EthereumDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_eth_price_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get ETH price: {str(e)}"}
        return EthereumDataValue(result)

def get_wallet_balance_skill(context: Dict[str, Any]) -> EthereumWalletValue:
    print("🔧 Starting get_wallet_balance_skill...")

    wallet_address = context.get('wallet_address')

    if not wallet_address:
        result = {"error": "No wallet address provided"}
        return EthereumWalletValue(result)

    try:
        etherscan_component = context.get('etherscan_component')
        if not etherscan_component:
            result = {"error": "Etherscan component not available"}
            return EthereumWalletValue(result)

        print(f"💰 Getting balance for wallet: {wallet_address[:10]}...")

        balance_data = etherscan_component.get_wallet_balance(wallet_address)

        if not balance_data:
            result = {"error": f"Failed to get balance for wallet {wallet_address}"}
            return EthereumWalletValue(result)

        result = {
            "success": True,
            "wallet_address": wallet_address,
            "data": balance_data,
            "timestamp": datetime.now().isoformat()
        }

        balance_eth = balance_data.get('balance_eth', 0)
        print(f"✅ Wallet balance: {balance_eth:.6f} ETH")
        return EthereumWalletValue(result)

    except Exception as e:
        print(f"❌ Error in get_wallet_balance_skill: {e}")
        result = {"error": f"Failed to get wallet balance: {str(e)}"}
        return EthereumWalletValue(result)

def get_wallet_transactions_skill(context: Dict[str, Any]) -> EthereumDataValue:
    print("🔧 Starting get_wallet_transactions_skill...")

    wallet_address = context.get('wallet_address')
    limit = context.get('limit', 10)

    if not wallet_address:
        result = {"error": "No wallet address provided"}
        return EthereumDataValue(result)

    try:
        etherscan_component = context.get('etherscan_component')
        if not etherscan_component:
            result = {"error": "Etherscan component not available"}
            return EthereumDataValue(result)

        print(f"💰 Getting transactions for wallet: {wallet_address[:10]}...")

        transactions = etherscan_component.get_wallet_transactions(wallet_address, limit)

        if not transactions:
            result = {"error": f"Failed to get transactions for wallet {wallet_address}"}
            return EthereumDataValue(result)

        formatted_transactions = []
        total_sent = 0
        total_received = 0

        for tx in transactions:
            wallet_addr = wallet_address.lower()
            from_addr = tx.from_address.lower() if tx.from_address else ''
            to_addr = tx.to_address.lower() if tx.to_address else ''

            is_sent = from_addr == wallet_addr
            is_received = to_addr == wallet_addr

            formatted_tx = {
                "hash": tx.hash[:10] + "..." if tx.hash and len(tx.hash) > 10 else tx.hash or "",
                "from": from_addr[:10] + "..." if from_addr and len(from_addr) > 10 else from_addr or "",
                "to": to_addr[:10] + "..." if to_addr and len(to_addr) > 10 else to_addr or "",
                "value": tx.value,
                "gas": tx.gas,
                "gas_price": tx.gas_price,
                "gas_cost": (tx.gas * tx.gas_price) / 1_000_000_000,
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "status": tx.status,
                "direction": "sent" if is_sent else "received" if is_received else "unknown"
            }

            formatted_transactions.append(formatted_tx)

            if is_sent:
                total_sent += tx.value
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
        return EthereumDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_wallet_transactions_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get wallet transactions: {str(e)}"}
        return EthereumDataValue(result)

def get_gas_price_skill(context: Dict[str, Any]) -> EthereumDataValue:
    print("🔧 Starting get_gas_price_skill...")

    try:
        etherscan_component = context.get('etherscan_component')
        if not etherscan_component:
            result = {"error": "Etherscan component not available"}
            return EthereumDataValue(result)

        print("⛽ Getting Ethereum gas prices")

        gas_data = etherscan_component.get_gas_price()

        if not gas_data:
            result = {"error": "Failed to get gas prices"}
            return EthereumDataValue(result)

        result = {
            "success": True,
            "gas_data": gas_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Gas prices retrieved")
        return EthereumDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_gas_price_skill: {e}")
        result = {"error": f"Failed to get gas prices: {str(e)}"}
        return EthereumDataValue(result)
