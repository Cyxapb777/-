from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'customer_name',
                    'email',
                    'first_name',
                    'last_name'
                    )


class BelongTOInline(admin.TabularInline):
    model = BelongTO
    extra = 1
    verbose_name_plural = 'Orders list'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    def total(self, request):
        total = 0
        items = BelongTO.objects.filter(order_id=request.code)
        for i in items:
            computer = Computer.objects.get(name=i.item_id)
            total += computer.price
        return total

    readonly_fields = ('total',)
    list_display = ('code', 'customer', 'total', 'is_open', 'date',)
    inlines = (BelongTOInline,)


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    def orders(self, request):
        orders = []
        for s in BelongTO.objects.filter(item_id=request.name):
            orders.append(s.order_id)
        return orders

    inlines = (BelongTOInline,)
    list_display = ('name',
                    'price',
                    'description',
                    'pic',
                    'type',
                    'quantity',
                    'orders')
