from django.contrib import admin
from .models import Task, Habit, Goal, Document, Timetable, Transaction, Milestone


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1
    fields = ['title', 'due_date', 'completed', 'completed_date']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'frequency', 'current_streak', 'last_completed_date', 'created_at']
    list_filter = ['frequency', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'progress', 'target_date', 'created_at']
    list_filter = ['target_date', 'created_at']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MilestoneInline]
    
    fieldsets = (
        ('Goal Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Progress', {
            'fields': ('progress', 'target_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal', 'due_date', 'completed', 'completed_date']
    list_filter = ['completed', 'due_date']
    search_fields = ['title', 'goal__title']
    date_hierarchy = 'due_date'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['type', 'amount', 'category', 'date', 'user', 'created_at']
    list_filter = ['type', 'category', 'date', 'created_at']
    search_fields = ['description', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'type', 'amount', 'category', 'date', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'uploaded_at']
    list_filter = ['category', 'uploaded_at']
    search_fields = ['title', 'tags', 'user__email']
    readonly_fields = ['uploaded_at']
    date_hierarchy = 'uploaded_at'


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'active', 'updated_at']
    list_filter = ['active', 'created_at', 'updated_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
