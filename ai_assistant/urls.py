from django.urls import path
from . import views

urlpatterns = [
    path('', views.assistant_hub, name='assistant_hub'),
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('conversations/create/', views.conversation_create, name='conversation_create'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('chat/', views.chat_interface, name='chat_interface'),
    path('pdf/upload/', views.pdf_upload, name='pdf_upload'),
    path('pdf/<int:analysis_id>/', views.pdf_analyze, name='pdf_analyze'),
    path('templates/', views.prompt_template_list, name='prompt_template_list'),
    path('templates/create/', views.prompt_template_create, name='prompt_template_create'),
    path('study-helper/', views.study_helper, name='study_helper'),
    path('code-assistant/', views.code_assistant, name='code_assistant'),
    path('writing-assistant/', views.writing_assistant, name='writing_assistant'),
    path('course-recommendation/', views.course_recommendation, name='course_recommendation'),
]







