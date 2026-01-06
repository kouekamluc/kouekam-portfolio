from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True)
    semester = models.CharField(max_length=50, blank=True) # e.g. "Fall 2024"
    credits = models.DecimalField(max_digits=4, decimal_places=1, default=3.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    grade = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, help_text="Grade point (e.g. 4.0)")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at', 'name']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        indexes = [
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name

class Note(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='academic/notes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        return self.title

class Flashcard(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='flashcards')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'

    def __str__(self):
        return f"Flashcard for {self.course.code if self.course.code else self.course.name}"

class StudySession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='study_sessions')
    date = models.DateField()
    duration_minutes = models.IntegerField(help_text="Duration in minutes")
    topics_covered = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Study Session'
        verbose_name_plural = 'Study Sessions'

    def __str__(self):
        course_name = self.course.code if self.course.code else self.course.name
        return f"{course_name} session on {self.date}"
