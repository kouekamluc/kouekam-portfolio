from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from .models import BusinessIdea, MarketResearch, BusinessPlan, ImportExportRecord

User = get_user_model()


class BusinessIdeaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_business_idea_creation(self):
        idea = BusinessIdea.objects.create(
            user=self.user,
            title='Test Business',
            description='Test description',
            status='idea'
        )
        self.assertEqual(str(idea), 'Test Business')
        self.assertEqual(idea.user, self.user)


class MarketResearchModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.idea = BusinessIdea.objects.create(
            user=self.user,
            title='Test Business',
            description='Test'
        )

    def test_market_research_creation(self):
        research = MarketResearch.objects.create(
            business_idea=self.idea,
            user=self.user,
            findings='Test findings',
            date='2024-01-01'
        )
        self.assertIn('Test Business', str(research))


class BusinessPlanModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.idea = BusinessIdea.objects.create(
            user=self.user,
            title='Test Business',
            description='Test'
        )

    def test_business_plan_creation(self):
        plan = BusinessPlan.objects.create(
            business_idea=self.idea,
            user=self.user,
            executive_summary='Test summary',
            financial_data={'revenue': 100000}
        )
        self.assertIn('Test Business', str(plan))


class ImportExportRecordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_import_export_record_creation(self):
        record = ImportExportRecord.objects.create(
            user=self.user,
            product='Test Product',
            quantity=Decimal('100.00'),
            value=Decimal('5000.00'),
            country='USA',
            date='2024-01-01',
            type='export'
        )
        self.assertIn('Export', str(record))


class BusinessViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_business_dashboard_requires_login(self):
        response = self.client.get(reverse('business_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_business_dashboard_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('business_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_business_idea_list_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('business_idea_list'))
        self.assertEqual(response.status_code, 200)
