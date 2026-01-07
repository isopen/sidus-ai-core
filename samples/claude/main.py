import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.claude import create_claude_agent

def main():
    agent = create_claude_agent(
        os.environ.get('ANTHROPIC_API_KEY')
    )

    result = agent.create_message(
        prompt="Hello Claude, say hi back!",
        model="claude-sonnet-4-5",
        max_tokens=50
    )

    if result.get('success'):
        print(f"✅ Claude Response Successful")

        content = result.get('content', [])
        if content:
            text = content[0].get('text', '')
            print(f"\n   Claude says:\n")
            lines = text.split('\n')
            for line in lines:
                if line.strip():
                    print(f"   {line}")

        usage = result.get('usage', {})
        print(f"\n   Model: {result.get('model')}")
        print(f"   Input tokens: {usage.get('input_tokens', 0)}")
        print(f"   Output tokens: {usage.get('output_tokens', 0)}")
        print(f"   Stop reason: {result.get('stop_reason')}")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()
