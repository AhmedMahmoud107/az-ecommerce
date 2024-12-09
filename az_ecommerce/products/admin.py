from django.contrib import admin

from az_ecommerce.products.models import (
    Category,
    Product,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    search_fields = ("name",)

