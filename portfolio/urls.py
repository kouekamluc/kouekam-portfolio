from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('skills/', views.skills, name='skills'),
    path('contact/', views.contact, name='contact'),
    path('download-cv/', views.download_cv, name='download_cv'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/<slug:slug>/update/', views.project_update, name='project_update'),
    path('projects/<slug:slug>/delete/', views.project_delete, name='project_delete'),
    path('projects/<slug:slug>/images/add/', views.project_image_add, name='project_image_add'),
    path('projects/images/<int:image_id>/delete/', views.project_image_delete, name='project_image_delete'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search, name='search'),
    path('debug/static-url/', views.debug_static_url, name='debug_static_url'),
]
