from typing import Dict, Any
from datetime import datetime

class DogCEODataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def get_all_breeds_skill(context: Dict[str, Any]) -> DogCEODataValue:
    print("Starting get_all_breeds_skill...")

    try:
        dog_component = context.get('dog_component')
        if not dog_component:
            result = {"error": "Dog CEO component not available"}
            return DogCEODataValue(result)

        print("Getting all dog breeds...")

        breeds_data = dog_component.get_all_breeds()

        if breeds_data.get('success'):
            breeds = breeds_data.get('breeds', [])
            categories = breeds_data.get('categories', {})

            result = {
                "success": True,
                "breeds": breeds,
                "categories": categories,
                "total_breeds": len(breeds),
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(breeds)} dog breeds")
        else:
            result = {
                "success": False,
                "error": breeds_data.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get breeds")

        return DogCEODataValue(result)

    except Exception as e:
        print(f"Error in get_all_breeds_skill: {e}")
        result = {"error": f"Failed to get dog breeds: {str(e)}"}
        return DogCEODataValue(result)

def get_random_dog_skill(context: Dict[str, Any]) -> DogCEODataValue:
    print("Starting get_random_dog_skill...")

    breed = context.get('breed')
    count = context.get('count', 1)

    try:
        dog_component = context.get('dog_component')
        if not dog_component:
            result = {"error": "Dog CEO component not available"}
            return DogCEODataValue(result)

        if breed:
            print(f"Fetching random {breed} image(s)...")
        else:
            print(f"Fetching random dog image(s)...")

        dog_data = dog_component.get_random_dog(breed, count)

        if dog_data.get('success'):
            images = dog_data.get('images', [])
            result_breed = dog_data.get('breed', 'random')

            result = {
                "success": True,
                "images": images,
                "breed": result_breed,
                "count": len(images),
                "message": f"Found {len(images)} image(s) of {result_breed if result_breed else 'random dogs'}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(images)} dog image(s)")
        else:
            result = {
                "success": False,
                "error": dog_data.get('error', 'Unknown error'),
                "breed": breed,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get dog image(s)")

        return DogCEODataValue(result)

    except Exception as e:
        print(f"Error in get_random_dog_skill: {e}")
        result = {"error": f"Failed to get dog image: {str(e)}"}
        return DogCEODataValue(result)

def get_breed_images_skill(context: Dict[str, Any]) -> DogCEODataValue:
    print("Starting get_breed_images_skill...")

    breed = context.get('breed')
    count = context.get('count', 10)

    if not breed:
        result = {"error": "No breed specified"}
        return DogCEODataValue(result)

    try:
        dog_component = context.get('dog_component')
        if not dog_component:
            result = {"error": "Dog CEO component not available"}
            return DogCEODataValue(result)

        print(f"Fetching images for breed: {breed}")

        breed_data = dog_component.get_breed_images(breed, count)

        if breed_data.get('success'):
            images = breed_data.get('images', [])

            result = {
                "success": True,
                "images": images,
                "breed": breed,
                "count": len(images),
                "message": f"Found {len(images)} images of {breed}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(images)} images of {breed}")
        else:
            result = {
                "success": False,
                "error": breed_data.get('error', 'Unknown error'),
                "breed": breed,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get images for {breed}")

        return DogCEODataValue(result)

    except Exception as e:
        print(f"Error in get_breed_images_skill: {e}")
        result = {"error": f"Failed to get breed images: {str(e)}"}
        return DogCEODataValue(result)

def get_sub_breeds_skill(context: Dict[str, Any]) -> DogCEODataValue:
    print("Starting get_sub_breeds_skill...")

    breed = context.get('breed')

    if not breed:
        result = {"error": "No breed specified"}
        return DogCEODataValue(result)

    try:
        dog_component = context.get('dog_component')
        if not dog_component:
            result = {"error": "Dog CEO component not available"}
            return DogCEODataValue(result)

        print(f"Fetching sub-breeds for: {breed}")

        sub_breeds_data = dog_component.get_sub_breeds(breed)

        if sub_breeds_data.get('success'):
            sub_breeds = sub_breeds_data.get('sub_breeds', [])

            result = {
                "success": True,
                "breed": breed,
                "sub_breeds": sub_breeds,
                "count": len(sub_breeds),
                "message": f"Found {len(sub_breeds)} sub-breeds of {breed}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(sub_breeds)} sub-breeds of {breed}")
        else:
            result = {
                "success": False,
                "error": sub_breeds_data.get('error', 'Unknown error'),
                "breed": breed,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get sub-breeds for {breed}")

        return DogCEODataValue(result)

    except Exception as e:
        print(f"Error in get_sub_breeds_skill: {e}")
        result = {"error": f"Failed to get sub-breeds: {str(e)}"}
        return DogCEODataValue(result)

def dogceo_chat_skill(chat_value) -> any:
    print("Starting dogceo_chat_skill...")

    try:
        messages = getattr(chat_value, 'messages', [])

        if not messages:
            response = {
                "messages": [{
                    "role": "assistant",
                    "content": "Dog CEO Image Generator Assistant\n\nI can help you find and generate images of different dog breeds using Dog CEO API!\n\nAvailable Commands:\n• breeds - List all dog breeds\n• breeds [category] - List breeds by category\n• random - Get random dog image\n• random [breed] - Get random image of specific breed\n• images [breed] - Get multiple images of a breed\n• subbreeds [breed] - Get sub-breeds of a breed\n• popular - Show popular breeds\n• search [query] - Search for breeds\n• help - Show this help message\n\nCategories: Small, Medium, Large, Working, Sporting, Toy, Herding, Hound, Terrier\n\nExamples:\n• breeds\n• breeds small\n• random\n• random labrador\n• images german shepherd\n• subbreeds bulldog\n• popular\n• search terrier\n• help\n\nPopular breeds: labrador, german shepherd, golden retriever, french bulldog, beagle"
                }]
            }
            return response

        last_message = messages[-1]['content'] if messages else ''

        dog_component = getattr(chat_value, 'context', {}).get('dog_component')

        if not dog_component:
            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "Dog CEO component not available"
                }]
            }

        if 'help' in last_message.lower():
            help_text = "Dog CEO Image Generator Assistant\n\nAvailable Commands:\n• breeds - List all dog breeds\n• breeds [category] - List breeds by category (small, medium, large, working, sporting, toy, herding, hound, terrier)\n• random - Get random dog image\n• random [breed] - Get random image of specific breed\n• images [breed] - Get multiple images of a breed\n• subbreeds [breed] - Get sub-breeds of a breed\n• popular - Show popular breeds\n• search [query] - Search for breeds\n• help - Show this help message\n\nExamples:\n• breeds\n• breeds small\n• random\n• random labrador\n• images german shepherd\n• subbreeds bulldog\n• popular\n• search terrier\n• help\n\nTry: random for a surprise dog picture!"

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": help_text
                }]
            }

        elif 'breeds' in last_message.lower():
            command = last_message.lower().replace('breeds', '').strip()

            breeds_data = dog_component.get_all_breeds()

            if not breeds_data.get('success'):
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": f"Failed to get breeds: {breeds_data.get('error', 'Unknown error')}"
                    }]
                }

            all_breeds = breeds_data.get('breeds', [])
            categories = breeds_data.get('categories', {})

            if command and command in ['small', 'medium', 'large', 'working', 'sporting', 'toy', 'herding', 'hound', 'terrier']:
                category_key = f"{command.title()} Dogs"
                category_breeds = categories.get(category_key, [])

                if category_breeds:
                    response = [f"{category_key}:\n"]
                    for breed in category_breeds[:15]:
                        breed_name = breed['name'].title()
                        sub_count = breed['total_sub_breeds']
                        if sub_count > 0:
                            response.append(f"• {breed_name} ({sub_count} sub-breeds)")
                        else:
                            response.append(f"• {breed_name}")

                    if len(category_breeds) > 15:
                        response.append(f"\n... and {len(category_breeds) - 15} more")

                    response.append(f"\nTotal: {len(category_breeds)} breeds")
                else:
                    response = [f"No breeds found in category: {command}"]
            else:
                response = [f"All Dog Breeds\n"]
                response.append(f"Total: {len(all_breeds)} breeds\n")

                response.append("Categories:")
                for category, category_breeds in categories.items():
                    response.append(f"• {category}: {len(category_breeds)} breeds")

                response.append("\nPopular breeds:")
                popular = ['labrador', 'german shepherd', 'golden retriever', 'french bulldog', 'beagle', 'poodle']
                for breed_name in popular:
                    for breed in all_breeds:
                        if breed_name.lower() in breed['name'].lower():
                            response.append(f"• {breed['name'].title()}")
                            break

                response.append("\nUsage: breeds [category] or images [breed]")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'random' in last_message.lower():
            command = last_message.lower().replace('random', '').strip()

            if command:
                breed = command
                dog_data = dog_component.get_random_dog(breed, 1)
            else:
                dog_data = dog_component.get_random_dog(None, 1)

            if dog_data.get('success'):
                images = dog_data.get('images', [])
                breed_name = dog_data.get('breed', 'random dog').title()

                if images:
                    image_url = images[0]
                    response = [
                        f"Random {breed_name} Image",
                        "",
                        f"Image URL: {image_url}",
                        "",
                        "Commands:",
                        "• random - Another random dog",
                        "• random [breed] - Random specific breed",
                        "• images [breed] - More images of this breed"
                    ]
                else:
                    response = [f"No images found for {breed_name}"]
            else:
                response = [f"Error: {dog_data.get('error', 'Failed to get dog image')}"]

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'images' in last_message.lower():
            command = last_message.lower().replace('images', '').strip()

            if not command:
                response = ["Please specify a breed. Example: images labrador"]
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "\n".join(response)
                    }]
                }

            dog_data = dog_component.get_breed_images(command, 5)

            if dog_data.get('success'):
                images = dog_data.get('images', [])
                breed_name = command.title()

                response = [f"Images of {breed_name}\n"]

                for i, image_url in enumerate(images[:5], 1):
                    response.append(f"{i}. {image_url}")

                response.append(f"\nTotal found: {len(images)} images")
                response.append(f"\nTry: random {command} for a single random image")
            else:
                response = [f"Error: {dog_data.get('error', 'Breed not found')}"]
                response.append("\nTry: breeds to see available breeds")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'subbreeds' in last_message.lower():
            command = last_message.lower().replace('subbreeds', '').strip()

            if not command:
                response = ["Please specify a breed. Example: subbreeds bulldog"]
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "\n".join(response)
                    }]
                }

            sub_data = dog_component.get_sub_breeds(command)

            if sub_data.get('success'):
                sub_breeds = sub_data.get('sub_breeds', [])
                breed_name = command.title()

                if sub_breeds:
                    response = [f"Sub-breeds of {breed_name}:\n"]

                    for sub_breed in sub_breeds:
                        response.append(f"• {sub_breed.title()}")

                    response.append(f"\nTotal: {len(sub_breeds)} sub-breeds")
                    response.append(f"\nTry: images {command} [subbreed] for images")
                else:
                    response = [f"{breed_name} has no sub-breeds"]
            else:
                response = [f"Error: {sub_data.get('error', 'Breed not found')}"]

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'popular' in last_message.lower():
            popular_breeds = dog_component.get_popular_breeds(10)

            response = ["Popular Dog Breeds:\n"]

            for i, breed in enumerate(popular_breeds, 1):
                breed_name = breed['name'].title()
                sub_count = breed.get('total_sub_breeds', 0)

                if sub_count > 0:
                    response.append(f"{i}. {breed_name} ({sub_count} sub-breeds)")
                else:
                    response.append(f"{i}. {breed_name}")

            response.append("\nCommands:")
            response.append("• images [breed] - Get images of a breed")
            response.append("• random [breed] - Get random image")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'search' in last_message.lower():
            query = last_message.lower().replace('search', '').strip()

            if not query:
                response = ["Please specify search query. Example: search terrier"]
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "\n".join(response)
                    }]
                }

            search_results = dog_component.search_breeds(query)

            if search_results:
                response = [f"Search results for '{query}':\n"]

                for breed in search_results[:10]:
                    breed_name = breed['name'].title()
                    sub_count = breed.get('total_sub_breeds', 0)

                    if sub_count > 0:
                        response.append(f"• {breed_name} ({sub_count} sub-breeds)")
                    else:
                        response.append(f"• {breed_name}")

                if len(search_results) > 10:
                    response.append(f"\n... and {len(search_results) - 10} more")

                response.append(f"\nTotal found: {len(search_results)} breeds")
            else:
                response = [f"No breeds found matching '{query}'"]
                response.append("\nTry: breeds to see all available breeds")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        else:
            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": f"I didn't understand that dog command.\n\nTry: help for available commands or random for a dog picture!"
                }]
            }

    except Exception as e:
        print(f"Error in dogceo_chat_skill: {e}")
        return {
            "messages": messages + [{
                "role": "assistant",
                "content": f"Error: {str(e)}"
            }]
        }
