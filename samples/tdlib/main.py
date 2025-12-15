import os
import sys
import time
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.tdlib import TDLibAiAgent
from ctypes.util import find_library

def main():
    print("TDLib Assistent")
    print("="*60)

    API_ID = os.environ.get('TDLIB_API_ID') #94575
    API_HASH = os.environ.get('TDLIB_API_HASH') #"a3406de8d171bb422bb6ddf3bbd800e2"
    TDLIB_PATH = os.environ.get('TDLIB_PATH') #find_library("tdjson")

    print(f"Using API ID: {API_ID}")

    try:
        agent = TDLibAiAgent(
            api_id=API_ID,
            api_hash=API_HASH,
            system_prompt="Assistant",
            database_directory="./tdlib",
            tdlib_directory=TDLIB_PATH
        )

        print(f"\n✓ Agent created")
        print(f"Client ID: {agent.tdlib_manager.client_id}")

        def auth_handler(client_id: int, auth_type: str):
            print(f"\n[Authentication required] Type: {auth_type}")

            if auth_type == 'phone':
                phone = input("Please enter your phone number (international format): ")
                if phone:
                    agent.send({
                        "@type": "setAuthenticationPhoneNumber",
                        "phone_number": phone
                    })

            elif auth_type == 'code':
                code = input("Please enter the authentication code you received: ")
                if code:
                    agent.send({
                        "@type": "checkAuthenticationCode",
                        "code": code
                    })

            elif auth_type == 'password':
                password = input("Please enter your password: ")
                if password:
                    agent.send({
                        "@type": "checkAuthenticationPassword",
                        "password": password
                    })

        agent.on_auth_required = auth_handler

        print("\n" + "="*60)
        print("Agent is running. Waiting for TDLib response...")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")

        try:
            counter = 0
            while True:
                agent._tdlib_polling_loop()

                counter += 1
                if counter % 100 == 0:
                    print(f"[{counter}] Running...")

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\nStopping agent...")

        finally:
            agent.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
