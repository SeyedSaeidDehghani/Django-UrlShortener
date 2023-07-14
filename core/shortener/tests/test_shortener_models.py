from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import Shortener
from django.contrib.auth import get_user_model

User = get_user_model()


class TestShortenerModel(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(email="test@test.com", password="123qwe!@#")
        user1 = User.objects.create(email="test1@test.com", password="123qwe!@#")
        user2 = User.objects.create(email="test2@test.com", password="123qwe!@#")
        Shortener.objects.create(user=user1, original_url="http://www.example1.com")
        Shortener.objects.create(user=user1, original_url="http://www.example2.com")
        Shortener.objects.create(user=user2, original_url="http://www.example1.com")
        Shortener.objects.create(user=user2, original_url="http://www.example2.com")

    def test_create_shortener_with_valid_data(self):
        shortener = Shortener.objects.create(
            user=self.user, original_url="http://www.example.com"
        )
        self.assertTrue(Shortener.objects.filter(pk=shortener.pk).exists())

    def test_create_shortener_with_invalid_data(self):
        shortener = Shortener(user=self.user, original_url="example")
        with self.assertRaises(ValidationError):
            # Validation Error because this original url invalid format
            shortener.save()
        self.assertFalse(Shortener.objects.filter(pk=shortener.pk).exists())

    def test_unique_original_url(self):
        """
        this is a method for testing unique original url for user
        """

        shortener1 = Shortener.objects.create(
            user=self.user, original_url="http://www.example.com"
        )
        shortener2 = Shortener(user=self.user, original_url="http://www.example.com")
        self.assertTrue(Shortener.objects.filter(pk=shortener1.pk).exists())
        with self.assertRaises(ValidationError):
            # Validation Error because this original url for this user is exists
            shortener2.save()

        self.assertFalse(Shortener.objects.filter(pk=shortener2.pk).exists())

    def test_unique_short_url(self):
        test1 = Shortener.objects.get(
            user__email="test1@test.com", original_url="http://www.example1.com"
        )
        test2 = Shortener.objects.get(
            user__email="test2@test.com", original_url="http://www.example1.com"
        )

        self.assertNotEqual(test1.short_url, test2.short_url)

    def test_str(self):
        test1 = Shortener.objects.get(
            user__email="test1@test.com", original_url="http://www.example1.com"
        )
        test2 = Shortener.objects.get(
            user__email="test2@test.com", original_url="http://www.example2.com"
        )
        test1_str_temp = f"{test1.original_url} to {test1.short_url}"
        test2_str_temp = f"{test2.original_url} to {test2.short_url}"

        self.assertEquals(test1.__str__(), test1_str_temp)
        self.assertEquals(test2.__str__(), test2_str_temp)
