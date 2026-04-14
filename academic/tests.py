from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date
from .models import Course, Note, Flashcard, StudySession
from .forms import CourseForm, NoteForm, FlashcardForm, StudySessionForm

User = get_user_model()


def create_test_user(email='test@example.com', password='testpass123', username='testuser'):
    return User.objects.create_user(username=username, email=email, password=password)


class CourseModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_course_creation(self):
        course = Course.objects.create(
            user=self.user,
            name='Introduction to Python',
            code='CS101',
            semester='Fall 2024',
            credits=3.0,
            status='ongoing'
        )
        self.assertEqual(str(course), 'CS101 - Introduction to Python')
        self.assertEqual(course.user, self.user)

    def test_course_without_code(self):
        course = Course.objects.create(
            user=self.user,
            name='Introduction to Python',
            credits=3.0
        )
        self.assertEqual(str(course), 'Introduction to Python')


class NoteModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()
        self.course = Course.objects.create(
            user=self.user,
            name='Test Course',
            credits=3.0
        )

    def test_note_creation(self):
        note = Note.objects.create(
            course=self.course,
            title='Test Note',
            content='Test content'
        )
        self.assertEqual(str(note), 'Test Note')
        self.assertEqual(note.course, self.course)


class FlashcardModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()
        self.course = Course.objects.create(
            user=self.user,
            name='Test Course',
            code='CS101'
        )

    def test_flashcard_creation(self):
        flashcard = Flashcard.objects.create(
            course=self.course,
            question='What is Python?',
            answer='A programming language'
        )
        self.assertIn('CS101', str(flashcard))


class StudySessionModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()
        self.course = Course.objects.create(
            user=self.user,
            name='Test Course',
            code='CS101'
        )

    def test_study_session_creation(self):
        session = StudySession.objects.create(
            course=self.course,
            date=date.today(),
            duration_minutes=60,
            topics_covered='Variables, Functions'
        )
        self.assertIn('CS101', str(session))


class AcademicViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_test_user()
        self.course = Course.objects.create(
            user=self.user,
            name='Test Course',
            code='CS101',
            credits=3.0
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('academic_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('academic_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_course_list_requires_login(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 302)

    def test_course_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)

    def test_course_create_requires_login(self):
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 302)

    def test_course_create_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 200)

    def test_course_detail(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_note_create(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('note_create', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_flashcard_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('flashcard_list', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)


class AcademicFormsTest(TestCase):
    def setUp(self):
        self.user = create_test_user()
        self.course = Course.objects.create(
            user=self.user,
            name='Test Course',
            credits=3.0
        )

    def test_course_form_valid(self):
        form = CourseForm(data={
            'name': 'New Course',
            'code': 'CS102',
            'learning_type': 'course',
            'credits': 3.0,
            'status': 'ongoing'
        })
        self.assertTrue(form.is_valid())

    def test_note_form_valid(self):
        form = NoteForm(data={
            'title': 'Test Note',
            'content': 'Test content'
        })
        self.assertTrue(form.is_valid())

    def test_flashcard_form_valid(self):
        form = FlashcardForm(data={
            'question': 'What is Django?',
            'answer': 'A web framework'
        })
        self.assertTrue(form.is_valid())

    def test_study_session_form_valid(self):
        form = StudySessionForm(data={
            'date': date.today(),
            'duration_minutes': 60,
            'topics_covered': 'Test topics'
        })
        self.assertTrue(form.is_valid())

    def test_course_form_rejects_grade_for_ongoing_course(self):
        form = CourseForm(data={
            'name': 'New Course',
            'code': 'CS102',
            'credits': 3.0,
            'status': 'ongoing',
            'grade': 3.8,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('grade', form.errors)

    def test_certification_requires_provider(self):
        form = CourseForm(data={
            'name': 'AWS Cloud Practitioner',
            'learning_type': 'certification',
            'credits': 0,
            'effort_hours': 40,
            'status': 'completed',
            'completion_date': date.today(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn('provider', form.errors)

    def test_self_study_can_use_hours_without_credits(self):
        form = CourseForm(data={
            'name': 'Embedded Systems Interview Prep',
            'learning_type': 'self_study',
            'credits': 0,
            'effort_hours': 25,
            'status': 'ongoing',
        })
        self.assertTrue(form.is_valid())
