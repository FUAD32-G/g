from django import forms
from .models import Case

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['customer_name', 'phone_number', 'product_type', 'priority', 'deadline']