from django.contrib.auth.views import LogoutView
from django.urls import path, include
from .views import SignUpView

app_name = "accounts"

urlpatterns = [
    path(
        "logout/",
        LogoutView.as_view(next_page="accounts:login"),
        name="logout",
    ),
    path("singnup/", SignUpView.as_view(), name="signup"),
    path("", include("django.contrib.auth.urls")),
]
