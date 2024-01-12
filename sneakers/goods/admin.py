from django.contrib import admin
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin

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


@admin.register(Sneakers)
class SneakersAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'title', 'get_html_main_photo', 'price', 'discount', 'time_create', 'is_published')
    list_display_links = ('id', 'title')
    inlines = [SneakersImageInline,  ]
    search_fields = ('id', 'title', 'content')
    list_editable = ('discount','is_published',)
    list_filter = ('is_published', 'time_create', 'discount')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('variations',)
    fields = (
    'title',  'cat', ('price', 'discount', 'calculate_discount'), 'content', ('tags', 'get_html_tag_list'), 'color', 'size', 'quantity', 'variations', 'slug', 'is_published', 'time_create',
    )
    readonly_fields = ('get_html_main_photo', 'time_create', 'get_html_tag_list', 'calculate_discount')

    def get_html_content(self, object):
        if object.content:
            return object.content[:24] + '...'

    def get_html_main_photo(self, object):
        main_photo = object.images.first()
        if main_photo:
            return mark_safe(f"<img src = '{main_photo.image.url}' width=100 >")

    def get_html_tag_list(self, object):
        if object.tags.exists():
            return u", ".join(o.name for o in object.tags.all())
        return 'Тегів немає'

    def calculate_discount(self, object):
        s = f"Актуальна ціна: {object.sell_price} \n "
        discount = 100
        if object.price:
            discount = (object.price - object.discount) * 100 / object.price

        if discount < 100:
            s += f"Знижка: {discount} %"
        return s

    get_html_content.short_description = 'Опис'
    get_html_main_photo.short_description = 'Головне фото'
    get_html_tag_list.short_description = 'Теги'
    calculate_discount.short_description = 'Актуальна ціна'


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
#     list_display_links = ('id', 'name')
#     search_fields = ('name',)
#     prepopulated_fields = {'slug': ('name',)}
@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    """
    Админ-панель модели категорий
    """
    list_display = ('tree_actions', 'indented_title', 'id', 'title', 'slug')
    list_display_links = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Основная информация', {'fields': ('title', 'slug', 'parent')}),
    )