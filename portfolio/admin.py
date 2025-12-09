from django.contrib import admin
from .models import Profile, Timeline, Skill, Project, ProjectImage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'tagline', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__email', 'user__username', 'tagline', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'tagline', 'bio')
        }),
        ('Media', {
            'fields': ('photo', 'cv_file')
        }),
        ('Social Links', {
            'fields': ('social_links',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'category']
    list_filter = ['category', 'year']
    search_fields = ['title', 'description', 'year']
    
    fieldsets = (
        ('Timeline Information', {
            'fields': ('year', 'title', 'category', 'description')
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency_level', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Skill Information', {
            'fields': ('name', 'category', 'proficiency_level')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'description', 'tech_stack']
    readonly_fields = ['slug', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]
    
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'slug', 'description', 'category', 'status')
        }),
        ('Technical Details', {
            'fields': ('tech_stack', 'image')
        }),
        ('Links', {
            'fields': ('github_url', 'live_link')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'caption', 'created_at']
    list_filter = ['created_at']
    search_fields = ['project__title', 'caption']
    readonly_fields = ['created_at']
