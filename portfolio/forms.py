from django import forms
from .models import Profile, Project, Skill, Timeline, ProjectImage


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
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        social_links = {}
        if self.cleaned_data.get('linkedin'):
            social_links['linkedin'] = self.cleaned_data['linkedin']
        if self.cleaned_data.get('github'):
            social_links['github'] = self.cleaned_data['github']
        if self.cleaned_data.get('twitter'):
            social_links['twitter'] = self.cleaned_data['twitter']
        if self.cleaned_data.get('website'):
            social_links['website'] = self.cleaned_data['website']
        profile.social_links = social_links
        if commit:
            profile.save()
        return profile


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'category', 'tech_stack', 'image', 'github_url', 'live_link', 'status']
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
            'tech_stack': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Python, Django, React'
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

    def clean_tech_stack(self):
        tech_stack = self.cleaned_data.get('tech_stack')
        if isinstance(tech_stack, str):
            # Convert comma-separated string to list
            tech_list = [tech.strip() for tech in tech_stack.split(',') if tech.strip()]
            return tech_list
        return tech_stack


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


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
        }







