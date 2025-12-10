from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.templatetags.static import static
from .models import Profile, Timeline, Skill, Project
from .forms import ProfileForm

def home(request):
    profile = Profile.objects.first() # Simplification for single-user portfolio
    skills = Skill.objects.all()
    timeline = Timeline.objects.all()
    # Featured/Recent projects can also be added here
    recent_projects = Project.objects.filter(status='active').order_by('-created_at')[:3]
    context = {
        'profile': profile,
        'skills': skills,
        'timeline': timeline,
        'recent_projects': recent_projects
    }
    return render(request, 'home.html', context)

def about(request):
    profile = Profile.objects.first()
    timeline = Timeline.objects.all()
    context = {
        'profile': profile,
        'timeline': timeline,
    }
    return render(request, 'portfolio/about.html', context)

def skills(request):
    skills = Skill.objects.all()
    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    context = {
        'skills': skills,
        'skills_by_category': skills_by_category,
    }
    return render(request, 'portfolio/skills.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and message:
            try:
                send_mail(
                    subject=f'Contact Form: {subject}',
                    message=f'From: {name} ({email})\n\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL or email,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL or 'admin@example.com'],
                    fail_silently=False,
                )
                messages.success(request, 'Thank you! Your message has been sent successfully.')
                return HttpResponseRedirect(request.path)
            except Exception as e:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    profile = Profile.objects.first()
    return render(request, 'portfolio/contact.html', {'profile': profile})

def download_cv(request):
    profile = Profile.objects.first()
    if profile and profile.cv_file:
        response = HttpResponse(profile.cv_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{profile.cv_file.name}"'
        return response
    else:
        messages.error(request, 'CV not available.')
        return HttpResponseRedirect('/')

def project_list(request):
    try:
        projects = Project.objects.filter(status__in=['active', 'completed']).order_by('-created_at')
        category = request.GET.get('category')
        if category:
            projects = projects.filter(category=category)
        return render(request, 'portfolio/project_list.html', {'projects': projects, 'active_category': category})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in project_list view: {e}", exc_info=True)
        # Return empty projects list on error
        return render(request, 'portfolio/project_list.html', {'projects': [], 'active_category': None})

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'portfolio/project_detail.html', {'project': project})

@login_required
def view_profile(request):
    """View user's own profile"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'portfolio/profile_view.html', {'profile': profile})


@login_required
def edit_profile(request):
    """Edit user's own profile"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('view_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'portfolio/profile_edit.html', {'form': form, 'profile': profile})


def debug_static_url(request):
    """Debug endpoint to check static file URL generation"""
    from django.templatetags.static import static as static_tag
    from django.template import Template, Context
    from django.template.loader import render_to_string
    from django.contrib.staticfiles.storage import staticfiles_storage
    
    css_url = static_tag('css/output.css')
    
    # Check what staticfiles_storage actually is
    storage_type = type(staticfiles_storage).__name__
    storage_module = type(staticfiles_storage).__module__
    
    # Also check what the storage backend generates
    storage_url = None
    storage_exists = False
    try:
        from kouekam_hub.storage import StaticStorage
        storage = StaticStorage()
        storage_url = storage.url('css/output.css')
        storage_exists = storage.exists('css/output.css')
        
        # Also check what staticfiles_storage generates
        staticfiles_storage_url = staticfiles_storage.url('css/output.css')
    except Exception as e:
        storage_url = f"Error: {e}"
        staticfiles_storage_url = f"Error: {e}"
    
    # Render the actual template tag to see what it generates
    template = Template('{% load static %}{% static "css/output.css" %}')
    context = Context({})
    rendered_url = template.render(context)
    
    # Check what the actual HTML template generates
    try:
        html_snippet = render_to_string('base.html', {})
        import re
        css_link_match = re.search(r'<link[^>]*href=["\']([^"\']*output\.css[^"\']*)["\']', html_snippet)
        html_css_url = css_link_match.group(1) if css_link_match else 'Not found in HTML'
    except Exception as e:
        html_css_url = f"Error: {e}"
    
    return JsonResponse({
        'css_url_from_static_tag': css_url,
        'css_url_from_template': rendered_url,
        'css_url_from_html': html_css_url,
        'css_url_from_storage': storage_url,
        'css_url_from_staticfiles_storage': staticfiles_storage_url,
        'css_exists_in_s3': storage_exists,
        'staticfiles_storage_type': storage_type,
        'staticfiles_storage_module': storage_module,
        'static_url_setting': getattr(settings, 'STATIC_URL', 'Not set'),
        'use_s3': getattr(settings, 'USE_S3', False),
        'staticfiles_storage_setting': getattr(settings, 'STATICFILES_STORAGE', 'Not set'),
        'expected_url': 'https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css',
        'urls_match': rendered_url == 'https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css',
        'note': 'Check if css_url_from_template matches expected_url and css_exists_in_s3 is True',
    })
