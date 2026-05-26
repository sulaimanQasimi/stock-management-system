from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from authorization.models import AuthorizationAuditModel, build_model_permissions


class Currency(AuthorizationAuditModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5, blank=True)

    class Meta:
        permissions = build_model_permissions('currency', 'currency')

    def __str__(self):
        return f"{self.code} - {self.name}"


class Account(AuthorizationAuditModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        permissions = build_model_permissions('account', 'account')

    def __str__(self):
        return f"{self.code} - {self.name}"


class Transaction(AuthorizationAuditModel):
    TRANSACTION_TYPE = (
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        permissions = build_model_permissions('transaction', 'transaction')

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


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
