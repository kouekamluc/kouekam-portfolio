from django.contrib import admin
from .models import BlogPost, CodeSnippet, Tutorial


class CodeSnippetInline(admin.TabularInline):
    model = CodeSnippet
    extra = 1
    fields = ['title', 'language', 'code', 'description']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'featured', 'published_date', 'created_at']
    list_filter = ['category', 'featured', 'published_date', 'created_at']
    search_fields = ['title', 'content', 'author__email']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CodeSnippetInline]
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Post Information', {
            'fields': ('author', 'title', 'slug', 'category', 'featured')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Publishing', {
            'fields': ('published_date',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'blog_post', 'language', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['title', 'code', 'description', 'blog_post__title']
    readonly_fields = ['created_at']


@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'difficulty', 'parts', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['title', 'description', 'author__email']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Tutorial Information', {
            'fields': ('author', 'title', 'slug', 'difficulty', 'parts')
        }),
        ('Content', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
