import os
from django.conf import settings
from openai import OpenAI
from io import BytesIO

try:
    import PyPDF2
    PDF2_AVAILABLE = True
except ImportError:
    PDF2_AVAILABLE = False

# Initialize OpenAI client
client = None
if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_chat_completion(messages, model="gpt-4o-mini", temperature=0.7, max_tokens=1000, stream=False):
    """
    Get chat completion from OpenAI API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (default: gpt-4o-mini)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response
    
    Returns:
        Response text from the assistant (or generator if streaming)
    """
    if not client:
        raise Exception("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment variables.")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        
        if stream:
            def stream_generator():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            return stream_generator()
        else:
            return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")


def estimate_tokens(text):
    """
    Rough estimation of token count (approximation: ~4 characters per token).
    
    Args:
        text: Text to estimate
    
    Returns:
        Estimated token count
    """
    return len(text) // 4


def count_message_tokens(messages):
    """
    Estimate total tokens in a list of messages.
    
    Args:
        messages: List of message dicts
    
    Returns:
        Estimated total token count
    """
    total = 0
    for msg in messages:
        total += estimate_tokens(str(msg.get('role', '')) + str(msg.get('content', '')))
    return total

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_file: Django UploadedFile object
    
    Returns:
        Extracted text as string
    """
    if not PDF2_AVAILABLE:
        raise Exception("PyPDF2 is not installed. Please install it with: pip install PyPDF2")
    
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def analyze_pdf(pdf_file, filename=""):
    """
    Analyze a PDF and generate summary and key points.
    
    Args:
        pdf_file: Django UploadedFile object
        filename: Original filename
    
    Returns:
        Dict with 'summary' and 'key_points'
    """
    if not client:
        raise Exception("OpenAI API key not configured.")
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)
        
        if len(text) < 100:
            return {
                'summary': 'PDF appears to be empty or contains only images.',
                'key_points': []
            }
        
        # Truncate if too long (keep first 10000 chars)
        if len(text) > 10000:
            text = text[:10000] + "... [truncated]"
        
        # Generate summary and key points
        prompt = f"""Analyze the following document and provide:
1. A concise summary (2-3 paragraphs)
2. A list of 5-10 key points

Document:
{text}

Format your response as:
SUMMARY:
[your summary here]

KEY POINTS:
1. [point 1]
2. [point 2]
...
"""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes documents and extracts key information."},
            {"role": "user", "content": prompt}
        ]
        
        response = get_chat_completion(messages, max_tokens=1500)
        
        # Parse response
        summary = ""
        key_points = []
        
        if "SUMMARY:" in response:
            parts = response.split("KEY POINTS:")
            summary = parts[0].replace("SUMMARY:", "").strip()
            if len(parts) > 1:
                points_text = parts[1].strip()
                key_points = [p.strip() for p in points_text.split('\n') if p.strip() and (p.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '-')))]
        else:
            summary = response
            key_points = []
        
        return {
            'summary': summary,
            'key_points': key_points
        }
    except Exception as e:
        raise Exception(f"Error analyzing PDF: {str(e)}")

def generate_questions(course_name, topic, num_questions=5):
    """
    Generate study questions for a course topic.
    
    Args:
        course_name: Name of the course
        topic: Topic to generate questions about
        num_questions: Number of questions to generate
    
    Returns:
        List of question strings
    """
    if not client:
        raise Exception("OpenAI API key not configured.")
    
    try:
        prompt = f"""Generate {num_questions} study questions for the course "{course_name}" on the topic: {topic}

Format each question on a new line, numbered 1-{num_questions}.
Make the questions challenging but appropriate for the course level.
"""
        
        messages = [
            {"role": "system", "content": "You are an educational assistant that creates study questions."},
            {"role": "user", "content": prompt}
        ]
        
        response = get_chat_completion(messages, max_tokens=1000)
        
        # Parse questions
        questions = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('Q')):
                # Remove numbering
                question = line.split('.', 1)[-1].strip()
                if question:
                    questions.append(question)
        
        # If parsing failed, split by newlines
        if not questions:
            questions = [q.strip() for q in response.split('\n') if q.strip()]
        
        return questions[:num_questions]
    except Exception as e:
        raise Exception(f"Error generating questions: {str(e)}")

def get_study_help(course_name, topic, question):
    """
    Get study help for a specific question.
    
    Args:
        course_name: Name of the course
        topic: Topic area
        question: Student's question
    
    Returns:
        Helpful response text
    """
    if not client:
        raise Exception("OpenAI API key not configured.")
    
    try:
        prompt = f"""You are a study assistant for the course "{course_name}" focusing on "{topic}".

Student's question: {question}

Provide a clear, educational answer that helps the student understand the concept.
"""
        
        messages = [
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": prompt}
        ]
        
        return get_chat_completion(messages, max_tokens=1000)
    except Exception as e:
        raise Exception(f"Error getting study help: {str(e)}")

def get_code_assistance(code, language, question=""):
    """
    Get code assistance (review, debugging help, etc.).
    
    Args:
        code: Code snippet
        language: Programming language
        question: Specific question or request
    
    Returns:
        Assistance response
    """
    if not client:
        raise Exception("OpenAI API key not configured.")
    
    try:
        prompt = f"""You are a code assistant. Review this {language} code and provide helpful feedback.

Code:
```{language}
{code}
```

Question/Request: {question or "Please review this code and provide suggestions for improvement."}

Provide:
1. Code review comments
2. Suggestions for improvement
3. Any potential bugs or issues
"""
        
        messages = [
            {"role": "system", "content": "You are an expert code reviewer and programming assistant."},
            {"role": "user", "content": prompt}
        ]
        
        return get_chat_completion(messages, max_tokens=1500)
    except Exception as e:
        raise Exception(f"Error getting code assistance: {str(e)}")

def get_writing_assistance(text, request_type="review"):
    """
    Get writing assistance (review, editing, suggestions).
    
    Args:
        text: Text to review
        request_type: Type of assistance (review, edit, improve, etc.)
    
    Returns:
        Assistance response
    """
    if not client:
        raise Exception("OpenAI API key not configured.")
    
    try:
        prompt = f"""You are a writing assistant. {request_type.capitalize()} the following text:

{text}

Provide:
1. Overall feedback
2. Grammar and style suggestions
3. Suggestions for improvement
"""
        
        messages = [
            {"role": "system", "content": "You are a helpful writing assistant."},
            {"role": "user", "content": prompt}
        ]
        
        return get_chat_completion(messages, max_tokens=1500)
    except Exception as e:
        raise Exception(f"Error getting writing assistance: {str(e)}")

def get_course_recommendations(interests, current_courses=None):
    """
    Get course recommendations based on interests.
    
    Args:
        interests: List of interests or single interest string
        current_courses: List of current courses (optional)
    
    Returns:
        Recommendation text
    """
    if not client:
        raise Exception("OpenAI API key not configured.")
    
    try:
        if isinstance(interests, list):
            interests_str = ", ".join(interests)
        else:
            interests_str = interests
        
        current_str = ""
        if current_courses:
            current_str = f"\nCurrent courses: {', '.join(current_courses)}"
        
        prompt = f"""Based on the following interests, recommend relevant courses or learning paths:

Interests: {interests_str}
{current_str}

Provide:
1. Recommended courses
2. Why these courses are relevant
3. Suggested learning path
"""
        
        messages = [
            {"role": "system", "content": "You are an educational advisor that recommends courses."},
            {"role": "user", "content": prompt}
        ]
        
        return get_chat_completion(messages, max_tokens=1000)
    except Exception as e:
        raise Exception(f"Error getting course recommendations: {str(e)}")

