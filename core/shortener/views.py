from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect
from .forms import ShortenerForm
from .models import Shortener


# Create your views here.


class ShortenerListView(LoginRequiredMixin, generic.ListView):
    """
    this is a class base view for List of Urls page
    """

    model = Shortener
    paginate_by = 6

    def get_queryset(self):
        return Shortener.objects.filter(user=self.request.user)


class ShortenerDetailView(LoginRequiredMixin, generic.DetailView):
    """
    this is a class base view for Detail of Url Page
    """

    model = Shortener

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class ShortenerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Shortener
    form_class = ShortenerForm
    template_name = "shortener/shortener_create.html"
    success_url = reverse_lazy("shortener:list")

    def form_valid(self, form):
        original_url = form.instance.original_url

        if Shortener.objects.filter(
            original_url=original_url, user=self.request.user
        ).exists():
            form.add_error(None, "This url is exist")
            return super().form_invalid(form)

        form.instance.user = self.request.user
        return super().form_valid(form)


class ShortenerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Shortener
    success_url = reverse_lazy("shortener:list")


class ShortenerRedirectView(LoginRequiredMixin, View):
    """
    this is a class base view for Redirect url
    """

    def get(self, request, short_url, *args, **kwargs):
        obj = get_object_or_404(Shortener, short_url=short_url)
        return HttpResponsePermanentRedirect(obj.original_url)
