from django import template
import markdown
from markdown.extensions import codehilite, fenced_code
import re

register = template.Library()

@register.filter
def markdownify(content):
    """Convert markdown text to HTML."""
    md = markdown.Markdown(extensions=['codehilite', 'fenced_code'])
    return md.convert(content)

@register.filter
def markdown_excerpt(content, length=150):
    """Extract plain text excerpt from markdown content."""
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Truncate
    if len(text) > length:
        text = text[:length].rsplit(' ', 1)[0] + '...'
    return text

@register.filter
def reading_time(content):
    """Estimate reading time in minutes (average 200 words per minute)."""
    # Remove markdown syntax for word count
    text = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    word_count = len(text.split())
    minutes = max(1, round(word_count / 200))
    return f"{minutes} min read"
