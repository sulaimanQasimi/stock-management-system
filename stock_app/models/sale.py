from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .constants import ZERO
from .core import Party, Product
from .purchase import PurchaseBatch, PurchaseItem


class Sale(AuthorizationAuditModel):
    sale_number = models.CharField(max_length=100, unique=True)
    date = models.DateField()
    party = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='sales')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='sales')
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    net_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    reference_number = models.CharField(max_length=100, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-id']
        permissions = build_model_permissions('sale', 'sale')

    def __str__(self):
        return f"Sale {self.sale_number}"

    def clean(self):
        if self.party_id and not self.party.can_buy:
            raise ValidationError({'party': 'Sale party must be a customer or both.'})
        if self.discount > self.total:
            raise ValidationError({'discount': 'Discount cannot be greater than sale total.'})

    def update_total(self):
        total = self.items.aggregate(total=models.Sum('total'))['total'] or ZERO
        self.total = total
        self.net_total = total - self.discount
        self.save(update_fields=['total', 'net_total', 'updated_at'])
        return self.net_total

    @property
    def cost_of_goods_sold(self):
        return self.items.aggregate(total=models.Sum('cost_total'))['total'] or ZERO

    @property
    def gross_profit(self):
        return self.net_total - self.cost_of_goods_sold

    @property
    def profit_margin_percent(self):
        return ZERO if not self.net_total else (self.gross_profit / self.net_total) * Decimal('100')


class SaleItem(AuthorizationAuditModel):
    SALE_UNIT_CHOICES = (('piece', 'Piece'), ('pack', 'Pack'))
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.PROTECT, related_name='sale_items')
    purchase_batch = models.ForeignKey(PurchaseBatch, on_delete=models.PROTECT, related_name='sale_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    pack_or_piece = models.CharField(max_length=10, choices=SALE_UNIT_CHOICES, default='piece')
    per_pack = models.DecimalField(max_digits=12, decimal_places=2, default=1, validators=[MinValueValidator(Decimal('0.01'))])
    total_base_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    cost_per_base_unit = models.DecimalField(max_digits=15, decimal_places=6, default=0, validators=[MinValueValidator(Decimal('0'))])
    cost_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin_percent = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['id']
        permissions = build_model_permissions('saleitem', 'sale item')

    def __str__(self):
        return f"{self.product} - {self.quantity} {self.pack_or_piece}"

    def _calculate_totals(self):
        self.product = self.purchase_item.product
        self.purchase_batch = self.purchase_item.purchase
        if self.pack_or_piece == 'pack':
            self.per_pack = self.purchase_item.per_pack
            self.total_base_unit = self.quantity * self.per_pack
            self.unit_price = self.product.pack_sale_price
        else:
            self.total_base_unit = self.quantity
            self.unit_price = self.product.unit_sale_price
        self.total = self.quantity * self.unit_price
        self.cost_per_base_unit = self.purchase_item.cost_per_base_unit
        self.cost_total = self.total_base_unit * self.cost_per_base_unit
        self.gross_profit = self.total - self.cost_total
        self.profit_margin_percent = ZERO if not self.total else (self.gross_profit / self.total) * Decimal('100')

    def clean(self):
        old = SaleItem.objects.filter(pk=self.pk).first() if self.pk else None
        if old and old.purchase_item_id != self.purchase_item_id:
            raise ValidationError({'purchase_item': 'Purchase item cannot be changed after sale item is posted.'})
        self._calculate_totals()
        current_base_unit = old.total_base_unit if old else ZERO
        available_by_batch = self.purchase_item.remaining_base_unit + current_base_unit
        if self.total_base_unit > available_by_batch:
            raise ValidationError('Sale quantity is greater than the remaining quantity in this purchase item.')
        from .stock import StockMovement
        ledger_available = StockMovement.ledger_quantity(self.product) + current_base_unit
        if self.total_base_unit > ledger_available:
            raise ValidationError('Sale quantity is greater than the current stock ledger quantity.')

    def save(self, *args, **kwargs):
        from .stock import StockMovement
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.sale.update_total()
            StockMovement.post_delta(product=self.product, movement_type=StockMovement.DECREASE, target_quantity=self.total_base_unit, source_type=StockMovement.SOURCE_SALE, source_id=self.sale_id, source_line_id=self.id, reference_number=self.sale.sale_number, reason='Sale stock issued', note=self.note, user=self.updated_by or self.created_by)


class SalePayment(AuthorizationAuditModel):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    account = models.ForeignKey('finance.Account', on_delete=models.PROTECT, related_name='sale_payments')
    transaction = models.OneToOneField('finance.Transaction', on_delete=models.PROTECT, related_name='sale_payment')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='sale_payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    class Meta:
        permissions = build_model_permissions('salepayment', 'sale payment')

    def clean(self):
        if self.transaction_id and self.amount != self.transaction.amount:
            raise ValidationError({'amount': 'Sale payment amount must match the linked transaction amount.'})

    def __str__(self):
        return f"Payment for {self.sale.sale_number}"
