from django.db import models

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .transaction import Transaction


class ExpenseType(AuthorizationAuditModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('expensetype', 'expense type')

    def __str__(self):
        return self.name


class Expense(AuthorizationAuditModel):
    name = models.CharField(max_length=200)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True, blank=True, related_name='expense')
    description = models.TextField(blank=True)

    class Meta:
        permissions = build_model_permissions('expense', 'expense')

    def __str__(self):
        return self.name
