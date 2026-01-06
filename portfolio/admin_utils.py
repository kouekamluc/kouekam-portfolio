"""
Utility functions for handling JSONFields in Django admin forms.
This module provides consistent, production-safe methods for parsing
and handling JSONField data in admin forms.
"""
import json
import logging

logger = logging.getLogger(__name__)


def parse_json_field_string(data, default_value=None, field_type='list'):
    """
    Safely parse a JSON field string from form data.
    
    Args:
        data: String data from form (can be JSON or comma-separated)
        default_value: Default value to return if parsing fails (default: [] for list, {} for dict)
        field_type: Expected type - 'list' or 'dict' (default: 'list')
    
    Returns:
        Parsed JSON data (list or dict) or default_value
    """
    if not data:
        return default_value if default_value is not None else ([] if field_type == 'list' else {})
    
    if not isinstance(data, str):
        data = str(data) if data else ''
    
    data = data.strip()
    if not data:
        return default_value if default_value is not None else ([] if field_type == 'list' else {})
    
    # Try to parse as JSON first
    try:
        parsed = json.loads(data)
        if field_type == 'list':
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
            else:
                return [str(parsed).strip()] if parsed else []
        elif field_type == 'dict':
            if isinstance(parsed, dict):
                return parsed
            else:
                return {}
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.debug(f"JSON parsing failed, trying comma-separated: {e}")
        # If not JSON, try comma-separated (for lists only)
        if field_type == 'list':
            items = [item.strip() for item in data.split(',') if item.strip()]
            return items if items else []
        else:
            # For dict, if JSON parsing fails, return default
            return default_value if default_value is not None else {}
    
    return default_value if default_value is not None else ([] if field_type == 'list' else {})


def safe_get_cleaned_data(form, field_name, default=''):
    """
    Safely get cleaned_data from a form, with fallback to form data.
    
    Args:
        form: Django form instance
        field_name: Name of the field to get
        default: Default value if field not found
    
    Returns:
        Field value from cleaned_data or form data, or default
    """
    try:
        if hasattr(form, 'cleaned_data') and form.cleaned_data and field_name in form.cleaned_data:
            return form.cleaned_data.get(field_name, default)
    except (KeyError, AttributeError):
        pass
    
    # Fallback to form data
    try:
        if hasattr(form, 'data') and form.data and field_name in form.data:
            return form.data.get(field_name, default)
    except (KeyError, AttributeError):
        pass
    
    return default


def validate_form_before_save(form):
    """
    Validate that form is valid before attempting to save.
    
    Args:
        form: Django form instance
    
    Returns:
        bool: True if form is valid and ready to save
    """
    if not hasattr(form, 'cleaned_data'):
        return False
    
    if not form.cleaned_data:
        return False
    
    if not form.is_valid():
        return False
    
    return True



