from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.views.generic.edit import FormMixin
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ViewSet, ModelViewSet

from sneakers.settings import MAX_RECENT_VIEWED_PRODUCTS
from .forms import ReviewForm
from .mixins import WishMixin
from .models import *
from django.views.generic import ListView, DetailView

from .serializers import SneakersSerializer
from .utils import DataMixin, SneakersFilter, get_product_from_wishes


class SneakersHome(DataMixin, ListView):
    model = Sneakers  # модель
    template_name = 'goods/index.html'
    context_object_name = 'sneakers'

    def get_context_data(self, *, object_list=None, **kwargs):  # формирует контекст который передаеться в шаблон
        context = super().get_context_data(**kwargs)  # получить контекст который уже есть
        promo_products = self.model.objects.filter(is_published=1).annotate(
            sneakers_first_image=F("first_image__image"),
            total_quantity=Sum('variations__quantity')).filter(discount__gt=0.0)
        brands = Brand.objects.all()
        c_def = self.get_user_context(title='Shop home',
                                      promo_products=promo_products,
                                      brands=brands)

        return dict(list(context.items()) + list(c_def.items()))


class SneakersDetail(DataMixin, FormMixin, DetailView):
    template_name = "goods/product.html"
    slug_url_kwarg = 'product_slug'
    form_class = ReviewForm
    context_object_name = 'post'

    def get_object(self, queryset=None):
        product = Sneakers.objects.prefetch_related('variations', 'reviews__user').annotate(
            sneakers_first_image=F("first_image__image"),
            total_quantity=Sum('variations__quantity')).get(slug=self.kwargs.get(self.slug_url_kwarg))

        recently_viewed(self.request, self.kwargs.get(self.slug_url_kwarg))
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        average_rating = round(self.object.reviews.aggregate(Avg('rate'))['rate__avg'] or 0, 1)

        reviews = self.object.reviews.all().select_related('user').order_by('-date')

        c_def = self.get_user_context(title=self.object.title,
                                             request=self.request,
                                             rating=average_rating,
                                             reviews=reviews,
                                             form=self.form_class)

        return dict(list(context.items()) + list(c_def.items()))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        try:
            review = form.save(commit=False)
            if not self.request.user.is_authenticated:
                raise ValidationError('Ви повинні авторизуватися')
            review.user = self.request.user
            review.product = self.get_object()
            review.save()
            messages.success(self.request, 'Ваш відгук опубліковано')
            return redirect(self.request.path)

        except ValidationError:
            messages.error(self.request, 'Ваш відгук не опубліковано')
            return self.render_to_response({'form': form})

    def form_invalid(self, form):
        messages.error(self.request, 'Ваш відгук не опубліковано')
        return self.render_to_response({'form': form})


class SneakersCategories(DataMixin, ListView):
    queryset = Sneakers.objects.all().filter(is_published=True)
    template_name = 'goods/catalog.html'
    context_object_name = 'sneakers'
    allow_empty = True
    sneakers_filter = None

    def get_template_names(self):
        if self.request.htmx:
            return 'includes/products_list.html'
        return self.template_name

    def get_queryset(self):
        cat_slug = self.kwargs['cat_slug'].split('/')[-1]
        self.current_category = get_object_or_404(Category, slug=cat_slug)
        subcategories = self.current_category.get_descendants(include_self=True)
        queryset = super().get_queryset().filter(cat__in=subcategories).select_related('cat').annotate(
            sneakers_first_image=F("first_image__image"),
            total_quantity=Sum('variations__quantity')
        )

        self.sneakers_filter = SneakersFilter(self.request.GET, queryset=queryset)
        queryset = self.sneakers_filter.qs

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.get(slug=self.kwargs['cat_slug'].split('/')[-1])
        cur_cat = self.current_category
        c_def = self.get_user_context(cats=cats,
                                      filter=self.sneakers_filter,
                                      cur_cat=cur_cat)
        return dict(list(context.items()) + list(c_def.items()))


class SneakersSearch(DataMixin, ListView):
    queryset = Sneakers.objects.all().filter(is_published=True)
    template_name = 'goods/catalog.html'
    context_object_name = 'sneakers'
    allow_empty = True
    sneakers_filter = None

    def get_template_names(self):
        if self.request.htmx:
            return 'includes/products_list.html'
        return self.template_name

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            sneakers_first_image=F("first_image__image"))
        self.sneakers_filter = SneakersFilter(self.request.GET, queryset=queryset)
        queryset = self.sneakers_filter.qs

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(filter=self.sneakers_filter)
        context['is_search_page'] = True

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

    viewed_product = {'slug': product_slug, 'viewed_date': datetime.now().isoformat()}

    request.session["recently_viewed"] = [
        product for product in request.session["recently_viewed"] if product['slug'] != product_slug
    ]
    request.session["recently_viewed"].insert(0, viewed_product)
    if len(request.session["recently_viewed"]) > MAX_RECENT_VIEWED_PRODUCTS:
        request.session["recently_viewed"].pop()

    request.session.modified = True


class FilterReviewsView(View):
    def get(self, request):
        post_id = request.GET.get('post_id')
        sort_by = request.GET.get('sort_by')
        reviews = Review.objects.filter(product=post_id)

        reviews = reviews.order_by(sort_by)

        reviews_block_html = render_to_string(
            'includes/reviews_block.html', {'reviews': reviews}, request=request
        )
        response_data = {
            'reviews_block_html': reviews_block_html,
        }

        return JsonResponse(response_data)


class AddToWishListView(DataMixin, WishMixin, View):
    model = Sneakers

    def get(self, request):
        product_id = request.GET.get('product_id')
        product = self.model.objects.get(id=product_id)

        wish, is_created = self.get_wishes(request, product)

        if not is_created:
            wish.delete()
            message = 'Товар видалено зі списку побажань'
            change_value = -1
        else:
            message = 'Товар додано у список побажань'
            change_value = 1

        response_data = {
            'message': message,
            'change_value': change_value,
            'wish_list_container': self.render_wishes(request),
        }

        return JsonResponse(response_data)


class WishListView(DataMixin, ListView):
    model = Sneakers
    template_name = 'goods/wish_list.html'
    context_object_name = 'wishes'

    def get_queryset(self):
        return get_product_from_wishes(self.request)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TestProductsApiView(ModelViewSet):
    queryset = Sneakers.objects.all()
    serializer_class = SneakersSerializer
