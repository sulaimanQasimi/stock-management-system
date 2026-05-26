from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .core import Party, Product
from .purchase import PurchaseBatch, PurchaseItem
from .sale import Sale


class ProductReorderRule(AuthorizationAuditModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='reorder_rule')
    minimum_stock = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    reorder_quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    preferred_supplier = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True, related_name='preferred_reorder_products')
    is_active = models.BooleanField(default=True)

    class Meta:
        permissions = build_model_permissions('productreorderrule', 'product reorder rule')
        ordering = ['product__name']

    @property
    def is_low_stock(self):
        return self.is_active and self.product.quantity <= self.minimum_stock

    def __str__(self):
        return f'Reorder rule for {self.product}'


class ApprovalRequest(AuthorizationAuditModel):
    STATUS_CHOICES = (('draft', 'Draft'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('posted', 'Posted'))
    WORKFLOW_CHOICES = (('purchase', 'Purchase'), ('sale', 'Sale'), ('stock_transfer', 'Stock transfer'), ('stock_adjustment', 'Stock adjustment'), ('return', 'Return'))
    workflow_type = models.CharField(max_length=40, choices=WORKFLOW_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    title = models.CharField(max_length=200)
    reference_number = models.CharField(max_length=100, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    requested_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_requests')
    reviewed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('approvalrequest', 'approval request')
        ordering = ['-created_at']

    def approve(self, user=None):
        self.status = 'approved'
        self.reviewed_by = user if user and user.is_authenticated else None
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

    def reject(self, user=None):
        self.status = 'rejected'
        self.reviewed_by = user if user and user.is_authenticated else None
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

    def __str__(self):
        return f'{self.workflow_type}: {self.title}'


class BusinessDocument(AuthorizationAuditModel):
    DOCUMENT_TYPES = (('sale_invoice', 'Sale invoice'), ('purchase_invoice', 'Purchase invoice'), ('receipt', 'Receipt'), ('attachment', 'Attachment'))
    document_type = models.CharField(max_length=40, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    reference_number = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='business-documents/', blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    issued_at = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = build_model_permissions('businessdocument', 'business document')
        ordering = ['-issued_at']

    def __str__(self):
        return self.title


class PartyLedgerEntry(AuthorizationAuditModel):
    ENTRY_TYPES = (('sale', 'Sale'), ('purchase', 'Purchase'), ('payment', 'Payment'), ('return', 'Return'), ('adjustment', 'Adjustment'))
    party = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='ledger_entries')
    entry_type = models.CharField(max_length=30, choices=ENTRY_TYPES)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    reference_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    posted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = build_model_permissions('partyledgerentry', 'party ledger entry')
        ordering = ['-posted_at']

    @property
    def balance_effect(self):
        return self.debit - self.credit

    def __str__(self):
        return f'{self.party} {self.entry_type} {self.balance_effect}'


class ReturnRecord(AuthorizationAuditModel):
    RETURN_TYPES = (('customer_return', 'Customer return'), ('supplier_return', 'Supplier return'), ('damaged_return', 'Damaged return'))
    STATUS_CHOICES = (('draft', 'Draft'), ('approved', 'Approved'), ('posted', 'Posted'), ('cancelled', 'Cancelled'))
    return_number = models.CharField(max_length=100, unique=True)
    return_type = models.CharField(max_length=30, choices=RETURN_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    party = models.ForeignKey(Party, on_delete=models.PROTECT, null=True, blank=True, related_name='returns')
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    purchase_batch = models.ForeignKey(PurchaseBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    reason = models.TextField(blank=True)
    return_date = models.DateField(default=timezone.now)

    class Meta:
        permissions = build_model_permissions('returnrecord', 'return record')
        ordering = ['-return_date', '-id']

    def __str__(self):
        return self.return_number


class ReturnItem(AuthorizationAuditModel):
    return_record = models.ForeignKey(ReturnRecord, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='return_items')
    quantity = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    note = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('returnitem', 'return item')

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f'{self.product} return {self.quantity}'


class StockAdjustmentReason(AuthorizationAuditModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    requires_approval = models.BooleanField(default=True)

    class Meta:
        permissions = build_model_permissions('stockadjustmentreason', 'stock adjustment reason')
        ordering = ['name']

    def __str__(self):
        return self.name


class StockCountSession(AuthorizationAuditModel):
    STATUS_CHOICES = (('draft', 'Draft'), ('counting', 'Counting'), ('review', 'Review'), ('posted', 'Posted'), ('cancelled', 'Cancelled'))
    count_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_date = models.DateField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('stockcountsession', 'stock count session')
        ordering = ['-scheduled_date', '-id']

    def __str__(self):
        return self.count_number


class StockCountLine(AuthorizationAuditModel):
    session = models.ForeignKey(StockCountSession, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_count_lines')
    system_quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    counted_quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    note = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('stockcountline', 'stock count line')
        unique_together = ('session', 'product')

    @property
    def difference(self):
        return self.counted_quantity - self.system_quantity

    def __str__(self):
        return f'{self.session} - {self.product}'


class ProductBatchTracking(AuthorizationAuditModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='tracked_batches')
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='tracked_batches')
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField(null=True, blank=True)
    manufacture_date = models.DateField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])

    class Meta:
        permissions = build_model_permissions('productbatchtracking', 'product batch tracking')
        ordering = ['expiry_date', 'batch_number']
        unique_together = ('product', 'batch_number')

    @property
    def is_expired(self):
        return bool(self.expiry_date and self.expiry_date < timezone.localdate())

    def __str__(self):
        return f'{self.product} - {self.batch_number}'


class CostingConfiguration(AuthorizationAuditModel):
    COSTING_METHODS = (('fifo', 'FIFO'), ('weighted_average', 'Weighted average'), ('batch', 'Batch specific'))
    name = models.CharField(max_length=100, unique=True)
    method = models.CharField(max_length=30, choices=COSTING_METHODS, default='fifo')
    is_default = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('costingconfiguration', 'costing configuration')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.method})'


class AdvancedReportRequest(AuthorizationAuditModel):
    REPORT_TYPES = (('stock_ledger', 'Stock ledger'), ('profit_loss', 'Profit and loss'), ('sales_history', 'Sales history'), ('purchase_history', 'Purchase history'), ('supplier_performance', 'Supplier performance'), ('stock_valuation', 'Stock valuation'))
    report_type = models.CharField(max_length=40, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    generated_file = models.FileField(upload_to='reports/', blank=True)

    class Meta:
        permissions = build_model_permissions('advancedreportrequest', 'advanced report request')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ExportJob(AuthorizationAuditModel):
    EXPORT_TYPES = (('products', 'Products'), ('sales', 'Sales'), ('purchases', 'Purchases'), ('stock_movements', 'Stock movements'), ('reports', 'Reports'))
    FORMAT_CHOICES = (('csv', 'CSV'), ('xlsx', 'Excel'), ('pdf', 'PDF'))
    STATUS_CHOICES = (('queued', 'Queued'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'))
    export_type = models.CharField(max_length=40, choices=EXPORT_TYPES)
    file_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='xlsx')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    file = models.FileField(upload_to='exports/', blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('exportjob', 'export job')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.export_type} export ({self.status})'
