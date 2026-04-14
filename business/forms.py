from decimal import Decimal, InvalidOperation
from django import forms
from django.utils import timezone
from .models import BusinessIdea, MarketResearch, BusinessPlan, ImportExportRecord


class BusinessIdeaForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        market_size = (cleaned_data.get('market_size') or '').strip()
        competitors = (cleaned_data.get('competitors') or '').strip()
        idea = self.instance

        has_market_context = bool(market_size and competitors)
        has_research = bool(getattr(idea, 'pk', None) and idea.market_research.exists())
        has_plan = bool(getattr(idea, 'pk', None) and hasattr(idea, 'business_plan'))

        if status == 'planning' and not (has_market_context or has_research):
            raise forms.ValidationError(
                'Add market sizing and competitor analysis or save at least one market research entry before moving an idea to planning.'
            )

        if status == 'active':
            if not has_plan:
                raise forms.ValidationError(
                    'Create a business plan before marking a business idea as active.'
                )
            if not (has_market_context or has_research):
                raise forms.ValidationError(
                    'Add market sizing, competitor analysis, or saved research before activating a business idea.'
                )

        return cleaned_data

    class Meta:
        model = BusinessIdea
        fields = ['title', 'description', 'status', 'market_size', 'competitors']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800',
                'rows': 6
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'market_size': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800',
                'rows': 4,
                'placeholder': 'Describe the target market size and characteristics...'
            }),
            'competitors': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800',
                'rows': 4,
                'placeholder': 'Analyze your competitors...'
            }),
        }


class MarketResearchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].required = False

    def clean_date(self):
        research_date = self.cleaned_data.get('date')
        if research_date and research_date > timezone.now().date():
            raise forms.ValidationError('Market research cannot be dated in the future.')
        return research_date

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

    def clean_funding_needed(self):
        funding_needed = (self.cleaned_data.get('funding_needed') or '').strip()
        if not funding_needed:
            return ''

        normalized = funding_needed.replace(',', '')
        try:
            amount = Decimal(normalized)
        except InvalidOperation as exc:
            raise forms.ValidationError('Funding needed must be a valid number.') from exc

        if amount < 0:
            raise forms.ValidationError('Funding needed cannot be negative.')

        return str(amount)

    def save(self, commit=True):
        try:
            plan = super().save(commit=False)
            
            # Build financial_data dict from form fields
            # Only access cleaned_data if form is valid
            if hasattr(self, 'cleaned_data') and self.cleaned_data:
                financial_data = {
                    'revenue_projections': self.cleaned_data.get('revenue_projections', '').strip(),
                    'expense_projections': self.cleaned_data.get('expense_projections', '').strip(),
                    'funding_needed': self.cleaned_data.get('funding_needed', '').strip(),
                }
                plan.financial_data = financial_data
            else:
                # If form is not valid, preserve existing financial_data
                if plan.pk and hasattr(plan, 'financial_data') and plan.financial_data:
                    # Keep existing financial_data if available
                    pass
                else:
                    plan.financial_data = {}
            
            if commit:
                try:
                    plan.save()
                except Exception as save_error:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error saving BusinessPlan instance in form: {save_error}", exc_info=True)
                    raise
            
            return plan
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in BusinessPlanForm.save: {e}", exc_info=True)
            raise


class ImportExportRecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].required = False

    def clean_date(self):
        record_date = self.cleaned_data.get('date')
        if record_date and record_date > timezone.now().date():
            raise forms.ValidationError('Trade records cannot be dated in the future.')
        return record_date

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than 0.')
        return quantity

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value is not None and value < 0:
            raise forms.ValidationError('Value cannot be negative.')
        return value

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



