from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from portfolio.models import Profile, Project, Skill
from academic.models import Course, Note, Flashcard, StudySession
from productivity.models import Task, Habit, Goal, Transaction, Milestone
from journal.models import JournalEntry, Philosophy, VisionGoal
from blog.models import BlogPost
from notifications.models import Notification
from .serializers import (
    UserSerializer, ProfileSerializer, ProjectSerializer, SkillSerializer,
    CourseSerializer, NoteSerializer, FlashcardSerializer, StudySessionSerializer,
    TaskSerializer, HabitSerializer, GoalSerializer, TransactionSerializer,
    JournalEntrySerializer, PhilosophySerializer, VisionGoalSerializer,
    BlogPostSerializer, NotificationSerializer
)

User = get_user_model()


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = []  # Public read access
    
    def get_queryset(self):
        return Project.objects.filter(status__in=['active', 'completed'])


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = []  # Public read access
    
    def get_queryset(self):
        return Skill.objects.all()


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Note.objects.filter(course__user=self.request.user)
    
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if course.user != self.request.user:
            raise PermissionError("You can only create notes for your own courses")
        serializer.save()


class FlashcardViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Flashcard.objects.filter(course__user=self.request.user)
    
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if course.user != self.request.user:
            raise PermissionError("You can only create flashcards for your own courses")
        serializer.save()


class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StudySession.objects.filter(course__user=self.request.user)
    
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if course.user != self.request.user:
            raise PermissionError("You can only create study sessions for your own courses")
        serializer.save()


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PhilosophyViewSet(viewsets.ModelViewSet):
    serializer_class = PhilosophySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Philosophy.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VisionGoalViewSet(viewsets.ModelViewSet):
    serializer_class = VisionGoalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return VisionGoal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogPostSerializer
    permission_classes = []  # Public read access
    
    def get_queryset(self):
        return BlogPost.objects.all()


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({'status': 'all marked as read'})

