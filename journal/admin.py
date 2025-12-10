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
    actions = ['mark_as_complete', 'reset_progress', 'increase_progress_25', 'increase_progress_50']
    
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
    
    @admin.action(description='Mark selected vision goals as complete (100%)')
    def mark_as_complete(self, request, queryset):
        updated = queryset.update(progress=100)
        self.message_user(request, f'{updated} vision goal(s) marked as complete.')
    
    @admin.action(description='Reset progress to 0%')
    def reset_progress(self, request, queryset):
        updated = queryset.update(progress=0)
        self.message_user(request, f'{updated} vision goal(s) progress reset.')
    
    @admin.action(description='Increase progress by 25%')
    def increase_progress_25(self, request, queryset):
        for goal in queryset:
            goal.progress = min(100, goal.progress + 25)
            goal.save()
        self.message_user(request, f'{queryset.count()} vision goal(s) progress increased by 25%.')
    
    @admin.action(description='Increase progress by 50%')
    def increase_progress_50(self, request, queryset):
        for goal in queryset:
            goal.progress = min(100, goal.progress + 50)
            goal.save()
        self.message_user(request, f'{queryset.count()} vision goal(s) progress increased by 50%.')


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
