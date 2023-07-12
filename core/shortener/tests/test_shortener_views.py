from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Shortener

User = get_user_model()


class TestShortenerView(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='test', password="123qwe!@#")
        self.shortener = Shortener.objects.create(
            user=self.user,
            original_url='http://www.example.com'
        )

    def test_shortener_urls_anonymous_response(self):
        url_list = reverse('shortener:list')
        url_detail = reverse('shortener:detail', kwargs={'pk': self.shortener.pk})
        url_create = reverse('shortener:create')
        url_delete = reverse('shortener:delete', kwargs={'pk': self.shortener.pk})
        url_redirect = reverse('shortener:redirect', kwargs={'short_url': self.shortener.short_url})

        response_list = self.client.get(url_list)
        response_detail = self.client.get(url_detail)
        response_create = self.client.post(url_create)
        response_delete = self.client.get(url_delete)
        response_redirect = self.client.get(url_redirect)

        self.assertEquals(response_list.status_code, 302)
        self.assertEquals(response_detail.status_code, 302)
        self.assertEquals(response_create.status_code, 302)
        self.assertEquals(response_delete.status_code, 302)
        self.assertEquals(response_redirect.status_code, 302)

    def test_shortener_list_view(self):
        self.client.force_login(self.user)
        url = reverse('shortener:list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(str(response.content).find(self.shortener.original_url), -1)
        for template in ('shortener/shortener_list.html', 'base.html'):
            self.assertTemplateUsed(response, template)

    def test_shortener_detail_url_successful_response(self):
        self.client.force_login(self.user)
        url = reverse('shortener:detail', kwargs={'pk': self.shortener.pk})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(str(response.content).find(self.shortener.short_url), -1)
        for template in ('shortener/shortener_detail.html', 'base.html'):
            self.assertTemplateUsed(response, template)

    def test_shortener_create_view(self):
        self.client.force_login(self.user)
        url = reverse('shortener:create')
        data = {
            'user': self.user,
            'original_url': 'http://www.example2.com'
        }
        invalid_data = {
            'user': self.user,
            'original_url': 'example2'
        }
        invalid_exist_data = {
            'user': self.user,
            'original_url': 'http://www.example2.com'
        }
        response_valid = self.client.post(url, data=data, follow=True)
        response_invalid = self.client.post(url, data=invalid_data, follow=True)
        response_invalid_exist = self.client.post(url, data=invalid_exist_data, follow=True)
        self.assertEquals(response_valid.status_code, 200)
        self.assertContains(response_invalid, 'Generate')
        self.assertContains(response_invalid_exist, 'This url is exist')
        self.assertNotEqual(str(response_valid.content).find(data['original_url']), -1)
        for template in ('shortener/shortener_list.html', 'base.html'):
            self.assertTemplateUsed(response_valid, template)

    def test_shortener_delete_view(self):
        self.client.force_login(self.user)
        shortener = Shortener.objects.create(user=self.user, original_url='http://www.example5.com')
        url = reverse('shortener:delete', kwargs={'pk': shortener.pk})
        response = self.client.post(url)
        self.assertEquals(response.status_code, 200)
        print(str(response.content))

    def test_shortener_redirect_view(self):
        self.client.force_login(self.user)
        shortener = Shortener.objects.create(user=self.user, original_url='https://testdriven.io')

        url = reverse('shortener:redirect', kwargs={'short_url': shortener.short_url})
        url_invalid_data = reverse('shortener:redirect', kwargs={'short_url': shortener.short_url + 'A'})

        response = self.client.get(url)
        response_invalid = self.client.get(url_invalid_data)

        self.assertEquals(response.status_code, 301)
        self.assertEquals(response_invalid.status_code, 404)
