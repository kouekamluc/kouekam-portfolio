from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='academic_dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('course/create/', views.course_create, name='course_create'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/update/', views.course_update, name='course_update'),
    path('course/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('course/<int:course_id>/notes/create/', views.note_create, name='note_create'),
    path('note/<int:note_id>/update/', views.note_update, name='note_update'),
    path('note/<int:note_id>/delete/', views.note_delete, name='note_delete'),
    path('course/<int:course_id>/flashcards/', views.flashcard_list, name='flashcard_list'),
    path('course/<int:course_id>/flashcards/create/', views.flashcard_create, name='flashcard_create'),
    path('course/<int:course_id>/flashcards/study/', views.flashcard_study, name='flashcard_study'),
    path('course/<int:course_id>/sessions/create/', views.study_session_create, name='study_session_create'),
    path('gpa-calculator/', views.gpa_calculator, name='gpa_calculator'),
    path('course/<int:course_id>/ai-questions/', views.ai_question_generator, name='ai_question_generator'),
    path('study-planner/', views.study_planner, name='study_planner'),
]
