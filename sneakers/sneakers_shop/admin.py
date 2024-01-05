from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *


class SneakersImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    readonly_fields = ['get_image']

    def get_image(self, object):
        return mark_safe(f"<img src='{object.image.url}' width='100' />")

    get_image.short_description = 'Зображення'


@admin.register(ProductImage)
class SneakersImages(admin.ModelAdmin):
    list_display = ('id', 'get_html_main_photo', 'product_id')
    list_display_links = ('id', 'get_html_main_photo', 'product_id')
    readonly_fields = ('get_html_main_photo',)

    def get_html_main_photo(self, object):
        if object.image:
            return mark_safe(f"<img src = '{object.image.url}' width=100 >")

    get_html_main_photo.short_description = 'Головне фото'


class ProductVariantsInline(admin.TabularInline):
    model = Variants
    readonly_fields = ('image_tag',)
    extra = 1
    show_change_link = True


@admin.register(Sneakers)
class SneakersAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'title', 'get_html_main_photo', 'get_html_content', 'get_html_tag_list', 'time_create', 'is_published')
    list_display_links = ('id', 'title')
    inlines = [SneakersImageInline, ProductVariantsInline, ]
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'time_create')
    prepopulated_fields = {'slug': ('title',)}
    fields = (
    'title', 'slug', 'price', 'discount', 'calculate_discount', 'content', 'cat', 'is_published', 'time_create', 'tags',
    'get_html_tag_list')
    readonly_fields = ('get_html_main_photo', 'time_create', 'get_html_tag_list', 'calculate_discount')

    def get_html_content(self, object):
        if object.content:
            return object.content[:24] + '...'

    def get_html_main_photo(self, object):
        main_photo = object.images.first()
        if main_photo:
            return mark_safe(f"<img src = '{main_photo.image.url}' width=100 >")

    def get_html_tag_list(self, object):
        return u", ".join(o.name for o in object.tags.all())

    def calculate_discount(self, object):
        s = f"Актуальна ціна: {object.sell_price} \n "

        discount = (object.price - object.discount) * 100 / object.price

        if discount < 100:
            s += f"Знижка: {discount} %"
        return s

    get_html_content.short_description = 'Опис'
    get_html_main_photo.short_description = 'Головне фото'
    get_html_tag_list.short_description = 'Теги'
    calculate_discount.short_description = 'Актуальна ціна'

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'color_tag']

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
