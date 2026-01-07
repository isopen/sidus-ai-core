from typing import Dict, Any, List
from datetime import datetime
import json

class ClaudeDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_message_skill(context: Dict[str, Any]) -> ClaudeDataValue:
    print("Starting create_message_skill...")

    prompt = context.get('prompt', '')
    model = context.get('model', 'claude-3-haiku-20240307')
    max_tokens = context.get('max_tokens', 1024)
    system = context.get('system')
    temperature = context.get('temperature', 0.7)
    top_p = context.get('top_p', 1.0)

    try:
        client = context.get('claude_client')

        if not client:
            result = {"success": False, "error": "Claude client not available"}
            return ClaudeDataValue(result)

        if not prompt:
            result = {"success": False, "error": "Prompt is required"}
            return ClaudeDataValue(result)

        print(f"Creating message with model: {model}")

        response = client.create_message(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            system=system,
            temperature=temperature,
            top_p=top_p
        )

        if response.get('success', False):
            content = response.get('content', [])

            analysis_result = {
                "success": True,
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "content_count": len(content),
                "content": [],
                "usage": response.get('usage', {}),
                "stop_reason": response.get('stop_reason', ''),
                "timestamp": datetime.now().isoformat()
            }

            for i, item in enumerate(content):
                if item.get('type') == 'text':
                    text = item.get('text', '')
                    item_data = {
                        "index": i,
                        "type": "text",
                        "text": text,
                        "citations": item.get('citations', []),
                        "token_count": len(text.split()) if text else 0
                    }
                    analysis_result["content"].append(item_data)

            if analysis_result["content"]:
                first_content = analysis_result["content"][0]
                print(f"Created message with {first_content['token_count']} tokens")
                print(f"Stop reason: {analysis_result['stop_reason']}")

            return ClaudeDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Message creation error: {response.get('error')}")
            return ClaudeDataValue(error_result)

    except Exception as e:
        print(f"Error in create_message_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ClaudeDataValue(result)

def count_tokens_skill(context: Dict[str, Any]) -> ClaudeDataValue:
    print("Starting count_tokens_skill...")

    messages = context.get('messages', [])
    model = context.get('model', 'claude-3-haiku-20240307')

    try:
        client = context.get('claude_client')

        if not client:
            result = {"success": False, "error": "Claude client not available"}
            return ClaudeDataValue(result)

        if not messages:
            result = {"success": False, "error": "Messages are required"}
            return ClaudeDataValue(result)

        print(f"Counting tokens with model: {model}")
        print(f"Messages count: {len(messages)}")

        response = client.count_tokens(
            messages=messages,
            model=model
        )

        if response.get('success', False):
            analysis_result = {
                "success": True,
                "model": model,
                "messages_count": len(messages),
                "input_tokens": response.get('input_tokens', 0),
                "timestamp": datetime.now().isoformat()
            }

            print(f"Token count: {analysis_result['input_tokens']}")

            return ClaudeDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Token counting error: {response.get('error')}")
            return ClaudeDataValue(error_result)

    except Exception as e:
        print(f"Error in count_tokens_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ClaudeDataValue(result)

def create_batch_skill(context: Dict[str, Any]) -> ClaudeDataValue:
    print("Starting create_batch_skill...")

    requests_list = context.get('requests', [])

    try:
        client = context.get('claude_client')

        if not client:
            result = {"success": False, "error": "Claude client not available"}
            return ClaudeDataValue(result)

        if not requests_list:
            result = {"success": False, "error": "Requests are required"}
            return ClaudeDataValue(result)

        print(f"Creating batch with {len(requests_list)} requests")

        response = client.create_batch(
            requests=requests_list
        )

        if response.get('success', False):
            analysis_result = {
                "success": True,
                "batch_id": response.get('id', ''),
                "requests_count": len(requests_list),
                "processing_status": response.get('processing_status', ''),
                "created_at": response.get('created_at', ''),
                "expires_at": response.get('expires_at', ''),
                "results_url": response.get('results_url', ''),
                "request_counts": response.get('request_counts', {}),
                "timestamp": datetime.now().isoformat()
            }

            print(f"Batch created: {analysis_result['batch_id']}")
            print(f"Status: {analysis_result['processing_status']}")

            return ClaudeDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Batch creation error: {response.get('error')}")
            return ClaudeDataValue(error_result)

    except Exception as e:
        print(f"Error in create_batch_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ClaudeDataValue(result)

def list_models_skill(context: Dict[str, Any]) -> ClaudeDataValue:
    print("Starting list_models_skill...")

    try:
        client = context.get('claude_client')

        if not client:
            result = {"success": False, "error": "Claude client not available"}
            return ClaudeDataValue(result)

        print("Listing available models...")

        response = client.list_models()

        if response.get('success', False):
            models = response.get('data', [])

            analysis_result = {
                "success": True,
                "models_count": len(models),
                "models": [],
                "has_more": response.get('has_more', False),
                "first_id": response.get('first_id', ''),
                "last_id": response.get('last_id', ''),
                "timestamp": datetime.now().isoformat()
            }

            for model in models:
                model_data = {
                    "id": model.get('id', ''),
                    "display_name": model.get('display_name', ''),
                    "created_at": model.get('created_at', ''),
                    "type": model.get('type', '')
                }
                analysis_result["models"].append(model_data)

            print(f"Found {len(models)} models")

            return ClaudeDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Models listing error: {response.get('error')}")
            return ClaudeDataValue(error_result)

    except Exception as e:
        print(f"Error in list_models_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ClaudeDataValue(result)

def upload_file_skill(context: Dict[str, Any]) -> ClaudeDataValue:
    print("Starting upload_file_skill...")

    file_path = context.get('file_path', '')

    try:
        client = context.get('claude_client')

        if not client:
            result = {"success": False, "error": "Claude client not available"}
            return ClaudeDataValue(result)

        if not file_path:
            result = {"success": False, "error": "File path is required"}
            return ClaudeDataValue(result)

        print(f"Uploading file: {file_path}")

        response = client.upload_file(file_path)

        if response.get('success', False):
            analysis_result = {
                "success": True,
                "file_id": response.get('id', ''),
                "filename": response.get('filename', ''),
                "mime_type": response.get('mime_type', ''),
                "size_bytes": response.get('size_bytes', 0),
                "created_at": response.get('created_at', ''),
                "downloadable": response.get('downloadable', False),
                "timestamp": datetime.now().isoformat()
            }

            print(f"File uploaded: {analysis_result['filename']}")
            print(f"File ID: {analysis_result['file_id']}")

            return ClaudeDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"File upload error: {response.get('error')}")
            return ClaudeDataValue(error_result)

    except Exception as e:
        print(f"Error in upload_file_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ClaudeDataValue(result)
