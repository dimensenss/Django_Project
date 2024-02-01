import datetime

from django.contrib import messages
from django.db.models import Prefetch, F

from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from sneakers.settings import MAX_RECENT_VIEWED_PRODUCTS
from .models import *
from django.views.generic import ListView, DetailView, CreateView
from .utils import DataMixin, SneakersFilter


class SneakersHome(DataMixin, ListView):
    model = Sneakers  # модель
    template_name = 'goods/index.html'  # путь к шаблону (по умолчанию sneakers_list)
    context_object_name = 'sneakers'  # имя коллекции для шаблона (по умолчанию objects_list)
    # allow_empty = False #если вернется пустой список из базы - ошибка 404
    tag = None
    sneakers_filter = None

    def get_queryset(self):
        queryset = Sneakers.objects.filter(is_published=1)

        self.sneakers_filter = SneakersFilter(self.request.GET, queryset=queryset)
        queryset = self.sneakers_filter.qs

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):  # формирует контекст который передаеться в шаблон
        context = super().get_context_data(**kwargs)  # получить контекст который уже есть

        c_def = self.get_user_context(title='Shop home',
                                      filter=self.sneakers_filter)
        return dict(list(context.items()) + list(c_def.items()))


def about(request):
    context = {
        'title': 'About',
    }
    return render(request, 'goods/about.html', context=context)


def shop(request):
    return HttpResponse("Shop")


def contacts(request):
    return HttpResponse("contacts")


def show_product(request, product_slug):
    product = Sneakers.objects.prefetch_related('variations').get(slug=product_slug)


    recently_viewed(request, product_slug)
    data = DataMixin().get_user_context(title=product.title, request=request)

    context = {"post": product, **data}

    return render(request, "goods/product.html", context=context)


class SneakersCategories(DataMixin, ListView):
    model = Sneakers  # модель
    template_name = 'goods/index.html'
    context_object_name = 'sneakers'
    allow_empty = False
    sneakers_filter = None

    def get_queryset(self):
        cat_slug = self.kwargs['cat_slug'].split('/')[-1]
        current_category = Category.objects.get(slug=cat_slug)

        subcategories = current_category.get_descendants(include_self=True)
        _queryset = Sneakers.objects.filter(cat__in=subcategories, is_published=True).select_related('cat')

        self.sneakers_filter = SneakersFilter(self.request.GET, queryset=_queryset)
        _queryset = self.sneakers_filter.qs

        return _queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.get(slug=self.kwargs['cat_slug'].split('/')[-1])
        c_def = self.get_user_context(cats=cats,
                                      filter=self.sneakers_filter)

        return dict(list(context.items()) + list(c_def.items()))


def PageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


def signup_redirect(request):
    messages.warning(request, 'Сталася помилка. Напевно користувач з таким email вже існує.')
    return redirect('goods:home')


def recently_viewed(request, product_slug):
    if "recently_viewed" not in request.session:
        request.session["recently_viewed"] = []
        request.session["recently_viewed"].append(product_slug)
    else:
        if product_slug in request.session["recently_viewed"]:
            request.session["recently_viewed"].remove(product_slug)
        request.session["recently_viewed"].insert(0, product_slug)
        if len(request.session["recently_viewed"]) > MAX_RECENT_VIEWED_PRODUCTS:
            del request.session["recently_viewed"][MAX_RECENT_VIEWED_PRODUCTS-1]
    request.session.modified = True
