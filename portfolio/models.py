from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    tagline = models.CharField(max_length=255, blank=True)
    cv_file = models.FileField(upload_to='profile/cv/', blank=True, null=True, help_text="Upload CV/Resume PDF")
    social_links = models.JSONField(default=dict, blank=True)  # e.g., {'linkedin': 'url', 'github': 'url'}
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Timeline(models.Model):
    year = models.CharField(max_length=20) # Can be a range "2020-2024"
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=[('education', 'Education'), ('work', 'Work'), ('award', 'Award')])
    
    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"{self.year} - {self.title}"

class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=[('frontend', 'Frontend'), ('backend', 'Backend'), ('tools', 'DevOps/Tools'), ('soft', 'Soft Skills')])
    proficiency_level = models.IntegerField(default=50, help_text="0-100")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=[('ai', 'AI & Machine Learning'), ('electronics', 'Electronics & IoT'), ('web', 'Web Development'), ('other', 'Other')])
    tech_stack = models.JSONField(default=list, help_text="List of technologies used e.g. ['Python', 'Django']")
    image = models.ImageField(upload_to='projects/', help_text="Main cover image", blank=True, null=True)
    github_url = models.URLField(blank=True)
    live_link = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def save(self, *args, **kwargs):
        try:
            if not self.slug and self.title:
                from django.utils.text import slugify
                base_slug = slugify(self.title)
                if not base_slug:  # If title doesn't produce a valid slug
                    base_slug = f"project-{self.id or 'new'}"
                self.slug = base_slug
                # Handle duplicate slugs
                counter = 1
                while Project.objects.filter(slug=self.slug).exclude(pk=self.pk if self.pk else None).exists():
                    self.slug = f"{base_slug}-{counter}"
                    counter += 1
                    if counter > 100:  # Safety limit
                        break
            super().save(*args, **kwargs)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving project: {e}", exc_info=True)
            raise

    def __str__(self):
        return self.title

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project Image'
        verbose_name_plural = 'Project Images'

    def __str__(self):
        return f"Image for {self.project.title}"
