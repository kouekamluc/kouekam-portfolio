from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from .models import BusinessIdea, MarketResearch, BusinessPlan, ImportExportRecord

User = get_user_model()


def create_test_user(email='test@example.com', password='testpass123', username='testuser'):
    return User.objects.create_user(username=username, email=email, password=password)


class BusinessIdeaModelTest(TestCase):
    def setUp(self):
        self.user = create_test_user()

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
        self.user = create_test_user()
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
        self.user = create_test_user()
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
        self.user = create_test_user()

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
        self.user = create_test_user()

    def test_business_dashboard_requires_login(self):
        response = self.client.get(reverse('business_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_business_dashboard_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('business_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_business_idea_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('business_idea_list'))
        self.assertEqual(response.status_code, 200)


class BusinessWorkflowValidationTest(TestCase):
    def setUp(self):
        self.user = create_test_user(username='businessuser')

    def test_active_business_idea_requires_plan(self):
        idea = BusinessIdea.objects.create(
            user=self.user,
            title='Campus Hardware Studio',
            description='A productized engineering service.',
            status='idea'
        )

        from .forms import BusinessIdeaForm
        form = BusinessIdeaForm(
            data={
                'title': idea.title,
                'description': idea.description,
                'status': 'active',
                'market_size': 'Engineering students and early-career professionals',
                'competitors': 'Freelance makerspaces',
            },
            instance=idea,
        )
        self.assertFalse(form.is_valid())

    def test_business_plan_form_rejects_negative_funding(self):
        from .forms import BusinessPlanForm

        form = BusinessPlanForm(data={
            'executive_summary': 'Summary',
            'revenue_projections': '10k',
            'expense_projections': '7k',
            'funding_needed': '-1000',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('funding_needed', form.errors)

    def test_active_business_idea_requires_market_validation_as_well(self):
        idea = BusinessIdea.objects.create(
            user=self.user,
            title='IoT Prototype Lab',
            description='Build devices for local SMEs.',
            status='planning'
        )
        BusinessPlan.objects.create(
            business_idea=idea,
            user=self.user,
            executive_summary='Plan',
            financial_data={},
        )

        from .forms import BusinessIdeaForm
        form = BusinessIdeaForm(
            data={
                'title': idea.title,
                'description': idea.description,
                'status': 'active',
                'market_size': '',
                'competitors': '',
            },
            instance=idea,
        )
        self.assertFalse(form.is_valid())

    def test_market_research_form_allows_blank_date(self):
        from .forms import MarketResearchForm

        form = MarketResearchForm(data={
            'findings': 'Students need affordable prototyping.',
            'sources': 'Interviews',
        })
        self.assertTrue(form.is_valid())

    def test_market_research_create_defaults_date_to_today(self):
        idea = BusinessIdea.objects.create(
            user=self.user,
            title='Research Driven Startup',
            description='Test description',
        )
        client = Client()
        client.force_login(self.user)

        response = client.post(reverse('market_research_create', args=[idea.id]), {
            'findings': 'Validated customer pain points',
            'sources': 'Survey results',
        })

        self.assertEqual(response.status_code, 302)
        research = MarketResearch.objects.get(business_idea=idea)
        self.assertEqual(research.date, timezone.now().date())

    def test_import_export_form_allows_blank_date(self):
        from .forms import ImportExportRecordForm

        form = ImportExportRecordForm(data={
            'product': 'Sensors',
            'quantity': '5',
            'value': '2500',
            'country': 'Italy',
            'type': 'import',
            'description': 'Sample batch',
        })
        self.assertTrue(form.is_valid())
