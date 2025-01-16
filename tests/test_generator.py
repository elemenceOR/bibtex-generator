import unittest
from unittest.mock import patch, Mock
from bibtex.generator import IEEEBibTeX

class TestIEEETex(unittest.TestCase):

    def setUp(self):
        self.generator = IEEEBibTeX()

    def test_format_authors(self):
        authors = "John Doe, Jane Smith"
        formatted_authors = self.generator._format_authors(authors)
        self.assertEqual(formatted_authors, "John Doe and Jane Smith")

    def test_create_article(self):
        citation_key = "doe2021example"
        title = "An Example Article"
        authors = "John Doe, Jane Smith"
        journal = "Journal of Examples"
        year = "2021"
        volume = "10"
        number = "2"
        pages = "123-456"
        doi = "10.1234/example.doi"
        
        article = self.generator.create_article(citation_key, title, authors, journal, year, volume, number, pages, doi)
        expected_article = (
            "@article{doe2021example,\n"
            "  author = {John Doe and Jane Smith},\n"
            "  title = {An Example Article},\n"
            "  journal = {Journal of Examples},\n"
            "  year = {2021},\n"
            "  volume = {10},\n"
            "  number = {2},\n"
            "  pages = {123-456},\n"
            "  doi = {10.1234/example.doi}\n"
            "}"
        )
        self.assertEqual(article, expected_article)

    def test_create_inproceeding(self):
        citation_key = "smith2021conference"
        title = "A Conference Paper"
        authors = "Jane Smith, John Doe"
        booktitle = "Proceedings of the Example Conference"
        year = "2021"
        pages = "789-1011"
        location = "Example City"
        doi = "10.5678/example.conference.doi"
        
        inproceeding = self.generator.create_inproceeding(citation_key, title, authors, booktitle, year, pages, location, doi)
        expected_inproceeding = (
            "@inproceeding{smith2021conference,\n"
            "  author = {Jane Smith and John Doe},\n"
            "  title = {A Conference Paper},\n"
            "  booktitle = {Proceedings of the Example Conference},\n"
            "  year = {2021},\n"
            "  pages = {789-1011},\n"
            "  address = {Example City},\n"
            "  doi = {10.5678/example.conference.doi}\n"
            "}"
        )
        self.assertEqual(inproceeding, expected_inproceeding)

    @patch('bibtex.generator.requests.get')
    def test_fetch_from_doi(self, mock_get):
        mock_response = Mock()
        expected_data = {
            'title': ['An Example Article'],
            'author': [{'given': 'John', 'family': 'Doe'}, {'given': 'Jane', 'family': 'Smith'}],
            'published-print': {'date-parts': [[2021]]},
            'type': 'journal-article',
            'container-title': ['Journal of Examples'],
            'volume': '10',
            'issue': '2',
            'page': '123-456'
        }
        mock_response.json.return_value = {'message': expected_data}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        doi = "10.1234/example.doi"
        pub_info = self.generator.fetch_from_doi(doi)
        
        expected_pub_info = {
            'title': 'An Example Article',
            'authors': 'John Doe, Jane Smith',
            'year': '2021',
            'doi': doi,
            'type': 'journal-article',
            'journal': 'Journal of Examples',
            'volume': '10',
            'number': '2',
            'pages': '123-456'
        }
        self.assertEqual(pub_info, expected_pub_info)

    def test_extract_doi_from_url(self):
        url = "https://doi.org/10.1234/example.doi"
        doi = self.generator.extract_doi_from_url(url)
        self.assertEqual(doi, "10.1234/example.doi")

    def test_generate_from_identifier(self):
        with patch.object(self.generator, 'fetch_from_doi') as mock_fetch:
            mock_fetch.return_value = {
                'title': 'An Example Article',
                'authors': 'John Doe, Jane Smith',
                'year': '2021',
                'doi': '10.1234/example.doi',
                'type': 'journal-article',
                'journal': 'Journal of Examples',
                'volume': '10',
                'number': '2',
                'pages': '123-456'
            }
            identifier = "10.1234/example.doi"
            bibtex_entry = self.generator.generate_from_identifier(identifier)
            expected_entry = (
                "@article{doe2021example,\n"
                "  author = {John Doe and Jane Smith},\n"
                "  title = {An Example Article},\n"
                "  journal = {Journal of Examples},\n"
                "  year = {2021},\n"
                "  volume = {10},\n"
                "  number = {2},\n"
                "  pages = {123-456},\n"
                "  doi = {10.1234/example.doi}\n"
                "}"
            )
            self.assertEqual(bibtex_entry, expected_entry)

if __name__ == '__main__':
    unittest.main()