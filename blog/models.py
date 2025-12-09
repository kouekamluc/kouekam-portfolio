from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('django', 'Django'),
        ('python', 'Python'),
        ('ai', 'AI & Machine Learning'),
        ('electronics', 'Electronics'),
        ('web', 'Web Development'),
        ('tutorial', 'Tutorial'),
        ('project', 'Project'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    published_date = models.DateTimeField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class CodeSnippet(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('django', 'Django'),
        ('sql', 'SQL'),
        ('bash', 'Bash'),
        ('other', 'Other'),
    ]
    
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='code_snippets', null=True, blank=True)
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='python')
    code = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} ({self.language})"

class Tutorial(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    parts = models.IntegerField(default=1, help_text="Number of parts in the tutorial series")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutorials')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
