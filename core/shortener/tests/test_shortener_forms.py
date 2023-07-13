from django.test import TestCase
from ..forms import ShortenerForm


class TestShortenerForm(TestCase):
    def test_shortener_form_with_valid_data(self):
        form = ShortenerForm(data={"original_url": "http://example.com"})
        self.assertTrue(form.is_valid())

    def test_shortener_form_with_invalid_data(self):
        form = ShortenerForm(data={"original_url": "example"})
        self.assertFalse(form.is_valid())

    def test_shortener_form_with_no_data(self):
        form = ShortenerForm(data={})
        self.assertFalse(form.is_valid())
