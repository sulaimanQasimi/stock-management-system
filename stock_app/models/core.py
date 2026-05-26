from django.db import models

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .constants import ZERO


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
