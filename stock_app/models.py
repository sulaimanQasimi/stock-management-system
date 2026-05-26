from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from authorization.models import AuthorizationAuditModel, build_model_permissions


ZERO = Decimal('0.00')


class Category(AuthorizationAuditModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('category', 'category')

    def __str__(self):
        return self.name


class Unit(AuthorizationAuditModel):
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True)

    class Meta:
        permissions = build_model_permissions('unit', 'unit')

    def __str__(self):
        return self.name


class Party(AuthorizationAuditModel):
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

    class Meta:
        permissions = build_model_permissions('party', 'party')

    def __str__(self):
        return self.name


class Product(AuthorizationAuditModel):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pack_sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('product', 'product')

    def __str__(self):
        return self.name

    @property
    def total_bought_base_unit(self):
        return self.purchase_items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO

    @property
    def total_sold_base_unit(self):
        return self.sale_items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO

    @property
    def total_sales_amount(self):
        return self.sale_items.aggregate(total=models.Sum('total'))['total'] or ZERO

    @property
    def total_cost_of_goods_sold(self):
        return self.sale_items.aggregate(total=models.Sum('cost_total'))['total'] or ZERO

    @property
    def gross_profit(self):
        return self.total_sales_amount - self.total_cost_of_goods_sold


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


class Sale(AuthorizationAuditModel):
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

    class Meta:
        ordering = ['-date', '-id']
        permissions = build_model_permissions('sale', 'sale')

    def __str__(self):
        return f"Sale {self.sale_number}"

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
        if not self.net_total:
            return ZERO
        return (self.gross_profit / self.net_total) * Decimal('100')


class SaleItem(AuthorizationAuditModel):
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
    cost_per_base_unit = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    cost_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin_percent = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['id']
        permissions = build_model_permissions('saleitem', 'sale item')

    def __str__(self):
        return f"{self.product} - {self.quantity} {self.pack_or_piece}"

    def clean(self):
        if self.purchase_item_id:
            if self.product_id and self.product_id != self.purchase_item.product_id:
                raise ValidationError('Selected product must match the selected purchase item product.')
            if self.purchase_batch_id and self.purchase_batch_id != self.purchase_item.purchase_id:
                raise ValidationError('Selected purchase batch must match the selected purchase item batch.')

            current_base_unit = ZERO
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
        self.cost_per_base_unit = self.purchase_item.cost_per_base_unit
        self.cost_total = self.total_base_unit * self.cost_per_base_unit
        self.gross_profit = self.total - self.cost_total
        self.profit_margin_percent = ZERO if not self.total else (self.gross_profit / self.total) * Decimal('100')
        self.clean()
        super().save(*args, **kwargs)
        self.sale.update_total()


class SalePayment(AuthorizationAuditModel):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    account = models.ForeignKey('finance.Account', on_delete=models.PROTECT, related_name='sale_payments')
    transaction = models.OneToOneField('finance.Transaction', on_delete=models.PROTECT, related_name='sale_payment')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, related_name='sale_payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        permissions = build_model_permissions('salepayment', 'sale payment')

    def __str__(self):
        return f"Payment for {self.sale.sale_number}"


class StockProfitReport(AuthorizationAuditModel):
    REPORT_SCOPE_CHOICES = (
        ('general', 'General'),
        ('batch', 'Purchase Batch'),
        ('product', 'Product'),
    )

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

        if self.purchase_batch_id:
            purchase_items = purchase_items.filter(purchase=self.purchase_batch)
            sale_items = sale_items.filter(purchase_batch=self.purchase_batch)

        if self.product_id:
            purchase_items = purchase_items.filter(product=self.product)
            sale_items = sale_items.filter(product=self.product)

        if self.date_from:
            purchase_items = purchase_items.filter(purchase__date__gte=self.date_from)
            sale_items = sale_items.filter(sale__date__gte=self.date_from)

        if self.date_to:
            purchase_items = purchase_items.filter(purchase__date__lte=self.date_to)
            sale_items = sale_items.filter(sale__date__lte=self.date_to)

        self.total_bought_base_unit = purchase_items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO
        self.total_sold_base_unit = sale_items.aggregate(total=models.Sum('total_base_unit'))['total'] or ZERO
        self.total_remaining_base_unit = self.total_bought_base_unit - self.total_sold_base_unit
        self.total_purchase_cost = purchase_items.aggregate(total=models.Sum('total'))['total'] or ZERO
        self.total_cost_of_goods_sold = sale_items.aggregate(total=models.Sum('cost_total'))['total'] or ZERO
        self.total_sales = sale_items.aggregate(total=models.Sum('total'))['total'] or ZERO
        self.gross_profit = self.total_sales - self.total_cost_of_goods_sold
        self.profit_margin_percent = ZERO if not self.total_sales else (self.gross_profit / self.total_sales) * Decimal('100')
        self.remaining_stock_value = self.total_purchase_cost - self.total_cost_of_goods_sold
        return self

    def save(self, *args, **kwargs):
        self.calculate()
        super().save(*args, **kwargs)
