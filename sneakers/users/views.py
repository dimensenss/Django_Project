from django.contrib import messages, auth
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes
from django.views.generic import CreateView, UpdateView

from carts.models import Cart
from users.forms import RegisterUserForm, LoginUserForm, ProfileUserForm
from goods.utils import DataMixin


# class RegisterUser(DataMixin, CreateView):
#     template_name = 'users/register.html'
#     form_class = RegisterUserForm
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title="Регістрація")
#
#         return dict(list(context.items())+list(c_def.items()))
#
#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)
#         messages.success(self.request, f'Ваш акаунт {user.username} зареєстровано')
#         return redirect('goods:home')
#
#
# class LoginUser(DataMixin, LoginView):
#     template_name = 'users/login.html'
#     form_class = LoginUserForm
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title="Авторизація")
#
#         return dict(list(context.items())+list(c_def.items()))
#
#     def get_success_url(self):
#         messages.success(self.request, "Ви авторизовані")
#
#         next_url = self.request.POST.get('next', None)
#         if next_url and next_url != reverse('users:logout'):
#             return next_url
#
#         return reverse('goods:home')


def LoginUser(request):
    if request.method == 'POST':
        form = LoginUserForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)

            session_key = request.session.session_key

            if user:
                auth.login(request, user)
                messages.success(request, f"Ви авторизовані")

                if session_key:
                    Cart.objects.filter(session_key=session_key).update(user=user)

                redirect_page = request.POST.get('next', None)
                if redirect_page and redirect_page != reverse('users:logout'):
                    return HttpResponseRedirect(request.POST.get('next'))

                return HttpResponseRedirect(reverse('goods:home'))
    else:
        form = LoginUserForm()

    context = {
        'title': 'Авторизація',
        'form': form
    }
    return render(request, 'users/login.html', context)


def RegisterUser(request):
    if request.method == 'POST':
        form = RegisterUserForm(data=request.POST)
        if form.is_valid():
            form.save()

            session_key = request.session.session_key

            user = form.instance
            auth.login(request, user)

            if session_key:
                Cart.objects.filter(session_key=session_key).update(user=user)

            messages.success(request, f"Ваш акаунт {user.username} зареєстровано")
            return HttpResponseRedirect(reverse('goods:home'))
    else:
        form = RegisterUserForm()

    context = {
        'title': 'Регістрація',
        'form': form
    }
    return render(request, 'users/register.html', context)
@login_required
def logout_user(request):
    messages.success(request, 'Ви вийшли з акаунту')
    logout(request)
    return redirect('goods:home')


class ProfileUser(LoginRequiredMixin, DataMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileUserForm

    def get_object(self, *args, **kwargs):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Дані збережено")
        return redirect('user:profile')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Профіль")

        return dict(list(context.items())+list(c_def.items()))


def users_cart(request):
    return render(request, 'users/user_cart.html')

