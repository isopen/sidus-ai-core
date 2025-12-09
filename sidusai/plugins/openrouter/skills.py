from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class OpenRouterDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

class OpenRouterModelValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def get_available_models_skill(context: Dict[str, Any]) -> OpenRouterDataValue:
    print("🔧 Starting get_available_models_skill...")

    free_only = context.get('free_only', True)

    try:
        openrouter_component = context.get('openrouter_component')
        if not openrouter_component:
            result = {"error": "OpenRouter component not available"}
            return OpenRouterDataValue(result)

        print(f"🤖 Getting available models (free_only: {free_only})")

        models = openrouter_component.get_available_models(free_only=free_only)

        if not models:
            result = {"error": "Failed to get available models"}
            return OpenRouterDataValue(result)

        result = {
            "success": True,
            "models": models,
            "total_models": len(models),
            "free_only": free_only,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(models)} models")
        return OpenRouterDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_available_models_skill: {e}")
        result = {"error": f"Failed to get available models: {str(e)}"}
        return OpenRouterDataValue(result)


def chat_completion_skill(context: Dict[str, Any]) -> OpenRouterDataValue:
    print("🔧 Starting chat_completion_skill...")

    messages = context.get('messages', [])
    model = context.get('model', 'amazon/nova-2-lite-v1:free')
    temperature = context.get('temperature', 0.7)
    max_tokens = context.get('max_tokens', 1000)

    if not messages:
        result = {"error": "No messages provided"}
        return OpenRouterDataValue(result)

    try:
        openrouter_component = context.get('openrouter_component')
        if not openrouter_component:
            result = {"error": "OpenRouter component not available"}
            return OpenRouterDataValue(result)

        print(f"💬 Sending chat completion request to {model}")

        response = openrouter_component.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        if response.get('success'):
            result = {
                "success": True,
                "model": response.get('model', model),
                "content": response.get('content', ''),
                "role": response.get('role', 'assistant'),
                "usage": response.get('usage', {}),
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Chat completion successful")
        else:
            result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "raw_response": response
            }
            print(f"❌ Chat completion failed")

        return OpenRouterDataValue(result)

    except Exception as e:
        print(f"❌ Error in chat_completion_skill: {e}")
        result = {"error": f"Failed to complete chat: {str(e)}"}
        return OpenRouterDataValue(result)


def text_completion_skill(context: Dict[str, Any]) -> OpenRouterDataValue:
    print("🔧 Starting text_completion_skill...")

    prompt = context.get('prompt', '')
    model = context.get('model', 'amazon/nova-2-lite-v1:free')
    temperature = context.get('temperature', 0.7)
    max_tokens = context.get('max_tokens', 500)

    if not prompt:
        result = {"error": "No prompt provided"}
        return OpenRouterDataValue(result)

    try:
        openrouter_component = context.get('openrouter_component')
        if not openrouter_component:
            result = {"error": "OpenRouter component not available"}
            return OpenRouterDataValue(result)

        print(f"📝 Sending text completion request to {model}")

        response = openrouter_component.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        if response.get('success'):
            result = {
                "success": True,
                "model": response.get('model', model),
                "content": response.get('content', ''),
                "usage": response.get('usage', {}),
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Text completion successful")
        else:
            result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "raw_response": response
            }
            print(f"❌ Text completion failed")

        return OpenRouterDataValue(result)

    except Exception as e:
        print(f"❌ Error in text_completion_skill: {e}")
        result = {"error": f"Failed to complete text: {str(e)}"}
        return OpenRouterDataValue(result)


def get_model_info_skill(context: Dict[str, Any]) -> OpenRouterModelValue:
    print("🔧 Starting get_model_info_skill...")

    model_id = context.get('model_id')

    if not model_id:
        result = {"error": "No model ID provided"}
        return OpenRouterModelValue(result)

    try:
        openrouter_component = context.get('openrouter_component')
        if not openrouter_component:
            result = {"error": "OpenRouter component not available"}
            return OpenRouterModelValue(result)

        print(f"ℹ️ Getting info for model: {model_id}")

        model_info = openrouter_component.get_detailed_model_info(model_id)

        if not model_info:
            result = {"error": f"Model {model_id} not found"}
            return OpenRouterModelValue(result)

        result = {
            "success": True,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Model info retrieved")
        return OpenRouterModelValue(result)

    except Exception as e:
        print(f"❌ Error in get_model_info_skill: {e}")
        result = {"error": f"Failed to get model info: {str(e)}"}
        return OpenRouterModelValue(result)


def calculate_cost_skill(context: Dict[str, Any]) -> OpenRouterDataValue:
    print("🔧 Starting calculate_cost_skill...")

    model = context.get('model')
    prompt_tokens = context.get('prompt_tokens', 0)
    completion_tokens = context.get('completion_tokens', 0)

    if not model:
        result = {"error": "No model provided"}
        return OpenRouterDataValue(result)

    try:
        openrouter_component = context.get('openrouter_component')
        if not openrouter_component:
            result = {"error": "OpenRouter component not available"}
            return OpenRouterDataValue(result)

        print(f"💰 Calculating cost for {model}")

        cost_info = openrouter_component.calculate_usage_cost(
            model, 
            prompt_tokens, 
            completion_tokens
        )

        if cost_info.get('success'):
            result = {
                "success": True,
                "cost_info": cost_info,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Cost calculated")
        else:
            result = {
                "success": False,
                "error": cost_info.get('error', 'Unknown error')
            }
            print(f"❌ Cost calculation failed")

        return OpenRouterDataValue(result)

    except Exception as e:
        print(f"❌ Error in calculate_cost_skill: {e}")
        result = {"error": f"Failed to calculate cost: {str(e)}"}
        return OpenRouterDataValue(result)


def openrouter_chat_skill(chat_value) -> any:
    print("🔧 Starting openrouter_chat_skill...")

    try:
        messages = getattr(chat_value, 'messages', [])

        if not messages:
            response = {
                "messages": [{
                    "role": "assistant",
                    "content": "🤖 **OpenRouter Assistant**\n\nI can help you with:\n• Listing available models\n• Chatting with AI models\n• Getting model information\n• Calculating costs\n\nType 'help' for commands."
                }]
            }
            return response

        last_message = messages[-1]['content'] if messages else ''

        openrouter_component = getattr(chat_value, 'context', {}).get('openrouter_component')

        if not openrouter_component:
            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "❌ OpenRouter component not available"
                }]
            }

        if 'help' in last_message.lower():
            help_text = """🤖 **OpenRouter Assistant Commands:**

**Basic Commands:**
• `list models` - Show all available models
• `list free` - Show only free models
• `info <model_id>` - Get model information
• `cost <model> <prompt_tokens> <completion_tokens>` - Calculate cost

**Chat Commands:**
• `chat <model> <message>` - Chat with specific model
• `chat <message>` - Chat with default model

**Examples:**
• list models
• list free
• info amazon/nova-2-lite-v1:free
• cost amazon/nova-2-lite-v1:free 0
• chat Hello!
• chat amazon/nova-2-lite-v1:free Write a poem

**Default model:** amazon/nova-2-lite-v1:free"""

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": help_text
                }]
            }

        elif 'list models' in last_message.lower():
            models = openrouter_component.get_available_models(free_only=False)

            if not models:
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "❌ Failed to get models"
                    }]
                }

            response = ["🤖 **Available Models:**\n"]

            for model in models[:15]:
                free = "🆓" if model.get('is_free') else "💰"
                model_id = model.get('id', 'Unknown')
                model_name = model.get('name', 'Unknown')
                response.append(f"{free} `{model_id}` - {model_name}")

            response.append(f"\n**Total:** {len(models)} models")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'list free' in last_message.lower():
            models = openrouter_component.get_available_models(free_only=True)

            if not models:
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "❌ No free models found"
                    }]
                }

            response = ["🆓 **Free Models:**\n"]

            for model in models[:10]:
                model_id = model.get('id', 'Unknown')
                model_name = model.get('name', 'Unknown')
                response.append(f"• `{model_id}` - {model_name}")

            response.append(f"\n**Total free models:** {len(models)}")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif last_message.lower().startswith('info '):
            model_id = last_message[5:].strip()

            model_info = openrouter_component.get_detailed_model_info(model_id)

            if not model_info:
                return {
                    "messages": messages + [{
                        "role": "assistant", 
                        "content": f"❌ Model '{model_id}' not found"
                    }]
                }

            response = [
                f"📊 **Model Info: {model_info.get('name', model_id)}**",
                f"**ID:** `{model_id}`",
                f"**Free:** {'✅ Yes' if model_info.get('is_free') else '❌ No'}",
                f"**Context Length:** {model_info.get('context_length', 'Unknown')} tokens",
            ]

            pricing = model_info.get('pricing', {})
            if pricing:
                response.append(f"**Pricing:**")
                response.append(f"  • Prompt: ${pricing.get('prompt', 0):.6f}/1K tokens")
                response.append(f"  • Completion: ${pricing.get('completion', 0):.6f}/1K tokens")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif last_message.lower().startswith('cost '):
            parts = last_message[5:].strip().split()
            if len(parts) != 3:
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "❌ Usage: cost <model> <prompt_tokens> <completion_tokens>"
                    }]
                }

            model_id, prompt_tokens_str, completion_tokens_str = parts

            try:
                prompt_tokens = int(prompt_tokens_str)
                completion_tokens = int(completion_tokens_str)

                cost_info = openrouter_component.calculate_usage_cost(
                    model_id, prompt_tokens, completion_tokens
                )

                if not cost_info.get('success'):
                    return {
                        "messages": messages + [{
                            "role": "assistant",
                            "content": f"❌ {cost_info.get('error', 'Cost calculation failed')}"
                        }]
                    }

                response = [
                    f"💰 **Cost Calculation for {model_id}**",
                    f"**Prompt Tokens:** {prompt_tokens}",
                    f"**Completion Tokens:** {completion_tokens}",
                    f"**Total Tokens:** {prompt_tokens + completion_tokens}",
                    f"**Prompt Cost:** ${cost_info.get('prompt_cost', 0):.6f}",
                    f"**Completion Cost:** ${cost_info.get('completion_cost', 0):.6f}",
                    f"**Total Cost:** ${cost_info.get('total_cost', 0):.6f} USD",
                ]

                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "\n".join(response)
                    }]
                }

            except ValueError:
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "❌ Invalid token numbers. Use integers."
                    }]
                }

        elif last_message.lower().startswith('chat '):
            chat_parts = last_message[5:].strip()
            parts = chat_parts.split(' ', 1)

            if len(parts) == 1:
                message = parts[0]
                model_id = 'amazon/nova-2-lite-v1:free'
            else:
                model_id = parts[0]
                message = parts[1]

            chat_response = openrouter_component.chat_completion(
                messages=[{"role": "user", "content": message}],
                model=model_id,
                temperature=0.7,
                max_tokens=500
            )

            if chat_response.get('success'):
                response_text = chat_response.get('content', '')

                usage = chat_response.get('usage', {})
                total_tokens = usage.get('total_tokens', 0)

                final_response = [
                    f"🤖 **Response from {model_id}**",
                    "",
                    response_text,
                    "",
                    f"*Tokens used: {total_tokens}*"
                ]

                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "\n".join(final_response)
                    }]
                }
            else:
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": f"❌ Error: {chat_response.get('error', 'Unknown error')}"
                    }]
                }

        else:
            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": f"I received: '{last_message}'\n\nType 'help' for available commands."
                }]
            }

    except Exception as e:
        print(f"❌ Error in openrouter_chat_skill: {e}")
        return {
            "messages": messages + [{
                "role": "assistant",
                "content": f"❌ Error: {str(e)}"
            }]
        }
