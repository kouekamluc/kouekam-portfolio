from django.contrib import admin
from django import forms
from .models import Profile, Timeline, Skill, Project, ProjectImage
from .admin_utils import parse_json_field_string, safe_get_cleaned_data, validate_form_before_save


class ProfileAdminForm(forms.ModelForm):
    """Custom form to handle social_links JSONField properly"""
    linkedin = forms.URLField(
        required=False,
        label='LinkedIn URL',
        help_text="Enter your LinkedIn profile URL",
        widget=forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/yourprofile'})
    )
    github = forms.URLField(
        required=False,
        label='GitHub URL',
        help_text="Enter your GitHub profile URL",
        widget=forms.URLInput(attrs={'placeholder': 'https://github.com/yourusername'})
    )
    twitter = forms.URLField(
        required=False,
        label='Twitter/X URL',
        help_text="Enter your Twitter/X profile URL",
        widget=forms.URLInput(attrs={'placeholder': 'https://twitter.com/yourusername'})
    )
    website = forms.URLField(
        required=False,
        label='Website URL',
        help_text="Enter your personal website URL",
        widget=forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'})
    )
    
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['social_links']  # Exclude the original field
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate social link fields from the instance
        try:
            if self.instance and self.instance.pk and hasattr(self.instance, 'social_links'):
                social_links = getattr(self.instance, 'social_links', {}) or {}
                if isinstance(social_links, dict):
                    self.initial['linkedin'] = social_links.get('linkedin', '')
                    self.initial['github'] = social_links.get('github', '')
                    self.initial['twitter'] = social_links.get('twitter', '')
                    self.initial['website'] = social_links.get('website', '')
        except (AttributeError, TypeError, KeyError) as e:
            # If there's any error, just leave them empty
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Error populating social links in ProfileAdminForm.__init__: {e}")
            pass
    
    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        # Additional validation can be added here if needed
        return cleaned_data
    
    def save(self, commit=True):
        try:
            instance = super().save(commit=False)
            # Build social_links dict from form fields
            # Only access cleaned_data if form is valid
            if validate_form_before_save(self):
                social_links = {}
                linkedin = safe_get_cleaned_data(self, 'linkedin', '').strip()
                github = safe_get_cleaned_data(self, 'github', '').strip()
                twitter = safe_get_cleaned_data(self, 'twitter', '').strip()
                website = safe_get_cleaned_data(self, 'website', '').strip()
                
                if linkedin:
                    social_links['linkedin'] = linkedin
                if github:
                    social_links['github'] = github
                if twitter:
                    social_links['twitter'] = twitter
                if website:
                    social_links['website'] = website
                
                instance.social_links = social_links
            else:
                # If form is not valid, preserve existing social_links
                if instance.pk and hasattr(instance, 'social_links'):
                    # Keep existing social_links if available
                    pass
                else:
                    instance.social_links = {}
            
            if commit:
                try:
                    instance.save()
                except Exception as save_error:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error saving Profile instance in form: {save_error}", exc_info=True)
                    raise
            
            return instance
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in ProfileAdminForm.save: {e}", exc_info=True)
            # Re-raise the exception so admin can handle it
            raise


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ['user', 'tagline', 'has_photo', 'has_cv', 'updated_at']
    list_filter = ['updated_at', 'created_at']
    search_fields = ['user__email', 'user__username', 'tagline', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['clear_social_links', 'clear_photo', 'clear_cv']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'tagline', 'bio')
        }),
        ('Media', {
            'fields': ('photo', 'cv_file')
        }),
        ('Social Links', {
            'fields': ('linkedin', 'github', 'twitter', 'website'),
            'description': 'Enter your social media and website URLs'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_photo(self, obj):
        """Check if profile has a photo"""
        if not obj or not obj.pk:
            return False
        try:
            return bool(obj.photo)
        except Exception:
            return False
    has_photo.boolean = True
    has_photo.short_description = 'Has Photo'
    
    def has_cv(self, obj):
        """Check if profile has a CV file"""
        if not obj or not obj.pk:
            return False
        try:
            return bool(obj.cv_file)
        except Exception:
            return False
    has_cv.boolean = True
    has_cv.short_description = 'Has CV'
    
    @admin.action(description='Clear social links for selected profiles')
    def clear_social_links(self, request, queryset):
        updated = queryset.update(social_links={})
        self.message_user(request, f'{updated} profile(s) social links cleared.')
    
    @admin.action(description='Clear photo for selected profiles')
    def clear_photo(self, request, queryset):
        count = 0
        for profile in queryset:
            if profile.photo:
                profile.photo.delete(save=False)
                profile.photo = None
                profile.save()
                count += 1
        self.message_user(request, f'{count} profile(s) photo(s) cleared.')
    
    @admin.action(description='Clear CV file for selected profiles')
    def clear_cv(self, request, queryset):
        count = 0
        for profile in queryset:
            if profile.cv_file:
                profile.cv_file.delete(save=False)
                profile.cv_file = None
                profile.save()
                count += 1
        self.message_user(request, f'{count} profile(s) CV file(s) cleared.')


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
            if self.instance and self.instance.pk and hasattr(self.instance, 'tech_stack'):
                tech_stack = getattr(self.instance, 'tech_stack', None)
                if isinstance(tech_stack, list):
                    self.initial['tech_stack_display'] = ', '.join(str(item) for item in tech_stack)
                elif tech_stack:
                    self.initial['tech_stack_display'] = str(tech_stack)
        except (AttributeError, TypeError, KeyError) as e:
            # If there's any error, just leave it empty
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Error populating tech_stack_display in ProjectAdminForm.__init__: {e}")
            pass
    
    def clean_tech_stack_display(self):
        # In clean_<fieldname>, just return the string value
        # Parsing will happen in save() method for better reliability
        # Get the value - in clean_<fieldname>, we can access it from cleaned_data after base clean
        try:
            data = self.cleaned_data.get('tech_stack_display', '')
        except (KeyError, AttributeError):
            # Fallback to form data if cleaned_data not available yet
            data = self.data.get('tech_stack_display', '') if hasattr(self, 'data') and self.data else ''
        
        # Handle empty or None values - return empty string, we'll convert to list in save()
        if not data:
            return ''
        
        # Ensure it's a string and return as-is (we'll parse it in save method)
        if not isinstance(data, str):
            data = str(data) if data else ''
        
        return data.strip()
    
    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        # Additional validation can be added here if needed
        return cleaned_data
    
    def save(self, commit=True):
        try:
            instance = super().save(commit=False)
            
            # Ensure slug is generated before saving (model's save method will handle this)
            # But we need to make sure title exists for slug generation
            if not instance.slug and instance.title:
                from django.utils.text import slugify
                base_slug = slugify(instance.title)
                if base_slug:
                    instance.slug = base_slug
            
            # Convert tech_stack_display string to list using utility function
            if validate_form_before_save(self):
                tech_stack_str = safe_get_cleaned_data(self, 'tech_stack_display', '')
                tech_stack_list = parse_json_field_string(tech_stack_str, default_value=[], field_type='list')
            else:
                # If form is not valid, preserve existing tech_stack or use default
                if instance.pk and hasattr(instance, 'tech_stack'):
                    tech_stack_list = instance.tech_stack if instance.tech_stack else []
                else:
                    tech_stack_list = []
            
            # Set tech_stack on instance
            instance.tech_stack = tech_stack_list
            
            if commit:
                try:
                    instance.save()
                except Exception as save_error:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error saving Project instance in form: {save_error}", exc_info=True)
                    # Re-raise to show error in admin
                    raise
            
            return instance
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in ProjectAdminForm.save: {e}", exc_info=True)
            # Re-raise the exception so admin can handle it
            raise


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ['title', 'category', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['slug', 'created_at']
    inlines = [ProjectImageInline]
    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_archived']
    
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
    
    @admin.action(description='Mark selected projects as active')
    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} project(s) marked as active.')
    
    @admin.action(description='Mark selected projects as completed')
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} project(s) marked as completed.')
    
    @admin.action(description='Mark selected projects as archived')
    def mark_as_archived(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} project(s) marked as archived.')


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'caption', 'created_at']
    list_filter = ['created_at']
    search_fields = ['project__title', 'caption']
    readonly_fields = ['created_at']
