from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date
from .models import Course, Note, Flashcard, StudySession
from .forms import CourseForm, NoteForm, FlashcardForm, StudySessionForm

User = get_user_model()


class CourseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

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
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
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
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
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
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
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
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
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
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('academic_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_course_list_requires_login(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 302)

    def test_course_list_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)

    def test_course_create_requires_login(self):
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 302)

    def test_course_create_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 200)

    def test_course_detail(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_note_create(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('note_create', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_flashcard_list(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('flashcard_list', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)


class AcademicFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            user=self.user,
            name='Test Course',
            credits=3.0
        )

    def test_course_form_valid(self):
        form = CourseForm(data={
            'name': 'New Course',
            'code': 'CS102',
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
