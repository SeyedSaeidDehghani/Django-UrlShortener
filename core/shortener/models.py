from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .utils import generate_shortener_url

# getting USER model
User = get_user_model()


# Create your models here.
class Shortener(models.Model):
    """
    this is a class to define model of Shortener app
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             null=True, blank=True)
    original_url = models.URLField()
    short_url = models.CharField(max_length=15, unique=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-create_date"]

    def __str__(self):
        return f"{self.original_url} to {self.short_url}"

    def clean(self):
        if Shortener.objects.filter(user=self.user, original_url=self.original_url).exists():
            raise ValidationError("this URL is exists!")

    def save(self, *args, **kwargs):
        """
        overwrite save method
        """
        if not self.short_url:
            self.short_url = generate_shortener_url(self)
        self.full_clean()
        super().save(*args, **kwargs)
