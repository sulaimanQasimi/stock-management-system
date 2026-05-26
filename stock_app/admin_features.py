from django.contrib import admin

from .models import (
    ProductReorderRule,
    ApprovalRequest,
    BusinessDocument,
    PartyLedgerEntry,
    ReturnRecord,
    ReturnItem,
    StockAdjustmentReason,
    StockCountSession,
    StockCountLine,
    ProductBatchTracking,
    CostingConfiguration,
    AdvancedReportRequest,
    ExportJob,
)


@admin.register(ProductReorderRule)
class ProductReorderRuleAdmin(admin.ModelAdmin):
    list_display = ('product', 'minimum_stock', 'reorder_quantity', 'preferred_supplier', 'is_active', 'is_low_stock')
    list_filter = ('is_active', 'preferred_supplier')
    search_fields = ('product__name', 'product__sku', 'preferred_supplier__name')


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('workflow_type', 'status', 'title', 'reference_number', 'requested_by', 'reviewed_by', 'created_at')
    list_filter = ('workflow_type', 'status', 'created_at')
    search_fields = ('title', 'reference_number', 'note')
    readonly_fields = ('reviewed_at',)


@admin.register(BusinessDocument)
class BusinessDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'title', 'reference_number', 'issued_at')
    list_filter = ('document_type', 'issued_at')
    search_fields = ('title', 'reference_number')


@admin.register(PartyLedgerEntry)
class PartyLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('party', 'entry_type', 'debit', 'credit', 'balance_effect', 'reference_number', 'posted_at')
    list_filter = ('entry_type', 'posted_at')
    search_fields = ('party__name', 'reference_number', 'description')


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 1
    readonly_fields = ('total',)


@admin.register(ReturnRecord)
class ReturnRecordAdmin(admin.ModelAdmin):
    list_display = ('return_number', 'return_type', 'status', 'party', 'return_date')
    list_filter = ('return_type', 'status', 'return_date')
    search_fields = ('return_number', 'party__name', 'reason')
    inlines = (ReturnItemInline,)


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ('return_record', 'product', 'quantity', 'unit_price', 'total')
    search_fields = ('return_record__return_number', 'product__name')


@admin.register(StockAdjustmentReason)
class StockAdjustmentReasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'requires_approval')
    search_fields = ('name', 'description')


class StockCountLineInline(admin.TabularInline):
    model = StockCountLine
    extra = 1
    readonly_fields = ('difference',)


@admin.register(StockCountSession)
class StockCountSessionAdmin(admin.ModelAdmin):
    list_display = ('count_number', 'status', 'scheduled_date', 'completed_at')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('count_number', 'note')
    inlines = (StockCountLineInline,)


@admin.register(StockCountLine)
class StockCountLineAdmin(admin.ModelAdmin):
    list_display = ('session', 'product', 'system_quantity', 'counted_quantity', 'difference')
    search_fields = ('session__count_number', 'product__name')


@admin.register(ProductBatchTracking)
class ProductBatchTrackingAdmin(admin.ModelAdmin):
    list_display = ('product', 'batch_number', 'expiry_date', 'quantity', 'is_expired')
    list_filter = ('expiry_date',)
    search_fields = ('product__name', 'batch_number')


@admin.register(CostingConfiguration)
class CostingConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'method', 'is_default')
    list_filter = ('method', 'is_default')
    search_fields = ('name', 'note')


@admin.register(AdvancedReportRequest)
class AdvancedReportRequestAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'title', 'date_from', 'date_to', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title',)


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ('export_type', 'file_format', 'status', 'created_at')
    list_filter = ('export_type', 'file_format', 'status')
