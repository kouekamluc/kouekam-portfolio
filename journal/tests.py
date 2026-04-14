from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import JournalEntry, Philosophy, VisionGoal, LifeLesson
from .forms import JournalEntryForm, LifeLessonForm

User = get_user_model()


def create_test_user(email='test@example.com', password='testpass123', username='testuser'):
    return User.objects.create_user(username=username, email=email, password=password)


class JournalEntryModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_journal_entry_creation(self):
        entry = JournalEntry.objects.create(
            user=self.user,
            date=date.today(),
            content='Test journal entry',
            mood='good',
            energy_level='high'
        )
        self.assertIn(str(date.today()), str(entry))
        self.assertEqual(entry.user, self.user)

    def test_journal_entry_unique_per_day(self):
        JournalEntry.objects.create(
            user=self.user,
            date=date.today(),
            content='First entry'
        )
        # Should allow only one entry per user per day
        # The unique_together constraint will prevent duplicate entries
        entry2 = JournalEntry(
            user=self.user,
            date=date.today(),
            content='Second entry'
        )
        # This should raise IntegrityError when saved
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            entry2.save()


class PhilosophyModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_philosophy_creation(self):
        philosophy = Philosophy.objects.create(
            user=self.user,
            title='Test Philosophy',
            content='Test content',
            category='life'
        )
        self.assertEqual(str(philosophy), 'Test Philosophy')


class VisionGoalModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_vision_goal_creation(self):
        goal = VisionGoal.objects.create(
            user=self.user,
            title='Test Vision Goal',
            description='Test description',
            category='career',
            progress=25
        )
        self.assertEqual(str(goal), 'Test Vision Goal')
        self.assertEqual(goal.progress, 25)


class LifeLessonModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_life_lesson_creation(self):
        lesson = LifeLesson.objects.create(
            user=self.user,
            title='Test Lesson',
            lesson='Test lesson content',
            date_learned=date.today()
        )
        self.assertEqual(str(lesson), 'Test Lesson')


class JournalViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_test_user()

    def test_journal_dashboard_requires_login(self):
        response = self.client.get(reverse('journal_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_journal_dashboard_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('journal_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_journal_entry_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('journal_entry_list'))
        self.assertEqual(response.status_code, 200)

    def test_philosophy_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('philosophy_list'))
        self.assertEqual(response.status_code, 200)

    def test_journal_entry_create_defaults_blank_date_to_today(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('journal_entry_create'), {
            'content': 'A solid day of engineering work.',
            'mood': 'good',
            'energy_level': 'high',
            'tags': 'work,focus',
        })
        self.assertEqual(response.status_code, 302)
        entry = JournalEntry.objects.get(user=self.user)
        self.assertEqual(entry.date, timezone.now().date())

    def test_journal_entry_update_rejects_duplicate_date(self):
        entry_one = JournalEntry.objects.create(user=self.user, date=date.today(), content='First')
        entry_two = JournalEntry.objects.create(user=self.user, date=date.today() - timedelta(days=1), content='Second')
        self.client.force_login(self.user)
        response = self.client.post(reverse('journal_entry_update', args=[entry_two.id]), {
            'date': entry_one.date,
            'content': 'Second updated',
            'mood': '',
            'energy_level': '',
            'tags': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already have an entry for this date')

    def test_life_lesson_create_defaults_blank_date_to_today(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('life_lessons_create'), {
            'title': 'Prototype faster',
            'lesson': 'Shorter feedback loops help.',
            'context': 'Capstone project',
        })
        self.assertEqual(response.status_code, 302)
        lesson = LifeLesson.objects.get(user=self.user)
        self.assertEqual(lesson.date_learned, timezone.now().date())


class JournalFormsTest(TestCase):
    def test_journal_entry_form_allows_blank_date(self):
        form = JournalEntryForm(data={
            'content': 'Reflection',
            'mood': 'good',
            'energy_level': 'medium',
            'tags': 'daily',
        })
        self.assertTrue(form.is_valid())

    def test_life_lesson_form_allows_blank_date(self):
        form = LifeLessonForm(data={
            'title': 'Listen more',
            'lesson': 'Listening changes the outcome.',
            'context': 'Team project',
        })
        self.assertTrue(form.is_valid())
