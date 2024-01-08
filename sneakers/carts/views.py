from django.shortcuts import render, redirect

# Create your views here.
from carts.models import Cart
from sneakers_shop.models import Sneakers


def cart_add(request, product_slug):
    product = Sneakers.objects.get(slug=product_slug)

    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user, product=product)

        if carts.exists():
            cart = carts[0]
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            Cart.objects.create(user=request.user, product=product, quantity=1)

    return redirect(request.META.get('HTTP_REFERER'))


def cart_change(request, product_slug):
    pass


def cart_delete(request, product_slug):
    pass

