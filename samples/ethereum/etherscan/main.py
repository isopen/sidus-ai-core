import sys
import time
import os
from datetime import datetime

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
from sidusai.plugins.ethereum.etherscan import EtherscanPlugin

def agent_creation():
    try:
        print("🤖 Creating Sidus AI agent...")
        agent = sai.Agent()
        print("✅ Sidus AI agent created")

        print("🔧 Creating Etherscan plugin...")
        api_key = os.environ.get('ETHERSCAN_API_KEY', '')
        plugin = EtherscanPlugin(api_key = api_key)
        print("✅ Etherscan plugin created")

        print("🔧 Applying Etherscan plugin to agent...")
        plugin.apply_plugin(agent)
        print("✅ Etherscan plugin applied")

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

        if hasattr(plugin, 'etherscan_client'):
            print("🔗 Testing Etherscan API connection...")
            if plugin.etherscan_client.test_connection():
                print("✅ Etherscan API connection successful")
            else:
                print("⚠️ Etherscan API connection issues")
                print("ℹ️ Make sure you have a valid API key from https://etherscan.io/apis")

        while True:
            try:
                print("\n" + "-"*50)
                print("Commands:")
                print("1. price            - Get ETH price")
                print("2. balance <addr>   - Get wallet balance")
                print("3. transactions <addr> - Get wallet transactions")
                print("4. gas              - Get current gas prices")
                print("5. exit             - Exit")
                print("-"*50)

                choice = input("\n🔧 Enter command number (1-5): ").strip()

                if choice == '1':
                    print(f"\n💰 Getting ETH price...")
                    result = plugin.etherscan_client.get_eth_price()

                    if result:
                        ethusd = result.get('ethusd', 0)
                        ethbtc = result.get('ethbtc', 0)

                        print(f"ETH Price:")
                        print(f"ETH/USD: ${ethusd:.2f}")
                        print(f"ETH/BTC: {ethbtc:.6f}")
                        print(f"Timestamp: {result.get('timestamp', '')}")
                    else:
                        print(f"❌ Failed to get ETH price")

                elif choice == '2':
                    wallet_address = input("Enter wallet address (0x...): ").strip()

                    if wallet_address:
                        print(f"\n💰 Getting balance for wallet...")
                        result = plugin.etherscan_client.get_wallet_balance(wallet_address)

                        if result:
                            balance_eth = result.get('balance_eth', 0)
                            balance_usd = result.get('balance_usd', 0)

                            print(f"Wallet: {wallet_address}")
                            print(f"Balance: {balance_eth:.6f} ETH")
                            print(f"Value: ${balance_usd:.2f} USD")
                        else:
                            print(f"❌ Failed to get wallet balance")
                    else:
                        print("❌ Please enter wallet address")

                elif choice == '3':
                    wallet_address = input("Enter wallet address (0x...): ").strip()
                    limit_input = input("Limit (default 10): ").strip()
                    limit = int(limit_input) if limit_input.isdigit() else 10

                    if wallet_address:
                        print(f"\n📊 Getting transactions for wallet...")
                        result = plugin.etherscan_client.get_wallet_transactions(wallet_address, limit)

                        if result:
                            print(f"Found {len(result)} transactions:")

                            for i, tx in enumerate(result[:limit], 1):
                                print(f"\n#{i}")
                                print(f"From: {tx.from_address}")
                                print(f"To: {tx.to_address}")
                                print(f"Amount: {tx.value:.6f} ETH")
                                print(f"Gas Price: {tx.gas_price:.2f} Gwei")
                                print(f"Gas Used: {tx.gas:,}")

                                gas_cost_eth = (tx.gas * tx.gas_price) / 1_000_000_000
                                print(f"Gas Cost: {gas_cost_eth:.6f} ETH")

                                if tx.timestamp:
                                    if isinstance(tx.timestamp, datetime):
                                        print(f"Time: {tx.timestamp.strftime('%Y-%m-%d %H:%M')}")
                                    else:
                                        try:
                                            dt = datetime.fromtimestamp(tx.timestamp)
                                            print(f"Time: {dt.strftime('%Y-%m-%d %H:%M')}")
                                        except:
                                            print(f"Time: {tx.timestamp}")

                                if tx.status:
                                    status = "Success" if tx.status == '1' else "Failed"
                                    print(f"Status: {status}")

                            if len(result) > limit:
                                print(f"\n... and {len(result) - limit} more transactions")
                        else:
                            print(f"❌ Failed to get transactions or no transactions found")
                    else:
                        print("❌ Please enter wallet address")

                elif choice == '4':
                    print(f"\n⛽ Getting gas prices...")
                    result = plugin.etherscan_client.get_gas_price()

                    if result:
                        safe = result.get('safe_gas_price', 0)
                        propose = result.get('propose_gas_price', 0)
                        fast = result.get('fast_gas_price', 0)
                        base_fee = result.get('suggest_base_fee', 0)

                        print(f"Gas Prices (Gwei):")
                        print(f"Slow: {safe} Gwei")
                        print(f"Average: {propose} Gwei")
                        print(f"Fast: {fast} Gwei")
                        print(f"Base Fee: {base_fee} Gwei")
                        print(f"Gas Used Ratio: {result.get('gas_used_ratio', '0')}")
                    else:
                        print(f"❌ Failed to get gas prices")

                elif choice == '5':
                    print("\n👋 Goodbye!")
                    break

                else:
                    print("❌ Invalid choice. Please enter 1-5.")

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
