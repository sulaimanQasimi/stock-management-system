from django.contrib import admin

from .models import (
    Category,
    Party,
    Product,
    PurchaseBatch,
    PurchaseItem,
    PurchasePayment,
    Sale,
    SaleItem,
    SalePayment,
    Unit,
)


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    readonly_fields = ('total_base_unit', 'total')


class PurchasePaymentInline(admin.TabularInline):
    model = PurchasePayment
    extra = 1


@admin.register(PurchaseBatch)
class PurchaseBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'date', 'party', 'currency', 'total')
    list_filter = ('date', 'currency')
    search_fields = ('batch_number', 'invoice_number', 'reference_number', 'party__name')
    readonly_fields = ('total',)
    inlines = (PurchaseItemInline, PurchasePaymentInline)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('purchase_batch', 'product', 'per_pack', 'total_base_unit', 'unit_price', 'total')


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_number', 'date', 'party', 'currency', 'total', 'discount', 'net_total')
    list_filter = ('date', 'currency')
    search_fields = ('sale_number', 'invoice_number', 'reference_number', 'party__name')
    readonly_fields = ('total', 'net_total')
    inlines = (SaleItemInline, SalePaymentInline)


admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(Party)
admin.site.register(Product)
admin.site.register(PurchaseItem)
admin.site.register(PurchasePayment)
admin.site.register(SaleItem)
admin.site.register(SalePayment)
