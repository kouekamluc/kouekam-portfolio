from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profile')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'notes', views.NoteViewSet, basename='note')
router.register(r'flashcards', views.FlashcardViewSet, basename='flashcard')
router.register(r'study-sessions', views.StudySessionViewSet, basename='studysession')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'habits', views.HabitViewSet, basename='habit')
router.register(r'goals', views.GoalViewSet, basename='goal')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'journal-entries', views.JournalEntryViewSet, basename='journalentry')
router.register(r'philosophies', views.PhilosophyViewSet, basename='philosophy')
router.register(r'vision-goals', views.VisionGoalViewSet, basename='visiongoal')
router.register(r'blog-posts', views.BlogPostViewSet, basename='blogpost')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]

