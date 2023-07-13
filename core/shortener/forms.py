from django import forms
from .models import Shortener


class ShortenerForm(forms.ModelForm):
    class Meta:
        model = Shortener
        fields = ("original_url",)

    def clean_original_url(self):
        original_url = self.cleaned_data["original_url"]
        return original_url
