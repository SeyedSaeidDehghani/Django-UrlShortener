from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as UserCreationBaseForm

User = get_user_model()


class UserCreationForm(UserCreationBaseForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
