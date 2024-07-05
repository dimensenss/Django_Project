from django.contrib import messages, auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.db.models import Prefetch, F
from django.shortcuts import redirect


from django.urls import reverse_lazy, reverse

from django.views.generic import CreateView, UpdateView

from carts.models import Cart
from orders.models import Order, OrderItem
from users.forms import RegisterUserForm, LoginUserForm, ProfileUserForm, UserPasswordChangeForm
from goods.utils import DataMixin
from users.models import User


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = LoginUserForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.success(self.request, f"Ви вже авторизовані")
            return redirect('goods:home')  # Redirect to the home page or any other page
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        redirect_page = self.request.POST.get('next', None)
        if redirect_page and redirect_page != reverse('users:logout'):
            return redirect(redirect_page)
        return reverse_lazy('goods:home')

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.get_user()

        if user:
            auth.login(self.request, user, backend='users.authentication.EmailAuthBackend')
            if session_key:

                forgotten_cart = Cart.objects.filter(user=user)
                if forgotten_cart.exists():
                    forgotten_cart.delete()

                Cart.objects.filter(session_key=session_key).update(user=user)
                messages.success(self.request, f"Ви авторизовані")

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизація'
        return context

# def LoginUser(request):
#     if request.user.is_authenticated:
#         return redirect('users:profile')
#     if request.method == 'POST':
#         form = LoginUserForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)
#
#             session_key = request.session.session_key
#
#             if user:
#                 auth.login(request, user)
#                 messages.success(request, f"Ви авторизовані")
#
#                 if session_key:
#                     Cart.objects.filter(session_key=session_key).update(user=user)
#
#                 redirect_page = request.POST.get('next', None)
#                 if redirect_page and redirect_page != reverse('users:logout'):
#                     return HttpResponseRedirect(request.POST.get('next'))
#
#                 return HttpResponseRedirect(reverse('goods:home'))
#     else:
#         form = LoginUserForm()
#
#     context = {
#         'title': 'Вхід',
#         'form': form
#     }
#     return render(request, 'users/login.html', context)


class RegisterUserView(CreateView):
    template_name = 'users/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('goods:profile')

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.instance

        if user:
            form.save()
            auth.login(self.request, user, backend='users.authentication.EmailAuthBackend')
            if session_key:
                Cart.objects.filter(session_key=session_key).update(user=user)
                existing_orders = Order.objects.filter(session=session_key)

                if existing_orders:
                    User.objects.get(username=existing_orders[0].user.username).delete()
                    for order in existing_orders:
                        order.update(user=user)
            messages.success(self.request, f"Ваш акаунт {user.username} зареєстровано")
            return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Реєстрація'
        return context

# def RegisterUser(request):
#     if request.method == 'POST':
#         form = RegisterUserForm(data=request.POST)
#         if form.is_valid():
#             form.save()
#
#             session_key = request.session.session_key
#
#             user = form.instance
#             user.backend = 'users.authentication.EmailAuthBackend'
#             auth.login(request, user)
#
#             if session_key:
#                 Cart.objects.filter(session_key=session_key).update(user=user)
#                 existing_orders = Order.objects.filter(session=session_key)
#
#                 # удалить временного пользователя
#                 User.objects.get(username=existing_orders[0].user.username).delete()
#
#                 if existing_orders:
#                     for order in existing_orders:
#                         order.update(user=user)
#
#             messages.success(request, f"Ваш акаунт {user.username} зареєстровано")
#             return HttpResponseRedirect(reverse('goods:home'))
#     else:
#         form = RegisterUserForm()
#
#     context = {
#         'title': 'Регістрація',
#         'form': form
#     }
#     return render(request, 'users/register.html', context)
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
        orders = Order.objects.filter(user=self.request.user).prefetch_related(
            Prefetch(
                "orderitem_set",
                queryset=OrderItem.objects.select_related("product__sneakers").annotate(
                    sneakers_slug=F("product__sneakers__slug"), sneakers_first_image = F("product__sneakers__first_image__image")
                ),
            )
        ).order_by("-id")

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f'Кабінет {self.get_object().username}', orders=orders)

        return dict(list(context.items())+list(c_def.items()))



class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "includes/password_change_form.html"





