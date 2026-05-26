from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., kg, piece, liter
    abbreviation = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Party(models.Model):
    PARTY_TYPE_CHOICES = (
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
        ('both', 'Supplier & Customer'),
    )

    name = models.CharField(max_length=200)
    party_type = models.CharField(max_length=20, choices=PARTY_TYPE_CHOICES, default='supplier')
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pack_sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PurchaseBatch(models.Model):
    batch_number = models.CharField(max_length=100, unique=True)
    date = models.DateField()
    party = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='purchase_batches')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='purchase_batches')
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=100, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_batches_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_batches_updated')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"Purchase {self.batch_number}"

    def update_total(self):
        total = self.items.aggregate(total=models.Sum('total'))['total'] or Decimal('0.00')
        self.total = total
        self.save(update_fields=['total', 'updated_at'])
        return self.total


class PurchaseItem(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.product} - {self.quantity} {self.piece_or_pack}"

    @property
    def sold_base_unit(self):
        return self.sale_items.aggregate(total=models.Sum('total_base_unit'))['total'] or Decimal('0.00')

    @property
    def remaining_base_unit(self):
        return self.total_base_unit - self.sold_base_unit

    def save(self, *args, **kwargs):
        if self.piece_or_pack == 'pack':
            self.total_base_unit = self.quantity * self.per_pack
        else:
            self.total_base_unit = self.quantity

        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.purchase.update_total()


class PurchasePayment(models.Model):
    purchase = models.ForeignKey(PurchaseBatch, on_delete=models.CASCADE, related_name='payments')
    account = models.ForeignKey('finance.Account', on_delete=models.PROTECT, related_name='purchase_payments')
    transaction = models.OneToOneField('finance.Transaction', on_delete=models.PROTECT, related_name='purchase_payment')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='purchase_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.purchase.batch_number}"


class Sale(models.Model):
    sale_number = models.CharField(max_length=100, unique=True)
    date = models.DateField()
    party = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='sales')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='sales')
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=100, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_updated')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"Sale {self.sale_number}"

    def update_total(self):
        total = self.items.aggregate(total=models.Sum('total'))['total'] or Decimal('0.00')
        self.total = total
        self.net_total = total - self.discount
        self.save(update_fields=['total', 'net_total', 'updated_at'])
        return self.net_total


class SaleItem(models.Model):
    SALE_UNIT_CHOICES = (
        ('piece', 'Piece'),
        ('pack', 'Pack'),
    )

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.PROTECT, related_name='sale_items')
    purchase_batch = models.ForeignKey(PurchaseBatch, on_delete=models.PROTECT, related_name='sale_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    pack_or_piece = models.CharField(max_length=10, choices=SALE_UNIT_CHOICES, default='piece')
    per_pack = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    total_base_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.product} - {self.quantity} {self.pack_or_piece}"

    def clean(self):
        if self.purchase_item_id:
            if self.product_id and self.product_id != self.purchase_item.product_id:
                raise ValidationError('Selected product must match the selected purchase item product.')
            if self.purchase_batch_id and self.purchase_batch_id != self.purchase_item.purchase_id:
                raise ValidationError('Selected purchase batch must match the selected purchase item batch.')

            current_base_unit = Decimal('0.00')
            if self.pk:
                old_item = SaleItem.objects.filter(pk=self.pk).first()
                if old_item:
                    current_base_unit = old_item.total_base_unit

            available = self.purchase_item.remaining_base_unit + current_base_unit
            if self.total_base_unit > available:
                raise ValidationError('Sale quantity is greater than the remaining quantity in this purchase item.')

    def save(self, *args, **kwargs):
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
        self.clean()
        super().save(*args, **kwargs)
        self.sale.update_total()


class SalePayment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    account = models.ForeignKey('finance.Account', on_delete=models.PROTECT, related_name='sale_payments')
    transaction = models.OneToOneField('finance.Transaction', on_delete=models.PROTECT, related_name='sale_payment')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='sale_payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.sale.sale_number}"
