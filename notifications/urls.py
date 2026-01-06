from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:notification_id>/read/', views.mark_as_read, name='notification_read'),
    path('mark-all-read/', views.mark_all_as_read, name='notification_mark_all_read'),
    path('unread-count/', views.get_unread_count, name='notification_unread_count'),
]

