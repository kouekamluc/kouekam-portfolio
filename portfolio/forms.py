from django import forms
from .models import Profile, Project, Skill, Timeline, ProjectImage
from .admin_utils import parse_json_field_string, safe_get_cleaned_data, validate_form_before_save


class ProfileForm(forms.ModelForm):
    linkedin = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400',
        'placeholder': 'https://linkedin.com/in/yourprofile'
    }))
    github = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400',
        'placeholder': 'https://github.com/yourusername'
    }))
    twitter = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400',
        'placeholder': 'https://twitter.com/yourusername'
    }))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400',
        'placeholder': 'https://yourwebsite.com'
    }))
    
    class Meta:
        model = Profile
        fields = ['bio', 'photo', 'tagline', 'cv_file']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:outline-none',
                'accept': 'image/*'
            }),
            'tagline': forms.TextInput(attrs={
                'class': 'input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400',
                'placeholder': 'A short tagline about yourself'
            }),
            'cv_file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:outline-none',
                'accept': '.pdf,.doc,.docx'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            social_links = self.instance.social_links or {}
            self.fields['linkedin'].initial = social_links.get('linkedin', '')
            self.fields['github'].initial = social_links.get('github', '')
            self.fields['twitter'].initial = social_links.get('twitter', '')
            self.fields['website'].initial = social_links.get('website', '')
    
    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        # Validate URLs if provided
        for field_name in ['linkedin', 'github', 'twitter', 'website']:
            url = cleaned_data.get(field_name, '')
            if url and not url.startswith(('http://', 'https://')):
                self.add_error(field_name, 'URL must start with http:// or https://')
        return cleaned_data
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        social_links = {}
        
        # Only access cleaned_data if form is valid
        if validate_form_before_save(self):
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
        else:
            # If form is not valid, preserve existing social_links
            if profile.pk and hasattr(profile, 'social_links'):
                social_links = profile.social_links or {}
        
        profile.social_links = social_links
        if commit:
            profile.save()
        return profile


class ProjectForm(forms.ModelForm):
    """Custom form to handle tech_stack JSONField properly"""
    tech_stack_display = forms.CharField(
        required=False,
        label='Tech Stack',
        help_text="Enter technologies separated by commas (e.g., Python, Django, React) or as JSON array (e.g., [\"Python\", \"Django\"])",
        widget=forms.Textarea(attrs={
            'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Python, Django, React'
        })
    )
    
    class Meta:
        model = Project
        fields = ['title', 'description', 'category', 'image', 'github_url', 'live_link', 'status']
        exclude = ['tech_stack']  # Exclude the original JSONField
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 6
            }),
            'category': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
                'accept': 'image/*'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'https://github.com/username/project'
            }),
            'live_link': forms.URLInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'https://project-demo.com'
            }),
            'status': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate tech_stack_display from the instance
        try:
            if self.instance and self.instance.pk and hasattr(self.instance, 'tech_stack'):
                tech_stack = getattr(self.instance, 'tech_stack', None)
                if isinstance(tech_stack, list):
                    self.initial['tech_stack_display'] = ', '.join(str(item) for item in tech_stack)
                elif tech_stack:
                    self.initial['tech_stack_display'] = str(tech_stack)
        except (AttributeError, TypeError, KeyError) as e:
            # If there's any error, just leave it empty
            pass
    
    def clean_tech_stack_display(self):
        """Clean the tech_stack_display field"""
        data = self.cleaned_data.get('tech_stack_display', '')
        if not data:
            return ''
        if not isinstance(data, str):
            data = str(data) if data else ''
        return data.strip()
    
    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        # Validate URLs if provided
        for field_name in ['github_url', 'live_link']:
            url = cleaned_data.get(field_name, '')
            if url and not url.startswith(('http://', 'https://')):
                self.add_error(field_name, 'URL must start with http:// or https://')
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Ensure slug is generated before saving (model's save method will handle this)
        if not instance.slug and instance.title:
            from django.utils.text import slugify
            base_slug = slugify(instance.title)
            if base_slug:
                instance.slug = base_slug
        
        # Convert tech_stack_display string to list
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
            instance.save()
        return instance


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency_level']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
            'category': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'proficiency_level': forms.NumberInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'min': 0,
                'max': 100
            }),
        }
    
    def clean_proficiency_level(self):
        """Validate proficiency level is between 0 and 100"""
        proficiency = self.cleaned_data.get('proficiency_level')
        if proficiency is not None:
            if proficiency < 0 or proficiency > 100:
                raise forms.ValidationError('Proficiency level must be between 0 and 100.')
        return proficiency
    
    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        return cleaned_data


class TimelineForm(forms.ModelForm):
    class Meta:
        model = Timeline
        fields = ['year', 'title', 'description', 'category']
        widgets = {
            'year': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': '2020-2024'
            }),
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 4
            }),
            'category': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
        }
    
    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        return cleaned_data


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['project', 'image', 'caption']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
        }
    
    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        return cleaned_data







