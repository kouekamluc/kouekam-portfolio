from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from .models import JournalEntry, Philosophy, VisionGoal, LifeLesson
from .forms import JournalEntryForm, PhilosophyForm, VisionGoalForm, LifeLessonForm

@login_required
def journal_dashboard(request):
    recent_entries = JournalEntry.objects.filter(user=request.user).order_by('-date')[:5]
    recent_philosophies = Philosophy.objects.filter(user=request.user).order_by('-date_written')[:3]
    active_goals = VisionGoal.objects.filter(user=request.user).order_by('target_date')[:5]
    
    # Journal analytics
    all_entries = JournalEntry.objects.filter(user=request.user)
    total_entries = all_entries.count()
    
    # Mood distribution
    mood_counts = {}
    for entry in all_entries.filter(mood__isnull=False):
        mood_counts[entry.mood] = mood_counts.get(entry.mood, 0) + 1
    
    # Energy level distribution
    energy_counts = {}
    for entry in all_entries.filter(energy_level__isnull=False):
        energy_counts[entry.energy_level] = energy_counts.get(entry.energy_level, 0) + 1
    
    # Entries over time (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    entries_over_time = {}
    for entry in all_entries.filter(date__gte=thirty_days_ago):
        date_str = entry.date.isoformat()
        entries_over_time[date_str] = entries_over_time.get(date_str, 0) + 1
    
    # Vision goal progress
    goal_progress_data = [g.progress for g in VisionGoal.objects.filter(user=request.user)]
    avg_goal_progress = sum(goal_progress_data) / len(goal_progress_data) if goal_progress_data else 0
    
    context = {
        'recent_entries': recent_entries,
        'recent_philosophies': recent_philosophies,
        'active_goals': active_goals,
        'total_entries': total_entries,
        'mood_counts': mood_counts,
        'energy_counts': energy_counts,
        'entries_over_time': entries_over_time,
        'avg_goal_progress': round(avg_goal_progress, 1),
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


@login_required
def export_journal_pdf(request):
    """Export journal entries as PDF"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER
        from io import BytesIO
    except ImportError:
        messages.error(request, 'ReportLab is required for PDF export. Please install it: pip install reportlab')
        return redirect('journal_dashboard')
    
    entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1e40af',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Journal Entries", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Entries
    for entry in entries:
        # Date header
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#374151',
            spaceAfter=12,
            spaceBefore=20
        )
        story.append(Paragraph(f"{entry.date.strftime('%B %d, %Y')}", date_style))
        
        # Mood and energy
        if entry.mood or entry.energy_level:
            info_text = []
            if entry.mood:
                info_text.append(f"Mood: {entry.get_mood_display()}")
            if entry.energy_level:
                info_text.append(f"Energy: {entry.get_energy_level_display()}")
            story.append(Paragraph(" | ".join(info_text), styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Content
        content_style = ParagraphStyle(
            'ContentStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            leftIndent=0.2*inch
        )
        story.append(Paragraph(entry.content.replace('\n', '<br/>'), content_style))
        
        # Tags
        if entry.tags:
            story.append(Paragraph(f"Tags: {entry.tags}", styles['Italic']))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(PageBreak())
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="journal_entries_{timezone.now().date()}.pdf"'
    return response
