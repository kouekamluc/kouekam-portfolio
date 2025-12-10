from django.contrib import admin
from django import forms
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


class ProjectAdminForm(forms.ModelForm):
    """Custom form to handle tech_stack JSONField properly"""
    tech_stack_display = forms.CharField(
        required=False,
        label='Tech Stack',
        help_text="Enter technologies separated by commas (e.g., Python, Django, React) or as JSON array (e.g., [\"Python\", \"Django\"])",
        widget=forms.Textarea(attrs={'rows': 3})
    )
    
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['tech_stack']  # Exclude the original field
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate tech_stack_display from the instance (works for both new and existing)
        try:
            if self.instance and hasattr(self.instance, 'tech_stack'):
                tech_stack = getattr(self.instance, 'tech_stack', None)
                if isinstance(tech_stack, list):
                    self.initial['tech_stack_display'] = ', '.join(str(item) for item in tech_stack)
                elif tech_stack:
                    self.initial['tech_stack_display'] = str(tech_stack)
        except Exception:
            # If there's any error, just leave it empty
            pass
    
    def clean_tech_stack_display(self):
        data = self.cleaned_data.get('tech_stack_display', '').strip()
        if not data:
            return []
        
        # Try to parse as JSON first
        import json
        try:
            parsed = json.loads(data)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
            else:
                return [str(parsed)]
        except (json.JSONDecodeError, ValueError):
            # If not JSON, split by comma
            items = [item.strip() for item in data.split(',') if item.strip()]
            return items
    
    def save(self, commit=True):
        try:
            instance = super().save(commit=False)
            # Set tech_stack from the cleaned display field
            tech_stack_list = self.cleaned_data.get('tech_stack_display', [])
            if not isinstance(tech_stack_list, list):
                tech_stack_list = []
            instance.tech_stack = tech_stack_list
            if commit:
                instance.save()
            return instance
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in ProjectAdminForm.save: {e}", exc_info=True)
            raise


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
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
            'fields': ('tech_stack_display', 'image')
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
