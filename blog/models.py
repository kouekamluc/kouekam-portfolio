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
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True, help_text="Featured image for the blog post")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    published_date = models.DateTimeField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date', '-created_at']
        
    def get_ordering_value(self):
        """Helper to get ordering value for posts with NULL published_date"""
        return self.published_date or self.created_at

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            # Truncate slug to max_length (255) to prevent database errors
            if len(base_slug) > 255:
                base_slug = base_slug[:255]
            slug = base_slug
            counter = 1
            # Handle slug collisions
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk if self.pk else None).exists():
                # Ensure slug with counter doesn't exceed max_length
                suffix = f"-{counter}"
                max_base_length = 255 - len(suffix)
                truncated_base = base_slug[:max_base_length] if len(base_slug) > max_base_length else base_slug
                slug = f"{truncated_base}{suffix}"
                counter += 1
            self.slug = slug
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
    slug = models.SlugField(unique=True, blank=True, max_length=255)
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
            base_slug = slugify(self.title)
            # Truncate slug to max_length (255) to prevent database errors
            if len(base_slug) > 255:
                base_slug = base_slug[:255]
            slug = base_slug
            counter = 1
            # Handle slug collisions
            while Tutorial.objects.filter(slug=slug).exclude(pk=self.pk if self.pk else None).exists():
                # Ensure slug with counter doesn't exceed max_length
                suffix = f"-{counter}"
                max_base_length = 255 - len(suffix)
                truncated_base = base_slug[:max_base_length] if len(base_slug) > max_base_length else base_slug
                slug = f"{truncated_base}{suffix}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
