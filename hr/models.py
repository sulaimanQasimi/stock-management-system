from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    grandfather_name = models.CharField(max_length=100, blank=True)
    nationality_number = models.CharField(max_length=20, unique=True)
    salary_per_month = models.DecimalField(max_digits=12, decimal_places=2)
    date_of_join = models.DateField()
    
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hr_employee_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hr_employee_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.father_name}"

class SalaryPayment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_payments')
    
    persian_year = models.IntegerField()  # e.g. 1405
    persian_month = models.IntegerField()  # 1-12
    payment_date = models.DateField()
    
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hr_payment_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hr_payment_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'persian_year', 'persian_month')

    def __str__(self):
        return f"Payment for {self.employee} - {self.persian_year}/{self.persian_month}"