from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date
from .models import JournalEntry, Philosophy, VisionGoal, LifeLesson

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
