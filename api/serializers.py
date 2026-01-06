from rest_framework import serializers
from django.contrib.auth import get_user_model
from portfolio.models import Profile, Project, Skill
from academic.models import Course, Note, Flashcard, StudySession
from productivity.models import Task, Habit, Goal, Transaction, Milestone
from journal.models import JournalEntry, Philosophy, VisionGoal
from blog.models import BlogPost
from notifications.models import Notification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'bio', 'tagline', 'photo', 'cv_file', 'social_links', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'slug', 'description', 'category', 'tech_stack', 'image', 
                  'github_url', 'live_link', 'status', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'proficiency_level', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'semester', 'credits', 'status', 'grade', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NoteSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'course', 'course_name', 'title', 'content', 'file', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FlashcardSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Flashcard
        fields = ['id', 'course', 'course_name', 'question', 'answer', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudySessionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = StudySession
        fields = ['id', 'course', 'course_name', 'date', 'duration_minutes', 'topics_covered', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'name', 'frequency', 'current_streak', 'last_completed_date', 'created_at']
        read_only_fields = ['id', 'created_at']


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['id', 'goal', 'title', 'description', 'completed', 'due_date', 'completed_date', 'created_at']
        read_only_fields = ['id', 'created_at']


class GoalSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)
    
    class Meta:
        model = Goal
        fields = ['id', 'title', 'description', 'target_date', 'progress', 'milestones', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'amount', 'category', 'date', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ['id', 'date', 'content', 'mood', 'energy_level', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PhilosophySerializer(serializers.ModelSerializer):
    class Meta:
        model = Philosophy
        fields = ['id', 'title', 'content', 'category', 'date_written', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VisionGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisionGoal
        fields = ['id', 'title', 'description', 'category', 'target_date', 'progress', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BlogPostSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'category', 'published_date', 'featured', 
                  'author', 'author_email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'read', 'created_at', 'related_url']
        read_only_fields = ['id', 'created_at']

