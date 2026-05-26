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
    StockProfitReport,
    Unit,
)


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    readonly_fields = (
        'total_base_unit',
        'sold_base_unit',
        'remaining_base_unit',
        'cost_per_base_unit',
        'sales_amount',
        'cost_of_goods_sold',
        'gross_profit',
        'remaining_cost_value',
        'total',
    )


class PurchasePaymentInline(admin.TabularInline):
    model = PurchasePayment
    extra = 1


@admin.register(PurchaseBatch)
class PurchaseBatchAdmin(admin.ModelAdmin):
    list_display = (
        'batch_number',
        'date',
        'party',
        'currency',
        'total',
        'sales_amount',
        'cost_of_goods_sold',
        'gross_profit',
        'remaining_stock_value',
    )
    list_filter = ('date', 'currency')
    search_fields = ('batch_number', 'invoice_number', 'reference_number', 'party__name')
    readonly_fields = (
        'total',
        'bought_base_unit',
        'sold_base_unit',
        'remaining_base_unit',
        'sales_amount',
        'cost_of_goods_sold',
        'gross_profit',
        'remaining_stock_value',
    )
    inlines = (PurchaseItemInline, PurchasePaymentInline)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = (
        'purchase_batch',
        'product',
        'per_pack',
        'total_base_unit',
        'unit_price',
        'total',
        'cost_per_base_unit',
        'cost_total',
        'gross_profit',
        'profit_margin_percent',
    )


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_number', 'date', 'party', 'currency', 'total', 'discount', 'net_total', 'cost_of_goods_sold', 'gross_profit', 'profit_margin_percent')
    list_filter = ('date', 'currency')
    search_fields = ('sale_number', 'invoice_number', 'reference_number', 'party__name')
    readonly_fields = ('total', 'net_total', 'cost_of_goods_sold', 'gross_profit', 'profit_margin_percent')
    inlines = (SaleItemInline, SalePaymentInline)


@admin.register(StockProfitReport)
class StockProfitReportAdmin(admin.ModelAdmin):
    list_display = (
        'report_scope',
        'purchase_batch',
        'product',
        'currency',
        'date_from',
        'date_to',
        'total_sales',
        'total_cost_of_goods_sold',
        'gross_profit',
        'profit_margin_percent',
        'remaining_stock_value',
        'generated_at',
    )
    list_filter = ('report_scope', 'currency', 'date_from', 'date_to')
    search_fields = ('purchase_batch__batch_number', 'product__name', 'note')
    readonly_fields = (
        'total_bought_base_unit',
        'total_sold_base_unit',
        'total_remaining_base_unit',
        'total_purchase_cost',
        'total_cost_of_goods_sold',
        'total_sales',
        'gross_profit',
        'profit_margin_percent',
        'remaining_stock_value',
        'generated_at',
    )


admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(Party)
admin.site.register(Product)
admin.site.register(PurchaseItem)
admin.site.register(PurchasePayment)
admin.site.register(SaleItem)
admin.site.register(SalePayment)
