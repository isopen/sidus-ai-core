import requests
import json
import time
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import quote, urljoin

@dataclass
class Author:
    key: str
    name: str
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    bio: Optional[Union[str, Dict]] = None
    photos: List[str] = field(default_factory=list)
    alternate_names: List[str] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    personal_name: Optional[str] = None
    title: Optional[str] = None
    remote_ids: Dict[str, str] = field(default_factory=dict)
    wikipedia: Optional[str] = None
    type: Dict[str, str] = field(default_factory=dict)

@dataclass
class Book:
    key: str
    title: str
    authors: List[Dict[str, str]] = field(default_factory=list)
    publish_date: Optional[str] = None
    publishers: List[str] = field(default_factory=list)
    isbn_10: List[str] = field(default_factory=list)
    isbn_13: List[str] = field(default_factory=list)
    number_of_pages: Optional[int] = None
    covers: List[int] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    description: Optional[Union[str, Dict]] = None
    first_sentence: Optional[Union[str, Dict]] = None
    works: List[str] = field(default_factory=list)
    type: Dict[str, str] = field(default_factory=dict)
    created: Optional[Dict] = None
    last_modified: Optional[Dict] = None
    latest_revision: Optional[int] = None
    revision: Optional[int] = None
    identifiers: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class Work:
    key: str
    title: str
    authors: List[Dict[str, str]] = field(default_factory=list)
    covers: List[int] = field(default_factory=list)
    subject_places: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    subject_people: List[str] = field(default_factory=list)
    description: Optional[Union[str, Dict]] = None
    first_publish_date: Optional[str] = None
    type: Dict[str, str] = field(default_factory=dict)

@dataclass
class SearchResult:
    key: str
    title: str
    author_name: List[str] = field(default_factory=list)
    publish_year: List[int] = field(default_factory=list)
    isbn: List[str] = field(default_factory=list)
    cover_i: Optional[int] = None
    edition_count: int = 0
    first_publish_year: Optional[int] = None
    has_fulltext: bool = False
    language: List[str] = field(default_factory=list)
    author_key: List[str] = field(default_factory=list)
    type: str = "work"

class OpenLibraryClient:
    def __init__(self, rate_limit_delay: float = 0.2):
        self.base_url = "https://openlibrary.org"
        self.covers_url = "https://covers.openlibrary.org"
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SidusAI-OpenLibrary/1.0',
            'Accept': 'application/json'
        })

    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        self._rate_limit()

        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            elif response.status_code == 429:
                time.sleep(2)
                return self._make_request(endpoint, params)
            else:
                return None

        except Exception:
            return None

    def search_books(self, query: str, limit: int = 10, page: int = 1) -> List[SearchResult]:
        endpoint = "/search.json"
        params = {
            'q': query,
            'limit': limit,
            'page': page,
            'fields': 'key,title,author_name,author_key,publish_year,isbn,cover_i,edition_count,first_publish_year,has_fulltext,language,type'
        }

        data = self._make_request(endpoint, params)
        if not data or 'docs' not in data:
            return []

        results = []
        for doc in data['docs']:
            result = SearchResult(
                key=doc.get('key', ''),
                title=doc.get('title', ''),
                author_name=doc.get('author_name', []),
                author_key=doc.get('author_key', []),
                publish_year=doc.get('publish_year', []),
                isbn=doc.get('isbn', []),
                cover_i=doc.get('cover_i'),
                edition_count=doc.get('edition_count', 0),
                first_publish_year=doc.get('first_publish_year'),
                has_fulltext=doc.get('has_fulltext', False),
                language=doc.get('language', []),
                type=doc.get('type', 'work')
            )
            results.append(result)

        return results

    def search_authors(self, query: str, limit: int = 10) -> List[Dict]:
        endpoint = "/search/authors.json"
        params = {
            'q': query,
            'limit': limit
        }

        data = self._make_request(endpoint, params)
        if not data or 'docs' not in data:
            return []

        return data['docs']

    def get_book(self, key: str) -> Optional[Book]:
        if not key:
            return None

        if isinstance(key, dict):
            if 'key' in key:
                key = key['key']
            else:
                return None

        key = str(key).strip()

        if re.match(r'^\d{10}(\d{3})?$', key.replace('-', '').replace(' ', '')):
            return self.get_book_by_isbn(key)

        if key.startswith('/'):
            key = key[1:]

        if not key.startswith('books/'):
            key = f"books/{key}"

        endpoint = f"/{key}.json"

        data = self._make_request(endpoint)
        if not data:
            return None

        description = data.get('description')
        if isinstance(description, dict):
            description = description.get('value', '')

        first_sentence = data.get('first_sentence')
        if isinstance(first_sentence, dict):
            first_sentence = first_sentence.get('value', '')

        authors = []
        if 'authors' in data:
            for author in data['authors']:
                if isinstance(author, dict):
                    if 'author' in author and isinstance(author['author'], dict):
                        authors.append({
                            'key': author['author'].get('key', ''),
                            'name': author.get('name', '')
                        })
                    elif 'key' in author:
                        authors.append({
                            'key': author.get('key', ''),
                            'name': author.get('name', '')
                        })

        return Book(
            key=data.get('key', ''),
            title=data.get('title', ''),
            authors=authors,
            publish_date=data.get('publish_date'),
            publishers=data.get('publishers', []),
            isbn_10=data.get('isbn_10', []),
            isbn_13=data.get('isbn_13', []),
            number_of_pages=data.get('number_of_pages'),
            covers=data.get('covers', []),
            subjects=data.get('subjects', []),
            description=description,
            first_sentence=first_sentence,
            works=data.get('works', []),
            type=data.get('type', {}),
            created=data.get('created'),
            last_modified=data.get('last_modified'),
            latest_revision=data.get('latest_revision'),
            revision=data.get('revision'),
            identifiers=data.get('identifiers', {})
        )

    def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        if not isbn:
            return None

        isbn_clean = re.sub(r'[-\s]', '', str(isbn))

        endpoint = f"/isbn/{isbn_clean}.json"

        data = self._make_request(endpoint)
        if not data:
            return None

        book_key = data.get('key')
        if not book_key:
            return None

        return self.get_book(book_key)

    def get_author(self, key: str) -> Optional[Author]:
        if not key:
            return None

        if isinstance(key, dict):
            if 'key' in key:
                key = key['key']
            else:
                return None

        key = str(key).strip()

        if key.startswith('/'):
            key = key[1:]

        if not key.startswith('authors/'):
            key = f"authors/{key}"

        endpoint = f"/{key}.json"

        data = self._make_request(endpoint)
        if not data:
            return None

        bio = data.get('bio')
        if isinstance(bio, dict):
            bio = bio.get('value', '')

        photos = []
        if 'photos' in data:
            photos = [f"{self.covers_url}/a/id/{photo}-M.jpg" for photo in data['photos']]

        return Author(
            key=data.get('key', ''),
            name=data.get('name', ''),
            birth_date=data.get('birth_date'),
            death_date=data.get('death_date'),
            bio=bio,
            photos=photos,
            alternate_names=data.get('alternate_names', []),
            links=data.get('links', []),
            personal_name=data.get('personal_name'),
            title=data.get('title'),
            remote_ids=data.get('remote_ids', {}),
            wikipedia=data.get('wikipedia'),
            type=data.get('type', {})
        )

    def get_work(self, key: str) -> Optional[Work]:
        if not key:
            return None

        if isinstance(key, dict):
            if 'key' in key:
                key = key['key']
            else:
                return None

        key = str(key).strip()

        if key.startswith('/'):
            key = key[1:]

        if not key.startswith('works/'):
            key = f"works/{key}"

        endpoint = f"/{key}.json"

        data = self._make_request(endpoint)
        if not data:
            return None

        description = data.get('description')
        if isinstance(description, dict):
            description = description.get('value', '')

        return Work(
            key=data.get('key', ''),
            title=data.get('title', ''),
            authors=data.get('authors', []),
            covers=data.get('covers', []),
            subject_places=data.get('subject_places', []),
            subjects=data.get('subjects', []),
            subject_people=data.get('subject_people', []),
            description=description,
            first_publish_date=data.get('first_publish_date'),
            type=data.get('type', {})
        )

    def get_work_editions(self, work_key: str, limit: int = 50) -> List[Dict]:
        if not work_key:
            return []

        if isinstance(work_key, dict):
            if 'key' in work_key:
                work_key = work_key['key']
            else:
                return []

        work_key = str(work_key).strip()

        if work_key.startswith('/'):
            work_key = work_key[1:]

        if not work_key.startswith('works/'):
            work_key = f"works/{work_key}"

        endpoint = f"/{work_key}/editions.json"
        params = {'limit': limit}

        data = self._make_request(endpoint, params)
        if not data or 'entries' not in data:
            return []

        return data['entries']

    def get_book_cover(self, cover_id: int, size: str = "M") -> Optional[str]:
        if not cover_id:
            return None

        sizes = {
            "S": "-S.jpg",
            "M": "-M.jpg",
            "L": "-L.jpg",
        }

        size_suffix = sizes.get(size.upper(), "-M.jpg")
        return f"{self.covers_url}/b/id/{cover_id}{size_suffix}"

    def get_author_photo(self, photo_id: int, size: str = "M") -> Optional[str]:
        if not photo_id:
            return None

        sizes = {
            "S": "-S.jpg",
            "M": "-M.jpg",
            "L": "-L.jpg",
        }

        size_suffix = sizes.get(size.upper(), "-M.jpg")
        return f"{self.covers_url}/a/id/{photo_id}{size_suffix}"

    def get_subject_books(self, subject: str, limit: int = 20) -> List[Dict]:
        subject_slug = quote(subject.lower().replace(' ', '_'))
        endpoint = f"/subjects/{subject_slug}.json"
        params = {'limit': limit}

        data = self._make_request(endpoint, params)
        if not data or 'works' not in data:
            return []

        return data['works']

    def get_author_by_name(self, name: str) -> Optional[Author]:
        authors = self.search_authors(name, limit=1)
        if not authors:
            return None

        author_data = authors[0]
        author_key = author_data.get('key', '')
        if author_key:
            return self.get_author(author_key)

        return None

    def test_connection(self) -> bool:
        try:
            endpoint = "/search.json"
            params = {'q': 'test', 'limit': 1}
            response = self.session.get(
                urljoin(self.base_url, endpoint),
                params=params,
                timeout=10
            )

            return response.status_code == 200

        except Exception:
            return False
