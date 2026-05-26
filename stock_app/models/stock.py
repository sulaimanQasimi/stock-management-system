from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .constants import ZERO
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
    INCREASE = 'increase'
    DECREASE = 'decrease'
    TRANSFER = 'transfer'

    MOVEMENT_TYPE_CHOICES = (
        (INCREASE, 'Increase'),
        (DECREASE, 'Decrease'),
        (TRANSFER, 'Transfer'),
    )

    SOURCE_MANUAL = 'manual'
    SOURCE_PURCHASE = 'purchase'
    SOURCE_SALE = 'sale'

    SOURCE_TYPE_CHOICES = (
        (SOURCE_MANUAL, 'Manual'),
        (SOURCE_PURCHASE, 'Purchase'),
        (SOURCE_SALE, 'Sale'),
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    from_department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='stock_out', null=True, blank=True)
    to_department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='stock_in', null=True, blank=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default=SOURCE_MANUAL)
    source_id = models.PositiveBigIntegerField(null=True, blank=True)
    source_line_id = models.PositiveBigIntegerField(null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    movement_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-movement_date', '-id']
        permissions = build_model_permissions('stockmovement', 'stock movement')

    def __str__(self):
        return f'{self.get_movement_type_display()} {self.quantity} {self.product}'

    @classmethod
    def ledger_quantity(cls, product):
        totals = cls.objects.filter(product=product).values('movement_type').annotate(total=Sum('quantity'))
        increased = ZERO
        decreased = ZERO
        for item in totals:
            if item['movement_type'] == cls.INCREASE:
                increased = item['total'] or ZERO
            elif item['movement_type'] == cls.DECREASE:
                decreased = item['total'] or ZERO
        return increased - decreased

    @classmethod
    def sync_product_quantity(cls, product):
        product.quantity = cls.ledger_quantity(product)
        product.save(update_fields=['quantity', 'updated_at'])
        return product.quantity

    @classmethod
    def posted_quantity(cls, *, source_type, source_line_id, movement_type):
        return cls.objects.filter(
            source_type=source_type,
            source_line_id=source_line_id,
            movement_type=movement_type,
        ).aggregate(total=Sum('quantity'))['total'] or ZERO

    @classmethod
    def post_delta(cls, *, product, movement_type, target_quantity, source_type, source_id=None, source_line_id=None, reference_number='', reason='', note='', user=None):
        if target_quantity is None:
            target_quantity = ZERO
        target_quantity = Decimal(str(target_quantity))
        posted = cls.posted_quantity(source_type=source_type, source_line_id=source_line_id, movement_type=movement_type)
        delta = target_quantity - posted
        if delta == ZERO:
            cls.sync_product_quantity(product)
            return None

        correcting_type = movement_type
        correcting_quantity = delta
        if delta < ZERO:
            correcting_type = cls.DECREASE if movement_type == cls.INCREASE else cls.INCREASE
            correcting_quantity = abs(delta)

        movement = cls(
            product=product,
            movement_type=correcting_type,
            quantity=correcting_quantity,
            source_type=source_type,
            source_id=source_id,
            source_line_id=source_line_id,
            reference_number=reference_number,
            reason=reason,
            note=note,
        )
        movement.set_created_user(user)
        movement.set_updated_user(user)
        movement.save(skip_stock_check=True)
        return movement

    def clean(self):
        super().clean()
        if self.quantity is None or self.quantity <= Decimal('0'):
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})
        if self.source_type == self.SOURCE_MANUAL:
            if self.movement_type == self.INCREASE and not self.to_department_id:
                raise ValidationError({'to_department': 'Select the department receiving the stock.'})
            if self.movement_type == self.DECREASE and not self.from_department_id:
                raise ValidationError({'from_department': 'Select the department where stock is reduced.'})
            if self.movement_type == self.TRANSFER:
                if not self.from_department_id or not self.to_department_id:
                    raise ValidationError('Transfer requires both from and to departments.')
                if self.from_department_id == self.to_department_id:
                    raise ValidationError({'to_department': 'Transfer departments must be different.'})

    def save(self, *args, **kwargs):
        skip_stock_check = kwargs.pop('skip_stock_check', False)
        if self.pk:
            raise ValidationError('Stock movements cannot be edited after posting. Create a correcting movement instead.')
        self.full_clean()
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.product_id)
            if not skip_stock_check and self.movement_type in [self.DECREASE, self.TRANSFER]:
                available = self.ledger_quantity(product)
                if available < self.quantity:
                    raise ValidationError({'quantity': 'Cannot move more stock than the product currently has.'})
            super().save(*args, **kwargs)
            self.sync_product_quantity(product)
