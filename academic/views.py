from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Course, Note, Flashcard, StudySession
from .forms import CourseForm, NoteForm, FlashcardForm, StudySessionForm
from ai_assistant.services import generate_questions

@login_required
def dashboard(request):
    courses = Course.objects.filter(user=request.user)
    
    # GPA Calculation - only include completed courses
    completed_courses = courses.filter(status='completed')
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
    
    context = {
        'courses': courses,
        'gpa': round(gpa, 2),
        'total_credits': total_credits,
        'recent_sessions': recent_sessions,
        'total_study_hours': total_study_hours,
        'study_time_by_course': study_time_by_course,
        'recent_sessions_data': recent_sessions_data,
        'course_status_data': course_status_data,
    }
    return render(request, 'academic/dashboard.html', context)

@login_required
def course_list(request):
    courses = Course.objects.filter(user=request.user).order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        courses = courses.filter(status=status_filter)
    return render(request, 'academic/course_list.html', {'courses': courses, 'status_filter': status_filter})

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
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
            messages.success(request, 'Course updated successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    return render(request, 'academic/course_form.html', {'form': form, 'course': course, 'form_type': 'Update'})

@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('academic_dashboard')
    return render(request, 'academic/course_confirm_delete.html', {'course': course})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    notes = course.notes.all().order_by('-updated_at')
    flashcards = course.flashcards.all()
    sessions = course.study_sessions.all().order_by('-date')
    
    context = {
        'course': course,
        'notes': notes,
        'flashcards': flashcards,
        'sessions': sessions
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
    courses = Course.objects.filter(user=request.user, status='completed')
    
    if request.method == 'POST':
        # Recalculate GPA
        total_points = 0
        total_credits = 0
        for course in courses:
            if course.grade and course.credits:
                total_points += (course.grade * course.credits)
                total_credits += course.credits
        
        gpa = total_points / total_credits if total_credits > 0 else 0.0
        
        return JsonResponse({'gpa': round(gpa, 2), 'total_credits': float(total_credits)})
    
    # Calculate current GPA
    total_points = 0
    total_credits = 0
    for course in courses:
        if course.grade and course.credits:
            total_points += (course.grade * course.credits)
            total_credits += course.credits
    
    gpa = total_points / total_credits if total_credits > 0 else 0.0
    
    context = {
        'courses': courses,
        'gpa': round(gpa, 2),
        'total_credits': total_credits,
    }
    return render(request, 'academic/gpa_calculator.html', context)

@login_required
def ai_question_generator(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    
    if request.method == 'POST':
        topic = request.POST.get('topic', '')
        num_questions = int(request.POST.get('num_questions', 5))
        
        try:
            questions = generate_questions(course.name, topic, num_questions)
            return render(request, 'academic/ai_question_generator.html', {
                'course': course,
                'questions': questions,
                'topic': topic,
            })
        except Exception as e:
            messages.error(request, f'Error generating questions: {str(e)}')
    
    return render(request, 'academic/ai_question_generator.html', {'course': course})

@login_required
def study_planner(request):
    courses = Course.objects.filter(user=request.user, status='ongoing')
    sessions = StudySession.objects.filter(course__user=request.user).order_by('-date')
    
    # Get calendar data for the next 30 days
    calendar_data = []
    today = timezone.now().date()
    for i in range(30):
        date = today + timedelta(days=i)
        day_sessions = sessions.filter(date=date)
        calendar_data.append({
            'date': date,
            'sessions': day_sessions,
        })
    
    context = {
        'courses': courses,
        'calendar_data': calendar_data,
    }
    return render(request, 'academic/study_planner.html', context)
