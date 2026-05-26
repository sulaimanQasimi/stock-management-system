from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Party(models.Model):
    name = models.CharField(max_length=200)
    party_type = models.CharField(
        max_length=20,
        choices=[
            ('customer', 'Customer'),
            ('supplier', 'Supplier'),
            ('both', 'Both'),
        ],
        default='customer'
    )
    
    is_customer = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    national_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    
    email = models.EmailField(blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='party_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='party_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Party"
        verbose_name_plural = "Parties"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_party_type_display()})"

    def save(self, *args, **kwargs):
        if self.party_type == 'both':
            self.is_customer = True
            self.is_supplier = True
        elif self.party_type == 'customer':
            self.is_customer = True
        elif self.party_type == 'supplier':
            self.is_supplier = True
        super().save(*args, **kwargs)
