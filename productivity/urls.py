from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.productivity_dashboard, name='productivity_dashboard'),
    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/update/', views.task_update, name='task_update'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    # Habits
    path('habits/', views.habit_list, name='habit_list'),
    path('habits/create/', views.habit_create, name='habit_create'),
    path('habits/<int:habit_id>/update/', views.habit_update, name='habit_update'),
    path('habits/<int:habit_id>/delete/', views.habit_delete, name='habit_delete'),
    path('habits/<int:habit_id>/track/', views.habit_track, name='habit_track'),
    # Goals
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:goal_id>/update/', views.goal_update, name='goal_update'),
    path('goals/<int:goal_id>/delete/', views.goal_delete, name='goal_delete'),
    path('goals/<int:goal_id>/milestones/', views.milestone_manage, name='milestone_manage'),
    # Timetable
    path('timetables/', views.timetable_list, name='timetable_list'),
    path('timetables/create/', views.timetable_create, name='timetable_create'),
    path('timetables/<int:timetable_id>/update/', views.timetable_update, name='timetable_update'),
    path('timetables/<int:timetable_id>/delete/', views.timetable_delete, name='timetable_delete'),
    path('timetables/generator/', views.timetable_generator, name='timetable_generator'),
    # Finance
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:transaction_id>/update/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:transaction_id>/delete/', views.transaction_delete, name='transaction_delete'),
    path('finance/', views.finance_dashboard, name='finance_dashboard'),
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
]
