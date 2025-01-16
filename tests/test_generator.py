import unittest
from unittest.mock import patch, Mock
import requests
from bibtex.generator import IEEEBibTeX  

class TestIEEEBibTeX(unittest.TestCase):
    def setUp(self):
        self.bibtex = IEEEBibTeX()
        
    def test_format_authors(self):
        """Test author name formatting"""
        # Test basic author formatting
        authors = "John Doe, Jane Smith, Bob Wilson"
        expected = "John Doe and Jane Smith and Bob Wilson"
        self.assertEqual(self.bibtex._format_authors(authors), expected)
        
        # Test handling of extra spaces
        authors = "John Doe ,  Jane Smith,Bob Wilson  "
        self.assertEqual(self.bibtex._format_authors(authors), expected)
        
        # Test single author
        self.assertEqual(self.bibtex._format_authors("John Doe"), "John Doe")

    def test_create_entry(self):
        """Test BibTeX entry creation"""
        entry_type = "article"
        citation_key = "doe2024analysis"
        fields = {
            "author": "John Doe",
            "title": "Analysis of Something",
            "journal": "Journal of Things",
            "year": "2024",
            "volume": "1",
            "number": "2",
            "pages": "34-45"
        }
        
        expected = '''@article{doe2024analysis,
    author = {John Doe},
    title = {Analysis of Something},
    journal = {Journal of Things},
    year = {2024},
    volume = {1},
    number = {2},
    pages = {34-45}
}'''
        
        result = self.bibtex._create_entry(entry_type, citation_key, fields)
        # Normalize whitespace for comparison
        self.assertEqual(result.strip(), expected.strip())
        
        # Test with missing optional fields
        fields_minimal = {
            "author": "John Doe",
            "title": "Analysis of Something",
            "journal": "Journal of Things",
            "year": "2024"
        }
        result_minimal = self.bibtex._create_entry(entry_type, citation_key, fields_minimal)
        self.assertNotIn("volume", result_minimal)
        self.assertNotIn("number", result_minimal)
        self.assertNotIn("pages", result_minimal)

    def test_extract_doi_from_url(self):
        """Test DOI extraction from URLs"""
        # Test various DOI URL formats
        urls = {
            "https://doi.org/10.1234/example.123": "10.1234/example.123",
            "https://example.com/article/doi:10.1234/example.123": "10.1234/example.123",
            "https://example.com/10.1234/example.123": "10.1234/example.123",
            "https://invalid-url.com": None
        }
        
        for url, expected_doi in urls.items():
            self.assertEqual(self.bibtex.extract_doi_from_url(url), expected_doi)

    @patch('requests.get')
    def test_fetch_from_doi(self, mock_get):
        """Test fetching metadata from CrossRef API"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'message': {
                'title': ['Test Article'],
                'author': [
                    {'given': 'John', 'family': 'Doe'},
                    {'given': 'Jane', 'family': 'Smith'}
                ],
                'published-print': {'date-parts': [[2024]]},
                'type': 'journal-article',
                'container-title': ['Test Journal'],
                'volume': '1',
                'issue': '2',
                'page': '34-45',
                'DOI': '10.1234/example.123'
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.bibtex.fetch_from_doi('10.1234/example.123')
        
        self.assertEqual(result['title'], 'Test Article')
        self.assertEqual(result['authors'], 'John Doe, Jane Smith')
        self.assertEqual(result['year'], '2024')
        self.assertEqual(result['type'], 'journal-article')
        
        # Test API error handling
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        with self.assertRaises(Exception):
            self.bibtex.fetch_from_doi('10.1234/example.123')

    def test_create_article(self):
        """Test article entry creation"""
        result = self.bibtex.create_article(
            citation_key="doe2024analysis",
            title="Analysis of Something",
            authors="John Doe, Jane Smith",
            journal="Journal of Things",
            year="2024",
            volume="1",
            number="2",
            pages="34-45",
            doi="10.1234/example.123"
        )
        
        expected = '''@article{doe2024analysis,
    author = {John Doe and Jane Smith},
    title = {Analysis of Something},
    journal = {Journal of Things},
    year = {2024},
    volume = {1},
    number = {2},
    pages = {34-45},
    doi = {10.1234/example.123}
}'''
        
        self.assertEqual(result.strip(), expected.strip())

    def test_create_inproceeding(self):
        """Test inproceeding entry creation"""
        result = self.bibtex.create_inproceeding(
            citation_key="doe2024analysis",
            title="Analysis of Something",
            authors="John Doe, Jane Smith",
            booktitle="Proceedings of Things",
            year="2024",
            pages="34-45",
            location="New York, NY",
            doi="10.1234/example.123"
        )
        
        expected = '''@inproceeding{doe2024analysis,
    author = {John Doe and Jane Smith},
    title = {Analysis of Something},
    booktitle = {Proceedings of Things},
    year = {2024},
    pages = {34-45},
    address = {New York, NY},
    doi = {10.1234/example.123}
}'''
        
        self.assertEqual(result.strip(), expected.strip())

    @patch('requests.get')
    def test_generate_from_identifier(self, mock_get):
        """Test BibTeX generation from DOI or URL"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'message': {
                'title': ['Test Article'],
                'author': [{'given': 'John', 'family': 'Doe'}],
                'published-print': {'date-parts': [[2024]]},
                'type': 'journal-article',
                'container-title': ['Test Journal'],
                'DOI': '10.1234/example.123'
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test with DOI
        result = self.bibtex.generate_from_identifier('10.1234/example.123')
        self.assertIn('@article{doe2024test', result)
        
        # Test with URL
        result = self.bibtex.generate_from_identifier('https://doi.org/10.1234/example.123')
        self.assertIn('@article{doe2024test', result)
        
        # Test with invalid URL
        with self.assertRaises(ValueError):
            self.bibtex.generate_from_identifier('https://invalid-url.com')

if __name__ == '__main__':
    unittest.main()