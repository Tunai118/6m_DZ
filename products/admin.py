from django.contrib import admin

from .models import Product, CeleryTaskLog


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'owner', 'created_at')
    search_fields = ('title', 'description', 'owner__email')


@admin.register(CeleryTaskLog)
class CeleryTaskLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'created_at')