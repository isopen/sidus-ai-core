from sidusai.core.plugin import ChatAgentValue, AgentValue
from typing import Dict, Any, List
from datetime import datetime
import re

class BookValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class AuthorValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class SearchResultValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class WorkValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

def search_books_skill(context: Dict[str, Any]) -> SearchResultValue:
    print("🔍 Starting search_books_skill...")

    query = context.get('query', '').strip()
    limit = min(int(context.get('limit', 10)), 100)
    page = max(int(context.get('page', 1)), 1)

    if not query:
        result = {"error": "No search query provided", "success": False}
        return SearchResultValue(result)

    try:
        client = context.get('openlibrary_component')
        if not client:
            result = {"error": "OpenLibrary client not available", "success": False}
            return SearchResultValue(result)

        print(f"📚 Searching books for: '{query}' (limit: {limit}, page: {page})")

        results = client.search_books(query, limit, page)

        if not results:
            result = {
                "success": True,
                "query": query,
                "results": [],
                "count": 0,
                "page": page,
                "has_more": False,
                "timestamp": datetime.now().isoformat()
            }
            return SearchResultValue(result)

        formatted_results = []
        for i, result in enumerate(results, 1):
            cover_url = None
            if result.cover_i:
                cover_url = client.get_book_cover(result.cover_i, "M")

            authors_info = []
            for author_name, author_key in zip(result.author_name, result.author_key):
                authors_info.append({
                    "name": author_name,
                    "key": author_key
                })

            formatted_results.append({
                "rank": i,
                "key": result.key,
                "title": result.title,
                "authors": authors_info,
                "author_names": result.author_name,
                "publish_years": result.publish_year,
                "first_publish_year": result.first_publish_year,
                "isbns": result.isbn[:3],
                "cover_url": cover_url,
                "edition_count": result.edition_count,
                "has_fulltext": result.has_fulltext,
                "languages": result.language,
                "type": result.type
            })

        has_more = len(results) >= limit

        result = {
            "success": True,
            "query": query,
            "page": page,
            "results": formatted_results,
            "count": len(formatted_results),
            "has_more": has_more,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Found {len(formatted_results)} results for '{query}'")
        return SearchResultValue(result)

    except Exception as e:
        print(f"❌ Error in search_books_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to search books: {str(e)}", "success": False}
        return SearchResultValue(result)

def search_authors_skill(context: Dict[str, Any]) -> AuthorValue:
    print("🔍 Starting search_authors_skill...")

    query = context.get('query', '').strip()
    limit = min(int(context.get('limit', 10)), 100)

    if not query:
        result = {"error": "No author search query provided", "success": False}
        return AuthorValue(result)

    try:
        client = context.get('openlibrary_component')
        if not client:
            result = {"error": "OpenLibrary client not available", "success": False}
            return AuthorValue(result)

        print(f"✍️ Searching authors for: '{query}'")

        authors_data = client.search_authors(query, limit)

        if not authors_data:
            result = {
                "success": True,
                "query": query,
                "authors": [],
                "count": 0,
                "timestamp": datetime.now().isoformat()
            }
            return AuthorValue(result)

        formatted_authors = []
        for i, author_data in enumerate(authors_data, 1):
            author_key = author_data.get('key', '')
            author = None

            if author_key:
                author = client.get_author(author_key)

            if author:
                photo_urls = []
                if author.photos:
                    photo_urls = author.photos[:3]

                formatted_authors.append({
                    "rank": i,
                    "key": author.key,
                    "name": author.name,
                    "birth_date": author.birth_date,
                    "death_date": author.death_date,
                    "bio": author.bio[:300] + "..." if author.bio and len(author.bio) > 300 else author.bio,
                    "photos": photo_urls,
                    "alternate_names": author.alternate_names[:5],
                    "work_count": author_data.get('work_count', 0),
                    "top_work": author_data.get('top_work', '')
                })
            else:
                # Fallback to search data
                formatted_authors.append({
                    "rank": i,
                    "key": author_data.get('key', ''),
                    "name": author_data.get('name', ''),
                    "birth_date": author_data.get('birth_date'),
                    "death_date": author_data.get('death_date'),
                    "bio": '',
                    "photos": [],
                    "alternate_names": author_data.get('alternate_names', []),
                    "work_count": author_data.get('work_count', 0),
                    "top_work": author_data.get('top_work', '')
                })

        result = {
            "success": True,
            "query": query,
            "authors": formatted_authors,
            "count": len(formatted_authors),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Found {len(formatted_authors)} authors for '{query}'")
        return AuthorValue(result)

    except Exception as e:
        print(f"❌ Error in search_authors_skill: {e}")
        result = {"error": f"Failed to search authors: {str(e)}", "success": False}
        return AuthorValue(result)

def get_book_details_skill(context: Dict[str, Any]) -> BookValue:
    print("📖 Starting get_book_details_skill...")

    identifier = context.get('book_key', '').strip()
    if not identifier:
        result = {"error": "No book identifier provided", "success": False}
        return BookValue(result)

    try:
        client = context.get('openlibrary_component')
        if not client:
            result = {"error": "OpenLibrary client not available", "success": False}
            return BookValue(result)

        print(f"📚 Getting book details for: {identifier}")

        book = None

        if re.match(r'^\d{10}(\d{3})?$', identifier.replace('-', '').replace(' ', '')):
            print(f"🔍 Looks like an ISBN, searching by ISBN...")
            book = client.get_book_by_isbn(identifier)

        elif re.match(r'^OL\d+[A-Z]$', identifier.upper()):
            print(f"🔍 Looks like an OLID, searching by OLID...")
            book = client.get_book_by_olid(identifier)

        else:
            print(f"🔍 Treating as book key...")
            book = client.get_book(identifier)

        if not book:
            result = {"error": f"Book '{identifier}' not found", "success": False}
            return BookValue(result)

        cover_urls = []
        if book.covers:
            for cover_id in book.covers[:3]:
                cover_url = client.get_book_cover(cover_id, "L")
                if cover_url:
                    cover_urls.append(cover_url)

        work_info = None
        if book.works:
            work_key = book.works[0] if isinstance(book.works, list) else book.works
            if work_key:
                work = client.get_work(work_key)
                if work:
                    work_info = {
                        "key": work.key,
                        "title": work.title,
                        "first_publish_date": work.first_publish_date,
                        "subjects": work.subjects[:10],
                        "subject_people": work.subject_people[:5]
                    }

        result = {
            "success": True,
            "book": {
                "key": book.key,
                "title": book.title,
                "authors": book.authors,
                "publish_date": book.publish_date,
                "publishers": book.publishers,
                "isbn_10": book.isbn_10,
                "isbn_13": book.isbn_13,
                "number_of_pages": book.number_of_pages,
                "covers": cover_urls,
                "subjects": book.subjects[:10],
                "description": str(book.description)[:500] + "..." if book.description and len(str(book.description)) > 500 else str(book.description),
                "first_sentence": str(book.first_sentence) if book.first_sentence else None,
                "works": book.works,
                "identifiers": book.identifiers,
                "work_info": work_info
            },
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Book details retrieved: {book.title}")
        return BookValue(result)

    except Exception as e:
        print(f"❌ Error in get_book_details_skill: {e}")
        result = {"error": f"Failed to get book details: {str(e)}", "success": False}
        return BookValue(result)

def get_author_info_skill(context: Dict[str, Any]) -> AuthorValue:
    """Get author details by key or name"""
    print("✍️ Starting get_author_info_skill...")

    identifier = context.get('author_key', '').strip()
    if not identifier:
        result = {"error": "No author identifier provided", "success": False}
        return AuthorValue(result)

    try:
        client = context.get('openlibrary_component')
        if not client:
            result = {"error": "OpenLibrary client not available", "success": False}
            return AuthorValue(result)

        print(f"🔍 Getting author info for: {identifier}")

        author = None

        if re.match(r'^OL\d+[A-Z]$', identifier.upper()):
            print(f"🔍 Looks like an author key...")
            author = client.get_author(identifier)
        else:
            print(f"🔍 Treating as author name, searching...")
            author = client.get_author_by_name(identifier)

        if not author:
            result = {"error": f"Author '{identifier}' not found", "success": False}
            return AuthorValue(result)

        author_books = []
        if author.key:
            books = client.get_books_by_author(author.key, limit=5)
            for i, book in enumerate(books[:5], 1):
                author_books.append({
                    "rank": i,
                    "key": book.key,
                    "title": book.title,
                    "publish_years": book.publish_year
                })

        photo_urls = []
        if author.photos:
            photo_urls = author.photos[:3]

        result = {
            "success": True,
            "author": {
                "key": author.key,
                "name": author.name,
                "birth_date": author.birth_date,
                "death_date": author.death_date,
                "bio": str(author.bio)[:500] + "..." if author.bio and len(str(author.bio)) > 500 else str(author.bio),
                "photos": photo_urls,
                "alternate_names": author.alternate_names[:5],
                "personal_name": author.personal_name,
                "wikipedia": author.wikipedia,
                "remote_ids": author.remote_ids,
                "books": author_books,
                "book_count": len(author_books)
            },
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Author info retrieved: {author.name}")
        return AuthorValue(result)

    except Exception as e:
        print(f"❌ Error in get_author_info_skill: {e}")
        result = {"error": f"Failed to get author info: {str(e)}", "success": False}
        return AuthorValue(result)

def get_work_details_skill(context: Dict[str, Any]) -> WorkValue:
    print("📚 Starting get_work_details_skill...")

    work_key = context.get('work_key', '').strip()
    if not work_key:
        result = {"error": "No work key provided", "success": False}
        return WorkValue(result)

    try:
        client = context.get('openlibrary_component')
        if not client:
            result = {"error": "OpenLibrary client not available", "success": False}
            return WorkValue(result)

        print(f"🔍 Getting work details for: {work_key}")

        work = client.get_work(work_key)

        if not work:
            result = {"error": f"Work '{work_key}' not found", "success": False}
            return WorkValue(result)

        editions = client.get_work_editions(work_key, limit=5)
        edition_count = len(editions) if editions else 0

        cover_urls = []
        if work.covers:
            for cover_id in work.covers[:3]:
                cover_url = client.get_book_cover(cover_id, "M")
                if cover_url:
                    cover_urls.append(cover_url)

        result = {
            "success": True,
            "work": {
                "key": work.key,
                "title": work.title,
                "authors": work.authors,
                "first_publish_date": work.first_publish_date,
                "subjects": work.subjects[:10],
                "subject_people": work.subject_people[:5],
                "subject_places": work.subject_places[:5],
                "description": str(work.description)[:500] + "..." if work.description and len(str(work.description)) > 500 else str(work.description),
                "covers": cover_urls,
                "edition_count": edition_count,
                "editions_sample": editions[:3] if editions else []
            },
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Work details retrieved: {work.title}")
        return WorkValue(result)

    except Exception as e:
        print(f"❌ Error in get_work_details_skill: {e}")
        result = {"error": f"Failed to get work details: {str(e)}", "success": False}
        return WorkValue(result)

def get_books_by_subject_skill(context: Dict[str, Any]) -> SearchResultValue:
    print("🏷️ Starting get_books_by_subject_skill...")

    subject = context.get('subject', '').strip()
    limit = min(int(context.get('limit', 20)), 100)

    if not subject:
        result = {"error": "No subject provided", "success": False}
        return SearchResultValue(result)

    try:
        client = context.get('openlibrary_component')
        if not client:
            result = {"error": "OpenLibrary client not available", "success": False}
            return SearchResultValue(result)

        print(f"📚 Getting books on subject: '{subject}'")

        works = client.get_subject_books(subject, limit)

        if not works:
            result = {
                "success": True,
                "subject": subject,
                "results": [],
                "count": 0,
                "timestamp": datetime.now().isoformat()
            }
            return SearchResultValue(result)

        formatted_results = []
        for i, work in enumerate(works[:limit], 1):
            cover_url = None
            if work.get('cover_id'):
                cover_url = client.get_book_cover(work['cover_id'], "M")

            formatted_results.append({
                "rank": i,
                "key": work.get('key', ''),
                "title": work.get('title', ''),
                "authors": [author.get('name', '') for author in work.get('authors', [])],
                "cover_url": cover_url,
                "edition_count": work.get('edition_count', 0),
                "first_publish_year": work.get('first_publish_year')
            })

        result = {
            "success": True,
            "subject": subject,
            "results": formatted_results,
            "count": len(formatted_results),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Found {len(formatted_results)} books on '{subject}'")
        return SearchResultValue(result)

    except Exception as e:
        print(f"❌ Error in get_books_by_subject_skill: {e}")
        result = {"error": f"Failed to get books by subject: {str(e)}", "success": False}
        return SearchResultValue(result)

def get_work_editions_skill(context: Dict[str, Any]) -> BookValue:
    print("📚 Starting get_work_editions_skill...")

    work_key = context.get('work_key', '').strip()
    limit = min(int(context.get('limit', 20)), 100)

    if not work_key:
        result = {"error": "No work key provided", "success": False}
        return BookValue(result)

    try:
        client = context.get('openlibrary_component')
        if not client:
            result = {"error": "OpenLibrary client not available", "success": False}
            return BookValue(result)

        print(f"🔍 Getting editions for work: {work_key}")

        editions = client.get_work_editions(work_key, limit)

        if not editions:
            result = {"error": f"No editions found for work '{work_key}'", "success": False}
            return BookValue(result)

        formatted_editions = []
        for i, edition in enumerate(editions[:limit], 1):
            cover_urls = []
            if edition.get('covers'):
                for cover_id in edition['covers'][:2]:
                    cover_url = client.get_book_cover(cover_id, "M")
                    if cover_url:
                        cover_urls.append(cover_url)

            formatted_editions.append({
                "rank": i,
                "key": edition.get('key', ''),
                "title": edition.get('title', ''),
                "publish_date": edition.get('publish_date'),
                "publishers": edition.get('publishers', []),
                "isbn_10": edition.get('isbn_10', [])[:2],
                "isbn_13": edition.get('isbn_13', [])[:2],
                "number_of_pages": edition.get('number_of_pages'),
                "covers": cover_urls,
                "languages": edition.get('languages', []),
                "physical_format": edition.get('physical_format')
            })

        result = {
            "success": True,
            "work_key": work_key,
            "editions": formatted_editions,
            "count": len(formatted_editions),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Found {len(formatted_editions)} editions")
        return BookValue(result)

    except Exception as e:
        print(f"❌ Error in get_work_editions_skill: {e}")
        result = {"error": f"Failed to get work editions: {str(e)}", "success": False}
        return BookValue(result)

def openlibrary_chat_skill(chat: ChatAgentValue) -> ChatAgentValue:
    print("💬 Starting openlibrary_chat_skill...")

    try:
        if not chat.messages:
            chat.append_assistant(
                "📚 OpenLibrary Assistant (Official API)\n\n"
                "I provide access to the OpenLibrary database with millions of books.\n\n"
                "🔍 Search Commands:\n"
                "• search books <query> - Search books by title/author\n"
                "• search authors <name> - Search for authors\n"
                "• subject <topic> - Get books by subject\n\n"
                "📖 Get Information:\n"
                "• book <key/isbn> - Get book details (e.g., OL7353617M or 9780545010221)\n"
                "• author <key/name> - Get author info (e.g., OL23919A or J.K. Rowling)\n"
                "• work <key> - Get work details (e.g., OL82563W)\n"
                "• editions <work_key> - Get work editions\n\n"
                "💡 Examples:\n"
                "• search books harry potter\n"
                "• search authors stephen king\n"
                "• subject science fiction\n"
                "• book OL7353617M\n"
                "• author J.K. Rowling\n"
                "• work OL82563W\n"
                "• editions OL82563W\n\n"
                "Type help to see this message again."
            )
            return chat

        last_message = chat.messages[-1]['content'].strip()

        client = chat.context.get('openlibrary_component') if hasattr(chat, 'context') else None

        if not client:
            chat.append_assistant("❌ OpenLibrary client not available")
            return chat

        if last_message.lower() == 'help':
            chat.append_assistant(
                "📚 OpenLibrary Assistant Commands\n\n"
                "Search:\n"
                "• search books <query> - Find books\n"
                "• search authors <name> - Find authors\n"
                "• subject <topic> - Books by subject\n\n"
                "Information:\n"
                "• book <key/isbn> - Book details\n"
                "• author <key/name> - Author details\n"
                "• work <key> - Work details\n"
                "• editions <key> - Work editions\n\n"
                "Examples:\n"
                "• search books lord of the rings\n"
                "• book 9780545010221\n"
                "• author Tolkien\n"
                "• subject fantasy"
            )
            return chat

        if last_message.lower().startswith('search books '):
            query = last_message[13:].strip()
            if not query:
                chat.append_assistant("❌ Please provide a search query for books")
                return chat

            context = {'query': query, 'limit': 10, 'openlibrary_component': client}
            result = search_books_skill(context)
            data = result.value

            if data.get('success'):
                if data['results']:
                    response = [f"🔍 Books found for '{query}'\n"]
                    for book in data['results']:
                        authors = ", ".join(book['author_names']) if book['author_names'] else "Unknown"
                        response.append(f"{book['rank']}. {book['title']}")
                        response.append(f"   👤 {authors}")
                        if book['first_publish_year']:
                            response.append(f"   📅 First published: {book['first_publish_year']}")
                        response.append(f"   📚 Editions: {book['edition_count']}")
                        response.append("")

                    response.append(f"📊 Total: {data['count']} books found")
                    response.append(f"💡 Use book <key> for details")

                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"🔍 No books found for '{query}'")
            else:
                chat.append_assistant(f"❌ Search failed: {data.get('error', 'Unknown error')}")

        elif last_message.lower().startswith('search authors '):
            query = last_message[15:].strip()
            if not query:
                chat.append_assistant("❌ Please provide an author name to search")
                return chat

            context = {'query': query, 'limit': 10, 'openlibrary_component': client}
            result = search_authors_skill(context)
            data = result.value

            if data.get('success'):
                if data['authors']:
                    response = [f"✍️ Authors found for '{query}'\n"]
                    for author in data['authors'][:5]:
                        response.append(f"{author['rank']}. {author['name']}")
                        if author['birth_date']:
                            dates = author['birth_date']
                            if author['death_date']:
                                dates += f" - {author['death_date']}"
                            response.append(f"   📅 {dates}")
                        if author['top_work']:
                            response.append(f"   📖 Known for: {author['top_work']}")
                        response.append(f"   📚 Works: {author['work_count']}")
                        response.append("")

                    response.append(f"📊 Total: {data['count']} authors found")
                    response.append(f"💡 Use author <name/key> for details")

                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"🔍 No authors found for '{query}'")
            else:
                chat.append_assistant(f"❌ Search failed: {data.get('error', 'Unknown error')}")

        elif last_message.lower().startswith('subject '):
            subject = last_message[8:].strip()
            if not subject:
                chat.append_assistant("❌ Please provide a subject")
                return chat

            context = {'subject': subject, 'limit': 10, 'openlibrary_component': client}
            result = get_books_by_subject_skill(context)
            data = result.value

            if data.get('success'):
                if data['results']:
                    response = [f"🏷️ Books on '{subject}'\n"]
                    for book in data['results'][:5]:
                        authors = ", ".join(book['authors']) if book['authors'] else "Unknown"
                        response.append(f"{book['rank']}. {book['title']}")
                        response.append(f"   👤 {authors}")
                        if book['first_publish_year']:
                            response.append(f"   📅 First published: {book['first_publish_year']}")
                        response.append("")

                    response.append(f"📊 Total: {data['count']} books")
                    response.append(f"💡 Use book <key> for details")

                    chat.append_assistant("\n".join(response))
                else:
                    chat.append_assistant(f"🔍 No books found on '{subject}'")
            else:
                chat.append_assistant(f"❌ Failed: {data.get('error', 'Unknown error')}")

        elif last_message.lower().startswith('book '):
            identifier = last_message[5:].strip()
            if not identifier:
                chat.append_assistant("❌ Please provide a book key, ISBN, or OLID")
                return chat

            context = {'book_key': identifier, 'openlibrary_component': client}
            result = get_book_details_skill(context)
            data = result.value

            if data.get('success'):
                book = data['book']
                response = [f"📖 {book['title']}\n"]

                if book['authors']:
                    authors = []
                    for author in book['authors']:
                        if isinstance(author, dict):
                            authors.append(f"{author.get('name', 'Unknown')}")
                        else:
                            authors.append(str(author))
                    response.append(f"Authors: {', '.join(authors)}")

                if book['publish_date']:
                    response.append(f"Published: {book['publish_date']}")

                if book['publishers']:
                    response.append(f"Publishers: {', '.join(book['publishers'])}")

                if book['number_of_pages']:
                    response.append(f"Pages: {book['number_of_pages']}")

                if book['isbn_10']:
                    response.append(f"ISBN-10: {', '.join(book['isbn_10'][:2])}")

                if book['isbn_13']:
                    response.append(f"ISBN-13: {', '.join(book['isbn_13'][:2])}")

                if book['subjects']:
                    response.append(f"Subjects: {', '.join(book['subjects'][:3])}")

                if book['description']:
                    response.append("\nDescription:")
                    response.append(book['description'])

                if book['covers']:
                    response.append("\nCover Images:")
                    for i, cover_url in enumerate(book['covers'][:2], 1):
                        response.append(f"{i}. {cover_url}")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Book not found: {data.get('error', 'Unknown error')}")

        elif last_message.lower().startswith('author '):
            identifier = last_message[7:].strip()
            if not identifier:
                chat.append_assistant("❌ Please provide an author name or key")
                return chat

            context = {'author_key': identifier, 'openlibrary_component': client}
            result = get_author_info_skill(context)
            data = result.value

            if data.get('success'):
                author = data['author']
                response = [f"✍️ {author['name']}\n"]

                if author['birth_date']:
                    dates = author['birth_date']
                    if author['death_date']:
                        dates += f" - {author['death_date']}"
                    response.append(f"Lifespan: {dates}")

                if author['alternate_names']:
                    response.append(f"Also known as: {', '.join(author['alternate_names'][:3])}")

                if author['bio']:
                    response.append("\nBiography:")
                    response.append(author['bio'])

                if author['wikipedia']:
                    response.append(f"\nWikipedia: {author['wikipedia']}")

                if author['books']:
                    response.append(f"\nTop Books ({author['book_count']}):")
                    for book in author['books'][:3]:
                        response.append(f"• {book['title']}")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Author not found: {data.get('error', 'Unknown error')}")

        elif last_message.lower().startswith('work '):
            work_key = last_message[5:].strip()
            if not work_key:
                chat.append_assistant("❌ Please provide a work key")
                return chat

            context = {'work_key': work_key, 'openlibrary_component': client}
            result = get_work_details_skill(context)
            data = result.value

            if data.get('success'):
                work = data['work']
                response = [f"📚 {work['title']}\n"]

                if work['first_publish_date']:
                    response.append(f"First published: {work['first_publish_date']}")

                if work['authors']:
                    authors = []
                    for author in work['authors']:
                        if isinstance(author, dict):
                            authors.append(f"{author.get('name', 'Unknown')}")
                    response.append(f"Authors: {', '.join(authors)}")

                if work['subjects']:
                    response.append(f"Subjects: {', '.join(work['subjects'][:3])}")

                if work['description']:
                    response.append("\nDescription:")
                    response.append(work['description'])

                response.append(f"\nEditions: {work['edition_count']}")
                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Work not found: {data.get('error', 'Unknown error')}")

        elif last_message.lower().startswith('editions '):
            work_key = last_message[9:].strip()
            if not work_key:
                chat.append_assistant("❌ Please provide a work key")
                return chat

            context = {'work_key': work_key, 'openlibrary_component': client}
            result = get_work_editions_skill(context)
            data = result.value

            if data.get('success'):
                response = [f"📚 Editions for {work_key}\n"]
                response.append(f"Found: {data['count']} editions\n")

                for edition in data['editions'][:5]:
                    response.append(f"{edition['rank']}. {edition['title']}")
                    if edition['publish_date']:
                        response.append(f"   📅 {edition['publish_date']}")
                    if edition['publishers']:
                        response.append(f"   🏢 {', '.join(edition['publishers'])}")
                    if edition['number_of_pages']:
                        response.append(f"   📄 {edition['number_of_pages']} pages")
                    response.append("")

                chat.append_assistant("\n".join(response))
            else:
                chat.append_assistant(f"❌ Failed: {data.get('error', 'Unknown error')}")

        else:
            if len(last_message.split()) <= 3:
                context = {'author_key': last_message, 'openlibrary_component': client}
                result = get_author_info_skill(context)
                if result.value.get('success'):
                    data = result.value
                    author = data['author']
                    response = [f"✍️ {author['name']}\n"]

                    if author['birth_date']:
                        dates = author['birth_date']
                        if author['death_date']:
                            dates += f" - {author['death_date']}"
                        response.append(f"Lifespan: {dates}")

                    if author['bio']:
                        response.append("\nBiography:")
                        response.append(author['bio'][:300] + "...")

                    chat.append_assistant("\n".join(response))
                    return chat

            chat.append_assistant(
                "🤔 I'm not sure what you're looking for.\n\n"
                "Try one of these:\n"
                "• search books <title> - Find books\n"
                "• search authors <name> - Find authors\n"
                "• book <key/isbn> - Get book details\n"
                "• author <name> - Get author info\n"
                "• subject <topic> - Books by subject\n\n"
                "Type help for all commands."
            )

    except Exception as e:
        print(f"❌ Error in openlibrary_chat_skill: {e}")
        import traceback
        traceback.print_exc()
        chat.append_assistant("❌ An error occurred while processing your request")

    return chat
