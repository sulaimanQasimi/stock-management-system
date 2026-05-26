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
