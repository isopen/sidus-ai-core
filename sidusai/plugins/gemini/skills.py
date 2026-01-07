from typing import Dict, Any
from datetime import datetime
import json

class GeminiDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def generate_text_skill(context: Dict[str, Any]) -> GeminiDataValue:
    print("Starting generate_text_skill...")

    prompt = context.get('prompt', '')
    model = context.get('model', 'gemini-2.0-flash-exp')
    temperature = context.get('temperature', 0.7)
    max_tokens = context.get('max_tokens', 1024)

    try:
        client = context.get('gemini_client')

        if not client:
            result = {"success": False, "error": "Gemini client not available"}
            return GeminiDataValue(result)

        if not prompt:
            result = {"success": False, "error": "Prompt is required"}
            return GeminiDataValue(result)

        print(f"Generating text with model: {model}")
        print(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")

        response = client.generate_text(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        if response.get('success', False):
            candidates = response.get('candidates', [])

            analysis_result = {
                "success": True,
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "candidates_count": len(candidates),
                "candidates": [],
                "timestamp": datetime.now().isoformat()
            }

            for i, candidate in enumerate(candidates):
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                text = parts[0].get('text', '') if parts else ''

                candidate_data = {
                    "index": i,
                    "text": text,
                    "finish_reason": candidate.get('finishReason', ''),
                    "safety_ratings": candidate.get('safetyRatings', []),
                    "token_count": len(text.split()) if text else 0
                }
                analysis_result["candidates"].append(candidate_data)

            if analysis_result["candidates"]:
                first_candidate = analysis_result["candidates"][0]
                print(f"✅ Generated text: {first_candidate['text'][:200]}..." if len(first_candidate['text']) > 200 else f"✅ Generated text: {first_candidate['text']}")
                print(f"   Token count: {first_candidate['token_count']}")
                print(f"   Finish reason: {first_candidate['finish_reason']}")

            return GeminiDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Text generation error: {response.get('error')}")
            return GeminiDataValue(error_result)

    except Exception as e:
        print(f"Error in generate_text_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return GeminiDataValue(result)

def generate_content_skill(context: Dict[str, Any]) -> GeminiDataValue:
    print("Starting generate_content_skill...")

    contents = context.get('contents', [])
    model = context.get('model', 'gemini-2.0-flash-exp')
    generation_config = context.get('generation_config', {})

    try:
        client = context.get('gemini_client')

        if not client:
            result = {"success": False, "error": "Gemini client not available"}
            return GeminiDataValue(result)

        if not contents:
            result = {"success": False, "error": "Contents are required"}
            return GeminiDataValue(result)

        print(f"Generating content with model: {model}")
        print(f"Contents count: {len(contents)}")

        response = client.generate_content(
            contents=contents,
            model=model,
            generation_config=generation_config
        )

        if response.get('success', False):
            candidates = response.get('candidates', [])

            analysis_result = {
                "success": True,
                "model": model,
                "contents_count": len(contents),
                "candidates_count": len(candidates),
                "candidates": [],
                "usage_metadata": response.get('usageMetadata', {}),
                "timestamp": datetime.now().isoformat()
            }

            for i, candidate in enumerate(candidates):
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                text = parts[0].get('text', '') if parts else ''

                candidate_data = {
                    "index": i,
                    "text": text,
                    "content": content,
                    "finish_reason": candidate.get('finishReason', ''),
                    "safety_ratings": candidate.get('safetyRatings', []),
                    "token_count": response.get('usageMetadata', {}).get('totalTokenCount', 0)
                }
                analysis_result["candidates"].append(candidate_data)

            if analysis_result["candidates"]:
                first_candidate = analysis_result["candidates"][0]
                print(f"✅ Generated content: {first_candidate['text'][:200]}..." if len(first_candidate['text']) > 200 else f"✅ Generated content: {first_candidate['text']}")

                usage = analysis_result["usage_metadata"]
                print(f"   Tokens used: {usage.get('totalTokenCount', 0)} (prompt: {usage.get('promptTokenCount', 0)}, candidates: {usage.get('candidatesTokenCount', 0)})")

            return GeminiDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Content generation error: {response.get('error')}")
            return GeminiDataValue(error_result)

    except Exception as e:
        print(f"Error in generate_content_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return GeminiDataValue(result)

def generate_image_skill(context: Dict[str, Any]) -> GeminiDataValue:
    print("Starting generate_image_skill...")

    prompt = context.get('prompt', '')
    model = context.get('model', 'imagen-4.0-generate-001')
    sample_count = context.get('sample_count', 4)
    parameters = context.get('parameters', {})

    try:
        client = context.get('gemini_client')

        if not client:
            result = {"success": False, "error": "Gemini client not available"}
            return GeminiDataValue(result)

        if not prompt:
            result = {"success": False, "error": "Prompt is required"}
            return GeminiDataValue(result)

        print(f"Generating image with model: {model}")
        print(f"Prompt: {prompt}")
        print(f"Sample count: {sample_count}")

        response = client.generate_image(
            prompt=prompt,
            model=model,
            sample_count=sample_count,
            parameters=parameters
        )

        if response.get('success', False):
            predictions = response.get('predictions', [])

            analysis_result = {
                "success": True,
                "model": model,
                "prompt": prompt,
                "sample_count": sample_count,
                "predictions_count": len(predictions),
                "predictions": [],
                "timestamp": datetime.now().isoformat()
            }

            for i, prediction in enumerate(predictions):
                prediction_data = {
                    "index": i,
                    "bytesBase64Encoded": prediction.get('bytesBase64Encoded', False),
                    "mimeType": prediction.get('mimeType', ''),
                    "image_size": len(prediction.get('bytes', '')) if prediction.get('bytes') else 0,
                    "bytes": prediction.get('bytes', ''),
                    "response": response
                }

                if prediction.get('bytes'):
                    prediction_data["has_image_data"] = True
                else:
                    prediction_data["has_image_data"] = False

                analysis_result["predictions"].append(prediction_data)

            print(f"✅ Generated {len(predictions)} images")
            for i, pred in enumerate(analysis_result["predictions"]):
                print(f"   Image {i+1}: {pred['mimeType']}, Size: {pred['image_size']} bytes")
                if pred.get('has_image_data'):
                    print(f"      Contains base64 image data")

            return GeminiDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Image generation error: {response.get('error')}")
            return GeminiDataValue(error_result)

    except Exception as e:
        print(f"Error in generate_image_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return GeminiDataValue(result)

def embed_content_skill(context: Dict[str, Any]) -> GeminiDataValue:
    print("Starting embed_content_skill...")

    text = context.get('text', '')
    model = context.get('model', 'models/embedding-001')

    try:
        client = context.get('gemini_client')

        if not client:
            result = {"success": False, "error": "Gemini client not available"}
            return GeminiDataValue(result)

        if not text:
            result = {"success": False, "error": "Text is required"}
            return GeminiDataValue(result)

        print(f"Creating embeddings with model: {model}")
        print(f"Text: {text[:100]}..." if len(text) > 100 else f"Text: {text}")

        response = client.embed_content(
            text=text,
            model=model
        )

        if response.get('success', False):
            embedding = response.get('embedding', {})

            analysis_result = {
                "success": True,
                "model": model,
                "text": text,
                "embedding": {
                    "values_count": len(embedding.get('values', [])),
                    "dimensions": len(embedding.get('values', [])),
                    "values_preview": embedding.get('values', [])[:5] if embedding.get('values') else []
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Created embedding with {analysis_result['embedding']['dimensions']} dimensions")
            print(f"   First 5 values: {analysis_result['embedding']['values_preview']}")

            return GeminiDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Embedding error: {response.get('error')}")
            return GeminiDataValue(error_result)

    except Exception as e:
        print(f"Error in embed_content_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return GeminiDataValue(result)

def batch_embed_contents_skill(context: Dict[str, Any]) -> GeminiDataValue:
    print("Starting batch_embed_contents_skill...")

    texts = context.get('texts', [])
    model = context.get('model', 'models/embedding-001')

    try:
        client = context.get('gemini_client')

        if not client:
            result = {"success": False, "error": "Gemini client not available"}
            return GeminiDataValue(result)

        if not texts:
            result = {"success": False, "error": "Texts are required"}
            return GeminiDataValue(result)

        print(f"Creating batch embeddings with model: {model}")
        print(f"Texts count: {len(texts)}")

        response = client.batch_embed_contents(
            texts=texts,
            model=model
        )

        if response.get('success', False):
            embeddings = response.get('embeddings', [])

            analysis_result = {
                "success": True,
                "model": model,
                "texts_count": len(texts),
                "embeddings_count": len(embeddings),
                "embeddings": [],
                "summary": {
                    "total_dimensions": 0,
                    "avg_dimensions": 0,
                    "sample_texts": texts[:3] if len(texts) > 3 else texts
                },
                "timestamp": datetime.now().isoformat()
            }

            total_dims = 0
            for i, embedding in enumerate(embeddings):
                values = embedding.get('values', [])
                dims = len(values)
                total_dims += dims

                embed_data = {
                    "index": i,
                    "text_preview": texts[i][:50] + "..." if len(texts[i]) > 50 else texts[i],
                    "dimensions": dims,
                    "values_preview": values[:3] if values else []
                }
                analysis_result["embeddings"].append(embed_data)

            if embeddings:
                analysis_result["summary"]["total_dimensions"] = total_dims
                analysis_result["summary"]["avg_dimensions"] = total_dims / len(embeddings)

            print(f"✅ Created {len(embeddings)} embeddings")
            print(f"   Average dimensions: {analysis_result['summary']['avg_dimensions']:.2f}")

            return GeminiDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Batch embedding error: {response.get('error')}")
            return GeminiDataValue(error_result)

    except Exception as e:
        print(f"Error in batch_embed_contents_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return GeminiDataValue(result)

def analyze_image_skill(context: Dict[str, Any]) -> GeminiDataValue:
    print("Starting analyze_image_skill...")

    image_path = context.get('image_path', '')
    prompt = context.get('prompt', '')
    model = context.get('model', 'gemini-2.0-flash-exp')
    temperature = context.get('temperature', 0.5)
    thinking_budget = context.get('thinking_budget', 0)

    try:
        client = context.get('gemini_client')

        if not client:
            result = {"success": False, "error": "Gemini client not available"}
            return GeminiDataValue(result)

        if not image_path:
            result = {"success": False, "error": "Image path is required"}
            return GeminiDataValue(result)

        if not prompt:
            result = {"success": False, "error": "Prompt is required"}
            return GeminiDataValue(result)

        print(f"Analyzing image with model: {model}")
        print(f"Image path: {image_path}")
        print(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")

        response = client.analyze_image(
            image_path=image_path,
            prompt=prompt,
            model=model,
            temperature=temperature,
            thinking_budget=thinking_budget
        )

        if response.get('success', False):
            candidates = response.get('candidates', [])

            analysis_result = {
                "success": True,
                "model": model,
                "image_path": image_path,
                "prompt": prompt,
                "temperature": temperature,
                "thinking_budget": thinking_budget,
                "candidates_count": len(candidates),
                "candidates": [],
                "timestamp": datetime.now().isoformat()
            }

            for i, candidate in enumerate(candidates):
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                text = parts[0].get('text', '') if parts else ''

                candidate_data = {
                    "index": i,
                    "text": text,
                    "text_response": text,
                    "content": content,
                    "finish_reason": candidate.get('finishReason', ''),
                    "safety_ratings": candidate.get('safetyRatings', [])
                }

                if text:
                    text = candidate_data['text_response']
                    if text.strip().startswith('[') or text.strip().startswith('{'):
                        try:
                            parsed_json = json.loads(text)
                            candidate_data["parsed_json"] = parsed_json
                            candidate_data["is_valid_json"] = True
                        except:
                            candidate_data["is_valid_json"] = False

                analysis_result["candidates"].append(candidate_data)

            if analysis_result["candidates"]:
                first_candidate = analysis_result["candidates"][0]
                print(f"✅ Image analysis complete")
                print(f"   Response: {first_candidate['text_response'][:200]}..." if len(first_candidate['text_response']) > 200 else f"   Response: {first_candidate['text_response']}")

                if first_candidate.get('is_valid_json'):
                    print(f"   Response is valid JSON")

            return GeminiDataValue(analysis_result)

        else:
            error_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Image analysis error: {response.get('error')}")
            return GeminiDataValue(error_result)

    except Exception as e:
        print(f"Error in analyze_image_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return GeminiDataValue(result)
