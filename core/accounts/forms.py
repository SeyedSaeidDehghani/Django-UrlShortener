from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# getting USER model
User = get_user_model()


# Sign Up Form
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "password1",
            "password2",
        ]
