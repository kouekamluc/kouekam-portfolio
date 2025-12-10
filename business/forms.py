from django import forms
from .models import BusinessIdea, MarketResearch, BusinessPlan, ImportExportRecord


class BusinessIdeaForm(forms.ModelForm):
    class Meta:
        model = BusinessIdea
        fields = ['title', 'description', 'status', 'market_size', 'competitors']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 6
            }),
            'status': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'market_size': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Describe the target market size and characteristics...'
            }),
            'competitors': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Analyze your competitors...'
            }),
        }


class MarketResearchForm(forms.ModelForm):
    class Meta:
        model = MarketResearch
        fields = ['findings', 'sources', 'date']
        widgets = {
            'findings': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 8,
                'placeholder': 'Enter your research findings...'
            }),
            'sources': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'List your sources and references...'
            }),
            'date': forms.DateInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
        }


class BusinessPlanForm(forms.ModelForm):
    executive_summary = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'rows': 8
        })
    )
    revenue_projections = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'rows': 4,
            'placeholder': 'Revenue projections...'
        })
    )
    expense_projections = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'rows': 4,
            'placeholder': 'Expense projections...'
        })
    )
    funding_needed = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Amount needed'
        })
    )

    class Meta:
        model = BusinessPlan
        fields = ['executive_summary']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If updating an existing plan, populate fields from financial_data
        if self.instance and self.instance.pk and self.instance.financial_data:
            financial_data = self.instance.financial_data
            self.fields['revenue_projections'].initial = financial_data.get('revenue_projections', '')
            self.fields['expense_projections'].initial = financial_data.get('expense_projections', '')
            self.fields['funding_needed'].initial = financial_data.get('funding_needed', '')

    def save(self, commit=True):
        plan = super().save(commit=False)
        financial_data = {
            'revenue_projections': self.cleaned_data.get('revenue_projections', ''),
            'expense_projections': self.cleaned_data.get('expense_projections', ''),
            'funding_needed': self.cleaned_data.get('funding_needed', ''),
        }
        plan.financial_data = financial_data
        if commit:
            plan.save()
        return plan


class ImportExportRecordForm(forms.ModelForm):
    class Meta:
        model = ImportExportRecord
        fields = ['product', 'quantity', 'value', 'country', 'date', 'type', 'description']
        widgets = {
            'product': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Value in USD'
            }),
            'country': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
            'date': forms.DateInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
            'type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 3
            }),
        }







