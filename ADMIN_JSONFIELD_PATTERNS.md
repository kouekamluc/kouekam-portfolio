# Admin JSONField Handling Patterns

This document outlines the standard patterns for handling JSONFields in Django admin forms to prevent 500 errors in production.

## Problem

When handling JSONFields in Django admin forms, common issues include:
- Accessing `cleaned_data` before form validation
- Returning wrong types from `clean_<fieldname>()` methods
- Not handling edge cases (empty values, invalid JSON, etc.)
- Not preserving existing data when form validation fails

## Solution Pattern

### 1. Use Utility Functions

Import and use utility functions from `portfolio.admin_utils`:

```python
from portfolio.admin_utils import (
    parse_json_field_string,
    safe_get_cleaned_data,
    validate_form_before_save
)
```

### 2. Form Structure

```python
class MyAdminForm(forms.ModelForm):
    # Custom display field (exclude original JSONField)
    json_field_display = forms.CharField(required=False, ...)
    
    class Meta:
        model = MyModel
        fields = '__all__'
        exclude = ['json_field']  # Exclude original JSONField
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate display field from instance
        if self.instance and self.instance.pk:
            json_data = getattr(self.instance, 'json_field', None)
            if json_data:
                # Convert to display format
                self.initial['json_field_display'] = format_for_display(json_data)
    
    def clean_json_field_display(self):
        # Just return the string value (don't parse here)
        data = safe_get_cleaned_data(self, 'json_field_display', '')
        return data.strip() if isinstance(data, str) else ''
    
    def save(self, commit=True):
        try:
            instance = super().save(commit=False)
            
            # Parse and set JSONField in save() method
            if validate_form_before_save(self):
                json_str = safe_get_cleaned_data(self, 'json_field_display', '')
                # Use utility function for parsing
                instance.json_field = parse_json_field_string(
                    json_str, 
                    default_value=[],  # or {} for dict
                    field_type='list'  # or 'dict'
                )
            else:
                # Preserve existing data if form invalid
                if instance.pk:
                    # Keep existing data
                    pass
                else:
                    instance.json_field = []  # or {} for dict
            
            if commit:
                try:
                    instance.save()
                except Exception as e:
                    logger.error(f"Error saving: {e}", exc_info=True)
                    raise
            
            return instance
        except Exception as e:
            logger.error(f"Error in form save: {e}", exc_info=True)
            raise
```

### 3. Key Principles

1. **Never parse in `clean_<fieldname>()`**: Just return the string value
2. **Parse in `save()` method**: Use utility functions for parsing
3. **Always validate before accessing cleaned_data**: Use `validate_form_before_save()`
4. **Preserve existing data**: If form is invalid, keep existing JSONField data
5. **Handle edge cases**: Empty values, None, invalid JSON, etc.
6. **Add error logging**: Log errors for production debugging

### 4. Utility Functions

#### `parse_json_field_string(data, default_value=None, field_type='list')`
Safely parses JSON string or comma-separated values.

#### `safe_get_cleaned_data(form, field_name, default='')`
Safely gets data from cleaned_data with fallback to form.data.

#### `validate_form_before_save(form)`
Validates that form is ready for saving.

## Examples

See:
- `portfolio/admin.py` - ProfileAdminForm, ProjectAdminForm
- `business/forms.py` - BusinessPlanForm

## Testing Checklist

- [ ] Form saves successfully with valid data
- [ ] Form handles empty values
- [ ] Form handles invalid JSON gracefully
- [ ] Form preserves existing data when validation fails
- [ ] Form works for both new and existing instances
- [ ] No 500 errors in production logs

