from django.contrib import messages
from django.db.models import Prefetch, F, Min, Max
from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from sneakers.settings import MAX_RECENT_VIEWED_PRODUCTS
from .forms import ReviewForm
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
        queryset = Sneakers.objects.filter(is_published=1).annotate(
            sneakers_first_image=F("first_image__image"))

        self.sneakers_filter = SneakersFilter(self.request.GET, queryset=queryset)
        queryset = self.sneakers_filter.qs

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):  # формирует контекст который передаеться в шаблон
        context = super().get_context_data(**kwargs)  # получить контекст который уже есть
        c_def = self.get_user_context(title='Shop home',
                                      filter=self.sneakers_filter)

        return dict(list(context.items()) + list(c_def.items()))


class SneakersDetail(DetailView):
    template_name = "goods/product.html"
    slug_url_kwarg = 'product_slug'
    form_class = ReviewForm
    context_object_name = 'post'

    def get_object(self, queryset=None):
        product = Sneakers.objects.prefetch_related('variations', 'reviews__user').annotate(
            sneakers_first_image=F("first_image__image")).get(slug=self.kwargs.get(self.slug_url_kwarg))

        recently_viewed(self.request, self.kwargs.get(self.slug_url_kwarg))
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        average_rating = self.object.reviews.aggregate(Avg('rate'))['rate__avg']

        if average_rating is not None:
            average_rating = round(average_rating, 1)
        else:
            average_rating = 0

        c_def = DataMixin().get_user_context(title=self.object.title,
                                             request=self.request,
                                             rating=average_rating,
                                             form=self.form_class)

        return dict(list(context.items()) + list(c_def.items()))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = self.get_object()
            review.save()
            messages.success(request, 'Ваш відгук опубліковано')
            return redirect(self.request.path)

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class SneakersCategories(DataMixin, ListView):
    model = Sneakers  # модель
    template_name = 'goods/index.html'
    context_object_name = 'sneakers'
    allow_empty = True
    sneakers_filter = None

    def get_queryset(self):
        cat_slug = self.kwargs['cat_slug'].split('/')[-1]
        current_category = get_object_or_404(Category, slug=cat_slug)

        subcategories = current_category.get_descendants(include_self=True)
        _queryset = Sneakers.objects.filter(cat__in=subcategories, is_published=True).select_related('cat').annotate(
            sneakers_first_image=F("first_image__image"))

        self.sneakers_filter = SneakersFilter(self.request.GET, queryset=_queryset)
        _queryset = self.sneakers_filter.qs

        return _queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.get(slug=self.kwargs['cat_slug'].split('/')[-1])
        c_def = self.get_user_context(cats=cats,
                                      filter=self.sneakers_filter,
                                      )

        return dict(list(context.items()) + list(c_def.items()))


def contacts(request):
    return HttpResponse("contacts")


def about(request):
    return HttpResponse("about")


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
            del request.session["recently_viewed"][MAX_RECENT_VIEWED_PRODUCTS - 1]
    request.session.modified = True


from dal import autocomplete


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Category.objects.all()

        if self.q:
            qs = qs.filter(title__istartswith=self.q)

        return qs


class SneakersAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SneakersVariations.objects.all()

        if self.q:
            qs = qs.filter(sneakers__title__istartswith=self.q)

        return qs


class BrandsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Brand.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs




def update_review(request):
    ...


def delete_review(request):
    ...
