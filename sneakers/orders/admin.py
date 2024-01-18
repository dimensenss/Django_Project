from django.contrib import admin

from orders.models import OrderItem, Order


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order',
                    'product',
                    'name',
                    'quantity',
                    'created_timestamp',)

    search_fields = ('order', 'product', 'name',)


class OrderItemAdminTabular(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'name', 'price', 'quantity')
    search_fields = ('product', 'name')
    extra = 0


class OrderAdminTabular(admin.TabularInline):
    model = Order
    fields = (
        "status",
        "requires_delivery",
        "payment_on_get",
        "is_paid",
        "created_timestamp",
    )

    search_fields = (
        "requires_delivery",
        "payment_on_get",
        "is_paid",
        "created_timestamp",
    )
    readonly_fields = ("created_timestamp",)
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "user",
                    "requires_delivery",
                    "status",
                    "payment_on_get",
                    "is_paid",
                    "created_timestamp",
                    )

    list_display_links = ('id', 'user')

    search_fields = ('id', 'is_paid', 'created_timestamp')
    list_filter = ('requires_delivery',
                   'payment_on_get',
                   'is_paid',
                   'created_timestamp',
                   'status',
                   )
    inlines = (OrderItemAdminTabular,)
