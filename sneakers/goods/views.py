import datetime

from django.contrib import messages


from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import *
from django.views.generic import ListView, DetailView, CreateView
from .utils import DataMixin, SneakersFilter


class SneakersHome(DataMixin, ListView):
    model = Sneakers  # модель
    template_name = 'goods/index.html'  # путь к шаблону (по умолчанию sneakers_list)
    context_object_name = 'sneakers'  # имя коллекции для шаблона (по умолчанию objects_list)
    # allow_empty = False #если вернется пустой список из базы - ошибка 404
    tag = None

    def get_queryset(self):
        _queryset = Sneakers.objects.filter(is_published=1)

        self.sneakers_filter = SneakersFilter(self.request.GET, queryset=_queryset)
        _queryset = self.sneakers_filter.qs

        return _queryset

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

    product = Sneakers.objects.get(slug=product_slug)
    sizes = SneakersVariations.objects.filter(sneakers=product)

    data = DataMixin().get_user_context(title=product.title)

    context = {'sizes': sizes,  "post": product, **data}

    return render(request, "goods/product.html", context=context)


class SneakersCategories(DataMixin, ListView):
    model = Sneakers  # модель
    template_name = 'goods/index.html'
    context_object_name = 'sneakers'
    allow_empty = False

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
