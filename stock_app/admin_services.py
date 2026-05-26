from django.contrib import admin

from .models import SaleServiceItem, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'created_by', 'updated_by')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        obj.set_created_user(request.user)
        obj.set_updated_user(request.user)
        super().save_model(request, obj, form, change)


@admin.register(SaleServiceItem)
class SaleServiceItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'service', 'quantity', 'unit_price', 'total')
    list_filter = ('service',)
    search_fields = ('sale__sale_number', 'service__name', 'note')
    readonly_fields = ('total', 'created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        obj.set_created_user(request.user)
        obj.set_updated_user(request.user)
        super().save_model(request, obj, form, change)
