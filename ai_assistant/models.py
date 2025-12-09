from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    ASSISTANT_TYPE_CHOICES = [
        ('general', 'General Assistant'),
        ('study', 'Study Helper'),
        ('code', 'Code Assistant'),
        ('writing', 'Writing Assistant'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True)
    assistant_type = models.CharField(max_length=20, choices=ASSISTANT_TYPE_CHOICES, default='general')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_date']

    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.assistant_type}"

class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

class PromptTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('study', 'Study'),
        ('code', 'Code'),
        ('writing', 'Writing'),
        ('business', 'Business'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompt_templates')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    template_text = models.TextField(help_text="Template with {variables} for dynamic content")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

class PDFAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_analyses')
    file = models.FileField(upload_to='ai_assistant/pdfs/')
    summary = models.TextField(blank=True)
    key_points = models.JSONField(default=list, help_text="List of key points extracted")
    date_analyzed = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-date_analyzed']
        verbose_name_plural = "PDF Analyses"

    def __str__(self):
        return f"Analysis: {self.original_filename or self.file.name}"
