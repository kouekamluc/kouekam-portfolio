"""
Sitemap configuration for Kouekam Portfolio Hub.
Generates sitemap.xml for search engine indexing.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from portfolio.models import Project
from blog.models import BlogPost, Tutorial


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        return [
            'home',
            'about',
            'skills',
            'contact',
            'project_list',
            'blog_list',
            'tutorial_list',
        ]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    """Sitemap for project detail pages."""
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return Project.objects.filter(status__in=['active', 'completed'])

    def lastmod(self, obj):
        return obj.created_at


class BlogPostSitemap(Sitemap):
    """Sitemap for blog post detail pages."""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(published_date__isnull=False)

    def lastmod(self, obj):
        return obj.updated_at or obj.published_date


class TutorialSitemap(Sitemap):
    """Sitemap for tutorial detail pages."""
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return Tutorial.objects.all()

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

