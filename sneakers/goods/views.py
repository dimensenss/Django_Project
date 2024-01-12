import datetime

from django.contrib.auth import login, logout

from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from taggit.models import Tag

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
        self.myFilter = SneakersFilter(self.request.GET, queryset=_queryset)
        _queryset = self.myFilter.qs
        return _queryset

    def get_context_data(self, *, object_list=None, **kwargs):  # формирует контекст который передаеться в шаблон
        context = super().get_context_data(**kwargs)  # получить контекст который уже есть
        c_def = self.get_user_context(title='Shop home', filter=self.myFilter)
        c_def['request'] = self.request
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


# class ShowProduct(DataMixin, DetailView):
#     model = Sneakers
#     template_name = 'goods/product.html'
#     context_object_name = 'post'
#     slug_url_kwarg = 'product_slug' # пользовательский слаг по умолчанию django ищет в path "slug"
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title = f"{context['post']}",
#                                       cat_selected = f"{context['post'].cat.slug}")
#
#         return dict(list(context.items())+list(c_def.items()))


def ShowProduct(request, product_slug):

    if product_slug == 'None':
        product_slug = request.POST.get('product_slug')
        product = Sneakers.objects.get(slug=product_slug)

        new_product_page = render_to_string(
            'goods/product_content.html', {'post': product}, request=request
        )
        response_data = {
            'new_product_page': new_product_page,
        }
        return JsonResponse(response_data)

    product = Sneakers.objects.get(slug=product_slug)

    data = DataMixin().get_user_context(title= product.title)
    context = {"post": product, **data}

    return render(request, "goods/product.html", context=context)


# def check_variations(request):
#     product_slug = request.POST.get('product_slug')
#
#     product = Sneakers.objects.get(slug=product_slug)
#
#     new_product_page = render_to_string(
#         'goods/product.html', {'post': product}, request=request
#     )
#     response_data = {
#         'new_product_page': new_product_page,
#     }
#
#     return JsonResponse(response_data)

class SneakersCategories(DataMixin, ListView):
    model = Sneakers  # модель
    template_name = 'goods/index.html'
    context_object_name = 'sneakers'
    allow_empty = False

    def get_queryset(self):
        current_category = Category.objects.get(slug=self.kwargs['cat_slug'])

        # Получаем все подкатегории текущей категории
        subcategories = current_category.get_descendants(include_self=True)

        # Получаем товары из текущей категории и ее подкатегорий
        _queryset = Sneakers.objects.filter(cat__in=subcategories, is_published=True).select_related('cat')
        self.myFilter = SneakersFilter(self.request.GET, queryset=_queryset)
        _queryset = self.myFilter.qs
        return _queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.get(slug=self.kwargs['cat_slug'])
        # title = f"{cats.name}",
        # cat_selected = f"{cats.slug}",
        c_def = self.get_user_context(cats = cats,
                                      filter=self.myFilter)

        return dict(list(context.items()) + list(c_def.items()))


def PageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
