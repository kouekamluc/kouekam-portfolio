import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kouekam_hub.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from blog.models import BlogPost

User = get_user_model()

# Get the first superuser or first user as author
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.first()
    if not user:
        print("Error: No users found. Please create a user first.")
        exit(1)

title = "Kouekam Portfolio Hub: A Comprehensive Django-Based Personal Productivity Platform"
slug = "kouekam-portfolio-hub-comprehensive-django-personal-productivity-platform"

# Check if post already exists
if BlogPost.objects.filter(slug=slug).exists():
    print(f"Blog post '{title}' already exists. Updating existing post...")
    post = BlogPost.objects.get(slug=slug)
else:
    post = BlogPost()
    post.title = title
    post.slug = slug
    post.author = user
    post.category = 'project'
    post.featured = True

content = """# Kouekam Portfolio Hub: A Comprehensive Django-Based Personal Productivity Platform

## Introduction

The **Kouekam Portfolio Hub** is a comprehensive Django-based web application that serves as both a professional portfolio showcase and an integrated personal productivity platform. This project represents a full-stack solution that combines portfolio management, academic tools, productivity features, AI assistant integration, business planning, journaling, and blogging capabilities into a single, cohesive platform.

## Project Overview

Built with Django 5.2.8 and modern web technologies, this platform addresses the need for a centralized hub where professionals can showcase their work while also managing various aspects of their personal and professional lives. The application is designed with scalability, maintainability, and user experience in mind.

## Key Features

### 1. Portfolio Management
- **Professional Showcase**: Display projects, skills, timeline, and professional profile
- **Project Gallery**: Showcase portfolio projects with images, descriptions, and links
- **Skills Tracking**: Organize technical skills by category with proficiency levels
- **Timeline Display**: Visual representation of career and educational milestones
- **Contact Integration**: Built-in contact form with email functionality
- **CV/Resume Download**: Secure file sharing for professional documents

### 2. Academic Tools
- **Course Management**: Track courses with codes, semesters, credits, and grades
- **GPA Calculation**: Automatic grade point average computation
- **Note Taking**: Digital note-taking with file attachments
- **Flashcard System**: Interactive study flashcards linked to courses
- **Study Session Tracking**: Monitor study time and topics covered
- **AI-Powered Question Generation**: Generate study questions using OpenAI integration

### 3. Productivity Suite
- **Task Management**: To-do lists with priorities, due dates, and status tracking
- **Habit Tracking**: Daily/weekly habit monitoring with streak tracking
- **Goal Setting**: Long-term goals with progress tracking and milestones
- **Document Management**: File storage and organization with tagging
- **Weekly Timetable**: Schedule management with JSON-based storage
- **Financial Tracking**: Personal finance management with income/expense tracking

### 4. AI Assistant Integration
- **Multi-Type Conversations**: General, study, code, and writing assistance
- **PDF Analysis**: Upload and analyze PDF documents with AI-powered summaries
- **Study Help**: Get assistance with academic questions and concepts
- **Code Review**: Receive code feedback and debugging help
- **Writing Assistance**: Text review and improvement suggestions
- **Course Recommendations**: Personalized learning path suggestions

### 5. Business Planning Tools
- **Idea Management**: Track business ideas through various stages
- **Market Research**: Document research findings and sources
- **Business Plans**: Comprehensive business plan creation with financial data
- **Import/Export Tracking**: Manage import/export transactions and records

### 6. Personal Journaling
- **Daily Entries**: Daily journal entries with mood and energy level tracking
- **Philosophy Documentation**: Record personal philosophies by category
- **Vision Goals**: Long-term vision goals with progress tracking
- **Life Lessons**: Repository of lessons learned with context

### 7. Blogging Platform
- **Blog Post Management**: Create and manage blog posts with categories
- **Code Snippets**: Embed code examples with syntax highlighting
- **Tutorial Series**: Create multi-part tutorials with difficulty levels
- **Featured Posts**: Highlight important content
- **Publishing Workflow**: Draft and publish system with scheduling

## Technology Stack

### Backend
- **Framework**: Django 5.2.8
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: django-allauth (email-based)
- **AI Integration**: OpenAI API (GPT-4o-mini)
- **File Storage**: Local filesystem (development), AWS S3 (production)
- **Image Processing**: Pillow

### Frontend
- **CSS Framework**: Tailwind CSS 3.4.17
- **UI Components**: Flowbite 4.0.1
- **Icons**: Font Awesome 6.4.0
- **Build Tool**: Tailwind CLI
- **JavaScript**: Vanilla JS with Flowbite integration

### Infrastructure
- **Deployment**: Railway/Heroku-ready with Gunicorn
- **Static Files**: AWS S3 integration for production
- **Email**: Configurable email backend (console, SMTP)
- **Environment Management**: python-dotenv

## Architecture & Design Patterns

### Application Structure
The project follows Django's app-based architecture with 7 main applications:
1. **portfolio** - Main portfolio showcase
2. **academic** - Academic management tools
3. **productivity** - Productivity suite
4. **ai_assistant** - AI integration
5. **business** - Business planning tools
6. **journal** - Personal journaling
7. **blog** - Blogging platform

### Design Principles
- **Separation of Concerns**: Each app handles its own domain
- **DRY (Don't Repeat Yourself)**: Reusable templates and components
- **User-Centric**: All data is user-scoped with authentication
- **Scalability**: JSON fields for flexible data, efficient queries
- **Security**: Production-ready security settings, file upload validation

### Database Design
- **User Relationships**: OneToOne and ForeignKey to User model for data isolation
- **JSON Fields**: Flexible storage for tech stacks, schedules, financial data
- **Image Handling**: Separate models for project galleries and blog images
- **Soft Relationships**: Optional relationships between models (e.g., CodeSnippet to BlogPost)

## Key Technical Highlights

### 1. Multi-App Integration
The platform seamlessly integrates multiple Django apps while maintaining clean separation. Each app is self-contained with its own models, views, URLs, and templates.

### 2. AI Integration
The AI Assistant app provides a centralized service layer (`services.py`) for OpenAI integration, used across multiple apps for enhanced functionality (study help, code review, PDF analysis).

### 3. File Management
Comprehensive file upload handling with:
- Image processing via Pillow
- Organized media structure by app and type
- AWS S3 integration for production
- File validation and secure storage

### 4. Authentication System
- Email-based authentication (no username required)
- django-allauth integration
- User profile extension via OneToOne relationship
- Secure session management

### 5. Template System
- Base template with consistent styling
- Reusable components (navbar, footer)
- Dark mode support
- Responsive design with Tailwind CSS
- Message/alerts system

## Development Workflow

### Local Development
1. Virtual environment setup
2. Dependency installation (Python + Node.js)
3. Environment variable configuration
4. Database migrations
5. Static file compilation (Tailwind CSS)
6. Development server

### Production Deployment
- Environment-based configuration
- PostgreSQL database
- AWS S3 for static/media files
- Gunicorn application server
- Security settings (HTTPS, secure cookies)
- Email configuration

## Lessons Learned & Best Practices

### What Worked Well
1. **App-Based Architecture**: Clear separation made development manageable
2. **Tailwind CSS**: Rapid UI development with consistent styling
3. **Django ORM**: Efficient data modeling and queries
4. **Template Inheritance**: DRY principle in templates
5. **Environment Variables**: Easy configuration management

### Challenges Overcome
1. **File Upload Handling**: Implemented comprehensive validation and storage
2. **S3 Integration**: Set up production file storage with proper permissions
3. **Multi-App Routing**: Organized URL patterns across apps
4. **AI Integration**: Created reusable service layer for OpenAI
5. **Production Security**: Configured security settings for production

## Future Enhancements

Potential improvements and features for future iterations:
- **Real-time Features**: WebSocket integration for live updates
- **Mobile App**: React Native or Flutter mobile application
- **Advanced Analytics**: User behavior tracking and insights
- **Collaboration Features**: Multi-user workspaces and sharing
- **API Expansion**: RESTful API for mobile and third-party integrations
- **Enhanced AI**: More AI models and capabilities
- **Performance Optimization**: Caching, database optimization
- **Internationalization**: Multi-language support

## Conclusion

The Kouekam Portfolio Hub represents a comprehensive solution for professionals seeking to combine portfolio showcasing with personal productivity management. Built with modern technologies and best practices, it demonstrates full-stack Django development skills while providing real-world utility.

The project showcases:
- **Full-Stack Development**: Django backend with modern frontend
- **System Design**: Multi-app architecture with clear separation
- **API Integration**: OpenAI integration for enhanced features
- **Production Deployment**: Railway/Heroku-ready with AWS S3
- **User Experience**: Intuitive interface with Tailwind CSS
- **Scalability**: Designed for growth and feature expansion

Whether you're a developer looking to build a similar platform, a professional seeking a productivity hub, or someone interested in Django best practices, this project provides a solid foundation and reference implementation.

## Resources

- **GitHub Repository**: [Repository URL]
- **Live Demo**: [Live URL]
- **Documentation**: See README.md and LLM_CONTEXT.md for detailed documentation

---

*This project is actively maintained and continuously improved based on user feedback and evolving requirements.*"""

post.content = content
post.published_date = timezone.now()
post.save()

print(f"Blog post '{title}' created/updated successfully!")
print(f"Post ID: {post.id}")
print(f"Slug: {post.slug}")
print(f"Category: {post.category}")
print(f"Featured: {post.featured}")
print(f"Published: {post.published_date}")
print(f"\nYou can view the post at: /blog/{post.slug}/")
