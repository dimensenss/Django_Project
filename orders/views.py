from django.contrib import messages, auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import FormView

from carts.models import Cart
from goods.utils import DataMixin
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem
from users.models import User


class CreateOrderView(DataMixin, FormView):
    template_name = 'orders/create_order.html'
    form_class = CreateOrderForm
    success_url = reverse_lazy('users:profile')

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['first_name'] = self.request.user.first_name
            initial['last_name'] = self.request.user.last_name
            initial['phone_number'] = self.request.user.phone_number
            initial['email'] = self.request.user.email
        return initial

    def form_valid(self, form):
        try:
            with transaction.atomic():
                session_key = self.request.session.session_key
                user = self.get_user(form)

                Cart.objects.filter(session_key=session_key).update(user=user)
                cart_items = Cart.objects.filter(user=user)

                if not cart_items.exists():
                    raise ValidationError(f'Ваш кошик порожній')

                order = self.create_order(user, form, session_key)
                self.create_order_items(order, cart_items)
                self.send_email(order)
                messages.success(self.request, 'Замовлення оформлено!')

                return self.handle_success_redirect(user, form)

        except ValidationError as e:
            messages.warning(self.request, '; '.join(e.messages))
            return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Помилка, спробуйте ще раз')
        return redirect('orders:create_order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.get_user_context(title="Створення замовлення", order=True, request=self.request)
        return dict(list(context.items()) + list(data.items()))

    def get_user(self, form):
        if self.request.user.is_authenticated:  # authorized
            return self.request.user

        if User.objects.filter(email=form.cleaned_data['email']):  # non authorized and exists
            messages.warning(self.request, 'Користувач з таким email вже існує. Будь ласка, увійдіть.')
            raise ValidationError(f'Користувач з таким email вже існує. Будь ласка, увійдіть.')

        if form.cleaned_data['requires_registration'] == '1':  # non authorized and want to register
            user = self.create_user(form, anonymous=False)
            return user

        if form.cleaned_data['requires_registration'] == '0':  # non authorized and does not want to register
            user = self.create_user(form, anonymous=True)
            return user

    def create_user(self, form, anonymous=False):
        random_password = User.objects.make_random_password()
        user = User.objects.create_user(
            username=form.cleaned_data['email'] if not anonymous else random_password,
            email=form.cleaned_data['email'] if not anonymous else random_password,
            password=form.cleaned_data['password1'] if not anonymous else random_password,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            phone_number=form.cleaned_data['phone_number'],
        )
        user.save()
        user.backend = 'users.authentication.EmailAuthBackend'
        return user

    def create_order(self, user, form, session_key):
        order = Order.objects.create(
            user=user,
            phone_number=form.cleaned_data['phone_number'],
            email=form.cleaned_data['email'],
            requires_delivery=form.cleaned_data['requires_delivery'],
            delivery_address=form.cleaned_data['delivery_address'],
            payment_on_get=form.cleaned_data['payment_on_get'],
            session=session_key
        )
        return order

    def create_order_items(self, order, cart_items):
        for cart_item in cart_items:
            product = cart_item.product  # SneakersVariations
            title = cart_item.product.sneakers.title
            price = cart_item.product.sneakers.sell_price
            quantity = cart_item.quantity

            if product.quantity < quantity:
                raise ValidationError(f'Недостатня кількість товарів {title} на складі \
                В наявності - {product.quantity}')

            OrderItem.objects.create(
                order=order,
                product=product,
                name=title,
                price=price,
                quantity=quantity,
            )
            product.quantity -= quantity
            product.save()

            cart_items.delete()

    def send_email(self, order):
        html_body = render_to_string('orders/order_email.html', {'order': order})

        msg = EmailMultiAlternatives(subject=f'Дякуємо за замовлення #{order.id} на Sneakers_shop.com',
                                     to=[order.email])
        msg.attach_alternative(html_body, 'text/html')
        msg.send()

    def handle_success_redirect(self, user, form):
        if self.request.user.is_authenticated:
            return redirect('user:profile')

        if form.cleaned_data['requires_registration'] == '1':
            auth.login(self.request, user)
            return redirect('user:profile')

        if form.cleaned_data['requires_registration'] == '0':
            return redirect('goods:home')



# def create_order(request):
#     if request.method == 'POST':
#         form = CreateOrderForm(data=request.POST)
#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     session_key = request.session.session_key
#                     if request.user.is_authenticated:  # authorized
#                         user = request.user
#
#                     elif User.objects.filter(email=form.cleaned_data['email']):  # non authorized and exists
#                         messages.warning(request, 'Користувач з таким email вже існує. Будь ласка, увійдіть.')
#                         return redirect('orders:create_order')
#
#                     elif form.cleaned_data['requires_registration'] == '1':  # non authorized and want to register
#                         # create user
#                         user = User.objects.create_user(
#                             username=form.cleaned_data['email'],
#                             email=form.cleaned_data['email'],
#                             password=form.cleaned_data['password1'],
#                             first_name=form.cleaned_data['first_name'],
#                             last_name=form.cleaned_data['last_name'],
#                             phone_number=form.cleaned_data['phone_number']
#                         )
#                         user.save()
#                         user.backend = 'users.authentication.EmailAuthBackend'
#
#                         Cart.objects.filter(session_key=session_key).update(user=user)
#
#                     elif form.cleaned_data[
#                         'requires_registration'] == '0':  # non authorized and does not want to register
#                         user = User.objects.create_user(User.objects.make_random_password(),
#                                                         User.objects.make_random_password(),
#                                                         first_name=form.cleaned_data['first_name'],
#                                                         last_name=form.cleaned_data['last_name'])
#                         Cart.objects.filter(session_key=session_key).update(user=user)
#
#                     cart_items = Cart.objects.filter(user=user)
#
#                     if cart_items.exists():
#                         # Создать заказ
#                         order = Order.objects.create(
#                             user=user,
#                             phone_number=form.cleaned_data['phone_number'],
#                             email=form.cleaned_data['email'],
#                             requires_delivery=form.cleaned_data['requires_delivery'],
#                             delivery_address=form.cleaned_data['delivery_address'],
#                             payment_on_get=form.cleaned_data['payment_on_get'],
#                             session=session_key
#                         )
#                         # Создать заказанные товары
#                         for cart_item in cart_items:
#                             product = cart_item.product  # SneakersVariations
#                             title = cart_item.product.sneakers.title
#                             price = cart_item.product.sneakers.sell_price
#                             quantity = cart_item.quantity
#
#                             if product.quantity < quantity:
#                                 raise ValidationError(f'Недостатня кількість товарів {title} на складі \
#                                 В наявності - {product.quantity}')
#
#                             OrderItem.objects.create(
#                                 order=order,
#                                 product=product,
#                                 name=title,
#                                 price=price,
#                                 quantity=quantity,
#                             )
#                             product.quantity -= quantity
#                             product.save()
#
#                         # clear cart
#                         cart_items.delete()
#
#                         html_body = render_to_string('orders/order_email.html', {'order': order})
#
#                         msg = EmailMultiAlternatives(subject=f'Дякуємо за замовлення №{order.id} на Sneakers_shop.com',
#                                                      to=[order.email])
#                         msg.attach_alternative(html_body, 'text/html')
#                         msg.send()
#
#                         messages.success(request, 'Замовлення оформлено!')
#
#                         if form.cleaned_data['requires_registration'] == '1':
#                             auth.login(request, user)
#
#                         if request.user.is_authenticated:
#                             return redirect('user:profile')
#
#                         if form.cleaned_data['requires_registration'] == '0':
#                             return redirect('goods:home')
#
#                     else:
#                         raise ValidationError(f'Ваш кошик порожній')
#
#             except ValidationError as e:
#                 messages.warning(request, '; '.join(e.messages))
#                 return redirect('orders:create_order')
#     else:
#         if request.user.is_authenticated:
#             initial = {
#                 'first_name': request.user.first_name,
#                 'last_name': request.user.last_name,
#                 'phone_number': request.user.phone_number,
#                 'email': request.user.email,
#             }
#             form = CreateOrderForm(initial=initial)
#         else:
#             form = CreateOrderForm()
#
#     data = DataMixin().get_user_context(title="Створення замовлення", request=request)
#     context = {'form': form, 'order': True, **data}
#
#     return render(request, 'orders/create_order.html', context=context)
