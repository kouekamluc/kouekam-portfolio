from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'photo', 'tagline', 'cv_file', 'social_links']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'cv_file': forms.FileInput(attrs={'class': 'form-control'}),
            'social_links': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'JSON format: {"linkedin": "url", "github": "url"}'
            }),
        }
        help_texts = {
            'social_links': 'Enter social links as JSON. Example: {"linkedin": "https://linkedin.com/in/username", "github": "https://github.com/username"}',
        }
