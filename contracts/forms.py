from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import (
    NegotiationThread, ChecklistItem, Workflow, WorkflowTemplate,
    DueDiligenceProcess, DueDiligenceTask, DueDiligenceRisk,
    Budget, BudgetExpense
)

User = get_user_model()


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class NegotiationThreadForm(forms.ModelForm):
    class Meta:
        model = NegotiationThread
        fields = ['round_number', 'internal_note', 'external_note', 'attachment']
        widgets = {
            'round_number': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'internal_note': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm', 'rows': 3}),
            'external_note': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm', 'rows': 3}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none'}),
        }

class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ['title', 'description', 'is_required', 'order']


class DueDiligenceProcessForm(forms.ModelForm):
    class Meta:
        model = DueDiligenceProcess
        fields = ['title', 'transaction_type', 'target_company', 'deal_value', 
                 'lead_attorney', 'start_date', 'target_completion_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_completion_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class DueDiligenceTaskForm(forms.ModelForm):
    class Meta:
        model = DueDiligenceTask
        fields = ['title', 'category', 'description', 'assigned_to', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class DueDiligenceRiskForm(forms.ModelForm):
    class Meta:
        model = DueDiligenceRisk
        fields = ['title', 'category', 'description', 'risk_level', 'likelihood', 
                 'impact', 'mitigation_strategy', 'owner', 'target_resolution_date']
        widgets = {
            'target_resolution_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'mitigation_strategy': forms.Textarea(attrs={'rows': 3}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['year', 'quarter', 'department', 'total_budget', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class BudgetExpenseForm(forms.ModelForm):
    class Meta:
        model = BudgetExpense
        fields = ['title', 'category', 'amount', 'description', 'date_incurred', 
                 'vendor', 'invoice_number']
        widgets = {
            'date_incurred': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['name', 'contract', 'template']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field w-full', 'placeholder': 'Enter workflow name...'}),
            'contract': forms.Select(attrs={'class': 'input-field w-full'}),
            'template': forms.Select(attrs={'class': 'input-field w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all contracts are available
        from .models import Contract
        self.fields['contract'].queryset = Contract.objects.all()
        self.fields['template'].queryset = WorkflowTemplate.objects.filter(is_active=True)
        self.fields['template'].required = False


class WorkflowTemplateForm(forms.ModelForm):
    class Meta:
        model = WorkflowTemplate
        fields = ['name', 'description', 'contract_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contract_type'].required = False


class DueDiligenceForm(forms.ModelForm):
    class Meta:
        model = DueDiligence
        fields = ['title', 'target_company', 'transaction_type', 'status', 'deal_value', 'lead_attorney', 'assigned_team', 'expected_closing', 'notes']
        widgets = {
            'expected_closing': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'assigned_team': forms.CheckboxSelectMultiple(),
        }


class DueDiligenceItemForm(forms.ModelForm):
    class Meta:
        model = DueDiligenceItem
        fields = ['category', 'title', 'description', 'assigned_to', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'category', 'amount', 'expense_date', 'vendor', 'receipt_uploaded', 'notes']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }