# Django-UrlShortener
This is URL shortener application written using the Django framework and dockerize.

## Table of Contents

* [Getting Started](#getting-started)
  + [Getting Docker](#getting-docker)
  + [Using Docker](#using-docker)
* [Manual Method](#manual-method)
* [Build from Scratch](#build-from-scratch)
  + [Create the Shortener App](#create-the-shortener-app)
  + [Create the Accounts App](#create-the-accounts-app)
  + [Create the Templates](#create-the-templates)
  + [Add Static files](#add-static-files)
  + [Change Django Settings](#change-django-settings)
  + [Add Docker and Compose](#add-docker-and-compose)
  + [Reformat and Lint code](#reformat-and-lint-code)

# Getting Started

## Getting Docker
  getting docker from this link:

  + https://docs.docker.com/engine/install/

  getting docker-compose form this link:

  + https://docs.docker.com/compose/install/

## Using Docker

- Clone the repo

```
git clone https://github.com/SeyedSaeidDehghani/Django-UrlShortener
```

- Bring up the app

```
 docker-compose -f docker-compose-stage.yml up --build
```

- Perform the migration

```
 docker exec backend sh -c "python manage.py makemigrations accounts"
 docker exec backend sh -c "python manage.py makemigrations shortener"
 docker exec backend sh -c "python manage.py migrate"
 docker exec backend sh -c "python manage.py migrate --run-syncdb"
```

- Testing the app

```
 docker exec backend sh -c "python manage.py test"
```

# Manual Method

- Create virtualenv and activate it:

```bash
virtualenv -p python3.10 venv
source venv/bin/activate
```

- Install the dependencies:

```bash
pip install -r requirements.txt
```

# Build from Scratch

- Create virtualenv and activate it:

```bash
virtualenv -p python3.10 venv
source venv/bin/activate
```

- Install Django:

```bash
pip install Django==4.2.3
```

- Create a `Django-UrlShortener` directory and go there:

```bash
mkdir -p Django-UrlShortener && cd Django-UrlShortener
```

- Create a Django project there:

```bash
django-admin startproject core
```

- By creating the Django project, the tree structure of the repo
would look like this:

```
Django-UrlShortener
└── core
    ├── manage.py
    └── core
        ├── asgi.py
        ├── __init__.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py

```

- Now, let's create the Django app for shortening the URLs and Accounts:

```bash
python manage.py startapp shortener

python manage.py startapp accounts
```

- It will create directory under `DjangoUrlShortener/core`:

```
DjangoUrlShortener
└── core
    ├── accounts
    │   ├── admin.py
    │   ├── apps.py
    │   ├── __init__.py
    │   ├── migrations
    │   ├── models.py
    │   ├── tests.py
    │   └── views.py
    ├── shortener
    │   ├── admin.py
    │   ├── apps.py
    │   ├── __init__.py
    │   ├── migrations
    │   ├── models.py
    │   ├── tests.py
    │   └── views.py
    ├── manage.py
    └── core
```

## Create the Shortener App

- Add `utils.py` to `shortener/` and edit it:

```python
from django.conf import settings
from random import choice

AVAILABLE_CHARS = settings.AVAILABLE_CHARS
URL_SIZE = settings.URL_SIZE


def generate_random_str() -> str:
    """
    Create a random string with URL_SIZE
    """
    return "".join(choice(AVAILABLE_CHARS) for _ in range(URL_SIZE))


def generate_shortener_url(instance_model) -> str:
    random_str = generate_random_str()
    # getting model class
    model_class = instance_model.__class__
    # Random string is unique
    if model_class.objects.filter(short_url=random_str).exists():
        # run again function
        return generate_shortener_url(instance_model)
    return random_str
```

- Head to `shortener/model.py` and edit it:

```python
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .utils import generate_shortener_url

# getting USER model
User = get_user_model()


class Shortener(models.Model):
    """
    this is a class to define model of Shortener app
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    original_url = models.URLField()
    short_url = models.CharField(max_length=15, unique=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-create_date"]

    def __str__(self):
        return f"{self.original_url} to {self.short_url}"

    def clean(self):
        if Shortener.objects.filter(
            user=self.user, original_url=self.original_url
        ).exists():
            raise ValidationError("this URL is exists!")

    def save(self, *args, **kwargs):
        """
        overwrite save method
        """
        if not self.short_url:
            self.short_url = generate_shortener_url(self)
        self.full_clean()
        super().save(*args, **kwargs)
```

- Now, we should Create a `forms.py` under `shortener`:
```bash
touch shortener/forms.py
```
- And fill it up:

```python
from django import forms
from .models import Shortener


class ShortenerForm(forms.ModelForm):
    class Meta:
        model = Shortener
        fields = ("original_url",)

    def clean_original_url(self):
        original_url = self.cleaned_data["original_url"]
        return original_url

```

- Head to `shortener/views.py` and edit it:

```python
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect
from .forms import ShortenerForm
from .models import Shortener


class ShortenerListView(LoginRequiredMixin, generic.ListView):
    """
    this is a class base view for List of Your URLs
    """

    model = Shortener
    paginate_by = 6

    def get_queryset(self):
        return Shortener.objects.filter(user=self.request.user)


class ShortenerDetailView(LoginRequiredMixin, generic.DetailView):
    """
    this is a class base view for Detail of Your URL
    """

    model = Shortener

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class ShortenerCreateView(LoginRequiredMixin, generic.CreateView):
    """
    this is a class base view for Creation New URL
    """
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
    """
    this is a class base view for Delete for once URL
    """
    model = Shortener
    success_url = reverse_lazy("shortener:list")


class ShortenerRedirectView(LoginRequiredMixin, View):
    """
    this is a class base view for Redirect URL
    """

    def get(self, request, short_url, *args, **kwargs):
        obj = get_object_or_404(Shortener, short_url=short_url)
        return HttpResponsePermanentRedirect(obj.original_url)


```

- Now, we should assign a URL to this function. Create a `urls.py` under `shortener`:

```bash
touch shortener/urls.py
```

- And fill it up:

```python
from django.urls import path
from . import views

app_name = "shortener"

urlpatterns = [
    path("", views.ShortenerListView.as_view(), name="list"),
    path("<int:pk>/", views.ShortenerDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.ShortenerDeleteView.as_view(), name="delete"),
    path("create/", views.ShortenerCreateView.as_view(), name="create"),
    path(
        "<str:short_url>",
        views.ShortenerRedirectView.as_view(),
        name="redirect",
    ),
]
```

- It will create directory under `tests` directory under `core/shortener`:
```bash
mkdir tests
````
- Create `test` file for `forms.py`:
```bash
touch tests/test_shortener_forms.py
```
- And fill it up:

```python
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
```

- Create `test` file for `models.py`:
```bash
touch tests/test_shortener_models.py
```
- And fill it up:

```python
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

```

- Create `test` file for `urls.py`:
```bash
touch tests/test_shortener_urls.py
```
- And fill it up:

```python
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .. import views


class TestUrl(SimpleTestCase):
    def test_shortener_list_url_resolve(self):
        url = reverse("shortener:list")
        self.assertEquals(resolve(url).func.view_class, views.ShortenerListView)

    def test_shortener_detail_url_resolve(self):
        url = reverse("shortener:detail", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, views.ShortenerDetailView)

    def test_shortener_create_url_resolve(self):
        url = reverse("shortener:create")
        self.assertEquals(resolve(url).func.view_class, views.ShortenerCreateView)

    def test_shortener_delete_url_resolve(self):
        url = reverse("shortener:delete", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, views.ShortenerDeleteView)

    def test_shortener_redirect_url_resolve(self):
        url = reverse("shortener:redirect", kwargs={"short_url": "gD6ZYIof"})
        self.assertEquals(resolve(url).func.view_class, views.ShortenerRedirectView)

```

- Create `test` file for `utils.py`:

```bash
touch tests/test_shortener_utils.py
```
- And fill it up:

```python
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

```

- Create `test` file for `views.py`:

```bash
touch tests/test_shortener_views.py
```
- And fill it up:

```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Shortener

User = get_user_model()


class TestShortenerView(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(email="test@test.com", password="123qwe!@#")
        self.shortener = Shortener.objects.create(
            user=self.user, original_url="http://www.example.com"
        )

    def test_shortener_urls_anonymous_response(self):
        url_list = reverse("shortener:list")
        url_detail = reverse("shortener:detail", kwargs={"pk": self.shortener.pk})
        url_create = reverse("shortener:create")
        url_delete = reverse("shortener:delete", kwargs={"pk": self.shortener.pk})
        url_redirect = reverse(
            "shortener:redirect",
            kwargs={"short_url": self.shortener.short_url},
        )

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
        url = reverse("shortener:list")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(str(response.content).find(self.shortener.original_url), -1)
        for template in ("shortener/shortener_list.html", "base.html"):
            self.assertTemplateUsed(response, template)

    def test_shortener_detail_url_successful_response(self):
        self.client.force_login(self.user)
        url = reverse("shortener:detail", kwargs={"pk": self.shortener.pk})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(str(response.content).find(self.shortener.short_url), -1)
        for template in ("shortener/shortener_detail.html", "base.html"):
            self.assertTemplateUsed(response, template)

    def test_shortener_create_view(self):
        self.client.force_login(self.user)
        url = reverse("shortener:create")
        data = {"user": self.user, "original_url": "http://www.example2.com"}
        invalid_data = {"user": self.user, "original_url": "example2"}
        invalid_exist_data = {
            "user": self.user,
            "original_url": "http://www.example2.com",
        }
        response_valid = self.client.post(url, data=data, follow=True)
        response_invalid = self.client.post(url, data=invalid_data, follow=True)
        response_invalid_exist = self.client.post(
            url, data=invalid_exist_data, follow=True
        )
        self.assertEquals(response_valid.status_code, 200)
        self.assertContains(response_invalid, "Generate")
        self.assertContains(response_invalid_exist, "This url is exist")
        self.assertNotEqual(str(response_valid.content).find(data["original_url"]), -1)
        for template in ("shortener/shortener_list.html", "base.html"):
            self.assertTemplateUsed(response_valid, template)

    def test_shortener_delete_view(self):
        self.client.force_login(self.user)
        shortener = Shortener.objects.create(
            user=self.user, original_url="http://www.example5.com"
        )
        url = reverse("shortener:delete", kwargs={"pk": shortener.pk})
        response = self.client.post(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_shortener_redirect_view(self):
        self.client.force_login(self.user)
        shortener = Shortener.objects.create(
            user=self.user, original_url="https://testdriven.io"
        )

        url = reverse("shortener:redirect", kwargs={"short_url": shortener.short_url})
        url_invalid_data = reverse(
            "shortener:redirect",
            kwargs={"short_url": shortener.short_url + "A"},
        )

        response = self.client.get(url)
        response_invalid = self.client.get(url_invalid_data)

        self.assertEquals(response.status_code, 301)
        self.assertEquals(response_invalid.status_code, 404)

```

- Project directory look like:
```
Django-UrlShortener
└── core
    ├── accounts
    ├── shortener
    │   ├── admin.py
    │   ├── apps.py
    │   ├── __init__.py
    │   ├── migrations
    │   ├── models.py
    │   ├── tests.py
    │   ├── views.py
    │   └── tests
    │       ├──__init__.py
    │       ├──test_shortener_forms.py
    │       ├──test_shortener_models.py
    │       ├──test_shortener_urls.py
    │       ├──test_shortener_utils.py
    │       ├──test_shortener_views.py
    ├── manage.py
    └── core
```

## Create the Accounts App

- Head to `accounts/model.py` and edit it:

```python
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    this is a custom User model for projects
    """

    email = models.EmailField(max_length=255, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __str__(self):
        return self.email
```

- Now, we should Create a `forms.py` under `accounts`:
```bash
touch accounts/forms.py
```
- And fill it up:

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as UserCreationBaseForm

User = get_user_model()


class UserCreationForm(UserCreationBaseForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
```

- Head to `accounts/views.py` and edit it:

```python
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


# Sign Up View
class SignUpView(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "registration/signup.html"
    success_message = _("Your user was created successfully")
```

- Now, we should assign a URL to this function. Create a `urls.py` under `accounts`:

```bash
touch accounts/urls.py
```
- And fill it up:

```python
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
    path("signup/", SignUpView.as_view(), name="signup"),
    path("", include("django.contrib.auth.urls")),
]

```


- Now head back to the `core/urls.py` and include the newly created `urls.py` file:

```python
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/shortener/")),
    path("shortener/", include("shortener.urls")),
    path("accounts/", include("accounts.urls")),
]
```

## Create the Templates

### Create Base Template

- let's create `base.html` file:

```bash
mkdir core/templates

touch core/templates/base.html
```

- Open the `base.html` and fill it up with following content link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/templates/base.html
### Create Accounts App Templates
- Create `login.html` and `signup.html` files under `templates/registration` directory:

```bash
cd templates

mkdir templates/registration

touch templates/registration/login.html

touch templates/registration/signup.html
```

- Open the `login.html` and fill it up with following content link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/templates/registration/login.html

- Open the `signup.html` and fill it up with following content link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/templates/registration/signup.html

### Create Shortener App Templates

- Create `shortener_create.html`, `shortener_detail.html` and `shortener_list.html` files under `templates/shortener` directory:

```bash
mkdir templates/shortener

touch templates/shortener/shortener_create.html

touch templates/shortener/shortener_detail.html

touch templates/shortener/shortener_list.html
```

- Open the `shortener_create.html` and fill it up with following content Link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/templates/shortener/shortener_create.html

- Open the `shortener_detail.html` and fill it up with following content Link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/templates/shortener/shortener_detail.html

- Open the `shortener_list.html` and fill it up with following content Link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/templates/shortener/shortener_list.html

- Project directory look like:

```
Django-UrlShortener
└── core
    ├── accounts
    ├── shortener
    ├── templates
    │   ├── registration
    │       ├── login.html
    │       └── signup.html
    │   ├── shortener
    │       ├── shortener_create.html
    │       ├── shortener_detail.html
    │       └── shortener_list.html
    │   └── base.html
    ├── manage.py
    └── core
```

## Add Static files

### Add Jquery file

- Use `jquery` library, version `3.7.0.min`.

- Create `jquery-3.7.0.min.js`files under `static/js` directory:

```bash
cd static

mkdir js

touch js/jquery-3.7.0.min.js
```
- Open the `jquery-3.7.0.min.js` and fill it up with following content Link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/static/js/jquery-3.7.0.min.js

### Add JavaScript files for Shortener app

- Create `shortener_detail.js` and `shortener_list.js` files under `static/js/shortener` directory:

```bash
cd js

mkdir shortener

touch shortener/shortener_detail.js

touch shortener/shortener_list.js
```

- Open the `shortener_detail.js` and fill it up with following content Link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/static/js/shortener/shortener_detail.js

- Open the `shortener_list.js` and fill it up with following content Link:

https://github.com/SeyedSaeidDehghani/Django-UrlShortener/blob/master/core/static/js/shortener/shortener_list.js

### Admin Static Files


- Copy from `venv/lib/python3.10/site-packages/django/contrib/admin/static/*` directory and paste into `static/` directory.

- Project directory look like:

```
Django-UrlShortener
└── core
    ├── accounts
    ├── shortener
    ├── templates
    ├── static
    │   ├── admin
    │       ├── css
    │       ├── img
    │       └── js
    │   ├── js
    │       ├── shortener
    │           ├── shortener_detail.js
    │           └── shortener_list.js
    │       └── jquery-3.7.0.min.js
    ├── manage.py
    └── core
```

## Change Django Settings

### Install dependencies

- Installing `python-decouple` package for environment variable and `psycopg2-binary` for connect to PostgresSql:

```bash
pip install psycopg2-binary==2.9.6

pip install python-decouple==3.8
```

- Add to requirements.txt file:

```bash
pip freeze > requirements.txt
```

- Then import `python-decouple` package in head of `settings.py` under `core/core` directory: 

```python
from decouple import config
```
### Get Important Variable
- Get environment variable from Docker Compose [Docker Compose](#add-docker-and-docker-compose) File:

`settings.py`
```python
SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default="*",
)
```

### Add DataBase

- Add PostgresSql DataBase in `core/settings.py` and get environment variables:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASS"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}
```

### Add Important URL
- Add static and media url in `core/settings.py` file:

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]

LOGIN_REDIRECT_URL = "/shortener/"
```

### Add Settings variable for Shortener URL

- Import `string` built-in python package on head of `core/settings.py` file, `AVAILABLE_CHARS` variable for choose random character for generate short url.

- Define `URL_SIZE` integer variable for length of short url, maximum length for this variable 15:

```python
from string import ascii_letters, digits
...
...
...
# define character usage for create short url
AVAILABLE_CHARS = ascii_letters + digits
# define short url length, maximum length is 15
URL_SIZE = 8
```

### Add Installed Apps 

- Now head to `core/settings.py` add `'accounts'` and `'shortener'` to the end of the list `INSTALLED_APPS`:

```python
...

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "shortener",
]

...
```

- Now run the development server:

```bash
python manage.py runserver
```

- This time go to the root and check it: [`127.0.0.1:8000`](http://127.0.0.1:8000/)

## Add Docker and Compose

### Install dependencies

- To use Docker Compose with the current setup, first add `Gunicorn` package:

```bash
pip install gunicorn==20.1.0
```

- Then added to requirements.txt file:

```bash
pip freeze > requirements.txt
```

### Add Docker file

+ First push docker image from `python:3.10-slim-buster`.
+ Define Work directory `WORKDIR /app`.
+ Copy `requirements.txt` file into the directory `COPY ./requirements.txt /app/`.
+ Run command for install dependencies `RUN pip install --upgrade pip, RUN pip install -r requirements.txt`.
+ Copy project directory to docker work directory `COPY ./core /app`.

```dockerfile
FROM python:3.10-slim-buster
LABEL authors="saeid"

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./core /app
```

### Add Docker Compose file for testing

- Now, create the following `docker-compose.yml` file for testing in the root of the repo.
- Add `backend` service for web container and important variable:

```yml
version: "3.10"
services:
  backend:
    build: .
    container_name: backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./core:/app
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=test
      - DEBUG=True
      - DB_HOST=db
      - DB_NAME=testDB
      - DB_USER=test
      - DB_PASS=test
      - DB_PORT=5432
    depends_on:
      - db
 ```
- Then add postgres database, important variable and detabase volume:
```yml
  db:
    image: postgres
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
      - POSTGRES_DB=testDB
    ports:
      - "5432"

volumes:
  postgres_data:
```
- Now, start the app using Docker Compose:

```bash
docker-compose up --build -d
```

- The server should run on port 8000 now: [`127.0.0.1:8000`](http://127.0.0.1:8000/)

- Now you can testing Project:
```bash
docker exec backend sh -c "python manage.py test"
```

### Test Coverage

- Install `coverage` package for test coverage:

```bash
docker exec backend sh -c "pip install coverage"
```
- Create Migrations
```bash
  docker exec backend sh -c "python manage.py makemigrations accounts"
  docker exec backend sh -c "python manage.py makemigrations shortener"
  docker exec backend sh -c "python manage.py migrate"
  docker exec backend sh -c "python manage.py migrate --run-syncdb"
```
- Testing project
```bash
 docker exec backend sh -c "coverage run --source='.' manage.py test"
```
- Then get report
```bash
 docker exec backend sh -c "coverage report"
```

```coverage report

Name                                       Stmts   Miss  Cover
--------------------------------------------------------------
accounts/__init__.py                           0      0   100%
accounts/admin.py                              3      0   100%
accounts/apps.py                               4      0   100%
accounts/forms.py                              7      0   100%
accounts/migrations/0001_initial.py            5      0   100%
accounts/migrations/__init__.py                0      0   100%
accounts/models.py                            32     15    53%
accounts/tests.py                              0      0   100%
accounts/urls.py                               5      0   100%
accounts/views.py                             10      0   100%
core/__init__.py                               0      0   100%
core/asgi.py                                   4      4     0%
core/settings.py                              28      0   100%
core/urls.py                                   4      0   100%
core/wsgi.py                                   4      4     0%
manage.py                                     12      2    83%
shortener/__init__.py                          0      0   100%
shortener/admin.py                             3      0   100%
shortener/apps.py                              4      0   100%
shortener/forms.py                             9      0   100%
shortener/migrations/0001_initial.py           7      0   100%
shortener/migrations/__init__.py               0      0   100%
shortener/models.py                           22      0   100%
shortener/tests/__init__.py                    0      0   100%
shortener/tests/test_shortener_forms.py       12      0   100%
shortener/tests/test_shortener_models.py      40      0   100%
shortener/tests/test_shortener_urls.py        19      0   100%
shortener/tests/test_shortener_utils.py       16      0   100%
shortener/tests/test_shortener_views.py       71      0   100%
shortener/urls.py                              4      0   100%
shortener/utils.py                            12      1    92%
shortener/views.py                            35      0   100%
--------------------------------------------------------------
TOTAL                                        372     26    93%

```

### Create Docker Compose Stage file
- Create the following `docker-compose-stage.yml` file for production in the root of the repo.
- Add `backend` service for web container, `DEBUG=False`, important variable and volume binding for static files and media:

```yml
version: "3.10"
services:
  backend:
    build: .
    container_name: backend
    command: gunicorn core.wsgi --bind 0.0.0.0:8000
    volumes:
      - ./core:/app
      - static_volume:/app/static
      - media_volume:/app/media
    expose:
      - "8000"
    environment:
      - SECRET_KEY=django-insecure-4p%-v14=xj)wem==*dw6vyaklsb*h0d=@fc0r1t15z1#sefo2l
      - DEBUG=False
      - DB_HOST=db
      - DB_NAME=proddb
      - DB_USER=prod
      - DB_PASS=prod
      - DB_PORT=5432
    depends_on:
      - db
```
- Add postgres database, important variable and detabase volume:
```yml
  db:
    image: postgres
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=prod
      - POSTGRES_PASSWORD=prod
      - POSTGRES_DB=proddb
    ports:
      - "5432"
```
- Then added nginx service for serve web server in port `80` and binding static files volume:

```yml
  nginx:
    image: nginx
    container_name: nginx
    restart: always
    ports:
      - "80:80"

    volumes:
      - ./default.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/home/app/static
      - media_volume:/home/app/media
    depends_on:
      - backend
```
- Define volumes:
```yml
volumes:
  static_volume:
  media_volume:
  postgres_data:
```
- Create nginx config, serve and define route for static URL:
```nginx configuration
upstream django {
  server backend:8000;
}

server {
    listen 80;

    location /static/ {
        autoindex on;
        alias /home/app/static/;
    }
    location /media/ {
        autoindex on;
        alias /home/app/media/;
    }

    location / {
        proxy_pass http://django;

        proxy_set_header Host $host;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    }
}
```

- Now, start the app using docker-compose-stage:

```bash
docker-compose -f docker-compose-stage.yml up -d
```
- Then Create migrations:
```bash
  docker exec backend sh -c "python manage.py makemigrations accounts"
  docker exec backend sh -c "python manage.py makemigrations shortener"
  docker exec backend sh -c "python manage.py migrate"
  docker exec backend sh -c "python manage.py migrate --run-syncdb"
```
- The server should run on port 80 now: [`127.0.0.1`](http://127.0.0.1/)

## Reformat and Lint code

### Install dependencies with docker

- Install `flake8` package for checking project with PEP8, and install `black` for reformatted code: 

```bash
docker-compose exec backend sh -c "pip install flake8"
docker-compose exec backend sh -c "pip install black"
```
- Add to requirements.txt files:

```requirements.txt
 black==23.7.0
 flake8==6.0.0
```
- Create `.flake8` config file under `Django-UrlShortener/core` directory:
```bash
cd core
touch core/.flake8
```
- And fill it up:

```.flake8
[flake8]
exclude =
    .git,
    .gitignore,
    *.pot,
    *.py[co],
    __pycache__,
    venv,
    .env,
    settings.py,
    __init__.py,
ignore =
    E501
```
- Now, run `flake8` for this command:

```bash
docker exec backend sh -c "flake8 ."
```
- Checking and solved error and run `black` package:

```bash
docker exec backend sh -c "black ."
```
- And Then run again `flake8`:

```bash
docker exec backend sh -c "flake8 ."
```
- Now, code is reformatted and checked with PEP8.
