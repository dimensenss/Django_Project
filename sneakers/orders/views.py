from random import randint

from django.contrib import messages, auth
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect

from carts.models import Cart
from goods.utils import DataMixin
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem
from users.models import User


def create_order(request):
    if request.method == 'POST':
        form = CreateOrderForm(data=request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():

                    session_key = request.session.session_key

                    if request.user.is_authenticated: #Авторизирован
                        user = request.user
                    elif User.objects.filter(email=form.cleaned_data['email']): #Не авторизирован но есть аккаунт
                        messages.warning(request, 'Користувач з таким email вже існує. Будь ласка, увійдіть.')
                        return redirect('orders:create_order')

                    elif form.cleaned_data['requires_registration'] == '1': #Не авторизирован и хочет рег
                        # Если неавторизован, создаем нового пользователя
                        user = User.objects.create_user(
                            username=form.cleaned_data['email'],
                            email=form.cleaned_data['email'],
                            password=form.cleaned_data['password1'],
                            first_name=form.cleaned_data['first_name'],
                            last_name=form.cleaned_data['last_name'],
                            phone_number=form.cleaned_data['phone_number']
                        )
                        user.save()
                        user.backend = 'users.authentication.EmailAuthBackend'

                        Cart.objects.filter(session_key=session_key).update(user=user)

                    elif form.cleaned_data['requires_registration'] == '0': #Не авторизирован и не хочет рег
                        user = User.objects.create_user(session_key, User.objects.make_random_password(), f'user{randint(1, 99999)}@example.com')
                        Cart.objects.filter(session_key=session_key).update(user=user)



                    cart_items = Cart.objects.filter(user=user)

                    if cart_items.exists():
                        # Создать заказ
                        order = Order.objects.create(
                            user=user,
                            phone_number=form.cleaned_data['phone_number'],
                            email=form.cleaned_data['email'],
                            requires_delivery=form.cleaned_data['requires_delivery'],
                            delivery_address=form.cleaned_data['delivery_address'],
                            payment_on_get=form.cleaned_data['payment_on_get'],
                            session=Session.objects.get(session_key=session_key)
                        )
                        # Создать заказанные товары
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

                        # Очистить корзину пользователя после создания заказа
                        cart_items.delete()

                        messages.success(request, 'Замовлення оформлено!')

                        if form.cleaned_data['requires_registration'] == '1':
                            auth.login(request, user)

                        if not form.cleaned_data['requires_registration'] == '0' or user.is_authenticated:
                            return redirect('user:profile')

                    else:
                        raise ValidationError(f'Ваш кошик порожній')

            except ValidationError as e:
                messages.warning(request, '; '.join(e.messages))
                return redirect('orders:create_order')
    else:
        if request.user.is_authenticated:
            initial = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone_number': request.user.phone_number,
                'email': request.user.email,
            }
            form = CreateOrderForm(initial=initial)
        else:
            form = CreateOrderForm()

    data = DataMixin().get_user_context(title="Створення замовлення")
    context = {'form': form, 'order': True, **data}

    return render(request, 'orders/create_order.html', context=context)
