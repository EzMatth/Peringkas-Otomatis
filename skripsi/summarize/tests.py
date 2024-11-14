from django.test import TestCase
from django.urls import reverse
import requests
from unittest.mock import patch

class SummarizeFromUrlTests(TestCase):
    def test_summarize_from_url(self):
        url = 'http://example.com'
        html_content = '<html><body><p>This is a test paragraph.</p></body></html>'
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = html_content
            response = self.client.post(reverse('summarize_from_url'), {'url_input': url})
            self.assertEqual(response.status_code, 200)
            self.assertIn('This is a test paragraph.', response.content.decode())
