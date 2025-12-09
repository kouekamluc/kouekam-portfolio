from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class JournalEntry(models.Model):
    MOOD_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('okay', 'Okay'),
        ('poor', 'Poor'),
        ('terrible', 'Terrible'),
    ]
    
    ENERGY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    date = models.DateField()
    content = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True)
    energy_level = models.CharField(max_length=20, choices=ENERGY_CHOICES, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date']
        verbose_name_plural = "Journal Entries"

    def __str__(self):
        return f"Entry: {self.date}"

class Philosophy(models.Model):
    CATEGORY_CHOICES = [
        ('life', 'Life Philosophy'),
        ('work', 'Work Philosophy'),
        ('relationships', 'Relationships'),
        ('growth', 'Personal Growth'),
        ('values', 'Values & Beliefs'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='philosophies')
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='life')
    date_written = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_written']
        verbose_name_plural = "Philosophies"

    def __str__(self):
        return self.title

class VisionGoal(models.Model):
    CATEGORY_CHOICES = [
        ('career', 'Career'),
        ('education', 'Education'),
        ('business', 'Business'),
        ('personal', 'Personal'),
        ('africa', 'African Impact'),
        ('financial', 'Financial'),
        ('health', 'Health'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vision_goals')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='personal')
    target_date = models.DateField(null=True, blank=True)
    progress = models.IntegerField(default=0, help_text="Progress in %")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['target_date', '-created_at']

    def __str__(self):
        return self.title

class LifeLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='life_lessons')
    title = models.CharField(max_length=255)
    lesson = models.TextField(help_text="The lesson learned")
    context = models.TextField(blank=True, help_text="Context or situation where this lesson was learned")
    date_learned = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_learned']

    def __str__(self):
        return self.title
