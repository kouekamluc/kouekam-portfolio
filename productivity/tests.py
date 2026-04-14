from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import Task, Habit, Goal, Document, Timetable, Transaction, Milestone
from .forms import TaskForm, HabitForm, GoalForm, TransactionForm

User = get_user_model()


def create_test_user(email='test@example.com', password='testpass123', username='testuser'):
    return User.objects.create_user(username=username, email=email, password=password)


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_task_creation(self):
        task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='Test description',
            status='todo',
            priority='high'
        )
        self.assertEqual(str(task), 'Test Task')
        self.assertEqual(task.user, self.user)

    def test_task_ordering(self):
        task1 = Task.objects.create(
            user=self.user,
            title='Task 1',
            priority='low',
            due_date=date.today() + timedelta(days=2)
        )
        task2 = Task.objects.create(
            user=self.user,
            title='Task 2',
            priority='high',
            due_date=date.today() + timedelta(days=1)
        )
        tasks = list(Task.objects.filter(user=self.user))
        self.assertEqual(tasks[0], task2)  # Higher priority, earlier due date


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_habit_creation(self):
        habit = Habit.objects.create(
            user=self.user,
            name='Exercise',
            frequency='daily',
            current_streak=5
        )
        self.assertEqual(str(habit), 'Exercise')
        self.assertEqual(habit.current_streak, 5)


class GoalModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_goal_creation(self):
        goal = Goal.objects.create(
            user=self.user,
            title='Learn Python',
            description='Complete Python course',
            progress=50
        )
        self.assertEqual(str(goal), 'Learn Python')
        self.assertEqual(goal.progress, 50)


class MilestoneModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()
        self.goal = Goal.objects.create(
            user=self.user,
            title='Test Goal',
            progress=0
        )

    def test_milestone_creation(self):
        milestone = Milestone.objects.create(
            goal=self.goal,
            title='Milestone 1',
            description='First milestone',
            completed=False
        )
        self.assertIn('Test Goal', str(milestone))


class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            user=self.user,
            type='expense',
            amount=Decimal('50.00'),
            category='food',
            date=date.today()
        )
        self.assertIn('Expense', str(transaction))
        self.assertEqual(transaction.amount, Decimal('50.00'))


class ProductivityViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_test_user()

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('productivity_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('productivity_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_task_list_requires_login(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 302)

    def test_task_list_authenticated(self):
        self.client.force_login(self.user)
        Task.objects.create(
            user=self.user,
            title='Test Task',
            status='todo'
        )
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)

    def test_habit_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('habit_list'))
        self.assertEqual(response.status_code, 200)

    def test_goal_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('goal_list'))
        self.assertEqual(response.status_code, 200)

    def test_transaction_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)


class ProductivityFormsTest(TestCase):
    def test_task_form_valid(self):
        form = TaskForm(data={
            'title': 'Test Task',
            'description': 'Test description',
            'status': 'todo',
            'priority': 'medium'
        })
        self.assertTrue(form.is_valid())

    def test_habit_form_valid(self):
        form = HabitForm(data={
            'name': 'Exercise',
            'frequency': 'daily'
        })
        self.assertTrue(form.is_valid())

    def test_goal_form_valid(self):
        form = GoalForm(data={
            'title': 'Test Goal',
            'description': 'Test description',
            'progress': 0
        })
        self.assertTrue(form.is_valid())

    def test_transaction_form_valid(self):
        form = TransactionForm(data={
            'type': 'expense',
            'amount': '50.00',
            'category': 'food',
            'date': date.today()
        })
        self.assertTrue(form.is_valid())

    def test_transaction_form_rejects_income_with_expense_category(self):
        form = TransactionForm(data={
            'type': 'income',
            'amount': '50.00',
            'category': 'food',
            'date': date.today()
        })
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)


class ProductivityWorkflowLogicTest(TestCase):
    def setUp(self):
        self.user = create_test_user(username='productivityuser')

    def test_weekly_habit_tracks_once_per_week(self):
        client = Client()
        client.force_login(self.user)
        habit = Habit.objects.create(
            user=self.user,
            name='Weekly Review',
            frequency='weekly',
            current_streak=2,
            last_completed_date=date.today() - timedelta(days=7),
        )

        response = client.post(reverse('habit_track', args=[habit.id]))

        self.assertEqual(response.status_code, 302)
        habit.refresh_from_db()
        self.assertEqual(habit.current_streak, 3)

    def test_goal_progress_updates_from_completed_milestones(self):
        client = Client()
        client.force_login(self.user)
        goal = Goal.objects.create(user=self.user, title='Launch Portfolio', progress=0)
        Milestone.objects.create(goal=goal, title='Resume', completed=False)
        completed = Milestone.objects.create(goal=goal, title='Projects', completed=False)

        response = client.post(reverse('milestone_manage', args=[goal.id]), {
            'complete': '1',
            'milestone_id': completed.id,
        })

        self.assertEqual(response.status_code, 302)
        goal.refresh_from_db()
        self.assertEqual(goal.progress, 50)
