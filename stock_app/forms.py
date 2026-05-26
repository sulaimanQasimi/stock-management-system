from django import forms

from .models import Department, StockMovement


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'from_department', 'to_department', 'reference_number', 'reason', 'note']

    def save(self, commit=True):
        movement = super().save(commit=False)
        movement.source_type = StockMovement.SOURCE_MANUAL
        if commit:
            movement.save()
        return movement
