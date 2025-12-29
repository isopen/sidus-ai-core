import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.dyor import create_dyor_agent

def main():
    print("DEEP DRIVE")
    print("=" * 50)

    agent = create_dyor_agent()

    jettons_to_analyze = [
        ("STON", "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO"),
        ("NOT", "EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT"),
        ("USDT", "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"),
    ]

    print("\n1. Individual token analysis:")
    print("-" * 30)

    for token_name, token_address in jettons_to_analyze:        
        agent.analyze_jetton(token_address)

    print("\n2. Technical analysis:")
    print("-" * 30)

    agent.analyze_technical("EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT")

    print("\n3. Token comparison:")
    print("-" * 30)

    addresses = [addr for _, addr in jettons_to_analyze]

    agent.compare_jettons(addresses)

    print("\n4. Full token report:")
    print("-" * 30)

    agent.generate_report("EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs")

if __name__ == "__main__":
    main()