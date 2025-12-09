from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Conversation, Message, PromptTemplate, PDFAnalysis
from .forms import ConversationForm, PromptTemplateForm, PDFUploadForm, MessageForm
from .services import (
    get_chat_completion, analyze_pdf, generate_questions,
    get_study_help, get_code_assistance, get_writing_assistance,
    get_course_recommendations
)
import json

@login_required
def assistant_hub(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_date')[:10]
    recent_analyses = PDFAnalysis.objects.filter(user=request.user).order_by('-date_analyzed')[:5]
    templates = PromptTemplate.objects.filter(user=request.user)[:5]
    
    context = {
        'conversations': conversations,
        'recent_analyses': recent_analyses,
        'templates': templates,
    }
    return render(request, 'ai_assistant/assistant_hub.html', context)

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_date')
    assistant_type = request.GET.get('type')
    if assistant_type:
        conversations = conversations.filter(assistant_type=assistant_type)
    return render(request, 'ai_assistant/conversation_list.html', {
        'conversations': conversations,
        'assistant_type': assistant_type
    })

@login_required
def conversation_create(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.user = request.user
            conversation.save()
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = ConversationForm()
    return render(request, 'ai_assistant/conversation_form.html', {'form': form})

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    messages_list = conversation.messages.all()
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data.get('message', '')
            if user_message:
                # Save user message
                Message.objects.create(
                    conversation=conversation,
                    role='user',
                    content=user_message
                )
                
                # Get conversation history
                history = []
                for msg in messages_list:
                    history.append({
                        'role': msg.role,
                        'content': msg.content
                    })
                
                # Add new user message
                history.append({
                    'role': 'user',
                    'content': user_message
                })
                
                try:
                    # Get AI response based on assistant type
                    if conversation.assistant_type == 'study':
                        system_prompt = "You are a helpful study assistant."
                    elif conversation.assistant_type == 'code':
                        system_prompt = "You are an expert code assistant and programming mentor."
                    elif conversation.assistant_type == 'writing':
                        system_prompt = "You are a writing assistant that helps improve writing quality."
                    else:
                        system_prompt = "You are a helpful assistant."
                    
                    messages_for_api = [{"role": "system", "content": system_prompt}] + history
                    
                    response_text = get_chat_completion(messages_for_api)
                    
                    # Save assistant response
                    Message.objects.create(
                        conversation=conversation,
                        role='assistant',
                        content=response_text
                    )
                    
                    # Update conversation title if it's still default
                    if conversation.title == 'New Conversation' and len(user_message) < 50:
                        conversation.title = user_message[:50]
                        conversation.save()
                    
                    return JsonResponse({
                        'success': True,
                        'response': response_text
                    })
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=500)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid form data'
                }, status=400)
    
    form = MessageForm()
    return render(request, 'ai_assistant/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages_list,
        'form': form
    })

@login_required
def chat_interface(request):
    # Create or get a general conversation
    conversation, created = Conversation.objects.get_or_create(
        user=request.user,
        assistant_type='general',
        defaults={'title': 'General Chat'}
    )
    return redirect('conversation_detail', conversation_id=conversation.id)

@login_required
def pdf_upload(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['file']
            if not pdf_file.name.endswith('.pdf'):
                messages.error(request, 'Please upload a PDF file.')
                return redirect('pdf_upload')
            
            try:
                # Analyze PDF
                analysis = analyze_pdf(pdf_file, pdf_file.name)
                
                # Save analysis
                pdf_analysis = PDFAnalysis.objects.create(
                    user=request.user,
                    file=pdf_file,
                    summary=analysis['summary'],
                    key_points=analysis['key_points'],
                    original_filename=pdf_file.name
                )
                
                messages.success(request, 'PDF analyzed successfully!')
                return redirect('pdf_analyze', analysis_id=pdf_analysis.id)
            except Exception as e:
                messages.error(request, f'Error analyzing PDF: {str(e)}')
                return redirect('pdf_upload')
    else:
        form = PDFUploadForm()
    
    return render(request, 'ai_assistant/pdf_upload.html', {'form': form})

@login_required
def pdf_analyze(request, analysis_id):
    analysis = get_object_or_404(PDFAnalysis, id=analysis_id, user=request.user)
    return render(request, 'ai_assistant/pdf_analyze.html', {'analysis': analysis})

@login_required
def prompt_template_list(request):
    templates = PromptTemplate.objects.filter(user=request.user).order_by('category', 'name')
    category_filter = request.GET.get('category')
    if category_filter:
        templates = templates.filter(category=category_filter)
    return render(request, 'ai_assistant/prompt_template_list.html', {
        'templates': templates,
        'category_filter': category_filter
    })

@login_required
def prompt_template_create(request):
    if request.method == 'POST':
        form = PromptTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, 'Prompt template created!')
            return redirect('prompt_template_list')
    else:
        form = PromptTemplateForm()
    return render(request, 'ai_assistant/prompt_template_form.html', {'form': form})

@login_required
def study_helper(request):
    from academic.models import Course
    courses = Course.objects.filter(user=request.user)
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        topic = request.POST.get('topic', '')
        question = request.POST.get('question', '')
        
        if course_id:
            course = get_object_or_404(Course, id=course_id, user=request.user)
            try:
                if question:
                    response = get_study_help(course.name, topic, question)
                else:
                    response = "Please provide a question or topic to get study help."
                
                return render(request, 'ai_assistant/study_helper.html', {
                    'courses': courses,
                    'selected_course': course,
                    'topic': topic,
                    'question': question,
                    'response': response
                })
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'ai_assistant/study_helper.html', {'courses': courses})

@login_required
def code_assistant(request):
    if request.method == 'POST':
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        question = request.POST.get('question', '')
        
        if code:
            try:
                response = get_code_assistance(code, language, question)
                return render(request, 'ai_assistant/code_assistant.html', {
                    'code': code,
                    'language': language,
                    'question': question,
                    'response': response
                })
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'ai_assistant/code_assistant.html')

@login_required
def writing_assistant(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        request_type = request.POST.get('request_type', 'review')
        
        if text:
            try:
                response = get_writing_assistance(text, request_type)
                return render(request, 'ai_assistant/writing_assistant.html', {
                    'text': text,
                    'request_type': request_type,
                    'response': response
                })
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'ai_assistant/writing_assistant.html')

@login_required
def course_recommendation(request):
    if request.method == 'POST':
        interests = request.POST.get('interests', '')
        current_courses = request.POST.get('current_courses', '')
        
        if interests:
            try:
                interests_list = [i.strip() for i in interests.split(',')]
                current_list = [c.strip() for c in current_courses.split(',')] if current_courses else None
                
                response = get_course_recommendations(interests_list, current_list)
                return render(request, 'ai_assistant/course_recommendation.html', {
                    'interests': interests,
                    'current_courses': current_courses,
                    'response': response
                })
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'ai_assistant/course_recommendation.html')
