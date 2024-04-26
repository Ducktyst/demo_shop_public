from django.contrib.auth import forms as auth_forms
from django import forms
from django.contrib.auth import get_user_model


class LoginForm(auth_forms.AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(auth_forms.UserCreationForm):
    password2 = None

    class Meta:
        model = get_user_model()
        fields = ["username", "password1"]


class OrderResponseForm(forms.Form):
    message = forms.CharField(required=False, widget=forms.Textarea)

