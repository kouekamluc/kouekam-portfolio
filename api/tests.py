from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import BlogPost


User = get_user_model()


class PublicBlogPostApiTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="testpass123",
        )

    def test_public_blog_api_only_returns_published_posts(self):
        published = BlogPost.objects.create(
            title="Published Post",
            content="Visible content",
            status=BlogPost.STATUS_PUBLISHED,
            published_date=timezone.now(),
            author=self.author,
        )
        BlogPost.objects.create(
            title="Draft Post",
            content="Private draft content",
            status=BlogPost.STATUS_DRAFT,
            author=self.author,
        )
        BlogPost.objects.create(
            title="Scheduled Post",
            content="Private scheduled content",
            status=BlogPost.STATUS_SCHEDULED,
            published_date=timezone.now() + timezone.timedelta(days=1),
            author=self.author,
        )

        response = self.client.get(reverse("blogpost-list"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        results = payload.get("results", payload)
        titles = {item["title"] for item in results}
        self.assertEqual(titles, {published.title})
