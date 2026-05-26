from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Employee(models.Model):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    grandfather_name = models.CharField(max_length=100, blank=True)
    nationality_number = models.CharField(max_length=20, unique=True)
    salary_per_month = models.DecimalField(max_digits=12, decimal_places=2)
    date_of_join = models.DateField()
    
    # Extra useful fields
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
    
    # Persian calendar for month-based deduction
    persian_year = models.IntegerField()      # e.g., 1405
    persian_month = models.IntegerField()     # 1-12
    payment_date = models.DateField()         # Gregorian date for internal use
    
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)   # Partial / chunk payment
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hr_payment_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hr_payment_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'persian_year', 'persian_month')

    def __str__(self):
        return f"Payment for {self.employee} - {self.persian_year}/{self.persian_month}"


class HRExpense(models.Model):
    """HR-specific expenses/deductions from employee salary"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='hr_expenses')
    
    # Persian calendar for month-based deduction
    persian_year = models.IntegerField()      # e.g., 1405
    persian_month = models.IntegerField()     # 1-12
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Amount to deduct
    reason = models.CharField(max_length=255)                      # e.g., "Advance", "Penalty", "Loan"
    description = models.TextField(blank=True)
    
    # Optional link to salary payment
    salary_payment = models.ForeignKey(
        'SalaryPayment', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deductions'
    )
    
    expense_date = models.DateField(default=timezone.now)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hr_expense_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hr_expense_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HR Expense"
        verbose_name_plural = "HR Expenses"
        ordering = ['-persian_year', '-persian_month']

    def __str__(self):
        return f"{self.amount} deduction for {self.employee} - {self.persian_year}/{self.persian_month}"