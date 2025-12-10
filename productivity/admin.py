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
    actions = ['mark_as_done', 'mark_as_in_progress', 'mark_as_todo', 'set_high_priority', 'set_low_priority']
    
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
    
    @admin.action(description='Mark selected tasks as done')
    def mark_as_done(self, request, queryset):
        updated = queryset.update(status='done')
        self.message_user(request, f'{updated} task(s) marked as done.')
    
    @admin.action(description='Mark selected tasks as in progress')
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} task(s) marked as in progress.')
    
    @admin.action(description='Mark selected tasks as to do')
    def mark_as_todo(self, request, queryset):
        updated = queryset.update(status='todo')
        self.message_user(request, f'{updated} task(s) marked as to do.')
    
    @admin.action(description='Set selected tasks to high priority')
    def set_high_priority(self, request, queryset):
        updated = queryset.update(priority='high')
        self.message_user(request, f'{updated} task(s) set to high priority.')
    
    @admin.action(description='Set selected tasks to low priority')
    def set_low_priority(self, request, queryset):
        updated = queryset.update(priority='low')
        self.message_user(request, f'{updated} task(s) set to low priority.')


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
    actions = ['mark_as_complete', 'reset_progress', 'increase_progress_25', 'increase_progress_50']
    
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
    
    @admin.action(description='Mark selected goals as complete (100%)')
    def mark_as_complete(self, request, queryset):
        updated = queryset.update(progress=100)
        self.message_user(request, f'{updated} goal(s) marked as complete.')
    
    @admin.action(description='Reset progress to 0%')
    def reset_progress(self, request, queryset):
        updated = queryset.update(progress=0)
        self.message_user(request, f'{updated} goal(s) progress reset.')
    
    @admin.action(description='Increase progress by 25%')
    def increase_progress_25(self, request, queryset):
        for goal in queryset:
            goal.progress = min(100, goal.progress + 25)
            goal.save()
        self.message_user(request, f'{queryset.count()} goal(s) progress increased by 25%.')
    
    @admin.action(description='Increase progress by 50%')
    def increase_progress_50(self, request, queryset):
        for goal in queryset:
            goal.progress = min(100, goal.progress + 50)
            goal.save()
        self.message_user(request, f'{queryset.count()} goal(s) progress increased by 50%.')


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal', 'due_date', 'completed', 'completed_date']
    list_filter = ['completed', 'due_date']
    search_fields = ['title', 'goal__title']
    date_hierarchy = 'due_date'
    actions = ['mark_as_completed', 'mark_as_incomplete']
    
    @admin.action(description='Mark selected milestones as completed')
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(completed=True, completed_date=timezone.now().date())
        self.message_user(request, f'{updated} milestone(s) marked as completed.')
    
    @admin.action(description='Mark selected milestones as incomplete')
    def mark_as_incomplete(self, request, queryset):
        updated = queryset.update(completed=False, completed_date=None)
        self.message_user(request, f'{updated} milestone(s) marked as incomplete.')


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
