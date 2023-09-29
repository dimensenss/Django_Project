from django.contrib import admin
from django.utils.html import format_html

from .models import *
class SneakerImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class SneakersAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'photo', 'time_create', 'is_published')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'time_create')
    prepopulated_fields = {'slug':('title',)}
    inlines = [SneakerImageInline]

    actions = ['delete_selected_images']

    def delete_selected_images(self, request, queryset):
        for sneaker in queryset:
            sneaker.image_set.all().delete()  # Удаляем все связанные изображения
        self.message_user(request, 'Выбранные изображения были удалены.')

    delete_selected_images.short_description = 'Удалить выбранные изображения'



class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Sneakers, SneakersAdmin)
admin.site.register(Category, CategoryAdmin)

