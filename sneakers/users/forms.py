from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from users.models import User



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

class LoginUserForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField()
    class Meta:
        model = User
        fields = ('username', 'password')

class ProfileUserForm(UserChangeForm):
    image = forms.ImageField(required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('image', 'first_name', 'last_name', 'username', 'email', 'phone', 'address')
