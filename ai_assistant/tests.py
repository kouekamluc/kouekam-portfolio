from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Conversation, Message, PromptTemplate, PDFAnalysis

User = get_user_model()


class ConversationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_conversation_creation(self):
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            assistant_type='general'
        )
        self.assertIn('Test Conversation', str(conversation))
        self.assertEqual(conversation.user, self.user)

    def test_conversation_without_title(self):
        conversation = Conversation.objects.create(
            user=self.user,
            assistant_type='study'
        )
        self.assertIn('Untitled', str(conversation))


class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            assistant_type='general'
        )

    def test_message_creation(self):
        message = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content='Hello, AI!'
        )
        self.assertIn('user', str(message))
        self.assertIn('Hello', str(message))


class PromptTemplateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_prompt_template_creation(self):
        template = PromptTemplate.objects.create(
            user=self.user,
            name='Study Helper',
            category='study',
            template_text='Help me study {topic}'
        )
        self.assertEqual(str(template), 'Study Helper')
        self.assertEqual(template.category, 'study')


class AIAssistantViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_assistant_hub_requires_login(self):
        response = self.client.get(reverse('assistant_hub'))
        self.assertEqual(response.status_code, 302)

    def test_assistant_hub_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('assistant_hub'))
        self.assertEqual(response.status_code, 200)

    def test_conversation_list_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('conversation_list'))
        self.assertEqual(response.status_code, 200)

    def test_prompt_template_list_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('prompt_template_list'))
        self.assertEqual(response.status_code, 200)
