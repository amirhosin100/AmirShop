from apps.user.models import User
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

class UserCreationForm(BaseUserCreationForm):

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ("phone","password1","password2")

class UserChangeForm(BaseUserChangeForm):

    class Meta(BaseUserChangeForm):
        model = User
        fields = "__all__"