import json
from django import forms
from .models import Profile, Project, ProjectImage

class ProfileForm(forms.ModelForm):
    def clean_social_links(self):
        social_links = self.cleaned_data.get('social_links')
        if isinstance(social_links, dict):
            return {str(key).strip().lower(): str(value).strip() for key, value in social_links.items() if str(value).strip()}

        if not social_links:
            return {}

        if isinstance(social_links, str):
            raw_value = social_links.strip()
            if not raw_value:
                return {}

            try:
                parsed = json.loads(raw_value)
            except json.JSONDecodeError:
                parsed = {}
                for line in raw_value.splitlines():
                    if ':' not in line:
                        raise forms.ValidationError(
                            'Enter social links as JSON or one "platform: url" pair per line.'
                        )
                    platform, url = line.split(':', 1)
                    if platform.strip() and url.strip():
                        parsed[platform.strip().lower()] = url.strip()
                return parsed

            if not isinstance(parsed, dict):
                raise forms.ValidationError('Social links must be a JSON object or "platform: url" pairs.')
            return {str(key).strip().lower(): str(value).strip() for key, value in parsed.items() if str(value).strip()}

        raise forms.ValidationError('Unsupported social links format.')

    class Meta:
        model = Profile
        fields = ['bio', 'photo', 'tagline', 'cv_file', 'social_links']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 5, 
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'tagline': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md cursor-pointer bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500'
            }),
            'cv_file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md cursor-pointer bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500'
            }),
            'social_links': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800',
                'placeholder': 'JSON format or one per line, e.g. linkedin: https://...'
            }),
        }
        help_texts = {
            'social_links': 'Enter social links as JSON or one "platform: url" pair per line.',
        }

class ProjectForm(forms.ModelForm):
    tech_stack_display = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800 font-mono',
            'placeholder': 'Enter technologies separated by commas, e.g., Python, Django, React, PostgreSQL'
        }),
        help_text='Enter technologies separated by commas. They will be converted to a list automatically.'
    )
    
    class Meta:
        model = Project
        fields = ['title', 'description', 'category', 'status', 'image', 'github_url', 'live_link']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'description': forms.Textarea(attrs={
                'rows': 10,
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'category': forms.Select(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md cursor-pointer bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500',
                'accept': 'image/*'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
            'live_link': forms.URLInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Convert tech_stack list to comma-separated string for display
            tech_stack = self.instance.tech_stack or []
            self.initial['tech_stack_display'] = ', '.join(str(tech) for tech in tech_stack)
    
    def clean_tech_stack_display(self):
        tech_stack_str = self.cleaned_data.get('tech_stack_display', '') or ''
        if tech_stack_str:
            # Split by comma and clean up each tech
            tech_list = [tech.strip() for tech in tech_stack_str.split(',') if tech.strip()]
            return tech_list
        return []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set tech_stack from tech_stack_display (which is now a list after cleaning)
        tech_stack_list = self.cleaned_data.get('tech_stack_display', [])
        if isinstance(tech_stack_list, str):
            # If it's still a string, split it
            tech_stack_list = [tech.strip() for tech in tech_stack_list.split(',') if tech.strip()]
        instance.tech_stack = tech_stack_list
        if commit:
            instance.save()
        return instance

class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md cursor-pointer bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-blue-600 dark:focus:ring-blue-500 sm:text-sm sm:leading-6 bg-white dark:bg-gray-800'
            }),
        }
