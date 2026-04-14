from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Course, Note, Flashcard, StudySession
from .forms import CourseForm, NoteForm, FlashcardForm, StudySessionForm
from ai_assistant.services import generate_questions


def _recommended_session_minutes(course, session_count):
    base_minutes = 60 if course.learning_type in {'course', 'research'} else 45
    if session_count == 0:
        base_minutes += 15
    if course.effort_hours and course.effort_hours >= 40:
        base_minutes += 15
    return base_minutes


def _workflow_actions(course, note_count, flashcard_count, session_count, last_session, today):
    actions = []

    if note_count == 0:
        actions.append('Capture your first note so the record has real learning context.')

    if course.learning_type in {'course', 'certification', 'self_study', 'research'} and flashcard_count == 0:
        actions.append('Create flashcards for the core concepts you want to retain.')

    if session_count == 0:
        actions.append('Log your first focused study or practice session.')
    elif last_session and (today - last_session.date).days >= 7 and course.status == 'ongoing':
        actions.append('Record a fresh study session to keep this record active.')

    if course.status == 'ongoing':
        if course.learning_type == 'course':
            actions.append('When the class ends, mark it completed and add the final grade if available.')
        else:
            actions.append('When this learning track ends, add the completion date and the real outcome.')
    elif course.status == 'completed':
        if not course.outcome:
            actions.append('Add the outcome so this completed record is useful later in your career.')
        if course.learning_type == 'course' and course.grade is None:
            actions.append('Add the final grade when it is released to keep GPA reporting accurate.')
    elif course.status == 'dropped' and not course.outcome:
        actions.append('Document why this record was dropped so future planning stays grounded.')

    return actions


def _build_record_snapshot(course, today):
    note_count = course.notes.count()
    flashcard_count = course.flashcards.count()
    sessions = list(course.study_sessions.all().order_by('-date', '-created_at'))
    session_count = len(sessions)
    last_session = sessions[0] if sessions else None
    total_minutes = sum(session.duration_minutes for session in sessions)
    workflow_actions = _workflow_actions(
        course,
        note_count,
        flashcard_count,
        session_count,
        last_session,
        today,
    )

    return {
        'course': course,
        'note_count': note_count,
        'flashcard_count': flashcard_count,
        'session_count': session_count,
        'last_session': last_session,
        'total_minutes': total_minutes,
        'recommended_minutes': _recommended_session_minutes(course, session_count),
        'workflow_actions': workflow_actions,
        'next_action': workflow_actions[0] if workflow_actions else 'This record is in a healthy state.',
    }

@login_required
def dashboard(request):
    today = timezone.now().date()
    courses = Course.objects.filter(user=request.user).prefetch_related('notes', 'flashcards', 'study_sessions')
    academic_courses = courses.filter(learning_type='course')
    professional_learning = courses.exclude(learning_type='course')
    
    # GPA Calculation - only include completed courses
    completed_courses = academic_courses.filter(status='completed')
    total_points = 0
    total_credits = 0
    for course in completed_courses:
        if course.grade and course.credits:
            total_points += (course.grade * course.credits)
            total_credits += course.credits
    
    gpa = total_points / total_credits if total_credits > 0 else 0.0
    
    # Recent study sessions
    recent_sessions = StudySession.objects.filter(course__user=request.user).order_by('-date')[:5]
    
    # Study analytics
    all_sessions = StudySession.objects.filter(course__user=request.user)
    total_study_time = sum(s.duration_minutes for s in all_sessions)
    total_study_hours = round(total_study_time / 60, 1) if total_study_time > 0 else 0
    total_learning_hours = sum(course.effort_hours for course in courses)
    
    # Study time by course
    study_time_by_course = {}
    for session in all_sessions:
        course_name = session.course.name
        study_time_by_course[course_name] = study_time_by_course.get(course_name, 0) + session.duration_minutes
    
    # Study sessions over time (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_sessions_data = {}
    for session in all_sessions.filter(date__gte=thirty_days_ago):
        date_str = session.date.isoformat()
        recent_sessions_data[date_str] = recent_sessions_data.get(date_str, 0) + session.duration_minutes
    
    # Course status breakdown
    course_status_data = {
        'ongoing': courses.filter(status='ongoing').count(),
        'completed': courses.filter(status='completed').count(),
        'dropped': courses.filter(status='dropped').count(),
    }

    professional_status_data = {
        'active_development': professional_learning.filter(status='ongoing').count(),
        'completed_credentials': courses.filter(
            learning_type__in=['certification', 'training'],
            status='completed'
        ).count(),
        'self_study_tracks': courses.filter(learning_type='self_study').count(),
    }

    development_breakdown = {
        'academic': academic_courses.count(),
        'professional': professional_learning.count(),
    }

    recent_completions = courses.filter(status='completed').order_by('-completion_date', '-updated_at')[:5]
    records_needing_attention = [
        snapshot for snapshot in
        (_build_record_snapshot(course, today) for course in courses)
        if snapshot['workflow_actions']
    ][:5]
    
    context = {
        'courses': courses,
        'academic_courses': academic_courses,
        'professional_learning': professional_learning,
        'gpa': round(gpa, 2),
        'total_credits': total_credits,
        'recent_sessions': recent_sessions,
        'total_study_hours': total_study_hours,
        'total_learning_hours': total_learning_hours,
        'study_time_by_course': study_time_by_course,
        'recent_sessions_data': recent_sessions_data,
        'course_status_data': course_status_data,
        'professional_status_data': professional_status_data,
        'development_breakdown': development_breakdown,
        'recent_completions': recent_completions,
        'records_needing_attention': records_needing_attention,
    }
    return render(request, 'academic/dashboard.html', context)

@login_required
def course_list(request):
    courses = Course.objects.filter(user=request.user).order_by('-created_at')
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    if status_filter:
        courses = courses.filter(status=status_filter)
    if type_filter:
        courses = courses.filter(learning_type=type_filter)
    return render(request, 'academic/course_list.html', {
        'courses': courses,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'status_choices': Course.STATUS_CHOICES,
        'type_choices': Course.LEARNING_TYPE_CHOICES,
    })

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            messages.success(request, 'Learning record created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm()
    return render(request, 'academic/course_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Learning record updated successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    return render(request, 'academic/course_form.html', {'form': form, 'course': course, 'form_type': 'Update'})

@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Learning record deleted successfully!')
        return redirect('academic_dashboard')
    return render(request, 'academic/course_confirm_delete.html', {'course': course})

@login_required
def course_detail(request, course_id):
    today = timezone.now().date()
    course = get_object_or_404(
        Course.objects.prefetch_related('notes', 'flashcards', 'study_sessions'),
        id=course_id,
        user=request.user,
    )
    notes = course.notes.all().order_by('-updated_at')
    flashcards = course.flashcards.all()
    sessions = course.study_sessions.all().order_by('-date')
    total_session_minutes = sum(session.duration_minutes for session in sessions)
    last_session = sessions.first()
    workflow_actions = _workflow_actions(
        course,
        notes.count(),
        flashcards.count(),
        sessions.count(),
        last_session,
        today,
    )
    
    context = {
        'course': course,
        'notes': notes,
        'flashcards': flashcards,
        'sessions': sessions,
        'total_session_minutes': total_session_minutes,
        'last_session': last_session,
        'workflow_actions': workflow_actions,
        'next_action': workflow_actions[0] if workflow_actions else 'This record is well documented and up to date.',
        'recommended_minutes': _recommended_session_minutes(course, sessions.count()),
    }
    return render(request, 'academic/course_detail.html', context)

@login_required
def note_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.course = course
            note.save()
            messages.success(request, 'Note created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = NoteForm()
    return render(request, 'academic/note_form.html', {'form': form, 'course': course, 'form_type': 'Create'})

@login_required
def note_update(request, note_id):
    note = get_object_or_404(Note, id=note_id, course__user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated successfully!')
            return redirect('course_detail', course_id=note.course.id)
    else:
        form = NoteForm(instance=note)
    return render(request, 'academic/note_form.html', {'form': form, 'note': note, 'course': note.course, 'form_type': 'Update'})

@login_required
def note_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id, course__user=request.user)
    course_id = note.course.id
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('course_detail', course_id=course_id)
    return render(request, 'academic/note_confirm_delete.html', {'note': note})

@login_required
def flashcard_list(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    flashcards = course.flashcards.all()
    return render(request, 'academic/flashcard_list.html', {'course': course, 'flashcards': flashcards})

@login_required
def flashcard_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    if request.method == 'POST':
        form = FlashcardForm(request.POST)
        if form.is_valid():
            flashcard = form.save(commit=False)
            flashcard.course = course
            flashcard.save()
            messages.success(request, 'Flashcard created successfully!')
            return redirect('flashcard_list', course_id=course.id)
    else:
        form = FlashcardForm()
    return render(request, 'academic/flashcard_form.html', {'form': form, 'course': course})

@login_required
def flashcard_update(request, flashcard_id):
    flashcard = get_object_or_404(Flashcard, id=flashcard_id, course__user=request.user)
    if request.method == 'POST':
        form = FlashcardForm(request.POST, instance=flashcard)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flashcard updated successfully!')
            return redirect('flashcard_list', course_id=flashcard.course.id)
    else:
        form = FlashcardForm(instance=flashcard)
    return render(request, 'academic/flashcard_form.html', {'form': form, 'course': flashcard.course, 'flashcard': flashcard})

@login_required
def flashcard_delete(request, flashcard_id):
    flashcard = get_object_or_404(Flashcard, id=flashcard_id, course__user=request.user)
    course_id = flashcard.course.id
    if request.method == 'POST':
        flashcard.delete()
        messages.success(request, 'Flashcard deleted successfully!')
        return redirect('flashcard_list', course_id=course_id)
    return render(request, 'academic/flashcard_confirm_delete.html', {'flashcard': flashcard})

@login_required
def flashcard_study(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    flashcards = course.flashcards.all()
    # Serialize flashcards to JSON for JavaScript
    flashcards_json = [{'question': card.question, 'answer': card.answer} for card in flashcards]
    import json
    return render(request, 'academic/flashcard_study.html', {
        'course': course, 
        'flashcards': flashcards,
        'flashcards_json': json.dumps(flashcards_json)
    })

@login_required
def study_session_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    if request.method == 'POST':
        form = StudySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.course = course
            if not session.date:
                session.date = timezone.now().date()
            session.save()
            messages.success(request, 'Study session recorded!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = StudySessionForm(initial={'date': timezone.now().date()})
    return render(request, 'academic/study_session_form.html', {'form': form, 'course': course})

@login_required
def study_session_update(request, session_id):
    session = get_object_or_404(StudySession, id=session_id, course__user=request.user)
    if request.method == 'POST':
        form = StudySessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Study session updated successfully!')
            return redirect('course_detail', course_id=session.course.id)
    else:
        form = StudySessionForm(instance=session)
    return render(request, 'academic/study_session_form.html', {'form': form, 'course': session.course, 'session': session})

@login_required
def study_session_delete(request, session_id):
    session = get_object_or_404(StudySession, id=session_id, course__user=request.user)
    course_id = session.course.id
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Study session deleted successfully!')
        return redirect('course_detail', course_id=course_id)
    return render(request, 'academic/study_session_confirm_delete.html', {'session': session})

@login_required
def gpa_calculator(request):
    courses = Course.objects.filter(user=request.user, status='completed', learning_type='course')
    course_rows = []
    
    total_points = 0
    total_credits = 0
    for course in courses:
        if course.grade and course.credits:
            course_points = course.grade * course.credits
            total_points += course_points
            total_credits += course.credits
            course_rows.append({
                'course': course,
                'points': round(course_points, 2),
            })
    
    gpa = total_points / total_credits if total_credits > 0 else 0.0

    if request.method == 'POST':
        return JsonResponse({'gpa': round(gpa, 2), 'total_credits': float(total_credits)})
    
    context = {
        'course_rows': course_rows,
        'gpa': round(gpa, 2),
        'total_credits': total_credits,
        'total_points': round(total_points, 2),
    }
    return render(request, 'academic/gpa_calculator.html', context)

@login_required
def ai_question_generator(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    num_questions = 5
    topic = ''
    
    if request.method == 'POST':
        topic = request.POST.get('topic', '')
        try:
            num_questions = int(request.POST.get('num_questions', 5))
        except (TypeError, ValueError):
            num_questions = 5
        num_questions = max(1, min(num_questions, 10))
        
        try:
            questions = generate_questions(course.name, topic, num_questions)
            return render(request, 'academic/ai_question_generator.html', {
                'course': course,
                'questions': questions,
                'topic': topic,
                'num_questions': num_questions,
            })
        except Exception as e:
            messages.error(request, f'Error generating questions: {str(e)}')
    
    return render(request, 'academic/ai_question_generator.html', {
        'course': course,
        'num_questions': num_questions,
        'topic': topic,
    })

@login_required
def study_planner(request):
    today = timezone.now().date()
    courses = Course.objects.filter(user=request.user, status='ongoing').prefetch_related('notes', 'flashcards', 'study_sessions')
    focus_records = sorted(
        (_build_record_snapshot(course, today) for course in courses),
        key=lambda snapshot: (
            snapshot['session_count'] > 0,
            snapshot['last_session'].date if snapshot['last_session'] else today - timedelta(days=3650),
            snapshot['note_count'] + snapshot['flashcard_count'],
        ),
    )
    recent_sessions = StudySession.objects.filter(course__user=request.user).select_related('course').order_by('-date', '-created_at')[:10]
    planner_days = []
    today = timezone.now().date()
    planning_window = max(7, len(focus_records))
    for i in range(planning_window):
        date = today + timedelta(days=i)
        focus_record = focus_records[i % len(focus_records)] if focus_records else None
        planner_days.append({
            'date': date,
            'focus_record': focus_record,
        })
    
    context = {
        'courses': courses,
        'focus_records': focus_records,
        'planner_days': planner_days,
        'recent_sessions': recent_sessions,
    }
    return render(request, 'academic/study_planner.html', context)
