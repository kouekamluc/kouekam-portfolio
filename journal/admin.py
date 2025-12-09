from django.contrib import admin
from .models import JournalEntry, Philosophy, VisionGoal, LifeLesson


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'mood', 'energy_level', 'created_at']
    list_filter = ['mood', 'energy_level', 'date', 'created_at']
    search_fields = ['content', 'tags', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('user', 'date', 'content')
        }),
        ('Tracking', {
            'fields': ('mood', 'energy_level', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Philosophy)
class PhilosophyAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'date_written', 'created_at']
    list_filter = ['category', 'date_written', 'created_at']
    search_fields = ['title', 'content', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'date_written']
    date_hierarchy = 'date_written'
    
    fieldsets = (
        ('Philosophy Information', {
            'fields': ('user', 'title', 'category', 'content')
        }),
        ('Timestamps', {
            'fields': ('date_written', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VisionGoal)
class VisionGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'progress', 'target_date', 'created_at']
    list_filter = ['category', 'target_date', 'created_at']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'target_date'
    
    fieldsets = (
        ('Goal Information', {
            'fields': ('user', 'title', 'description', 'category')
        }),
        ('Progress', {
            'fields': ('progress', 'target_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LifeLesson)
class LifeLessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'date_learned', 'created_at']
    list_filter = ['date_learned', 'created_at']
    search_fields = ['title', 'lesson', 'context', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'date_learned'
    
    fieldsets = (
        ('Lesson Information', {
            'fields': ('user', 'title', 'date_learned')
        }),
        ('Content', {
            'fields': ('lesson', 'context')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
