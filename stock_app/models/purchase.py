from django.db import models

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .constants import ZERO
from .core import Party, Product, Unit


class PurchaseBatch(AuthorizationAuditModel):
    batch_number = models.CharField(max_length=100, unique=True)
    date = models.DateField()
    party = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='purchase_batches')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='purchase_batches')
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=100, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-id']
        permissions = build_model_permissions('purchasebatch', 'purchase batch')

    def __str__(self):
        return f"Purchase {self.batch_number}"

    def update_total(self):
        total = self.items.aggregate(total=models.Sum('total'))['total'] or ZERO
        self.total = total
        self.save(update_fields=['total', 'updated_at'])
        return self.total

    @property
    def bought_base_unit(self):
        return self.items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO

    @property
    def sold_base_unit(self):
        return self.sale_items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO

    @property
    def remaining_base_unit(self):
        return self.bought_base_unit - self.sold_base_unit

    @property
    def sales_amount(self):
        return self.sale_items.aggregate(total=models.Sum('total'))['total'] or ZERO

    @property
    def cost_of_goods_sold(self):
        return self.sale_items.aggregate(total=models.Sum('cost_total'))['total'] or ZERO

    @property
    def gross_profit(self):
        return self.sales_amount - self.cost_of_goods_sold

    @property
    def remaining_stock_value(self):
        return self.items.aggregate(total=models.Sum('remaining_cost_value'))['total'] or ZERO


class PurchaseItem(AuthorizationAuditModel):
    PURCHASE_UNIT_CHOICES = (
        ('piece', 'Piece'),
        ('pack', 'Pack'),
    )

    purchase = models.ForeignKey(PurchaseBatch, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    piece_or_pack = models.CharField(max_length=10, choices=PURCHASE_UNIT_CHOICES, default='piece')
    unit_for_piece = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='purchase_piece_items')
    unit_for_pack = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='purchase_pack_items', null=True, blank=True)
    per_pack = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    total_base_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['id']
        permissions = build_model_permissions('purchaseitem', 'purchase item')

    def __str__(self):
        return f"{self.product} - {self.quantity} {self.piece_or_pack}"

    @property
    def sold_base_unit(self):
        return self.sale_items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO

    @property
    def remaining_base_unit(self):
        return self.total_base_unit - self.sold_base_unit

    @property
    def cost_per_base_unit(self):
        if not self.total_base_unit:
            return ZERO
        return self.total / self.total_base_unit

    @property
    def sales_amount(self):
        return self.sale_items.aggregate(total=models.Sum('total'))['total'] or ZERO

    @property
    def cost_of_goods_sold(self):
        return self.sale_items.aggregate(total=models.Sum('cost_total'))['total'] or ZERO

    @property
    def gross_profit(self):
        return self.sales_amount - self.cost_of_goods_sold

    @property
    def remaining_cost_value(self):
        return self.remaining_base_unit * self.cost_per_base_unit

    def save(self, *args, **kwargs):
        if self.piece_or_pack == 'pack':
            self.total_base_unit = self.quantity * self.per_pack
        else:
            self.total_base_unit = self.quantity

        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.purchase.update_total()


class PurchasePayment(AuthorizationAuditModel):
    purchase = models.ForeignKey(PurchaseBatch, on_delete=models.CASCADE, related_name='payments')
    account = models.ForeignKey('finance.Account', on_delete=models.PROTECT, related_name='purchase_payments')
    transaction = models.OneToOneField('finance.Transaction', on_delete=models.PROTECT, related_name='purchase_payment')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='purchase_payments')

    class Meta:
        permissions = build_model_permissions('purchasepayment', 'purchase payment')

    def __str__(self):
        return f"Payment for {self.purchase.batch_number}"
