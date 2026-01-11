from django import forms
from .models import BlogPost, CodeSnippet, Tutorial


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'image', 'category', 'featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 dark:bg-gray-800 dark:border-gray-600 p-2.5 text-sm text-gray-900 dark:text-white focus:border-blue-500 focus:ring-blue-500 dark:focus:border-blue-500'
            }),
            'content': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 dark:bg-gray-800 dark:border-gray-600 p-2.5 text-sm text-gray-900 dark:text-white focus:border-blue-500 focus:ring-blue-500 dark:focus:border-blue-500',
                'rows': 20
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400',
                'accept': 'image/*'
            }),
            'category': forms.Select(attrs={
                'class': 'bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:focus:border-blue-500 block w-full p-2.5'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 cursor-pointer'
            }),
        }


class CodeSnippetForm(forms.ModelForm):
    class Meta:
        model = CodeSnippet
        fields = ['title', 'language', 'code', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
            'language': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'code': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 font-mono focus:border-blue-500 focus:ring-blue-500',
                'rows': 15
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 3
            }),
        }


class TutorialForm(forms.ModelForm):
    class Meta:
        model = Tutorial
        fields = ['title', 'description', 'difficulty', 'parts']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'rows': 8
            }),
            'difficulty': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'parts': forms.NumberInput(attrs={
                'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500',
                'min': '1'
            }),
        }









