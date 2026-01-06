from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Profile, Timeline, Skill, Project, ProjectImage

User = get_user_model()


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_creation(self):
        profile = Profile.objects.create(
            user=self.user,
            bio='Test bio',
            tagline='Test tagline'
        )
        self.assertEqual(str(profile), f"{self.user.username}'s Profile")
        self.assertEqual(profile.user, self.user)

    def test_profile_social_links(self):
        profile = Profile.objects.create(
            user=self.user,
            social_links={'linkedin': 'https://linkedin.com/test', 'github': 'https://github.com/test'}
        )
        self.assertIn('linkedin', profile.social_links)
        self.assertEqual(profile.social_links['github'], 'https://github.com/test')


class TimelineModelTest(TestCase):
    def test_timeline_creation(self):
        timeline = Timeline.objects.create(
            year='2024',
            title='Test Event',
            description='Test description',
            category='work'
        )
        self.assertEqual(str(timeline), '2024 - Test Event')
        self.assertEqual(timeline.category, 'work')


class SkillModelTest(TestCase):
    def test_skill_creation(self):
        skill = Skill.objects.create(
            name='Python',
            category='backend',
            proficiency_level=85
        )
        self.assertEqual(str(skill), 'Python')
        self.assertEqual(skill.proficiency_level, 85)


class ProjectModelTest(TestCase):
    def test_project_creation(self):
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category='web',
            tech_stack=['Python', 'Django']
        )
        self.assertEqual(str(project), 'Test Project')
        self.assertIn('Python', project.tech_stack)

    def test_project_slug_generation(self):
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category='web'
        )
        self.assertTrue(project.slug)
        self.assertIn('test-project', project.slug.lower())


class ProjectImageViewTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category='web'
        )

    def test_project_image_creation(self):
        image = ProjectImage.objects.create(
            project=self.project,
            caption='Test caption'
        )
        self.assertEqual(str(image), f"Image for {self.project.title}")


class PortfolioViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.skill = Skill.objects.create(name='Python', category='backend')
        self.timeline = Timeline.objects.create(
            year='2024',
            title='Test Event',
            description='Test',
            category='work'
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kouekam')

    def test_about_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_skills_view(self):
        response = self.client.get(reverse('skills'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')

    def test_project_list_view(self):
        Project.objects.create(
            title='Test Project',
            description='Test',
            category='web',
            status='active'
        )
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)

    def test_project_detail_view(self):
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category='web',
            slug='test-project'
        )
        response = self.client.get(reverse('project_detail', args=[project.slug]))
        self.assertEqual(response.status_code, 200)

    def test_contact_view_get(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_view_post(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_view_profile_requires_login(self):
        response = self.client.get(reverse('view_profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_view_profile_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('view_profile'))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
