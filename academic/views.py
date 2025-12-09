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
    
    # Simple GPA Calculation
    total_points = 0
    total_credits = 0
    for course in courses:
        if course.grade and course.credits:
            total_points += (course.grade * course.credits)
            total_credits += course.credits
    
    gpa = total_points / total_credits if total_credits > 0 else 0.0
    
    # Recent study sessions
    recent_sessions = StudySession.objects.filter(course__user=request.user).order_by('-date')[:5]
    
    context = {
        'courses': courses,
        'gpa': round(gpa, 2),
        'total_credits': total_credits,
        'recent_sessions': recent_sessions,
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
def flashcard_study(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    flashcards = list(course.flashcards.all())
    return render(request, 'academic/flashcard_study.html', {'course': course, 'flashcards': flashcards})

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
        
        return JsonResponse({'gpa': round(gpa, 2), 'total_credits': total_credits})
    
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
