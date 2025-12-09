from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import JournalEntry, Philosophy, VisionGoal, LifeLesson
from .forms import JournalEntryForm, PhilosophyForm, VisionGoalForm, LifeLessonForm

@login_required
def journal_dashboard(request):
    recent_entries = JournalEntry.objects.filter(user=request.user).order_by('-date')[:5]
    recent_philosophies = Philosophy.objects.filter(user=request.user).order_by('-date_written')[:3]
    active_goals = VisionGoal.objects.filter(user=request.user).order_by('target_date')[:5]
    
    context = {
        'recent_entries': recent_entries,
        'recent_philosophies': recent_philosophies,
        'active_goals': active_goals,
    }
    return render(request, 'journal/journal_dashboard.html', context)

# Journal Entry Views
@login_required
def journal_entry_list(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
    date_filter = request.GET.get('date')
    if date_filter:
        entries = entries.filter(date=date_filter)
    return render(request, 'journal/journal_entry_list.html', {
        'entries': entries,
        'date_filter': date_filter
    })

@login_required
def journal_entry_create(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry, created = JournalEntry.objects.update_or_create(
                user=request.user,
                date=form.cleaned_data.get('date') or timezone.now().date(),
                defaults={
                    'content': form.cleaned_data.get('content'),
                    'mood': form.cleaned_data.get('mood', ''),
                    'energy_level': form.cleaned_data.get('energy_level', ''),
                    'tags': form.cleaned_data.get('tags', ''),
                }
            )
            messages.success(request, 'Journal entry saved!')
            return redirect('journal_entry_detail', entry_id=entry.id)
    else:
        form = JournalEntryForm(initial={'date': timezone.now().date()})
    return render(request, 'journal/journal_entry_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def journal_entry_detail(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    return render(request, 'journal/journal_entry_detail.html', {'entry': entry})

@login_required
def journal_entry_update(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Journal entry updated!')
            return redirect('journal_entry_detail', entry_id=entry.id)
    else:
        form = JournalEntryForm(instance=entry)
    return render(request, 'journal/journal_entry_form.html', {'form': form, 'entry': entry, 'form_type': 'Update'})

@login_required
def mood_tracker(request):
    entries = JournalEntry.objects.filter(
        user=request.user,
        mood__isnull=False,
        mood__gt=''
    ).order_by('date')
    
    # Prepare data for charts
    mood_data = []
    energy_data = []
    
    for entry in entries:
        mood_data.append({
            'date': entry.date.isoformat(),
            'mood': entry.mood,
        })
        if entry.energy_level:
            energy_data.append({
                'date': entry.date.isoformat(),
                'energy': entry.energy_level,
            })
    
    # Calculate statistics
    mood_counts = {}
    for entry in entries:
        mood_counts[entry.mood] = mood_counts.get(entry.mood, 0) + 1
    
    context = {
        'entries': entries,
        'mood_data': mood_data,
        'energy_data': energy_data,
        'mood_counts': mood_counts,
    }
    return render(request, 'journal/mood_tracker.html', context)

# Philosophy Views
@login_required
def philosophy_list(request):
    philosophies = Philosophy.objects.filter(user=request.user).order_by('-date_written')
    category_filter = request.GET.get('category')
    if category_filter:
        philosophies = philosophies.filter(category=category_filter)
    return render(request, 'journal/philosophy_list.html', {
        'philosophies': philosophies,
        'category_filter': category_filter
    })

@login_required
def philosophy_create(request):
    if request.method == 'POST':
        form = PhilosophyForm(request.POST)
        if form.is_valid():
            philosophy = form.save(commit=False)
            philosophy.user = request.user
            philosophy.save()
            messages.success(request, 'Philosophy saved!')
            return redirect('philosophy_list')
    else:
        form = PhilosophyForm()
    return render(request, 'journal/philosophy_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def philosophy_update(request, philosophy_id):
    philosophy = get_object_or_404(Philosophy, id=philosophy_id, user=request.user)
    if request.method == 'POST':
        form = PhilosophyForm(request.POST, instance=philosophy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Philosophy updated!')
            return redirect('philosophy_list')
    else:
        form = PhilosophyForm(instance=philosophy)
    return render(request, 'journal/philosophy_form.html', {'form': form, 'philosophy': philosophy, 'form_type': 'Update'})

# Vision Goal Views
@login_required
def vision_board(request):
    goals = VisionGoal.objects.filter(user=request.user).order_by('target_date')
    category_filter = request.GET.get('category')
    if category_filter:
        goals = goals.filter(category=category_filter)
    
    # Group by category
    goals_by_category = {}
    for goal in goals:
        if goal.category not in goals_by_category:
            goals_by_category[goal.category] = []
        goals_by_category[goal.category].append(goal)
    
    context = {
        'goals': goals,
        'goals_by_category': goals_by_category,
        'category_filter': category_filter,
    }
    return render(request, 'journal/vision_board.html', context)

@login_required
def vision_goal_create(request):
    if request.method == 'POST':
        form = VisionGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Vision goal created!')
            return redirect('vision_board')
    else:
        form = VisionGoalForm()
    return render(request, 'journal/vision_goal_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def vision_goal_update(request, goal_id):
    goal = get_object_or_404(VisionGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = VisionGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vision goal updated!')
            return redirect('vision_board')
    else:
        form = VisionGoalForm(instance=goal)
    return render(request, 'journal/vision_goal_form.html', {'form': form, 'goal': goal, 'form_type': 'Update'})

# Life Lesson Views
@login_required
def life_lessons_list(request):
    lessons = LifeLesson.objects.filter(user=request.user).order_by('-date_learned')
    return render(request, 'journal/life_lessons_list.html', {'lessons': lessons})

@login_required
def life_lessons_create(request):
    if request.method == 'POST':
        form = LifeLessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.user = request.user
            if not lesson.date_learned:
                lesson.date_learned = timezone.now().date()
            lesson.save()
            messages.success(request, 'Life lesson saved!')
            return redirect('life_lessons_list')
    else:
        form = LifeLessonForm(initial={'date_learned': timezone.now().date()})
    return render(request, 'journal/life_lessons_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def life_lessons_update(request, lesson_id):
    lesson = get_object_or_404(LifeLesson, id=lesson_id, user=request.user)
    if request.method == 'POST':
        form = LifeLessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Life lesson updated!')
            return redirect('life_lessons_list')
    else:
        form = LifeLessonForm(instance=lesson)
    return render(request, 'journal/life_lessons_form.html', {'form': form, 'lesson': lesson, 'form_type': 'Update'})
