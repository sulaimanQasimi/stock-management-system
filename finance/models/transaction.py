from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .account import Account


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
