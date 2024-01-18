from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Такий email вже існує")
        return email

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
    phone_number = forms.CharField(required=False)
    address = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('image', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'address')



class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField()
    new_password1 = forms.CharField()
    new_password2 = forms.CharField()
