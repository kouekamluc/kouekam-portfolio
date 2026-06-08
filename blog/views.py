from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .models import BlogPost, CodeSnippet, Tutorial
from .forms import BlogPostForm, CodeSnippetForm, TutorialForm

def blog_list(request):
    now = timezone.now()
    public_filter = Q(status=BlogPost.STATUS_PUBLISHED, published_date__lte=now)

    if request.user.is_authenticated:
        posts = BlogPost.objects.filter(public_filter | Q(author=request.user))
    else:
        posts = BlogPost.objects.filter(public_filter)
    
    # Order by published_date (if exists) or created_at, with published posts first
    posts = posts.order_by('-published_date', '-created_at')
    
    # Filtering
    category_filter = request.GET.get('category')
    if category_filter:
        posts = posts.filter(category=category_filter)
    
    featured = request.GET.get('featured')
    if featured == 'true':
        posts = posts.filter(featured=True)
    
    # Show drafts filter
    show_drafts = request.GET.get('drafts')
    show_scheduled = request.GET.get('scheduled')
    if show_drafts == 'true' and request.user.is_authenticated:
        posts = posts.filter(author=request.user, status=BlogPost.STATUS_DRAFT)
    elif show_scheduled == 'true' and request.user.is_authenticated:
        posts = posts.filter(author=request.user, status=BlogPost.STATUS_SCHEDULED)
    elif show_drafts == 'false' or (show_drafts is None and request.user.is_authenticated):
        # By default, show published posts + user's drafts mixed together
        # This is already handled above
        pass
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_filter': category_filter,
        'featured': featured,
        'show_drafts': show_drafts,
        'show_scheduled': show_scheduled,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    code_snippets = post.code_snippets.all()
    
    if not post.is_public and request.user != post.author:
        messages.error(request, 'This post is not published yet.')
        return redirect('blog_list')
    
    context = {
        'post': post,
        'code_snippets': code_snippets,
    }
    return render(request, 'blog/blog_detail.html', context)

@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                if request.POST.get('publish'):
                    post.status = BlogPost.STATUS_PUBLISHED
                    post.published_date = timezone.now()
                post.save()
                
                if post.status == BlogPost.STATUS_PUBLISHED:
                    messages.success(request, 'Blog post published!')
                elif post.status == BlogPost.STATUS_SCHEDULED:
                    messages.success(request, 'Blog post scheduled!')
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
            except Exception as e:
                messages.error(request, f'An error occurred while saving the post: {str(e)}')
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error creating blog post: {str(e)}', exc_info=True)
    else:
        form = BlogPostForm()
    return render(request, 'blog/blog_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def blog_update(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                was_published = bool(post.published_date)
                
                # Check which button was clicked - check both key existence and value
                publish_clicked = 'publish' in request.POST or request.POST.get('publish') == '1'
                unpublish_clicked = 'unpublish' in request.POST or request.POST.get('unpublish') == '1'
                
                if publish_clicked:
                    post.status = BlogPost.STATUS_PUBLISHED
                    post.published_date = timezone.now()
                elif unpublish_clicked:
                    post.status = BlogPost.STATUS_DRAFT
                    post.published_date = None
                
                # Save the post with the updated published_date
                post.save()
                
                # Refresh from database to ensure we have the latest data
                post.refresh_from_db()
                
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
                
                # Show appropriate message
                if publish_clicked:
                    if was_published:
                        messages.success(request, 'Blog post updated and republished!')
                    else:
                        messages.success(request, 'Blog post published successfully!')
                elif unpublish_clicked:
                    messages.success(request, 'Blog post unpublished and saved as draft!')
                elif post.status == BlogPost.STATUS_SCHEDULED:
                    messages.success(request, 'Blog post scheduled!')
                else:
                    messages.success(request, 'Blog post updated!')
                
                return redirect('blog_detail', slug=post.slug)
            except Exception as e:
                messages.error(request, f'An error occurred while updating the post: {str(e)}')
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error updating blog post: {str(e)}', exc_info=True)
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'blog/blog_form.html', {'form': form, 'post': post, 'form_type': 'Update'})

@login_required
def blog_delete(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)
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
