import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from taggit.models import Tag

from .forms import RegisterUserForm, LoginUserForm
from .models import *
from django.views.generic import ListView, DetailView, CreateView
from .utils import DataMixin


class SneakersHome(DataMixin, ListView):
    model = Sneakers # модель
    template_name = 'sneakers_shop/index.html' # путь к шаблону (по умолчанию sneakers_list)
    context_object_name = 'sneakers' #имя коллекции для шаблона (по умолчанию objects_list)
    allow_empty = False #если вернется пустой список из базы - ошибка 404

    tag = None

    def get_queryset(self):
        queryset = Sneakers.objects.filter(is_published = 1)
        return queryset



    def get_context_data(self, *, object_list=None, **kwargs): #формирует контекст который передаеться в шаблон
        context = super().get_context_data(**kwargs) # получить контекст который уже есть
        c_def = self.get_user_context(title = 'Shop home', )
        return dict(list(context.items())+list(c_def.items()))

class SneakersTags(SneakersHome):
    tag = None
    def get_queryset(self):
        queryset = Sneakers.objects.filter(is_published = 1)
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[self.tag])
        return queryset

def about(request):
    context = {
        'title': 'About',
    }
    return render(request, 'sneakers_shop/about.html', context= context)

def shop(request):
    return HttpResponse("Shop")

def contacts(request):
    return HttpResponse("contacts")

def logout_user(request):
    logout(request)
    return redirect('home')

class ShowProduct(DataMixin, DetailView):
    model = Sneakers
    template_name = 'sneakers_shop/product.html'
    context_object_name = 'post'
    slug_url_kwarg = 'product_slug' # пользовательский слаг по умолчанию django ищет в path "slug"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = f"{context['post']}",
                                      cat_selected = f"{context['post'].cat.slug}")

        return dict(list(context.items())+list(c_def.items()))


class SneakersCategories(DataMixin, ListView):
    model = Sneakers # модель
    template_name = 'sneakers_shop/index.html'
    context_object_name = 'sneakers'
    allow_empty = False

    def get_queryset(self):
        return Sneakers.objects.filter(cat__slug = self.kwargs['cat_slug'],
                                       is_published = True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.get(slug = self.kwargs['cat_slug'])

        c_def = self.get_user_context(title=f"{cats.name}",
                                      cat_selected=f"{cats.slug}")

        return dict(list(context.items())+list(c_def.items()))


class RegisterUser(DataMixin, CreateView):
    template_name = 'sneakers_shop/register.html'
    success_url = reverse_lazy('login')
    form_class = RegisterUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Register")

        return dict(list(context.items())+list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(DataMixin, LoginView):
    template_name = 'sneakers_shop/login.html'
    form_class = LoginUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Login")

        return dict(list(context.items())+list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')


def PageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')