import sys
import time
import os

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
from sidusai.plugins.coinmarketcap import CoinMarketCapPlugin
from sidusai.plugins.coinmarketcap.skills import coinmarketcap_chat_skill
from sidusai.core.plugin import ChatAgentValue

def agent_creation():
    try:
        print("🤖 Creating crypto assistent...")
        agent = sai.Agent()
        print("✅ Crypto assistent created")

        print("🔧 Creating CoinMarketCap plugin...")
        api_key = os.environ.get('COINMARKETCAP_API_KEY')
        plugin = CoinMarketCapPlugin(api_key=api_key)
        print("✅ CoinMarketCap plugin created")

        print("🔧 Applying CoinMarketCap plugin to agent...")
        plugin.apply_plugin(agent)
        print("✅ CoinMarketCap plugin applied")

        if hasattr(agent, 'register_skill'):
            print("🛠️ Registering coinmarketcap_chat_skill...")
            agent.register_skill(
                name="coinmarketcap_chat",
                description="Chat interface for cryptocurrency queries",
                func=coinmarketcap_chat_skill
            )
            print("✅ Skill registered")

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

        print("\n🤖 Crypto assistant:")
        print("• price <symbol>       - Get cryptocurrency price")
        print("• market [limit]       - Get top cryptocurrencies")
        print("• trending             - Get trending cryptocurrencies")
        print("• convert <amount> <from> <to> - Convert cryptocurrency")
        print("• history <symbol> [period] - Get historical data")
        print("• info <symbol>        - Get cryptocurrency information")
        print("• global               - Get global market metrics")
        print("• search <query>       - Search cryptocurrencies")
        print("• help                 - Show help")
        print("• exit                 - Exit")
        print("\nType commands directly or ask natural language questions")
        print("-"*60)

        chat_history = ChatAgentValue(messages=[])

        while True:
            try:
                user_input = input("💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Goodbye!")
                    break

                chat_history.append_user(user_input)

                print("🤖 Processing...")
                start_time = time.time()

                context = {'coinmarketcap_component': agent.coinmarketcap_client}
                
                if hasattr(chat_history, 'context'):
                    chat_history.context = context
                elif hasattr(chat_history, 'add_context'):
                    chat_history.add_context(context)
                else:
                    setattr(chat_history, 'context', context)

                result = coinmarketcap_chat_skill(chat_history)
                response_time = time.time() - start_time

                if result and hasattr(result, 'messages'):
                    last_assistant_msg = None
                    for msg in reversed(result.messages):
                        if msg['role'] == 'assistant':
                            last_assistant_msg = msg['content']
                            break

                    if last_assistant_msg:
                        print(f"\n🤖 Crypto Assistant ({response_time:.2f}s):")
                        print("-" * 50)
                        print(last_assistant_msg)
                        print("-" * 50)
                        chat_history = result
                    else:
                        print("\n🤖 Crypto Assistant: No response received")
                        if hasattr(chat_history, 'append_assistant'):
                            chat_history.append_assistant("No response received")
                else:
                    print("\n🤖 Crypto Assistant: Failed to process request")

                time.sleep(0.5)

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
    if not os.environ.get('SIDUS_AI_CORE_PATH'):
        print("⚠️ SIDUS_AI_CORE_PATH environment variable not set")
        print("Please set it to the path of Sidus AI core library")
        return
        
    if not os.environ.get('COINMARKETCAP_API_KEY'):
        print("⚠️ COINMARKETCAP_API_KEY environment variable not set")
        print("Get a free API key from: https://coinmarketcap.com/api/")
        print("Then set it with: export COINMARKETCAP_API_KEY='your-api-key'")
        return

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