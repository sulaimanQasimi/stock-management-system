from django.db import models

from authorization.models import AuthorizationAuditModel, build_model_permissions
from .currency import Currency


class Account(AuthorizationAuditModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        permissions = build_model_permissions('account', 'account')

    def __str__(self):
        return f"{self.code} - {self.name}"
