from django import template
from django.utils.html import strip_tags
import re

register = template.Library()

@register.filter
def html_excerpt(content, length=150):
    """Extract plain text excerpt from HTML content."""
    # Strip HTML tags
    text = strip_tags(content)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Truncate
    if len(text) > length:
        text = text[:length].rsplit(' ', 1)[0] + '...'
    return text

@register.filter
def reading_time(content):
    """Estimate reading time in minutes (average 200 words per minute)."""
    # Strip HTML tags to get plain text
    text = strip_tags(content)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    word_count = len(text.split())
    minutes = max(1, round(word_count / 200))
    return f"{minutes} min read"

# Keep markdown_excerpt for backward compatibility (now handles HTML)
@register.filter
def markdown_excerpt(content, length=150):
    """Extract plain text excerpt from HTML content (backward compatibility)."""
    return html_excerpt(content, length)
