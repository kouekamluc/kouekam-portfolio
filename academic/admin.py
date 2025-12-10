from django.contrib import admin
from .models import Course, Note, Flashcard, StudySession


class NoteInline(admin.TabularInline):
    model = Note
    extra = 1
    fields = ['title', 'file', 'updated_at']


class FlashcardInline(admin.TabularInline):
    model = Flashcard
    extra = 1
    fields = ['question', 'answer']


class StudySessionInline(admin.TabularInline):
    model = StudySession
    extra = 0
    fields = ['date', 'duration_minutes', 'topics_covered']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'user', 'status', 'credits', 'grade', 'created_at']
    list_filter = ['status', 'semester', 'created_at']
    search_fields = ['name', 'code', 'user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [NoteInline, FlashcardInline, StudySessionInline]
    actions = ['mark_as_completed', 'mark_as_ongoing', 'mark_as_dropped']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'code', 'semester')
        }),
        ('Details', {
            'fields': ('credits', 'status', 'grade')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.action(description='Mark selected courses as completed')
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} course(s) marked as completed.')
    
    @admin.action(description='Mark selected courses as ongoing')
    def mark_as_ongoing(self, request, queryset):
        updated = queryset.update(status='ongoing')
        self.message_user(request, f'{updated} course(s) marked as ongoing.')
    
    @admin.action(description='Mark selected courses as dropped')
    def mark_as_dropped(self, request, queryset):
        updated = queryset.update(status='dropped')
        self.message_user(request, f'{updated} course(s) marked as dropped.')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content', 'course__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ['course', 'question_preview', 'created_at']
    list_filter = ['created_at', 'course']
    search_fields = ['question', 'answer', 'course__name']
    readonly_fields = ['created_at']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['course', 'date', 'duration_minutes', 'created_at']
    list_filter = ['date', 'created_at', 'course']
    search_fields = ['course__name', 'topics_covered']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
