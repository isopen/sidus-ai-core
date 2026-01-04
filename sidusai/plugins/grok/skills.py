from typing import Dict, Any
from datetime import datetime

class GrokDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def get_api_info_skill(context: Dict[str, Any]) -> GrokDataValue:
    try:
        client = context.get('grok_client')

        if not client:
            return GrokDataValue({"success": False, "error": "Grok client not available"})

        response = client.get_api_key_info()

        analysis_result = {
            "success": True,
            "api_key_info": {
                "key_id": response.get('api_key_id'),
                "name": response.get('name'),
                "user_id": response.get('user_id'),
                "team_id": response.get('team_id'),
                "status": {
                    "blocked": response.get('api_key_blocked', False),
                    "disabled": response.get('api_key_disabled', False),
                    "team_blocked": response.get('team_blocked', False)
                },
                "permissions": response.get('acls', []),
                "creation_time": response.get('create_time'),
                "modification_time": response.get('modify_time')
            },
            "timestamp": datetime.now().isoformat()
        }

        return GrokDataValue(analysis_result)

    except Exception as e:
        return GrokDataValue({"success": False, "error": f"Failed to get API info: {str(e)}"})

def list_models_skill(context: Dict[str, Any]) -> GrokDataValue:
    try:
        client = context.get('grok_client')

        if not client:
            return GrokDataValue({"success": False, "error": "Grok client not available"})

        model_type = context.get('model_type', 'all')

        if model_type == 'language':
            response = client.list_language_models()
            models = response.get('models', [])
        elif model_type == 'image':
            response = client.list_image_generation_models()
            models = response.get('models', [])
        else:
            response = client.list_models()
            models = response.get('data', [])

        model_categories = {
            "chat": [],
            "vision": [],
            "image_generation": [],
            "code": [],
            "legacy": []
        }

        for model in models:
            model_id = model.get('id', '').lower()

            if 'vision' in model_id or 'image' in model_id:
                if 'generation' in model_id or 'image' == model_id.split('-')[-1]:
                    model_categories["image_generation"].append(model)
                else:
                    model_categories["vision"].append(model)
            elif 'code' in model_id:
                model_categories["code"].append(model)
            elif 'mini' in model_id or 'beta' in model_id:
                model_categories["legacy"].append(model)
            else:
                model_categories["chat"].append(model)

        analysis_result = {
            "success": True,
            "model_type": model_type,
            "total_models": len(models),
            "models_by_category": {
                category: len(models_list) for category, models_list in model_categories.items()
            },
            "categories": model_categories,
            "available_models": [model.get('id') for model in models],
            "timestamp": datetime.now().isoformat()
        }

        return GrokDataValue(analysis_result)

    except Exception as e:
        return GrokDataValue({"success": False, "error": f"Failed to list models: {str(e)}"})

def chat_completion_skill(context: Dict[str, Any]) -> GrokDataValue:
    try:
        client = context.get('grok_client')

        if not client:
            return GrokDataValue({"success": False, "error": "Grok client not available"})

        messages = context.get('messages', [])

        if not messages:
            return GrokDataValue({"success": False, "error": "Messages are required"})

        model = context.get('model', 'grok-4-0709')
        max_tokens = context.get('max_tokens')
        temperature = context.get('temperature')
        tools = context.get('tools')
        tool_choice = context.get('tool_choice')

        response = client.chat_completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,
            tool_choice=tool_choice
        )

        choices = response.get('choices', [])

        analysis_result = {
            "success": True,
            "model": response.get('model'),
            "response_id": response.get('id'),
            "created": response.get('created'),
            "choices_count": len(choices),
            "choices": [],
            "usage": response.get('usage', {}),
            "system_fingerprint": response.get('system_fingerprint'),
            "timestamp": datetime.now().isoformat()
        }

        for choice in choices:
            message = choice.get('message', {})
            choice_data = {
                "index": choice.get('index'),
                "role": message.get('role'),
                "content": message.get('content'),
                "finish_reason": choice.get('finish_reason'),
                "refusal": message.get('refusal')
            }
            analysis_result["choices"].append(choice_data)

        return GrokDataValue(analysis_result)

    except Exception as e:
        return GrokDataValue({"success": False, "error": f"Failed to get chat completion: {str(e)}"})

def create_response_skill(context: Dict[str, Any]) -> GrokDataValue:
    try:
        client = context.get('grok_client')

        if not client:
            return GrokDataValue({"success": False, "error": "Grok client not available"})

        input_data = context.get('input')

        if not input_data:
            return GrokDataValue({"success": False, "error": "Input is required"})

        model = context.get('model', 'grok-4-0709')
        max_output_tokens = context.get('max_output_tokens')
        temperature = context.get('temperature')
        store = context.get('store', True)
        tools = context.get('tools')
        tool_choice = context.get('tool_choice')

        response = client.create_response(
            model=model,
            input=input_data,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            store=store,
            tools=tools,
            tool_choice=tool_choice
        )

        analysis_result = {
            "success": True,
            "response_id": response.get('id'),
            "model": response.get('model'),
            "created_at": response.get('created_at'),
            "status": response.get('status'),
            "output": response.get('output', []),
            "usage": response.get('usage', {}),
            "store": response.get('store', True),
            "timestamp": datetime.now().isoformat()
        }

        return GrokDataValue(analysis_result)

    except Exception as e:
        return GrokDataValue({"success": False, "error": f"Failed to create response: {str(e)}"})

def generate_image_skill(context: Dict[str, Any]) -> GrokDataValue:
    try:
        client = context.get('grok_client')

        if not client:
            return GrokDataValue({"success": False, "error": "Grok client not available"})

        prompt = context.get('prompt')

        if not prompt:
            return GrokDataValue({"success": False, "error": "Prompt is required"})

        model = context.get('model', 'grok-2-image')
        n = context.get('n', 1)
        size = context.get('size', '1024x1024')

        response = client.generate_image(
            prompt=prompt,
            model=model,
            n=n,
            size=size
        )

        images = response.get('data', [])

        analysis_result = {
            "success": True,
            "model": model,
            "images_count": len(images),
            "images": [],
            "timestamp": datetime.now().isoformat()
        }

        for image in images:
            image_data = {
                "url": image.get('url'),
                "revised_prompt": image.get('revised_prompt')
            }
            analysis_result["images"].append(image_data)

        return GrokDataValue(analysis_result)

    except Exception as e:
        return GrokDataValue({"success": False, "error": f"Failed to generate image: {str(e)}"})

def analyze_model_capabilities_skill(context: Dict[str, Any]) -> GrokDataValue:
    try:
        client = context.get('grok_client')

        if not client:
            return GrokDataValue({"success": False, "error": "Grok client not available"})

        model_id = context.get('model_id', 'grok-4-0709')

        try:
            response = client.get_language_model_info(model_id)
        except:
            response = client.get_model_info(model_id)

        input_modalities = response.get('input_modalities', [])
        output_modalities = response.get('output_modalities', [])

        capabilities = {
            "text_input": "text" in input_modalities,
            "image_input": "image" in input_modalities,
            "audio_input": "audio" in input_modalities,
            "text_output": "text" in output_modalities,
            "image_output": "image" in output_modalities,
            "reasoning": "reasoning" in model_id.lower() or "grok-4" in model_id,
            "vision": "vision" in model_id.lower(),
            "code": "code" in model_id.lower(),
            "image_generation": "image" in model_id.lower() and "generation" not in model_id.lower()
        }

        pricing_info = {}
        pricing_fields = ['prompt_text_token_price', 'cached_prompt_text_token_price', 
                         'prompt_image_token_price', 'completion_text_token_price',
                         'search_price', 'image_price', 'generated_image_token_price']

        for field in pricing_fields:
            if field in response:
                pricing_info[field] = response[field]

        analysis_result = {
            "success": True,
            "model_id": response.get('id'),
            "version": response.get('version'),
            "created": response.get('created'),
            "owned_by": response.get('owned_by'),
            "capabilities": capabilities,
            "modalities": {
                "input": input_modalities,
                "output": output_modalities
            },
            "pricing": pricing_info,
            "aliases": response.get('aliases', []),
            "fingerprint": response.get('fingerprint'),
            "timestamp": datetime.now().isoformat()
        }

        return GrokDataValue(analysis_result)

    except Exception as e:
        return GrokDataValue({"success": False, "error": f"Failed to analyze model capabilities: {str(e)}"})

def tokenize_text_skill(context: Dict[str, Any]) -> GrokDataValue:
    try:
        client = context.get('grok_client')

        if not client:
            return GrokDataValue({"success": False, "error": "Grok client not available"})

        text = context.get('text')

        if not text:
            return GrokDataValue({"success": False, "error": "Text is required"})

        model = context.get('model', 'grok-4-0709')

        response = client.tokenize_text(text, model)

        tokens = response.get('token_ids', [])

        analysis_result = {
            "success": True,
            "model": model,
            "text_length": len(text),
            "tokens_count": len(tokens),
            "tokens": tokens,
            "average_token_length": len(text) / max(len(tokens), 1),
            "timestamp": datetime.now().isoformat()
        }

        return GrokDataValue(analysis_result)

    except Exception as e:
        return GrokDataValue({"success": False, "error": f"Failed to tokenize text: {str(e)}"})
