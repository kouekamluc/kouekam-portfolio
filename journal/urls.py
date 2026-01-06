from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.journal_dashboard, name='journal_dashboard'),
    path('entries/', views.journal_entry_list, name='journal_entry_list'),
    path('entries/create/', views.journal_entry_create, name='journal_entry_create'),
    path('entries/<int:entry_id>/', views.journal_entry_detail, name='journal_entry_detail'),
    path('entries/<int:entry_id>/update/', views.journal_entry_update, name='journal_entry_update'),
    path('mood-tracker/', views.mood_tracker, name='mood_tracker'),
    path('philosophy/', views.philosophy_list, name='philosophy_list'),
    path('philosophy/create/', views.philosophy_create, name='philosophy_create'),
    path('philosophy/<int:philosophy_id>/update/', views.philosophy_update, name='philosophy_update'),
    path('vision-board/', views.vision_board, name='vision_board'),
    path('vision-goals/create/', views.vision_goal_create, name='vision_goal_create'),
    path('vision-goals/<int:goal_id>/update/', views.vision_goal_update, name='vision_goal_update'),
    path('life-lessons/', views.life_lessons_list, name='life_lessons_list'),
    path('life-lessons/create/', views.life_lessons_create, name='life_lessons_create'),
    path('life-lessons/<int:lesson_id>/update/', views.life_lessons_update, name='life_lessons_update'),
    path('export/pdf/', views.export_journal_pdf, name='export_journal_pdf'),
]









