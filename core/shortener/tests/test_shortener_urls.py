from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .. import views


class TestUrl(SimpleTestCase):

    def test_shortener_list_url_resolve(self):
        url = reverse('shortener:list')
        self.assertEquals(resolve(url).func.view_class, views.ShortenerListView)

    def test_shortener_detail_url_resolve(self):
        url = reverse('shortener:detail', kwargs={'pk': 1})
        self.assertEquals(resolve(url).func.view_class, views.ShortenerDetailView)

    def test_shortener_create_url_resolve(self):
        url = reverse('shortener:create')
        self.assertEquals(resolve(url).func.view_class, views.ShortenerCreateView)

    def test_shortener_delete_url_resolve(self):
        url = reverse('shortener:delete', kwargs={'pk': 1})
        self.assertEquals(resolve(url).func.view_class, views.ShortenerDeleteView)

    def test_shortener_redirect_url_resolve(self):
        url = reverse('shortener:redirect', kwargs={'short_url': 'gD6ZYIof'})
        self.assertEquals(resolve(url).func.view_class, views.ShortenerRedirectView)
