from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import View

from carts.mixins import CartMixin
from carts.models import Cart
from carts.utils import get_user_carts
from goods.models import Sneakers, SneakersVariations


class CartAddView(CartMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        size = request.POST.get('size')
        is_order = request.POST.get('is_order')
        product = SneakersVariations.objects.get(sneakers=product_id, size=size)

        carts = self.get_cart(request, product=product)
        if carts:
            cart = carts[0]
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            Cart.objects.create(user=request.user if request.user.is_authenticated else None,
                                session_key=request.session.session_key if not request.user.is_authenticated else None,
                                product=product, quantity=1)

        create_order_url = reverse_lazy('orders:create_order') if is_order == "true" else None
        response_data = {
            'message': 'Товар додано у кошик',
            'cart_items_html': self.render_cart(request),
            'create_order_url': create_order_url
        }

        return JsonResponse(response_data)


# def cart_add(request):
#     product_id = request.POST.get('product_id')
#     size = request.POST.get('size')
#     is_order = request.POST.get('is_order')
#
#     product = SneakersVariations.objects.get(sneakers=product_id, size=size)
#
#     if request.user.is_authenticated:
#         carts = Cart.objects.filter(user=request.user, product=product)
#
#         if carts.exists():
#             cart = carts[0]
#             if cart:
#                 cart.quantity += 1
#                 cart.save()
#         else:
#             Cart.objects.create(user=request.user, product=product, quantity=1)
#
#     else:
#         carts = Cart.objects.filter(session_key=request.session.session_key, product=product)
#
#         if carts.exists():
#             cart = carts[0]
#             if cart:
#                 cart.quantity += 1
#                 cart.save()
#         else:
#             Cart.objects.create(session_key=request.session.session_key, product=product, quantity=1)
#
#     user_carts = get_user_carts(request)
#
#     if is_order == "true":
#         create_order_url = reverse_lazy('orders:create_order')
#     else:
#         create_order_url = None
#
#     cart_items_html = render_to_string(
#         'carts/includes/included_cart.html', {'carts': user_carts, }, request=request
#     )
#     response_data = {
#         'message': 'Товар додано у кошик',
#         'cart_items_html' : cart_items_html,
#         'create_order_url': create_order_url
#     }
#
#     return JsonResponse(response_data)

class CartChangeView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get('cart_id')
        quantity = request.POST.get('quantity')

        cart = self.get_cart(request, cart_id=cart_id)
        cart.quantity = quantity
        cart.save()

        response_data = {
            'cart_items_html': self.render_cart(request),
        }

        return JsonResponse(response_data)

# def cart_change(request):
#     cart_id = request.POST.get('cart_id')
#     quantity = request.POST.get('quantity')
#
#     cart = Cart.objects.get(id=cart_id)
#     cart.quantity = quantity
#     cart.save()
#
#     user_carts = get_user_carts(request)
#     context = {"carts": user_carts}
#
#     # if referer page is create_order add key orders: True to context
#     referer = request.META.get('HTTP_REFERER')
#     if reverse('orders:create_order') in referer:
#         context["orders"] = True
#
#     cart_items_html = render_to_string(
#         'carts/includes/included_cart.html', context, request=request
#     )
#     response_data = {
#         'cart_items_html': cart_items_html,
#     }
#
#     return JsonResponse(response_data)


class CartDeleteView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get('cart_id')
        cart = self.get_cart(request, cart_id=cart_id)

        quantity_deleted = cart.quantity
        cart.delete()
        response_data = {
            'quantity_deleted': quantity_deleted,
            'message': 'Товар(и) видалено',
            'cart_items_html': self.render_cart(request),
        }

        return JsonResponse(response_data)


# def cart_remove(request):
#     cart_id = request.POST.get('cart_id')
#
#     cart = Cart.objects.get(id=cart_id)
#     quantity_deleted = cart.quantity
#     cart.delete()
#
#     user_carts = get_user_carts(request)
#     context = {"carts": user_carts}
#
#     # if referer page is create_order add key orders: True to context
#     referer = request.META.get('HTTP_REFERER')
#     if reverse('orders:create_order') in referer:
#         context["orders"] = True
#
#     cart_items_html = render_to_string(
#         'carts/includes/included_cart.html', context, request=request
#     )
#     response_data = {
#         'quantity_deleted': quantity_deleted,
#         'message': 'Товар(и) видалено',
#         'cart_items_html': cart_items_html,
#     }
#
#     return JsonResponse(response_data)
