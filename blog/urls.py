from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('post/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('post/create/', views.blog_create, name='blog_create'),
    path('post/<slug:slug>/update/', views.blog_update, name='blog_update'),
    path('post/<slug:slug>/delete/', views.blog_delete, name='blog_delete'),
    path('tutorials/', views.tutorial_list, name='tutorial_list'),
    path('tutorials/<slug:slug>/', views.tutorial_detail, name='tutorial_detail'),
]




