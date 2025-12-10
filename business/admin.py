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
    actions = ['mark_as_active', 'mark_as_researching', 'mark_as_planning', 'mark_as_paused', 'mark_as_abandoned']
    
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
    
    @admin.action(description='Mark selected ideas as active')
    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} idea(s) marked as active.')
    
    @admin.action(description='Mark selected ideas as researching')
    def mark_as_researching(self, request, queryset):
        updated = queryset.update(status='researching')
        self.message_user(request, f'{updated} idea(s) marked as researching.')
    
    @admin.action(description='Mark selected ideas as planning')
    def mark_as_planning(self, request, queryset):
        updated = queryset.update(status='planning')
        self.message_user(request, f'{updated} idea(s) marked as planning.')
    
    @admin.action(description='Mark selected ideas as paused')
    def mark_as_paused(self, request, queryset):
        updated = queryset.update(status='paused')
        self.message_user(request, f'{updated} idea(s) marked as paused.')
    
    @admin.action(description='Mark selected ideas as abandoned')
    def mark_as_abandoned(self, request, queryset):
        updated = queryset.update(status='abandoned')
        self.message_user(request, f'{updated} idea(s) marked as abandoned.')


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
