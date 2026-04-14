from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.templatetags.static import static
from django.db.models import Q
from .models import Profile, Timeline, Skill, Project, ProjectImage
from .forms import ProfileForm, ProjectForm, ProjectImageForm
from .email_utils import send_contact_form_email
from blog.models import BlogPost
from academic.models import Note

def home(request):
    profile = Profile.objects.first() # Simplification for single-user portfolio
    skills = Skill.objects.all()
    timeline = Timeline.objects.all()
    # Featured/Recent projects can also be added here
    recent_projects = Project.objects.filter(status__in=['active', 'completed']).order_by('-created_at')[:3]
    
    # Dynamic counts for stats - count all non-archived projects (active and completed)
    total_projects = Project.objects.filter(status__in=['active', 'completed']).count()
    published_blog_posts = BlogPost.objects.filter(published_date__isnull=False).count()
    total_skills = Skill.objects.count()
    
    context = {
        'profile': profile,
        'skills': skills,
        'timeline': timeline,
        'recent_projects': recent_projects,
        'total_projects': total_projects,
        'published_blog_posts': published_blog_posts,
        'total_skills': total_skills,
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
                import sys
                print(f"INFO: Contact form submission received from {name} ({email})", file=sys.stderr)
                print(f"INFO: Subject: {subject or 'No Subject'}", file=sys.stderr)
                
                # Send email via Brevo
                success = send_contact_form_email(name, email, subject, message)
                
                if success:
                    print(f"INFO: Contact form email sent successfully", file=sys.stderr)
                    messages.success(request, 'Thank you! Your message has been sent successfully.')
                    return HttpResponseRedirect(request.path)
                else:
                    # Log the failure reason for debugging
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error("Contact form email sending failed. Check Brevo configuration.")
                    print("ERROR: Contact form email sending failed. Check Brevo API key and configuration.", file=sys.stderr)
                    messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
            except Exception as e:
                import logging
                import sys
                logger = logging.getLogger(__name__)
                error_msg = f"Error in contact form: {str(e)}"
                logger.error(error_msg, exc_info=True)
                print(f"ERROR: {error_msg}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return HttpResponseRedirect(request.path)
    
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
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                project = form.save()
                messages.success(request, 'Project created successfully!')
                return redirect('project_detail', slug=project.slug)
            except Exception as e:
                messages.error(request, f'An error occurred while creating the project: {str(e)}')
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error creating project: {str(e)}', exc_info=True)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()
    return render(request, 'portfolio/project_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def project_update(request, slug):
    project = get_object_or_404(Project, slug=slug)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            try:
                project = form.save()
                messages.success(request, 'Project updated successfully!')
                return redirect('project_detail', slug=project.slug)
            except Exception as e:
                messages.error(request, f'An error occurred while updating the project: {str(e)}')
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error updating project: {str(e)}', exc_info=True)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'portfolio/project_form.html', {'form': form, 'project': project, 'form_type': 'Update'})

@login_required
def project_delete(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    return render(request, 'portfolio/project_confirm_delete.html', {'project': project})

@login_required
def project_image_add(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        form = ProjectImageForm(request.POST, request.FILES)
        if form.is_valid():
            project_image = form.save(commit=False)
            project_image.project = project
            project_image.save()
            messages.success(request, 'Image added successfully!')
            return redirect('project_detail', slug=project.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectImageForm()
    return render(request, 'portfolio/project_image_form.html', {'form': form, 'project': project})

@login_required
def project_image_delete(request, image_id):
    project_image = get_object_or_404(ProjectImage, id=image_id)
    project = project_image.project
    if request.method == 'POST':
        project_image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('project_detail', slug=project.slug)
    return render(request, 'portfolio/project_image_confirm_delete.html', {'project_image': project_image, 'project': project})

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


def search(request):
    """Global search across blog posts, projects, and notes"""
    query = request.GET.get('q', '').strip()
    results = {
        'blog_posts': [],
        'projects': [],
        'notes': [],
    }
    
    if query:
        # Search blog posts (public)
        blog_posts = BlogPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-published_date', '-created_at')[:10]
        results['blog_posts'] = blog_posts
        
        # Search projects (public)
        projects = Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query)
        ).filter(status__in=['active', 'completed']).order_by('-created_at')[:10]
        results['projects'] = projects
        
        # Search notes (only for authenticated users, their own notes)
        if request.user.is_authenticated:
            notes = Note.objects.filter(
                course__user=request.user
            ).filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).order_by('-updated_at')[:10]
            results['notes'] = notes
    
    context = {
        'query': query,
        'results': results,
        'total_results': sum(len(v) for v in results.values()),
    }
    return render(request, 'portfolio/search_results.html', context)
