from django.template.loader import render_to_string

from goods.models import Wish
from goods.utils import get_product_from_wishes


class WishMixin:
    def get_wishes(self, request, product=None):
        if request.user.is_authenticated:
            wish, created = Wish.objects.get_or_create(user=request.user, product=product)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            wish, created = Wish.objects.get_or_create(session_key=session_key, product=product)
        return wish, created

    def render_wishes(self, request):
        user_wishes = get_product_from_wishes(request)
        return render_to_string(
            'includes/wish_list_included.html', {'wishes': user_wishes}, request=request
        )
