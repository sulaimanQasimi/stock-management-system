from django.contrib import admin
from .models import Party

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['name', 'party_type', 'is_customer', 'is_supplier', 'phone_number', 'national_id', 'is_active']
    list_filter = ['party_type', 'is_customer', 'is_supplier', 'is_active']
    search_fields = ['name', 'phone_number', 'national_id']
    readonly_fields = ['created_at', 'updated_at']
