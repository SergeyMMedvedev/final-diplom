from django.contrib import admin

from .models import (
    Category,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
    User,
    Contact,
    Order,
    OrderItem,
    ConfirmEmailToken,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name',
        'last_name',
        'email',
        'password',
        'company',
        'position',
        'type',
    ]
    list_filter = ['first_name']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'url',
        'user',
        'state',
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'category',
    ]


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = [
        'model',
        'product',
        'shop',
        'quantity',
        'price',
        'price_rrc',
    ]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = [
        'product_info',
        'parameter',
        'value',
    ]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'city',
        'street',
        'house',
        'structure',
        'building',
        'apartment',
        'phone',
    ]
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'dt',
        'state',
        'contact',
    ]
    
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order',
        'product_info',
        'quantity',
    ]
    

@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'created_at',
        'key',
    ]