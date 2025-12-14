from typing import Dict, Any, List
from datetime import datetime
import os

class CatAPIDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def get_random_cat_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_random_cat_skill...")

    size = context.get('size')
    mime_types = context.get('mime_types')
    has_breeds = context.get('has_breeds')
    limit = context.get('limit', 1)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Fetching {limit} random cat image(s)...")

        cat_data = cat_component.get_random_cat(
            size=size,
            mime_types=mime_types,
            has_breeds=has_breeds,
            limit=limit
        )

        if cat_data.get('success'):
            images = cat_data.get('images', [])

            result = {
                "success": True,
                "images": images,
                "count": len(images),
                "message": f"Found {len(images)} random cat image(s)",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(images)} random cat image(s)")
        else:
            result = {
                "success": False,
                "error": cat_data.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get random cat image(s)")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_random_cat_skill: {e}")
        result = {"success": False, "error": f"Failed to get random cat: {str(e)}"}
        return CatAPIDataValue(result)

def get_breed_images_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_breed_images_skill...")

    breed_id = context.get('breed_id')
    limit = context.get('limit', 10)

    if not breed_id:
        result = {"success": False, "error": "No breed ID specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Fetching images for breed ID: {breed_id}")

        breed_data = cat_component.get_breed_images(breed_id, limit)

        if breed_data.get('success'):
            images = breed_data.get('images', [])

            result = {
                "success": True,
                "images": images,
                "breed_id": breed_id,
                "count": len(images),
                "message": f"Found {len(images)} images of breed {breed_id}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(images)} images for breed {breed_id}")
        else:
            result = {
                "success": False,
                "error": breed_data.get('error', 'Unknown error'),
                "breed_id": breed_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get images for breed {breed_id}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_breed_images_skill: {e}")
        result = {"success": False, "error": f"Failed to get breed images: {str(e)}"}
        return CatAPIDataValue(result)

def upload_image_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting upload_image_skill...")

    file_path = context.get('file_path')
    sub_id = context.get('sub_id')
    breed_ids = context.get('breed_ids')

    if not file_path:
        result = {"success": False, "error": "No file path specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Uploading image: {file_path}")

        upload_data = cat_component.upload_image(file_path, sub_id, breed_ids)

        if upload_data.get('success'):
            upload_info = upload_data.get('upload', {})

            result = {
                "success": True,
                "upload": upload_info,
                "message": f"Image uploaded successfully: {upload_info.get('id', 'Unknown')}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Image uploaded: {upload_info.get('id', 'Unknown')}")
        else:
            result = {
                "success": False,
                "error": upload_data.get('error', 'Unknown error'),
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to upload image: {file_path}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in upload_image_skill: {e}")
        result = {"success": False, "error": f"Failed to upload image: {str(e)}"}
        return CatAPIDataValue(result)

def delete_image_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting delete_image_skill...")

    image_id = context.get('image_id')

    if not image_id:
        result = {"success": False, "error": "No image ID specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Deleting image: {image_id}")

        delete_data = cat_component.delete_image(image_id)

        if delete_data.get('success'):
            result = {
                "success": True,
                "message": f"Image {image_id} deleted successfully",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Image deleted: {image_id}")
        else:
            result = {
                "success": False,
                "error": delete_data.get('error', 'Unknown error'),
                "image_id": image_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to delete image: {image_id}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in delete_image_skill: {e}")
        result = {"success": False, "error": f"Failed to delete image: {str(e)}"}
        return CatAPIDataValue(result)

def get_user_images_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_user_images_skill...")

    limit = context.get('limit', 10)
    page = context.get('page', 0)
    order = context.get('order', 'DESC')

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Getting user images (page: {page}, limit: {limit}, order: {order})")

        images_data = cat_component.get_user_images(limit, page, order)

        if images_data.get('success'):
            images = images_data.get('images', [])

            result = {
                "success": True,
                "images": images,
                "count": len(images),
                "page": page,
                "limit": limit,
                "order": order,
                "message": f"Found {len(images)} user uploaded images",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(images)} user images")
        else:
            result = {
                "success": False,
                "error": images_data.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get user images")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_user_images_skill: {e}")
        result = {"success": False, "error": f"Failed to get user images: {str(e)}"}
        return CatAPIDataValue(result)

def get_image_analysis_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_image_analysis_skill...")

    image_id = context.get('image_id')

    if not image_id:
        result = {"success": False, "error": "No image ID specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Getting analysis for image: {image_id}")

        analysis_data = cat_component.get_image_analysis(image_id)

        if analysis_data.get('success'):
            analysis = analysis_data.get('analysis', {})

            result = {
                "success": True,
                "analysis": analysis,
                "image_id": image_id,
                "message": f"Analysis retrieved for image {image_id}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Analysis retrieved for image: {image_id}")
        else:
            result = {
                "success": False,
                "error": analysis_data.get('error', 'Unknown error'),
                "image_id": image_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get analysis for image: {image_id}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_image_analysis_skill: {e}")
        result = {"success": False, "error": f"Failed to get image analysis: {str(e)}"}
        return CatAPIDataValue(result)

def get_all_breeds_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_all_breeds_skill...")

    limit = context.get('limit', 10)
    page = context.get('page', 0)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print("Getting all cat breeds...")

        breeds_data = cat_component.get_all_breeds(limit, page)

        if breeds_data.get('success'):
            breeds = breeds_data.get('breeds', [])
            categories = breeds_data.get('categories', {})

            result = {
                "success": True,
                "breeds": breeds,
                "categories": categories,
                "total_breeds": len(breeds),
                "page": page,
                "limit": limit,
                "message": f"Found {len(breeds)} cat breeds",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(breeds)} cat breeds")
        else:
            result = {
                "success": False,
                "error": breeds_data.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get breeds")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_all_breeds_skill: {e}")
        result = {"success": False, "error": f"Failed to get cat breeds: {str(e)}"}
        return CatAPIDataValue(result)

def search_breeds_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting search_breeds_skill...")

    query = context.get('query')
    attach_image = context.get('attach_image', 1)

    if not query:
        result = {"success": False, "error": "No search query specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Searching breeds for: {query}")

        search_data = cat_component.search_breeds(query, attach_image)

        if search_data.get('success'):
            breeds = search_data.get('breeds', [])

            result = {
                "success": True,
                "breeds": breeds,
                "query": query,
                "count": len(breeds),
                "message": f"Found {len(breeds)} breeds matching '{query}'",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Found {len(breeds)} breeds matching '{query}'")
        else:
            result = {
                "success": False,
                "error": search_data.get('error', 'Unknown error'),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to search breeds for: {query}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in search_breeds_skill: {e}")
        result = {"success": False, "error": f"Failed to search breeds: {str(e)}"}
        return CatAPIDataValue(result)

def get_favourites_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_favourites_skill...")

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print("Getting favourites...")

        favourites_data = cat_component.get_favourites()

        if favourites_data.get('success'):
            favourites = favourites_data.get('favourites', [])

            result = {
                "success": True,
                "favourites": favourites,
                "count": len(favourites),
                "message": f"Found {len(favourites)} favourites",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(favourites)} favourites")
        else:
            result = {
                "success": False,
                "error": favourites_data.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get favourites")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_favourites_skill: {e}")
        result = {"success": False, "error": f"Failed to get favourites: {str(e)}"}
        return CatAPIDataValue(result)

def add_favourite_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting add_favourite_skill...")

    image_id = context.get('image_id')
    sub_id = context.get('sub_id')

    if not image_id:
        result = {"success": False, "error": "No image ID specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Adding favourite for image: {image_id}")

        favourite_data = cat_component.add_favourite(image_id, sub_id)

        if favourite_data.get('success'):
            favourite_info = favourite_data.get('favourite', {})

            result = {
                "success": True,
                "favourite": favourite_info,
                "message": f"Image {image_id} added to favourites",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Added favourite: {favourite_info.get('id', 'Unknown')}")
        else:
            result = {
                "success": False,
                "error": favourite_data.get('error', 'Unknown error'),
                "image_id": image_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to add favourite for image: {image_id}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in add_favourite_skill: {e}")
        result = {"success": False, "error": f"Failed to add favourite: {str(e)}"}
        return CatAPIDataValue(result)

def delete_favourite_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting delete_favourite_skill...")

    favourite_id = context.get('favourite_id')

    if not favourite_id:
        result = {"success": False, "error": "No favourite ID specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Deleting favourite: {favourite_id}")

        delete_data = cat_component.delete_favourite(favourite_id)

        if delete_data.get('success'):
            result = {
                "success": True,
                "message": f"Favourite {favourite_id} deleted successfully",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Deleted favourite: {favourite_id}")
        else:
            result = {
                "success": False,
                "error": delete_data.get('error', 'Unknown error'),
                "favourite_id": favourite_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to delete favourite: {favourite_id}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in delete_favourite_skill: {e}")
        result = {"success": False, "error": f"Failed to delete favourite: {str(e)}"}
        return CatAPIDataValue(result)

def get_votes_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_votes_skill...")

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print("Getting votes...")

        votes_data = cat_component.get_votes()

        if votes_data.get('success'):
            votes = votes_data.get('votes', [])

            result = {
                "success": True,
                "votes": votes,
                "count": len(votes),
                "message": f"Found {len(votes)} votes",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(votes)} votes")
        else:
            result = {
                "success": False,
                "error": votes_data.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get votes")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_votes_skill: {e}")
        result = {"success": False, "error": f"Failed to get votes: {str(e)}"}
        return CatAPIDataValue(result)

def add_vote_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting add_vote_skill...")

    image_id = context.get('image_id')
    value = context.get('value')
    sub_id = context.get('sub_id')

    if not image_id:
        result = {"success": False, "error": "No image ID specified"}
        return CatAPIDataValue(result)

    if value is None:
        result = {"success": False, "error": "No vote value specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Adding vote for image: {image_id} (value: {value})")

        vote_data = cat_component.add_vote(image_id, value, sub_id)

        if vote_data.get('success'):
            vote_info = vote_data.get('vote', {})

            result = {
                "success": True,
                "vote": vote_info,
                "message": f"Vote added for image {image_id}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Added vote: {vote_info.get('id', 'Unknown')}")
        else:
            result = {
                "success": False,
                "error": vote_data.get('error', 'Unknown error'),
                "image_id": image_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to add vote for image: {image_id}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in add_vote_skill: {e}")
        result = {"success": False, "error": f"Failed to add vote: {str(e)}"}
        return CatAPIDataValue(result)

def delete_vote_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting delete_vote_skill...")

    vote_id = context.get('vote_id')

    if not vote_id:
        result = {"success": False, "error": "No vote ID specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Deleting vote: {vote_id}")

        delete_data = cat_component.delete_vote(vote_id)

        if delete_data.get('success'):
            result = {
                "success": True,
                "message": f"Vote {vote_id} deleted successfully",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Deleted vote: {vote_id}")
        else:
            result = {
                "success": False,
                "error": delete_data.get('error', 'Unknown error'),
                "vote_id": vote_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to delete vote: {vote_id}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in delete_vote_skill: {e}")
        result = {"success": False, "error": f"Failed to delete vote: {str(e)}"}
        return CatAPIDataValue(result)

def get_facts_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_facts_skill...")

    limit = context.get('limit', 1)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Getting {limit} random fact(s)...")

        facts_data = cat_component.get_facts(limit)

        if facts_data.get('success'):
            facts = facts_data.get('facts', [])

            result = {
                "success": True,
                "facts": facts,
                "count": len(facts),
                "message": f"Found {len(facts)} random fact(s)",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(facts)} random fact(s)")
        else:
            result = {
                "success": False,
                "error": facts_data.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get facts")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_facts_skill: {e}")
        result = {"success": False, "error": f"Failed to get facts: {str(e)}"}
        return CatAPIDataValue(result)

def get_breed_facts_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_breed_facts_skill...")

    breed_id = context.get('breed_id')
    limit = context.get('limit', 5)
    page = context.get('page', 0)
    order = context.get('order', 'ASC')

    if not breed_id:
        result = {"success": False, "error": "No breed ID specified"}
        return CatAPIDataValue(result)

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print(f"Getting facts for breed: {breed_id}")

        facts_data = cat_component.get_breed_facts(breed_id, limit, page, order)

        if facts_data.get('success'):
            facts = facts_data.get('facts', [])

            result = {
                "success": True,
                "facts": facts,
                "breed_id": breed_id,
                "count": len(facts),
                "page": page,
                "order": order,
                "message": f"Found {len(facts)} facts for breed {breed_id}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(facts)} facts for breed {breed_id}")
        else:
            result = {
                "success": False,
                "error": facts_data.get('error', 'Unknown error'),
                "breed_id": breed_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get facts for breed: {breed_id}")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_breed_facts_skill: {e}")
        result = {"success": False, "error": f"Failed to get breed facts: {str(e)}"}
        return CatAPIDataValue(result)

def get_categories_skill(context: Dict[str, Any]) -> CatAPIDataValue:
    print("Starting get_categories_skill...")

    try:
        cat_component = context.get('cat_component')
        if not cat_component:
            result = {"success": False, "error": "The Cat API component not available"}
            return CatAPIDataValue(result)

        print("Fetching categories...")

        categories_data = cat_component.get_categories()

        if categories_data.get('success'):
            categories = categories_data.get('categories', [])

            result = {
                "success": True,
                "categories": categories,
                "count": len(categories),
                "message": f"Found {len(categories)} categories",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Retrieved {len(categories)} categories")
        else:
            result = {
                "success": False,
                "error": categories_data.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get categories")

        return CatAPIDataValue(result)

    except Exception as e:
        print(f"Error in get_categories_skill: {e}")
        result = {"success": False, "error": f"Failed to get categories: {str(e)}"}
        return CatAPIDataValue(result)

def catapi_chat_skill(chat_value) -> any:
    print("Starting catapi_chat_skill...")

    try:
        messages = getattr(chat_value, 'messages', [])

        if not messages:
            response = {
                "messages": [{
                    "role": "assistant",
                    "content": "🐱 The Cat API Assistant\n\nI can help you with everything related to cats using The Cat API!\n\nAvailable Commands:\n• breeds - List all cat breeds\n• search [query] - Search for breeds\n• random - Get random cat image\n• images [breed_id] - Get images of a breed\n• upload [path] - Upload an image\n• favourites - Show your favourites\n• vote [image_id] [value] - Vote on an image\n• facts - Get random cat facts\n• facts [breed_id] - Get facts about a breed\n• categories - List image categories\n• myimages - Show your uploaded images\n• help - Show this help message\n\nExamples:\n• breeds\n• search siamese\n• random\n• images pers\n• upload /path/to/cat.jpg\n• favourites\n• vote abc123 1\n• facts\n• facts ragd\n• categories\n• myimages\n• help"
                }]
            }
            return response

        last_message = messages[-1]['content'] if messages else ''

        cat_component = getattr(chat_value, 'context', {}).get('cat_component')

        if not cat_component:
            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "The Cat API component not available"
                }]
            }

        if 'help' in last_message.lower():
            help_text = """🐱 The Cat API Assistant - Full Features

📸 IMAGES:
• random - Get random cat image
• random [size] - Get image of specific size (thumb, small, med, full)
• random gif - Get random GIF
• images [breed_id] - Get images of specific breed
• upload [file_path] - Upload your own cat image
• myimages - View your uploaded images

🐈 BREEDS:
• breeds - List all cat breeds
• breeds [page] [limit] - Paginated breed list
• search [query] - Search breeds by name
• facts [breed_id] - Get facts about specific breed

❤️ FAVOURITES & VOTES:
• favourites - List your favourite images
• favourite [image_id] - Add image to favourites
• votes - View your votes
• vote [image_id] [value] - Vote on image (1 for up, 0 for down)

📚 FACTS & CATEGORIES:
• facts - Get random cat facts
• facts [limit] - Get multiple facts
• categories - List all image categories

💡 Examples:
• random
• random med
• random gif
• images pers
• upload /photos/mycat.jpg
• breeds
• search bengal
• favourites
• vote abc123 1
• facts 5
• categories
• help"""

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": help_text
                }]
            }

        elif 'breeds' in last_message.lower():
            parts = last_message.lower().replace('breeds', '').strip().split()
            page = 0
            limit = 10

            if len(parts) >= 1:
                try:
                    page = int(parts[0])
                except:
                    pass
            if len(parts) >= 2:
                try:
                    limit = int(parts[1])
                except:
                    pass

            breeds_data = cat_component.get_all_breeds(limit, page)

            if not breeds_data.get('success'):
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": f"Failed to get breeds: {breeds_data.get('error', 'Unknown error')}"
                    }]
                }

            all_breeds = breeds_data.get('breeds', [])
            categories = breeds_data.get('categories', {})

            response = [f"🐱 Cat Breeds (Page {page + 1})\n"]
            response.append(f"Total on page: {len(all_breeds)} breeds\n")

            if page > 0:
                response.append(f"Previous page: breeds {page - 1} {limit}")

            if len(all_breeds) == limit:
                response.append(f"Next page: breeds {page + 1} {limit}")

            response.append("\nCategories:")
            for category, category_breeds in categories.items():
                response.append(f"• {category}: {len(category_breeds)} breeds")

            response.append("\nSample breeds:")
            for breed in all_breeds[:5]:
                breed_name = breed.get('name', 'Unknown').title()
                origin = breed.get('origin', 'Unknown')
                temperament = breed.get('temperament', '').split(',')[0]
                response.append(f"• {breed_name} ({origin}) - {temperament}")

            if len(all_breeds) > 5:
                response.append(f"\n... and {len(all_breeds) - 5} more")

            response.append(f"\nTry: search [name] or images [breed_id]")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'search' in last_message.lower():
            query = last_message.lower().replace('search', '').strip()

            if not query:
                response = ["Please specify search query. Example: search siamese"]
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "\n".join(response)
                    }]
                }

            search_data = cat_component.search_breeds(query)

            if search_data.get('success'):
                breeds = search_data.get('breeds', [])

                response = [f"🐱 Search results for '{query}':\n"]

                for breed in breeds[:10]:
                    breed_name = breed.get('name', 'Unknown').title()
                    breed_id = breed.get('id', 'Unknown')
                    origin = breed.get('origin', 'Unknown')
                    response.append(f"• {breed_name} (ID: {breed_id}) - {origin}")

                if len(breeds) > 10:
                    response.append(f"\n... and {len(breeds) - 10} more")

                response.append(f"\nTotal found: {len(breeds)} breeds")
                response.append(f"\nTry: images {breeds[0].get('id') if breeds else 'breed_id'} to see pictures")
            else:
                response = [f"No breeds found matching '{query}'"]
                response.append("\nTry: breeds to see all available breeds")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'random' in last_message.lower():
            command = last_message.lower().replace('random', '').strip()

            size = None
            mime_types = None

            if command in ['thumb', 'small', 'med', 'full']:
                size = command
            elif 'gif' in command:
                mime_types = 'gif'

            cat_data = cat_component.get_random_cat(size=size, mime_types=mime_types, limit=1)

            if cat_data.get('success'):
                images = cat_data.get('images', [])

                if images:
                    image = images[0]
                    response = [f"🐱 Random Cat Image\n"]

                    image_url = image.get('url', '')
                    if image_url:
                        response.append(f"URL: {image_url}")

                    if image.get('breeds'):
                        breed_info = image['breeds'][0]
                        breed_name = breed_info.get('name', 'Unknown').title()
                        response.append(f"Breed: {breed_name}")

                    response.append(f"\nSize: {image.get('width', '?')}x{image.get('height', '?')}")
                    response.append(f"Type: {image.get('mime_type', 'Unknown')}")

                    response.append("\nCommands:")
                    response.append("• random - Another random cat")
                    response.append("• random thumb/small/med/full - Specific size")
                    response.append("• random gif - Random GIF")
                else:
                    response = ["No images found"]
            else:
                response = [f"Error: {cat_data.get('error', 'Failed to get cat image')}"]

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'images' in last_message.lower():
            command = last_message.lower().replace('images', '').strip()

            if not command:
                response = ["Please specify a breed ID. Example: images pers"]
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "\n".join(response)
                    }]
                }

            cat_data = cat_component.get_breed_images(command, 3)

            if cat_data.get('success'):
                images = cat_data.get('images', [])
                breed_id = command

                response = [f"🐱 Images of Breed ID: {breed_id}\n"]

                for i, img in enumerate(images[:3], 1):
                    if isinstance(img, dict) and 'url' in img:
                        response.append(f"{i}. {img['url']}")

                response.append(f"\nTotal found: {len(images)} images")
                response.append(f"\nTry: search {breed_id} to learn more about this breed")
            else:
                response = [f"Error: {cat_data.get('error', 'Breed not found')}"]
                response.append("\nTry: breeds to see available breeds")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'upload' in last_message.lower():
            file_path = last_message.lower().replace('upload', '').strip()

            if not file_path:
                response = ["Please specify file path. Example: upload /photos/mycat.jpg"]
                return {
                    "messages": messages + [{
                        "role": "assistant",
                        "content": "\n".join(response)
                    }]
                }

            upload_data = cat_component.upload_image(file_path)

            if upload_data.get('success'):
                upload_info = upload_data.get('upload', {})

                response = [f"🐱 Image Upload Successful!\n"]
                response.append(f"Image ID: {upload_info.get('id', 'Unknown')}")
                response.append(f"URL: {upload_info.get('url', 'Unknown')}")

                if upload_info.get('width') and upload_info.get('height'):
                    response.append(f"Size: {upload_info['width']}x{upload_info['height']}")

                response.append(f"\nStatus: {'Approved' if upload_info.get('approved') else 'Pending'}")

                response.append("\nCommands:")
                response.append(f"• favourite {upload_info.get('id')} - Add to favourites")
                response.append(f"• vote {upload_info.get('id')} 1 - Upvote your image")
            else:
                response = [f"Upload failed: {upload_data.get('error', 'Unknown error')}"]
                response.append("\nMake sure the file exists and is a valid image.")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'favourites' in last_message.lower() or 'favourite' in last_message.lower():
            command = last_message.lower()

            if 'favourite' in command and command != 'favourites':
                parts = command.replace('favourite', '').strip().split()
                if parts:
                    image_id = parts[0]
                    favourite_data = cat_component.add_favourite(image_id)

                    if favourite_data.get('success'):
                        response = [f"❤️ Added to favourites!"]
                        response.append(f"Favourite ID: {favourite_data.get('favourite', {}).get('id', 'Unknown')}")
                    else:
                        response = [f"Error: {favourite_data.get('error', 'Failed to add favourite')}"]
                else:
                    response = ["Please specify image ID. Example: favourite abc123"]
            else:
                favourites_data = cat_component.get_favourites()

                if favourites_data.get('success'):
                    favourites = favourites_data.get('favourites', [])

                    if favourites:
                        response = [f"❤️ Your Favourites\n"]

                        for fav in favourites[:5]:
                            fav_id = fav.get('id', 'Unknown')
                            image_id = fav.get('image_id', 'Unknown')
                            created_at = fav.get('created_at', 'Unknown')[:10]
                            response.append(f"• ID: {fav_id} - Image: {image_id} - Added: {created_at}")

                        if len(favourites) > 5:
                            response.append(f"\n... and {len(favourites) - 5} more")

                        response.append(f"\nTotal: {len(favourites)} favourites")
                    else:
                        response = ["You have no favourites yet."]
                        response.append("\nTry: favourite [image_id] to add one")
                else:
                    response = [f"Error: {favourites_data.get('error', 'Failed to get favourites')}"]

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'vote' in last_message.lower():
            parts = last_message.lower().replace('vote', '').strip().split()

            if len(parts) >= 2:
                image_id = parts[0]
                try:
                    value = int(parts[1])
                    if value not in [0, 1]:
                        value = 1
                except:
                    value = 1

                vote_data = cat_component.add_vote(image_id, value)

                if vote_data.get('success'):
                    response = [f"🗳️ Vote recorded!"]
                    response.append(f"Vote ID: {vote_data.get('vote', {}).get('id', 'Unknown')}")
                    response.append(f"Image: {image_id}")
                    response.append(f"Value: {'👍 Up' if value == 1 else '👎 Down'}")
                else:
                    response = [f"Error: {vote_data.get('error', 'Failed to record vote')}"]
            elif len(parts) == 0:
                votes_data = cat_component.get_votes()

                if votes_data.get('success'):
                    votes = votes_data.get('votes', [])

                    if votes:
                        response = [f"🗳️ Your Votes\n"]

                        for vote in votes[:5]:
                            vote_id = vote.get('id', 'Unknown')
                            image_id = vote.get('image_id', 'Unknown')
                            value = vote.get('value', 0)
                            response.append(f"• ID: {vote_id} - Image: {image_id} - Vote: {'👍' if value == 1 else '👎'}")

                        if len(votes) > 5:
                            response.append(f"\n... and {len(votes) - 5} more")

                        response.append(f"\nTotal: {len(votes)} votes")
                    else:
                        response = ["You have no votes yet."]
                        response.append("\nTry: vote [image_id] [1/0] to vote")
                else:
                    response = [f"Error: {votes_data.get('error', 'Failed to get votes')}"]
            else:
                response = ["Please specify image ID and vote value (1 for up, 0 for down)."]
                response.append("Example: vote abc123 1")

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'facts' in last_message.lower():
            command = last_message.lower().replace('facts', '').strip()

            if command:
                parts = command.split()
                breed_id = parts[0]
                limit = 3

                if len(parts) > 1:
                    try:
                        limit = int(parts[1])
                    except:
                        pass

                facts_data = cat_component.get_breed_facts(breed_id, limit)

                if facts_data.get('success'):
                    facts = facts_data.get('facts', [])

                    if facts:
                        response = [f"📚 Facts about Breed: {breed_id}\n"]

                        for fact in facts:
                            fact_text = fact.get('fact', '')
                            title = fact.get('title', '')
                            if title:
                                response.append(f"• {title}: {fact_text}")
                            else:
                                response.append(f"• {fact_text}")

                        response.append(f"\nTotal: {len(facts)} facts")
                    else:
                        response = [f"No facts found for breed: {breed_id}"]
                else:
                    response = [f"Error: {facts_data.get('error', 'Failed to get facts')}"]
            else:
                facts_data = cat_component.get_facts(3)

                if facts_data.get('success'):
                    facts = facts_data.get('facts', [])

                    if facts:
                        response = ["📚 Random Cat Facts\n"]

                        for i, fact in enumerate(facts, 1):
                            fact_text = fact.get('fact', '')
                            breed_id = fact.get('breed_id', '')
                            if breed_id:
                                response.append(f"{i}. ({breed_id}) {fact_text}")
                            else:
                                response.append(f"{i}. {fact_text}")

                        response.append(f"\nTry: facts [breed_id] for breed-specific facts")
                    else:
                        response = ["No facts found."]
                else:
                    response = [f"Error: {facts_data.get('error', 'Failed to get facts')}"]

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'categories' in last_message.lower():
            categories_data = cat_component.get_categories()

            if categories_data.get('success'):
                categories = categories_data.get('categories', [])

                response = ["📂 Image Categories\n"]

                for cat in categories:
                    cat_id = cat.get('id', 'N/A')
                    cat_name = cat.get('name', 'Unnamed')
                    response.append(f"• ID {cat_id}: {cat_name}")

                response.append(f"\nTotal: {len(categories)} categories")
                response.append("\nUse category IDs when searching for images")
            else:
                response = [f"Error: {categories_data.get('error', 'Failed to get categories')}"]

            return {
                "messages": messages + [{
                    "role": "assistant",
                    "content": "\n".join(response)
                }]
            }

        elif 'myimages' in last_message.lower() or 'my images' in last_message.lower():
            images_data = cat_component.get_user_images(limit=5)

            if images_data.get('success'):
                images = images_data.get('images', [])

                if images:
                    response = ["📷 Your Uploaded Images\n"]

                    for img in images[:5]:
                        img_id = img.get('id', 'Unknown')
                        filename = img.get('original_filename', 'Unknown')
                        status = "Approved" if img.get('approved') else "Pending"
                        response.append(f"• {img_id}: {filename} ({status})")

                    if len(images) > 5:
                        response.append(f"\n... and {len(images) - 5} more")

                    response.append(f"\nTotal: {len(images)} images")
                    response.append("\nTry: upload [path] to add more images")
                else:
                    response = ["You haven't uploaded any images yet."]
                    response.append("\nTry: upload [file_path] to upload your first image")
            else:
                response = [f"Error: {images_data.get('error', 'Failed to get your images')}"]

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
                    "content": f"🐱 I didn't understand that command.\n\nTry: help for available commands or random for a cat picture!"
                }]
            }

    except Exception as e:
        print(f"Error in catapi_chat_skill: {e}")
        return {
            "messages": messages + [{
                "role": "assistant",
                "content": f"Error: {str(e)}"
            }]
        }
