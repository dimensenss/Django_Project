from django.contrib import admin

from .models import Cart


class CartTable(admin.TabularInline):
    model = Cart
    fields = ["product", "quantity", "created_timestamp"]
    search_fields = ["product", "quantity", "created_timestamp"]
    readonly_fields = ("created_timestamp",)
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['display_user', 'product', 'quantity', 'created_timestamp']
    list_filter = ['user', 'product', 'created_timestamp']
    readonly_fields = ("created_timestamp",)

    def display_user(self, obj):
        if obj.user:
            if obj.user.first_name and obj.user.last_name:
                return obj.user.first_name, obj.user.last_name
            else:
                return obj.user.username
        return 'Анонімний юзер'
