import datetime
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.generic import ListView, DetailView
from .utils import DataMixins


class SneakersHome(DataMixins,ListView):
    model = Sneakers # модель
    template_name = 'sneakers_shop/index.html' # путь к шаблону (по умолчанию sneakers_list)
    context_object_name = 'sneakers' #имя коллекции для шаблона (по умолчанию objects_list)
    allow_empty = False #если вернется пустой список из базы - ошибка 404

    def get_queryset(self):
        return Sneakers.objects.filter(is_published = 1)

    def get_context_data(self, *, object_list=None, **kwargs): #формирует контекст который передаеться в шаблон
        context = super().get_context_data(**kwargs) # получить контекст который уже есть
        c_def = self.get_user_context(title = 'Shop home')
        return dict(list(context.items())+list(c_def.items()))

def about(request):
    context = {
        'title': 'About',
    }
    return render(request, 'sneakers_shop/about.html', context= context)

def shop(request):
    return HttpResponse("Shop")

def contacts(request):
    return HttpResponse("contacts")

class ShowProduct(DataMixins,DetailView):
    model = Sneakers
    template_name = 'sneakers_shop/product.html'
    context_object_name = 'post'
    slug_url_kwarg = 'product_slug'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = f"{context['post']}",
                                      cat_selected = f"{context['post'].cat.slug}")

        return dict(list(context.items())+list(c_def.items()))


class SneakersCategories(DataMixins,ListView):
    model = Sneakers # модель
    template_name = 'sneakers_shop/index.html'
    context_object_name = 'sneakers'
    allow_empty = False

    def get_queryset(self):
        return Sneakers.objects.filter(cat__slug = self.kwargs['cat_slug'],
                                       is_published = True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f"{context['sneakers'][0].cat}",
                                      cat_selected=f"{context['sneakers'].first().cat.slug}")

        return dict(list(context.items())+list(c_def.items()))


def PageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')