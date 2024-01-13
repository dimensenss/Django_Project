from django.shortcuts import render

from goods.utils import DataMixin


def create_order(request):

    data = DataMixin().get_user_context(title="Створення замовлення")
    context = {**data}
    return render(request, 'orders/create_order.html', context = context)