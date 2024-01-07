from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

from django.urls import reverse_lazy
from django.views.generic import CreateView
from users.forms import RegisterUserForm, LoginUserForm
from sneakers_shop.utils import DataMixin


class RegisterUser(DataMixin, CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')
    form_class = RegisterUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регістрація")

        return dict(list(context.items())+list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    template_name = 'users/login.html'
    form_class = LoginUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизація")

        return dict(list(context.items())+list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

def logout_user(request):
    logout(request)
    return redirect('home')

def profile(request):

    return redirect('home')
