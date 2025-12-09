from django.contrib import admin
from .models import Conversation, Message, PromptTemplate, PDFAnalysis


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['role', 'content_preview', 'timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'assistant_type', 'updated_date', 'created_date']
    list_filter = ['assistant_type', 'created_date', 'updated_date']
    search_fields = ['title', 'user__email']
    readonly_fields = ['created_date', 'updated_date']
    inlines = [MessageInline]
    date_hierarchy = 'created_date'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_preview', 'timestamp']
    list_filter = ['role', 'timestamp']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'template_text', 'user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('user', 'name', 'category', 'description')
        }),
        ('Template Content', {
            'fields': ('template_text',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PDFAnalysis)
class PDFAnalysisAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'date_analyzed']
    list_filter = ['date_analyzed']
    search_fields = ['original_filename', 'summary', 'user__email']
    readonly_fields = ['date_analyzed', 'summary', 'key_points']
    date_hierarchy = 'date_analyzed'
    
    fieldsets = (
        ('File Information', {
            'fields': ('user', 'file', 'original_filename')
        }),
        ('Analysis Results', {
            'fields': ('summary', 'key_points')
        }),
        ('Timestamps', {
            'fields': ('date_analyzed',),
            'classes': ('collapse',)
        }),
    )
