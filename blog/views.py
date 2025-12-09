from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import BlogPost, CodeSnippet, Tutorial
from .forms import BlogPostForm, CodeSnippetForm, TutorialForm

def blog_list(request):
    posts = BlogPost.objects.filter(published_date__isnull=False).order_by('-published_date')
    
    # Filtering
    category_filter = request.GET.get('category')
    if category_filter:
        posts = posts.filter(category=category_filter)
    
    featured = request.GET.get('featured')
    if featured == 'true':
        posts = posts.filter(featured=True)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_filter': category_filter,
        'featured': featured,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    code_snippets = post.code_snippets.all()
    
    # Only show published posts to non-staff
    if not post.published_date and not request.user.is_staff:
        messages.error(request, 'This post is not published yet.')
        return redirect('blog_list')
    
    context = {
        'post': post,
        'code_snippets': code_snippets,
    }
    return render(request, 'blog/blog_detail.html', context)

@staff_member_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if request.POST.get('publish'):
                post.published_date = timezone.now()
            post.save()
            
            if post.published_date:
                messages.success(request, 'Blog post published!')
            else:
                messages.success(request, 'Blog post saved as draft!')
            
            # Handle code snippets separately if needed
            snippet_titles = request.POST.getlist('snippet_title')
            snippet_languages = request.POST.getlist('snippet_language')
            snippet_codes = request.POST.getlist('snippet_code')
            snippet_descriptions = request.POST.getlist('snippet_description')
            
            for title, language, code, description in zip(snippet_titles, snippet_languages, snippet_codes, snippet_descriptions):
                if title and code:
                    CodeSnippet.objects.create(
                        blog_post=post,
                        title=title,
                        language=language or 'python',
                        code=code,
                        description=description or '',
                    )
            
            return redirect('blog_detail', slug=post.slug)
    else:
        form = BlogPostForm()
    return render(request, 'blog/blog_form.html', {'form': form, 'form_type': 'Create'})

@staff_member_required
def blog_update(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if request.POST.get('publish') and not post.published_date:
                post.published_date = timezone.now()
            post.save()
            
            # Update code snippets (simplified - delete and recreate)
            post.code_snippets.all().delete()
            snippet_titles = request.POST.getlist('snippet_title')
            snippet_languages = request.POST.getlist('snippet_language')
            snippet_codes = request.POST.getlist('snippet_code')
            snippet_descriptions = request.POST.getlist('snippet_description')
            
            for title, language, code, description in zip(snippet_titles, snippet_languages, snippet_codes, snippet_descriptions):
                if title and code:
                    CodeSnippet.objects.create(
                        blog_post=post,
                        title=title,
                        language=language or 'python',
                        code=code,
                        description=description or '',
                    )
            
            messages.success(request, 'Blog post updated!')
            return redirect('blog_detail', slug=post.slug)
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'blog/blog_form.html', {'form': form, 'post': post, 'form_type': 'Update'})

@staff_member_required
def blog_delete(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted!')
        return redirect('blog_list')
    return render(request, 'blog/blog_confirm_delete.html', {'post': post})

def tutorial_list(request):
    tutorials = Tutorial.objects.all().order_by('-created_at')
    difficulty_filter = request.GET.get('difficulty')
    if difficulty_filter:
        tutorials = tutorials.filter(difficulty=difficulty_filter)
    
    context = {
        'tutorials': tutorials,
        'difficulty_filter': difficulty_filter,
    }
    return render(request, 'blog/tutorial_list.html', context)

def tutorial_detail(request, slug):
    tutorial = get_object_or_404(Tutorial, slug=slug)
    return render(request, 'blog/tutorial_detail.html', {'tutorial': tutorial})
