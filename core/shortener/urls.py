from django.urls import path
from . import views

app_name = "shortener"

urlpatterns = [
    path("", views.ShortenerListView.as_view(), name="list"),
    path("<int:pk>/", views.ShortenerDetailView.as_view(), name="detail"),
    path(
        "<int:pk>/delete/", views.ShortenerDeleteView.as_view(), name="delete"
    ),
    path("create/", views.ShortenerCreateView.as_view(), name="create"),
    path(
        "<str:short_url>",
        views.ShortenerRedirectView.as_view(),
        name="redirect",
    ),
]
