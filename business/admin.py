from django.contrib import admin
from .models import BusinessIdea, MarketResearch, BusinessPlan, ImportExportRecord


class MarketResearchInline(admin.TabularInline):
    model = MarketResearch
    extra = 1
    fields = ['findings', 'date', 'sources']


class BusinessPlanInline(admin.StackedInline):
    model = BusinessPlan
    extra = 0
    fields = ['executive_summary', 'financial_data']


@admin.register(BusinessIdea)
class BusinessIdeaAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MarketResearchInline, BusinessPlanInline]
    
    fieldsets = (
        ('Idea Information', {
            'fields': ('user', 'title', 'description', 'status')
        }),
        ('Market Analysis', {
            'fields': ('market_size', 'competitors')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MarketResearch)
class MarketResearchAdmin(admin.ModelAdmin):
    list_display = ['business_idea', 'date', 'user', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['findings', 'sources', 'business_idea__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'


@admin.register(BusinessPlan)
class BusinessPlanAdmin(admin.ModelAdmin):
    list_display = ['business_idea', 'user', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['executive_summary', 'business_idea__title', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('business_idea', 'user', 'executive_summary')
        }),
        ('Financial Data', {
            'fields': ('financial_data',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImportExportRecord)
class ImportExportRecordAdmin(admin.ModelAdmin):
    list_display = ['product', 'type', 'country', 'quantity', 'value', 'date', 'user']
    list_filter = ['type', 'date', 'country']
    search_fields = ['product', 'description', 'country', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Record Information', {
            'fields': ('user', 'type', 'product', 'country', 'date')
        }),
        ('Details', {
            'fields': ('quantity', 'value', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
