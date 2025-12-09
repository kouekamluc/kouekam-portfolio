from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.business_dashboard, name='business_dashboard'),
    path('ideas/', views.business_idea_list, name='business_idea_list'),
    path('ideas/create/', views.business_idea_create, name='business_idea_create'),
    path('ideas/<int:idea_id>/', views.business_idea_detail, name='business_idea_detail'),
    path('ideas/<int:idea_id>/update/', views.business_idea_update, name='business_idea_update'),
    path('ideas/<int:idea_id>/research/create/', views.market_research_create, name='market_research_create'),
    path('research/', views.market_research_list, name='market_research_list'),
    path('ideas/<int:idea_id>/plan/create/', views.business_plan_create, name='business_plan_create'),
    path('plans/<int:plan_id>/', views.business_plan_detail, name='business_plan_detail'),
    path('import-export/', views.import_export_list, name='import_export_list'),
    path('import-export/create/', views.import_export_create, name='import_export_create'),
    path('ideas/<int:idea_id>/projections/', views.financial_projections, name='financial_projections'),
]




