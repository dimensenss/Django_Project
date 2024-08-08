import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from users.models import User
from users.utils import validate_email, validate_username


class RegisterUserForm(UserCreationForm):
    username = forms.CharField()
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # наследуем UserCreationForm
        self.fields['email'].required = True
        del self.fields['username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']

        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data['email']
        validate_email(email)
        return email


class LoginUserForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean_username(self):
        email = self.cleaned_data['username']
        validate_username(email)
        return email


class ProfileUserForm(UserChangeForm):
    image = forms.ImageField(required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.CharField(required=False)
    address = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('image', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'address')

    def clean_email(self):
        email = self.cleaned_data['email']
        validate_email(self, email)
        return email

    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        data = re.sub(r'\D', '', data)

        if not data.isdigit():
            raise forms.ValidationError("Номер телефона потрібен містити тільки цифри")

        pattern = re.compile(r'^\d{10}$')
        if not pattern.match(data):
            raise forms.ValidationError("Невірний формат номера")

        return data



class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField()
    new_password1 = forms.CharField()
    new_password2 = forms.CharField()
