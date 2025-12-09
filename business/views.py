from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
import json
from .models import BusinessIdea, MarketResearch, BusinessPlan, ImportExportRecord
from .forms import BusinessIdeaForm, MarketResearchForm, BusinessPlanForm, ImportExportRecordForm

@login_required
def business_dashboard(request):
    ideas = BusinessIdea.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_records = ImportExportRecord.objects.filter(user=request.user).order_by('-date')[:5]
    
    context = {
        'ideas': ideas,
        'recent_records': recent_records,
    }
    return render(request, 'business/business_dashboard.html', context)

# Business Idea Views
@login_required
def business_idea_list(request):
    ideas = BusinessIdea.objects.filter(user=request.user).order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        ideas = ideas.filter(status=status_filter)
    return render(request, 'business/business_idea_list.html', {
        'ideas': ideas,
        'status_filter': status_filter
    })

@login_required
def business_idea_create(request):
    if request.method == 'POST':
        form = BusinessIdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.user = request.user
            idea.save()
            messages.success(request, 'Business idea created!')
            return redirect('business_idea_detail', idea_id=idea.id)
    else:
        form = BusinessIdeaForm()
    return render(request, 'business/business_idea_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def business_idea_detail(request, idea_id):
    idea = get_object_or_404(BusinessIdea, id=idea_id, user=request.user)
    market_research = idea.market_research.all().order_by('-date')
    business_plan = getattr(idea, 'business_plan', None)
    
    context = {
        'idea': idea,
        'market_research': market_research,
        'business_plan': business_plan,
    }
    return render(request, 'business/business_idea_detail.html', context)

@login_required
def business_idea_update(request, idea_id):
    idea = get_object_or_404(BusinessIdea, id=idea_id, user=request.user)
    if request.method == 'POST':
        form = BusinessIdeaForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            messages.success(request, 'Business idea updated!')
            return redirect('business_idea_detail', idea_id=idea.id)
    else:
        form = BusinessIdeaForm(instance=idea)
    return render(request, 'business/business_idea_form.html', {'form': form, 'idea': idea, 'form_type': 'Update'})

# Market Research Views
@login_required
def market_research_create(request, idea_id):
    idea = get_object_or_404(BusinessIdea, id=idea_id, user=request.user)
    if request.method == 'POST':
        form = MarketResearchForm(request.POST)
        if form.is_valid():
            research = form.save(commit=False)
            research.business_idea = idea
            research.user = request.user
            if not research.date:
                research.date = timezone.now().date()
            research.save()
            messages.success(request, 'Market research added!')
            return redirect('business_idea_detail', idea_id=idea.id)
    else:
        form = MarketResearchForm(initial={'date': timezone.now().date()})
    return render(request, 'business/market_research_form.html', {'form': form, 'idea': idea})

@login_required
def market_research_list(request):
    research = MarketResearch.objects.filter(user=request.user).order_by('-date')
    idea_filter = request.GET.get('idea_id')
    if idea_filter:
        research = research.filter(business_idea_id=idea_filter)
    return render(request, 'business/market_research_list.html', {
        'research': research,
        'idea_filter': idea_filter
    })

# Business Plan Views
@login_required
def business_plan_create(request, idea_id):
    idea = get_object_or_404(BusinessIdea, id=idea_id, user=request.user)
    
    if request.method == 'POST':
        form = BusinessPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.business_idea = idea
            plan.user = request.user
            plan.save()
            messages.success(request, 'Business plan saved!')
            return redirect('business_plan_detail', plan_id=plan.id)
    else:
        form = BusinessPlanForm()
    
    return render(request, 'business/business_plan_form.html', {'form': form, 'idea': idea})

@login_required
def business_plan_detail(request, plan_id):
    plan = get_object_or_404(BusinessPlan, id=plan_id, user=request.user)
    return render(request, 'business/business_plan_detail.html', {'plan': plan})

# Import/Export Views
@login_required
def import_export_list(request):
    records = ImportExportRecord.objects.filter(user=request.user).order_by('-date')
    type_filter = request.GET.get('type')
    if type_filter:
        records = records.filter(type=type_filter)
    return render(request, 'business/import_export_list.html', {
        'records': records,
        'type_filter': type_filter
    })

@login_required
def import_export_create(request):
    if request.method == 'POST':
        form = ImportExportRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            if not record.date:
                record.date = timezone.now().date()
            record.save()
            messages.success(request, 'Record created!')
            return redirect('import_export_list')
    else:
        form = ImportExportRecordForm(initial={'date': timezone.now().date()})
    return render(request, 'business/import_export_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def financial_projections(request, idea_id):
    idea = get_object_or_404(BusinessIdea, id=idea_id, user=request.user)
    business_plan = getattr(idea, 'business_plan', None)
    
    if request.method == 'POST':
        # Calculate projections based on inputs
        monthly_revenue = float(request.POST.get('monthly_revenue', 0))
        growth_rate = float(request.POST.get('growth_rate', 0)) / 100
        months = int(request.POST.get('months', 12))
        
        projections = []
        for month in range(1, months + 1):
            revenue = monthly_revenue * ((1 + growth_rate) ** (month - 1))
            projections.append({
                'month': month,
                'revenue': round(revenue, 2)
            })
        
        return render(request, 'business/financial_projections.html', {
            'idea': idea,
            'business_plan': business_plan,
            'projections': projections,
            'monthly_revenue': monthly_revenue,
            'growth_rate': growth_rate * 100,
            'months': months,
        })
    
    return render(request, 'business/financial_projections.html', {
        'idea': idea,
        'business_plan': business_plan,
    })
