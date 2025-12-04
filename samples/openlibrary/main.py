import sys
import time
import os

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))

try:
    import sidusai as sai
    from sidusai.plugins.openlibrary import create_openlibrary_agent
    from sidusai.core.plugin import ChatAgentValue
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please set SIDUS_AI_CORE_PATH environment variable")
    sys.exit(1)

def print_help():
    print("\nCOMMANDS:")
    print("-" * 40)
    print("Search:")
    print("  search books <query>      - Search books")
    print("  search authors <name>     - Search authors")
    print("  subject <topic>           - Books by subject")
    print("")
    print("Information:")
    print("  book <key/isbn>           - Book details")
    print("  author <key/name>         - Author details")
    print("  work <key>                - Work details")
    print("  editions <work_key>       - Work editions")
    print("")
    print("Utility:")
    print("  help                      - Show this help")
    print("  examples                  - Show examples")
    print("  exit                      - Exit program")
    print("-" * 40)

def print_examples():
    print("\nEXAMPLES:")
    print("-" * 40)
    print("Search:")
    print("  • search books harry potter")
    print("  • search authors stephen king")
    print("  • subject science fiction")
    print("")
    print("Get Details:")
    print("  • book 9780545010221          (by ISBN)")
    print("  • book OL7353617M             (by OLID)")
    print("  • author J.K. Rowling         (by name)")
    print("  • author OL23919A             (by key)")
    print("  • work OL82563W               (work details)")
    print("  • editions OL82563W           (work editions)")
    print("-" * 40)

def main():
    if not os.environ.get('SIDUS_AI_CORE_PATH'):
        print("❌ Error: SIDUS_AI_CORE_PATH environment variable not set")
        print("Please set it to the path of Sidus AI core library")
        print("Example: export SIDUS_AI_CORE_PATH=/path/to/sidus-ai-core")
        return

    try:
        print("\nCreating OpenLibrary agent...")
        agent = create_openlibrary_agent(rate_limit_delay=0.2)
        print("✅ Agent created successfully")

        print("Testing API connection...")
        if agent.openlibrary_client.test_connection():
            print("✅ Connected to OpenLibrary API")
        else:
            print("⚠️  API connection issues - some features may not work")

    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        import traceback
        traceback.print_exc()
        return

    print_help()

    while True:
        try:
            user_input = input("\n💬 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye! Happy reading!")
                break

            elif user_input.lower() == 'help':
                print_help()
                continue

            elif user_input.lower() == 'examples':
                print_examples()
                continue

            print("🤖 Processing...", end='', flush=True)
            start_time = time.time()

            try:
                response = agent.chat(user_input)
                response_time = time.time() - start_time

                print("\r" + " " * 30 + "\r", end='')

                print(f"\n📚 Assistant ({response_time:.1f}s):")
                print("-" * 50)
                print(response)
                print("-" * 50)

            except Exception as e:
                print(f"\r❌ Error in agent.chat(): {e}")
                continue

        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
            print("👋 Goodbye!")
            break

        except EOFError:
            print("\n\n👋 Goodbye!")
            break

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
