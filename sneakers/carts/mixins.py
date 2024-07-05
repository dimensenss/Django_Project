from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse

from carts.models import Cart
from carts.utils import get_user_carts


class CartMixin:
    def get_cart(self, request, product=None, cart_id=None):
        if not request.user.is_authenticated:
            query_kwargs = {'session_key': request.session.session_key}
        else:
            query_kwargs = {'user': request.user}

        if product:
            query_kwargs['product'] = product
        if cart_id:
            query_kwargs['id'] = cart_id

        return Cart.objects.filter(**query_kwargs).first()

    def render_cart(self, request):
        user_carts = get_user_carts(request)
        context = {'carts': user_carts}

        referer = request.META.get('HTTP_REFERER')
        if reverse('orders:create_order') in referer:
            context['order'] = True

        return render_to_string(
            'carts/includes/included_cart.html', context, request=request
        )