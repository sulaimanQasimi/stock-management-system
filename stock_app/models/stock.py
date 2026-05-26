from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .core import Product


class Department(AuthorizationAuditModel):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=30, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        permissions = build_model_permissions('department', 'department')

    def __str__(self):
        return self.name


class StockMovement(AuthorizationAuditModel):
    MOVEMENT_TYPE_CHOICES = (
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('transfer', 'Transfer'),
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    from_department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='stock_out', null=True, blank=True)
    to_department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='stock_in', null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    movement_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-movement_date', '-id']
        permissions = build_model_permissions('stockmovement', 'stock movement')

    def __str__(self):
        return f'{self.get_movement_type_display()} {self.quantity} {self.product}'

    def clean(self):
        super().clean()
        if self.quantity is None or self.quantity <= Decimal('0'):
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})
        if self.movement_type == 'increase' and not self.to_department_id:
            raise ValidationError({'to_department': 'Select the department receiving the stock.'})
        if self.movement_type == 'decrease' and not self.from_department_id:
            raise ValidationError({'from_department': 'Select the department where stock is reduced.'})
        if self.movement_type == 'transfer':
            if not self.from_department_id or not self.to_department_id:
                raise ValidationError('Transfer requires both from and to departments.')
            if self.from_department_id == self.to_department_id:
                raise ValidationError({'to_department': 'Transfer departments must be different.'})

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError('Stock movements cannot be edited after posting. Create a correcting movement instead.')
        self.full_clean()
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.product_id)
            if self.movement_type == 'increase':
                product.quantity = product.quantity + self.quantity
            elif self.movement_type == 'decrease':
                if product.quantity < self.quantity:
                    raise ValidationError({'quantity': 'Cannot decrease more stock than the product currently has.'})
                product.quantity = product.quantity - self.quantity
            elif self.movement_type == 'transfer' and product.quantity < self.quantity:
                raise ValidationError({'quantity': 'Cannot transfer more stock than the product currently has.'})
            product.save(update_fields=['quantity', 'updated_at'])
            super().save(*args, **kwargs)
