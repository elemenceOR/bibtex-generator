import requests
from typing import Dict, Optional, Union
from datetime import datetime
import re
from urllib.parse import urlparse

class IEEEBibTeX:
    """
    A library for generating BibTeX entries in IEEE format with DOI and URL lookup capabilities.
    """
    
    def __init__(self):
        self.entry_types = {
            'article': self.create_article,
            'inproceedings': self.create_inproceeding
        }

    def _format_authors(self, authors: str) -> str:
        """Format author names according to BibTeX standards."""
        return " and ".join([author.strip() for author in authors.split(",")])

    def _create_entry(self, entry_type: str, citation_key: str, fields: Dict[str, str]) -> str:
        """Create a BibTeX entry with the given fields."""
        entry = f"@{entry_type}{{{citation_key},\n"
        
        # Add required fields first, then optional ones if they exist
        for key, value in fields.items():
            if value:
                entry += f"  {key} = {{{value}}},\n"
        
        entry = entry.rstrip(",\n") + "\n}"
        return entry

    def extract_doi_from_url(self, url: str) -> Optional[str]:
        """Extract DOI from various publication URLs."""
        # Common DOI patterns
        doi_patterns = [
            r'doi\.org/([^/\s]+/[^/\s]+)',
            r'doi:([^/\s]+/[^/\s]+)',
            r'([0-9]+\.[0-9]+/[^/\s]+)'
        ]
        
        for pattern in doi_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        return None

    def fetch_from_doi(self, doi: str) -> Dict:
        """Fetch publication metadata from CrossRef using DOI."""
        crossref_url = f"https://api.crossref.org/works/{doi}"
        
        try:
            response = requests.get(crossref_url)
            response.raise_for_status()
            data = response.json()['message']
            print(data)
            
            # Extract relevant information
            publication_info = {
                'title': data.get('title', [None])[0],
                'authors': ", ".join([f"{author.get('given', '')} {author.get('family', '')}" 
                                    for author in data.get('author', [])]),
                'year': str(data.get('published-print', {}).get('date-parts', [[None]])[0][0]),
                'doi': doi,
                'type': data.get('type')
            }
            
            # Add type-specific fields
            if data.get('container-title'):
                publication_info['journal'] = data['container-title'][0]
            if data.get('volume'):
                publication_info['volume'] = data['volume']
            if data.get('issue'):
                publication_info['number'] = data['issue']
            if data.get('page'):
                publication_info['pages'] = data['page']
            
            return publication_info
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching DOI information: {str(e)}")

    def generate_from_identifier(self, identifier: str) -> str:
        """Generate BibTeX entry from DOI or URL."""
        # Check if input is URL or DOI
        if identifier.startswith('http'):
            doi = self.extract_doi_from_url(identifier)
            if not doi:
                raise ValueError("Could not extract DOI from URL")
        else:
            doi = identifier

        # Fetch metadata
        pub_info = self.fetch_from_doi(doi)
        
        # Generate citation key
        first_author = pub_info['authors'].split(',')[0].split()[-1].lower()
        citation_key = f"{first_author}{pub_info['year']}{pub_info['title'].split()[0].lower()}"
        
        # Map CrossRef type to BibTeX type
        type_mapping = {
            'journal-article': 'article',
            'proceedings-article': 'inproceedings',
            #'book': 'book',
            #'report': 'techreport'
        }
        
        entry_type = type_mapping.get(pub_info['type'], 'article')
        
        # Create appropriate entry based on type
        if entry_type == 'article':
            return self.create_article(
                citation_key=citation_key,
                title=pub_info['title'],
                authors=pub_info['authors'],
                journal=pub_info.get('journal', ''),
                year=pub_info['year'],
                volume=pub_info.get('volume'),
                number=pub_info.get('number'),
                pages=pub_info.get('pages'),
                doi=pub_info['doi']
            )
        if entry_type == 'inproceedings':
            return self.create_inproceeding(
                citation_key=citation_key,
                authors=pub_info['authors'],
                title=pub_info['title'],
                booktitle=pub_info.get('container-title'),
                year=pub_info['year'],
                pages=pub_info.get['pages'],
                location=pub_info.get['location'],
                doi=pub_info['doi']
            )
        return self._create_entry(entry_type, citation_key, pub_info)

    def create_article(self, citation_key: str, title: str, authors: str, journal: str, 
                        year: str, volume: Optional[str] = None, number: Optional[str] = None,
                        pages: Optional[str] = None, doi: Optional[str] = None) -> str:
        """Generate a BibTeX entry for a journal article."""
        fields = {
            "author": self._format_authors(authors),
            "title": title,
            "journal": journal,
            "year": year,
            "volume": volume,
            "number": number,
            "pages": pages,
            "doi": doi
        }
        return self._create_entry("article", citation_key, fields)
    
    def create_inproceeding(self, citation_key: str, title: str, authors: str, 
                        booktitle: str, year: str, pages: Optional[str] = None,
                        location: Optional[str] = None, doi: Optional[str] = None) -> str:
        """Generate a BibTeX entry for a journal inproceeding."""
        fields = {
            "author": self._format_authors(authors),
            "title": title,
            "booktitle": booktitle,
            "year": year,
            "pages": pages,
            "address": location,
            "doi": doi
        }
        return self._create_entry("inproceeding", citation_key, fields)