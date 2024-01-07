from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from users.forms import RegisterUserForm, LoginUserForm, ProfileUserForm
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
        messages.success(self.request, f'Ваш акаунт {user.username} зареєстровано')
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    template_name = 'users/login.html'
    form_class = LoginUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизація")

        return dict(list(context.items())+list(c_def.items()))

    def get_success_url(self):
        messages.success(self.request, "Ви авторизовані")
        return reverse_lazy('home')
@login_required
def logout_user(request):
    messages.success(request, 'Ви вийшли з акаунту')
    logout(request)
    return redirect('home')


class ProfileUser(LoginRequiredMixin, DataMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileUserForm
    success_url = reverse_lazy('user:profile')

    def get_object(self, *args, **kwargs):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Дані збережено")
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Профіль")

        return dict(list(context.items())+list(c_def.items()))

