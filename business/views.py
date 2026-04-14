from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
import json
from .models import BusinessIdea, MarketResearch, BusinessPlan, ImportExportRecord
from .forms import BusinessIdeaForm, MarketResearchForm, BusinessPlanForm, ImportExportRecordForm


def _idea_workflow_actions(idea, research_count, has_plan):
    actions = []
    has_market_context = bool((idea.market_size or '').strip() and (idea.competitors or '').strip())

    if research_count == 0:
        actions.append('Add a market research entry so the idea is grounded in real evidence.')

    if not has_market_context:
        actions.append('Document market size and competitor analysis before moving deeper into planning.')

    if not has_plan and idea.status in {'planning', 'active'}:
        actions.append('Create the business plan so execution has a real operating guide.')
    elif not has_plan:
        actions.append('Create the business plan once research is solid enough to test the model.')

    if idea.status == 'idea':
        actions.append('Refine the concept and collect first-pass market signals.')
    elif idea.status == 'researching':
        actions.append('Synthesize the research into a sharper target customer and offer.')
    elif idea.status == 'planning':
        actions.append('Validate assumptions, funding needs, and execution steps before launch.')
    elif idea.status == 'active':
        actions.append('Track traction, revenue assumptions, and operational learning consistently.')
    elif idea.status == 'paused':
        actions.append('Decide whether to restart with new evidence or archive the idea cleanly.')
    elif idea.status == 'abandoned':
        actions.append('Keep the lessons learned so a future version starts from stronger evidence.')

    return actions

@login_required
def business_dashboard(request):
    ideas = BusinessIdea.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_records = ImportExportRecord.objects.filter(user=request.user).order_by('-date')[:5]
    all_ideas = BusinessIdea.objects.filter(user=request.user)
    all_research = MarketResearch.objects.filter(user=request.user)
    active_ideas = all_ideas.filter(status='active').count()
    ready_for_planning = sum(
        1 for idea in all_ideas.filter(status__in=['idea', 'researching']).prefetch_related('market_research')
        if ((idea.market_size or '').strip() and (idea.competitors or '').strip()) or idea.market_research.exists()
    )
    ready_for_activation = sum(
        1 for idea in all_ideas.filter(status='planning').prefetch_related('market_research')
        if hasattr(idea, 'business_plan') and (
            ((idea.market_size or '').strip() and (idea.competitors or '').strip()) or idea.market_research.exists()
        )
    )
    ideas_by_status = {
        'idea': all_ideas.filter(status='idea').count(),
        'researching': all_ideas.filter(status='researching').count(),
        'planning': all_ideas.filter(status='planning').count(),
        'active': active_ideas,
        'paused': all_ideas.filter(status='paused').count(),
        'abandoned': all_ideas.filter(status='abandoned').count(),
    }
    recent_trade_value = sum(record.value for record in ImportExportRecord.objects.filter(user=request.user)[:20])
    
    context = {
        'ideas': ideas,
        'recent_records': recent_records,
        'total_ideas': all_ideas.count(),
        'active_ideas': active_ideas,
        'research_entries': all_research.count(),
        'ready_for_planning': ready_for_planning,
        'ready_for_activation': ready_for_activation,
        'ideas_by_status': ideas_by_status,
        'recent_trade_value': recent_trade_value,
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
    workflow_actions = _idea_workflow_actions(idea, market_research.count(), bool(business_plan))
    
    context = {
        'idea': idea,
        'market_research': market_research,
        'business_plan': business_plan,
        'workflow_actions': workflow_actions,
        'next_action': workflow_actions[0] if workflow_actions else 'This business idea is in a healthy operating state.',
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

@login_required
def business_idea_delete(request, idea_id):
    idea = get_object_or_404(BusinessIdea, id=idea_id, user=request.user)
    
    if request.method == 'POST':
        idea.delete()
        messages.success(request, 'Business idea deleted!')
        return redirect('business_idea_list')
    
    return render(request, 'business/business_idea_confirm_delete.html', {'idea': idea})

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
    return render(request, 'business/market_research_form.html', {'form': form, 'idea': idea, 'form_type': 'Create'})

@login_required
def market_research_update(request, research_id):
    research = get_object_or_404(MarketResearch, id=research_id, user=request.user)
    idea = research.business_idea
    
    if request.method == 'POST':
        form = MarketResearchForm(request.POST, instance=research)
        if form.is_valid():
            form.save()
            messages.success(request, 'Market research updated!')
            return redirect('business_idea_detail', idea_id=idea.id)
    else:
        form = MarketResearchForm(instance=research)
    
    return render(request, 'business/market_research_form.html', {'form': form, 'idea': idea, 'research': research, 'form_type': 'Update'})

@login_required
def market_research_delete(request, research_id):
    research = get_object_or_404(MarketResearch, id=research_id, user=request.user)
    idea_id = research.business_idea.id
    
    if request.method == 'POST':
        research.delete()
        messages.success(request, 'Market research deleted!')
        return redirect('business_idea_detail', idea_id=idea_id)
    
    return render(request, 'business/market_research_confirm_delete.html', {'research': research})

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
    
    # Check if plan already exists (OneToOne relationship)
    if hasattr(idea, 'business_plan'):
        messages.info(request, 'Business plan already exists. You can update it instead.')
        return redirect('business_plan_update', plan_id=idea.business_plan.id)
    
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
    
    return render(request, 'business/business_plan_form.html', {'form': form, 'idea': idea, 'form_type': 'Create'})

@login_required
def business_plan_update(request, plan_id):
    plan = get_object_or_404(BusinessPlan, id=plan_id, user=request.user)
    idea = plan.business_idea
    
    if request.method == 'POST':
        form = BusinessPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Business plan updated!')
            return redirect('business_plan_detail', plan_id=plan.id)
    else:
        form = BusinessPlanForm(instance=plan)
    
    return render(request, 'business/business_plan_form.html', {'form': form, 'idea': idea, 'plan': plan, 'form_type': 'Update'})

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
def import_export_update(request, record_id):
    record = get_object_or_404(ImportExportRecord, id=record_id, user=request.user)
    
    if request.method == 'POST':
        form = ImportExportRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record updated!')
            return redirect('import_export_list')
    else:
        form = ImportExportRecordForm(instance=record)
    
    return render(request, 'business/import_export_form.html', {'form': form, 'record': record, 'form_type': 'Update'})

@login_required
def import_export_delete(request, record_id):
    record = get_object_or_404(ImportExportRecord, id=record_id, user=request.user)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Record deleted!')
        return redirect('import_export_list')
    
    return render(request, 'business/import_export_confirm_delete.html', {'record': record})

@login_required
def financial_projections(request, idea_id):
    idea = get_object_or_404(BusinessIdea, id=idea_id, user=request.user)
    business_plan = getattr(idea, 'business_plan', None)
    
    if request.method == 'POST':
        try:
            monthly_revenue = float(request.POST.get('monthly_revenue', 0))
            growth_rate = float(request.POST.get('growth_rate', 0)) / 100
            months = int(request.POST.get('months', 12))
        except (TypeError, ValueError):
            messages.error(request, 'Enter valid numbers for revenue, growth rate, and months.')
            return render(request, 'business/financial_projections.html', {
                'idea': idea,
                'business_plan': business_plan,
            })

        if monthly_revenue < 0:
            messages.error(request, 'Monthly revenue cannot be negative.')
            return render(request, 'business/financial_projections.html', {
                'idea': idea,
                'business_plan': business_plan,
            })

        months = max(1, min(months, 60))
        
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
