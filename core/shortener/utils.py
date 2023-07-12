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