from django import forms
from .models import Contract

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'title',
            'description',
            'counterparty',
            'contract_type',
            'status',
            'execution_date',
            'effective_date',
            'expiration_date',
            'contract_document',
        ]
        widgets = {
            'execution_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.DateInput, forms.Textarea, forms.CheckboxInput)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
