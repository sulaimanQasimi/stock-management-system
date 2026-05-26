from django.contrib import admin
from .models import Employee, SalaryPayment

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'father_name', 'nationality_number', 'salary_per_month', 'date_of_join', 'is_active']
    list_filter = ['is_active', 'date_of_join']
    search_fields = ['name', 'father_name', 'nationality_number']

@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'persian_year', 'persian_month', 'amount_paid', 'payment_date']
    list_filter = ['persian_year', 'persian_month']
    search_fields = ['employee__name']