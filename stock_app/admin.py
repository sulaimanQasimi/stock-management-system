from django.contrib import admin, messages

from authorization.models import AuthorizationActivityLog

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


class AuthorizedAdminMixin:
    audit_readonly_fields = (
        'created_by', 'created_at', 'updated_by', 'updated_at',
        'is_trashed', 'trashed_by', 'trashed_at', 'restored_by', 'restored_at',
        'deleted_by', 'deleted_at', 'force_deleted_by', 'force_deleted_at',
    )
    actions = ('trash_selected_records', 'restore_selected_records', 'force_delete_selected_records')

    def get_queryset(self, request):
        manager = getattr(self.model, 'all_objects', None)
        if manager is not None:
            return manager.get_queryset()
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'set_created_user'):
            obj.set_created_user(request.user)
        if hasattr(obj, 'set_updated_user'):
            obj.set_updated_user(request.user)
        super().save_model(request, obj, form, change)
        AuthorizationActivityLog.log(obj, 'update' if change else 'create', request.user)

    @admin.action(description='Trash selected records')
    def trash_selected_records(self, request, queryset):
        count = 0
        for obj in queryset:
            if hasattr(obj, 'trash'):
                obj.trash(user=request.user)
                count += 1
        self.message_user(request, f'{count} record(s) moved to trash.', messages.SUCCESS)

    @admin.action(description='Restore selected records')
    def restore_selected_records(self, request, queryset):
        count = 0
        for obj in queryset:
            if hasattr(obj, 'restore'):
                obj.restore(user=request.user)
                count += 1
        self.message_user(request, f'{count} record(s) restored.', messages.SUCCESS)

    @admin.action(description='Force delete selected records permanently')
    def force_delete_selected_records(self, request, queryset):
        count = 0
        for obj in queryset:
            if hasattr(obj, 'force_delete'):
                obj.force_delete(user=request.user)
                count += 1
        self.message_user(request, f'{count} record(s) permanently deleted.', messages.WARNING)


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    readonly_fields = (
        'total_base_unit', 'sold_base_unit', 'remaining_base_unit', 'cost_per_base_unit',
        'sales_amount', 'cost_of_goods_sold', 'gross_profit', 'remaining_cost_value', 'total',
    )


class PurchasePaymentInline(admin.TabularInline):
    model = PurchasePayment
    extra = 1


@admin.register(PurchaseBatch)
class PurchaseBatchAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('batch_number', 'date', 'party', 'currency', 'total', 'sales_amount', 'cost_of_goods_sold', 'gross_profit', 'remaining_stock_value', 'is_trashed')
    list_filter = ('date', 'currency', 'is_trashed')
    search_fields = ('batch_number', 'invoice_number', 'reference_number', 'party__name')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields + (
        'total', 'bought_base_unit', 'sold_base_unit', 'remaining_base_unit',
        'sales_amount', 'cost_of_goods_sold', 'gross_profit', 'remaining_stock_value',
    )
    inlines = (PurchaseItemInline, PurchasePaymentInline)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = (
        'purchase_batch', 'product', 'per_pack', 'total_base_unit', 'unit_price', 'total',
        'cost_per_base_unit', 'cost_total', 'gross_profit', 'profit_margin_percent',
    )


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 1


@admin.register(Sale)
class SaleAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('sale_number', 'date', 'party', 'currency', 'total', 'discount', 'net_total', 'cost_of_goods_sold', 'gross_profit', 'profit_margin_percent', 'is_trashed')
    list_filter = ('date', 'currency', 'is_trashed')
    search_fields = ('sale_number', 'invoice_number', 'reference_number', 'party__name')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields + ('total', 'net_total', 'cost_of_goods_sold', 'gross_profit', 'profit_margin_percent')
    inlines = (SaleItemInline, SalePaymentInline)


@admin.register(StockProfitReport)
class StockProfitReportAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = (
        'report_scope', 'purchase_batch', 'product', 'currency', 'date_from', 'date_to',
        'total_sales', 'total_cost_of_goods_sold', 'gross_profit', 'profit_margin_percent',
        'remaining_stock_value', 'created_at', 'is_trashed',
    )
    list_filter = ('report_scope', 'currency', 'date_from', 'date_to', 'is_trashed')
    search_fields = ('purchase_batch__batch_number', 'product__name', 'note')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields + (
        'total_bought_base_unit', 'total_sold_base_unit', 'total_remaining_base_unit',
        'total_purchase_cost', 'total_cost_of_goods_sold', 'total_sales', 'gross_profit',
        'profit_margin_percent', 'remaining_stock_value',
    )


@admin.register(Category)
class CategoryAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'is_trashed', 'created_by', 'updated_by')
    list_filter = ('is_trashed',)
    search_fields = ('name',)
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields


@admin.register(Unit)
class UnitAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'is_trashed', 'created_by', 'updated_by')
    list_filter = ('is_trashed',)
    search_fields = ('name', 'abbreviation')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields


@admin.register(Party)
class PartyAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'party_type', 'phone', 'is_trashed', 'created_by', 'updated_by')
    list_filter = ('party_type', 'is_trashed')
    search_fields = ('name', 'phone')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields


@admin.register(Product)
class ProductAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'quantity', 'pack_sale_price', 'unit_sale_price', 'is_trashed')
    list_filter = ('category', 'unit', 'is_trashed')
    search_fields = ('name',)
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields + ('total_bought_base_unit', 'total_sold_base_unit', 'total_sales_amount', 'total_cost_of_goods_sold', 'gross_profit')


@admin.register(PurchaseItem)
class PurchaseItemAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('purchase', 'product', 'quantity', 'piece_or_pack', 'total_base_unit', 'unit_price', 'total', 'is_trashed')
    list_filter = ('piece_or_pack', 'is_trashed')
    search_fields = ('purchase__batch_number', 'product__name')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields + ('total_base_unit', 'total')


@admin.register(PurchasePayment)
class PurchasePaymentAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('purchase', 'account', 'currency', 'transaction', 'is_trashed')
    list_filter = ('currency', 'is_trashed')
    search_fields = ('purchase__batch_number', 'account__name')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields


@admin.register(SaleItem)
class SaleItemAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('sale', 'product', 'purchase_batch', 'quantity', 'pack_or_piece', 'total', 'gross_profit', 'is_trashed')
    list_filter = ('pack_or_piece', 'is_trashed')
    search_fields = ('sale__sale_number', 'product__name', 'purchase_batch__batch_number')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields + ('purchase_batch', 'product', 'total_base_unit', 'unit_price', 'total', 'cost_per_base_unit', 'cost_total', 'gross_profit', 'profit_margin_percent')


@admin.register(SalePayment)
class SalePaymentAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('sale', 'account', 'currency', 'amount', 'transaction', 'is_trashed')
    list_filter = ('currency', 'is_trashed')
    search_fields = ('sale__sale_number', 'account__name')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields
