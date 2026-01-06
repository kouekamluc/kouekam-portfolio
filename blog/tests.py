from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import BlogPost, CodeSnippet, Tutorial

User = get_user_model()


class BlogPostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_blog_post_creation(self):
        post = BlogPost.objects.create(
            title='Test Post',
            content='Test content',
            category='django',
            author=self.user
        )
        self.assertEqual(str(post), 'Test Post')
        self.assertTrue(post.slug)

    def test_blog_post_slug_generation(self):
        post = BlogPost.objects.create(
            title='Test Blog Post',
            content='Test',
            author=self.user
        )
        self.assertIn('test-blog-post', post.slug.lower())


class CodeSnippetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.post = BlogPost.objects.create(
            title='Test Post',
            content='Test',
            author=self.user
        )

    def test_code_snippet_creation(self):
        snippet = CodeSnippet.objects.create(
            blog_post=self.post,
            title='Test Snippet',
            language='python',
            code='print("Hello")'
        )
        self.assertIn('python', str(snippet).lower())


class TutorialModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_tutorial_creation(self):
        tutorial = Tutorial.objects.create(
            title='Django Tutorial',
            description='Learn Django',
            difficulty='beginner',
            author=self.user,
            parts=5
        )
        self.assertEqual(str(tutorial), 'Django Tutorial')
        self.assertTrue(tutorial.slug)


class BlogViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.post = BlogPost.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            slug='test-post'
        )

    def test_blog_list_view(self):
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_view(self):
        response = self.client.get(reverse('blog_detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)

    def test_blog_create_requires_login(self):
        response = self.client.get(reverse('blog_create'))
        self.assertEqual(response.status_code, 302)

    def test_tutorial_list_view(self):
        response = self.client.get(reverse('tutorial_list'))
        self.assertEqual(response.status_code, 200)
