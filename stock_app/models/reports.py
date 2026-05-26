from django.db import models

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .constants import ZERO
from .core import Product
from .purchase import PurchaseBatch, PurchaseItem
from .sale import SaleItem
from .stock import StockMovement


class StockProfitReport(AuthorizationAuditModel):
    REPORT_SCOPE_CHOICES = (('general', 'General'), ('batch', 'Purchase Batch'), ('product', 'Product'))
    report_scope = models.CharField(max_length=20, choices=REPORT_SCOPE_CHOICES, default='general')
    purchase_batch = models.ForeignKey(PurchaseBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name='profit_reports')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='profit_reports')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='stock_profit_reports')
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    total_bought_base_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_sold_base_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_remaining_base_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_purchase_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_cost_of_goods_sold = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin_percent = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    remaining_stock_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        permissions = build_model_permissions('stockprofitreport', 'stock profit report')

    def __str__(self):
        if self.report_scope == 'batch' and self.purchase_batch:
            return f"Profit Report - Batch {self.purchase_batch.batch_number}"
        if self.report_scope == 'product' and self.product:
            return f"Profit Report - Product {self.product.name}"
        return 'Profit Report - General'

    def calculate(self):
        purchase_items = PurchaseItem.objects.all()
        sale_items = SaleItem.objects.all()
        movements = StockMovement.objects.all()
        if self.purchase_batch_id:
            purchase_items = purchase_items.filter(purchase=self.purchase_batch)
            sale_items = sale_items.filter(purchase_batch=self.purchase_batch)
        if self.product_id:
            purchase_items = purchase_items.filter(product=self.product)
            sale_items = sale_items.filter(product=self.product)
            movements = movements.filter(product=self.product)
        if self.date_from:
            purchase_items = purchase_items.filter(purchase__date__gte=self.date_from)
            sale_items = sale_items.filter(sale__date__gte=self.date_from)
            movements = movements.filter(movement_date__gte=self.date_from)
        if self.date_to:
            purchase_items = purchase_items.filter(purchase__date__lte=self.date_to)
            sale_items = sale_items.filter(sale__date__lte=self.date_to)
            movements = movements.filter(movement_date__lte=self.date_to)
        increased = movements.filter(movement_type=StockMovement.INCREASE).aggregate(total=models.Sum('quantity'))['total'] or ZERO
        decreased = movements.filter(movement_type=StockMovement.DECREASE).aggregate(total=models.Sum('quantity'))['total'] or ZERO
        self.total_bought_base_unit = purchase_items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO
        self.total_sold_base_unit = sale_items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO
        self.total_remaining_base_unit = increased - decreased
        self.total_purchase_cost = purchase_items.aggregate(total=models.Sum('total'))['total'] or ZERO
        self.total_cost_of_goods_sold = sale_items.aggregate(total=models.Sum('cost_total'))['total'] or ZERO
        self.total_sales = sale_items.aggregate(total=models.Sum('total'))['total'] or ZERO
        self.gross_profit = self.total_sales - self.total_cost_of_goods_sold
        self.profit_margin_percent = ZERO if not self.total_sales else (self.gross_profit / self.total_sales) * 100
        self.remaining_stock_value = max(self.total_purchase_cost - self.total_cost_of_goods_sold, ZERO)
        return self

    def save(self, *args, **kwargs):
        self.calculate()
        super().save(*args, **kwargs)
