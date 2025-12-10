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
    search_fields = ['title', 'description']
    readonly_fields = ['slug', 'created_at']
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
    
    def save_model(self, request, obj, form, change):
        """Override save to handle tech_stack JSON field properly"""
        try:
            # Ensure tech_stack is a list if it's a string
            if isinstance(obj.tech_stack, str):
                try:
                    import json
                    obj.tech_stack = json.loads(obj.tech_stack)
                except (json.JSONDecodeError, ValueError):
                    # If it's not valid JSON, split by comma and create a list
                    obj.tech_stack = [item.strip() for item in obj.tech_stack.split(',') if item.strip()]
            elif obj.tech_stack is None:
                obj.tech_stack = []
            elif not isinstance(obj.tech_stack, list):
                obj.tech_stack = []
            
            # Ensure slug is set before saving
            if not obj.slug and obj.title:
                from django.utils.text import slugify
                base_slug = slugify(obj.title)
                obj.slug = base_slug
                # Handle duplicate slugs
                counter = 1
                while Project.objects.filter(slug=obj.slug).exclude(pk=obj.pk if obj.pk else None).exists():
                    obj.slug = f"{base_slug}-{counter}"
                    counter += 1
                    if counter > 100:  # Safety limit
                        break
            
            super().save_model(request, obj, form, change)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving project in admin: {e}", exc_info=True)
            raise


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'caption', 'created_at']
    list_filter = ['created_at']
    search_fields = ['project__title', 'caption']
    readonly_fields = ['created_at']
