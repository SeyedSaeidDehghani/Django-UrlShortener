from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from ..models import Shortener
from ..utils import generate_shortener_url, generate_random_str

User = get_user_model()


class TestUtils(TestCase):
    def test_generate_random_str(self):
        url_size = settings.URL_SIZE
        random_str = generate_random_str()
        self.assertEquals(len(random_str), url_size)

    def test_generate_shortener_url_unique(self):
        user = User.objects.create(email="test@test.com", password="123qwe!@#")
        shortener = Shortener.objects.create(
            user=user, original_url="http://www.example.com"
        )
        random_url = generate_shortener_url(shortener)
        self.assertNotEquals(random_url, shortener.short_url)
