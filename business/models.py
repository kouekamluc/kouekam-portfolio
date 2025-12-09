from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BusinessIdea(models.Model):
    STATUS_CHOICES = [
        ('idea', 'Idea'),
        ('researching', 'Researching'),
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_ideas')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idea')
    market_size = models.TextField(blank=True, help_text="Target market size and description")
    competitors = models.TextField(blank=True, help_text="Competitor analysis")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Business Idea'
        verbose_name_plural = 'Business Ideas'

    def __str__(self):
        return self.title

class MarketResearch(models.Model):
    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name='market_research')
    findings = models.TextField()
    sources = models.TextField(blank=True, help_text="Sources and references")
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='market_research')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Market Research'
        verbose_name_plural = 'Market Research'

    def __str__(self):
        return f"Research for {self.business_idea.title} - {self.date}"

class BusinessPlan(models.Model):
    business_idea = models.OneToOneField(BusinessIdea, on_delete=models.CASCADE, related_name='business_plan')
    executive_summary = models.TextField()
    financial_data = models.JSONField(default=dict, help_text="Financial projections and data")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Business Plan'
        verbose_name_plural = 'Business Plans'

    def __str__(self):
        return f"Plan for {self.business_idea.title}"

class ImportExportRecord(models.Model):
    TYPE_CHOICES = [
        ('import', 'Import'),
        ('export', 'Export'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_export_records')
    product = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.DecimalField(max_digits=12, decimal_places=2, help_text="Value in USD")
    country = models.CharField(max_length=100)
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Import/Export Record'
        verbose_name_plural = 'Import/Export Records'

    def __str__(self):
        return f"{self.type.title()}: {self.product} - {self.country}"
