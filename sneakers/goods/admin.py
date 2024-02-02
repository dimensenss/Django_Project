from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe
from django_mptt_admin.admin import DjangoMpttAdmin
from mptt.admin import DraggableMPTTAdmin
from django import forms
from taggit.forms import TagField, TagWidget
from taggit.models import Tag

from .models import *

class SneakersVariationInline(admin.TabularInline):
    model = SneakersVariations
    extra = 1




class SneakersImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    readonly_fields = ['get_image']

    def get_image(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' width='100' />")

    get_image.short_description = 'Зображення'


@admin.register(ProductImage)
class SneakersImages(admin.ModelAdmin):
    list_display = ('id', 'get_html_main_photo', 'product_id')
    list_display_links = ('id', 'get_html_main_photo', 'product_id')
    readonly_fields = ('get_html_main_photo',)

    def get_html_main_photo(self, obj):
        if obj.image:
            return mark_safe(f"<img src = '{obj.image.url}' width=100 >")

    get_html_main_photo.short_description = 'Головне фото'




@admin.register(Sneakers)
class SneakersAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_html_main_photo', 'price', 'discount', 'time_create', 'is_published')
    list_display_links = ('id', 'title')
    inlines = [SneakersImageInline, SneakersVariationInline]
    search_fields = ('id', 'title', 'content')
    list_editable = ('discount', 'is_published',)
    list_filter = ('is_published', 'time_create', 'discount')
    prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields = ('variations',)
    fields = (
        ('get_html_main_photo', 'first_image'), ('title','slug'), 'cat', ('price', 'discount', 'calculate_discount'), 'content',
        ('tags', 'get_html_tag_list'),  'is_published', 'time_create',
    )
    readonly_fields = ('get_html_main_photo', 'time_create', 'get_html_tag_list', 'calculate_discount')


    def get_html_content(self, obj):
        if obj.content:
            return obj.content[:24] + '...'

    def get_html_main_photo(self, obj):
        if obj.images.first():
            if not obj.first_image:
                obj.first_image = obj.images.first()
                obj.save()
            return mark_safe(f"<img src = '{obj.images.first().image.url}' width=100 >")

    def get_html_tag_list(self, obj):
        if obj.tags.exists():
            return u", ".join(o.name for o in obj.tags.all())
        return 'Тегів немає'


    def calculate_discount(self, obj):
        s = f"Актуальна ціна: {obj.sell_price} \n "
        discount = 100
        if obj.price:
            discount = (obj.price - obj.discount) * 100 / obj.price

        if discount < 100:
            s += f"Знижка: {discount} %"
        return s

    get_html_content.short_description = 'Опис'
    get_html_main_photo.short_description = 'Головне фото'
    get_html_tag_list.short_description = 'Теги'
    calculate_discount.short_description = 'Актуальна ціна'



@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    list_display = ('id', 'title', 'slug', 'count_products')
    list_display_links = ('id', 'title')
    readonly_fields = ('count_products',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(product_count=Count('sneakers'))
        return queryset

    def count_products(self, obj):
        return obj.product_count

    count_products.short_description = 'Кількість товарів'
