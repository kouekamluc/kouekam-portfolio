# Kouekam Portfolio Hub - LLM Context Documentation

## Project Overview

This is a comprehensive Django-based personal portfolio and productivity hub application called "Kouekam Digital Hub". It combines multiple functionality modules including portfolio management, academic tools, productivity features, AI assistant integration, business planning, journaling, and blogging capabilities.

## Technology Stack

### Backend
- **Framework**: Django 5.2.8
- **Database**: SQLite (development), PostgreSQL (production via DATABASE_URL)
- **Authentication**: django-allauth (email-based authentication)
- **AI Integration**: OpenAI API (GPT-4o-mini)
- **File Storage**: Local filesystem (development), AWS S3 (production)

### Frontend
- **CSS Framework**: Tailwind CSS 3.4.17
- **UI Components**: Flowbite 4.0.1
- **Icons**: Font Awesome 6.4.0
- **Build Tool**: Tailwind CLI (watch mode)

### Key Python Dependencies
- `Django>=5.2.8`
- `python-dotenv>=1.0.0` - Environment variable management
- `Pillow>=10.0.0` - Image processing
- `django-allauth>=0.57.0` - Authentication
- `openai>=1.0.0` - AI integration
- `boto3>=1.28.0` - AWS S3 integration
- `PyPDF2>=3.0.0` - PDF processing
- `dj-database-url>=2.1.0` - Database URL parsing
- `django-storages>=1.14.0` - S3 storage backend

## Application Structure

The project consists of 7 main Django apps:

### 1. Portfolio App (`portfolio/`)
**Purpose**: Personal portfolio website showcasing profile, skills, projects, and timeline.

**Models**:
- `Profile`: User profile with bio, photo, tagline, CV file, social links (OneToOne with User)
- `Timeline`: Career/education timeline entries with year, title, description, category
- `Skill`: Technical skills with name, category (frontend/backend/tools/soft), proficiency level (0-100)
- `Project`: Portfolio projects with title, slug, description, category, tech_stack (JSON), images, GitHub/live links, status
- `ProjectImage`: Gallery images for projects (ForeignKey to Project)

**URLs**: Root path `/` (handled by portfolio.urls)

**Key Views**:
- `home()`: Main landing page with profile, skills, timeline, recent projects
- `about()`, `skills()`, `contact()`, `download_cv()`
- `project_list()`, `project_detail(slug)`

**Features**:
- Contact form with email sending
- CV/Resume download
- Project filtering by category
- Image galleries for projects

---

### 2. Academic App (`academic/`)
**Purpose**: Academic management tools for courses, notes, flashcards, and study tracking.

**Models**:
- `Course`: Courses with name, code, semester, credits, status (ongoing/completed/dropped), grade
- `Note`: Course notes with title, content, optional file attachment
- `Flashcard`: Study flashcards with question/answer pairs (linked to Course)
- `StudySession`: Study session tracking with date, duration, topics covered

**URLs**: `/academic/`

**Features**:
- Course management and GPA calculation
- Note-taking with file uploads
- Flashcard creation and study mode
- Study session tracking
- AI-powered question generator (integrates with ai_assistant)

---

### 3. Productivity App (`productivity/`)
**Purpose**: Task management, habits, goals, documents, timetables, and financial tracking.

**Models**:
- `Task`: To-do items with title, description, status (todo/in_progress/done), priority (low/medium/high), due_date
- `Habit`: Habit tracking with name, frequency (daily/weekly), current_streak, last_completed_date
- `Goal`: Long-term goals with title, description, target_date, progress percentage
- `Milestone`: Sub-goals within Goals with title, description, completed status, due_date
- `Document`: File storage with title, file, category, tags
- `Timetable`: Weekly schedules stored as JSON
- `Transaction`: Financial transactions with type (income/expense), amount, category, date, description

**URLs**: `/productivity/`

**Features**:
- Task management with priorities and due dates
- Habit tracking with streaks
- Goal setting with progress tracking and milestones
- Document management with tagging
- Weekly timetable/schedule management
- Personal finance tracking

---

### 4. AI Assistant App (`ai_assistant/`)
**Purpose**: AI-powered conversation and assistance features using OpenAI API.

**Models**:
- `Conversation`: Chat conversations with user, title, assistant_type (general/study/code/writing)
- `Message`: Individual messages in conversations with role (user/assistant/system), content, timestamp
- `PromptTemplate`: Reusable prompt templates with name, category, template_text
- `PDFAnalysis`: PDF document analysis with file, summary, key_points (JSON), original_filename

**Services** (`services.py`):
- `get_chat_completion()`: OpenAI API chat completion wrapper
- `extract_text_from_pdf()`: PDF text extraction using PyPDF2
- `analyze_pdf()`: AI-powered PDF analysis with summary and key points
- `generate_questions()`: Generate study questions for courses
- `get_study_help()`: Study assistance
- `get_code_assistance()`: Code review and debugging help
- `get_writing_assistance()`: Writing review and suggestions
- `get_course_recommendations()`: Course recommendations
- Token estimation utilities

**URLs**: `/ai/`

**Features**:
- Multiple conversation types (general, study, code, writing)
- PDF document analysis
- Prompt template management
- Integration with academic app for study help

---

### 5. Business App (`business/`)
**Purpose**: Business idea management, market research, business planning, and import/export tracking.

**Models**:
- `BusinessIdea`: Business concepts with title, description, status (idea/researching/planning/active/paused/abandoned), market_size, competitors
- `MarketResearch`: Research findings linked to BusinessIdea with findings, sources, date
- `BusinessPlan`: Comprehensive business plans (OneToOne with BusinessIdea) with executive_summary, financial_data (JSON)
- `ImportExportRecord`: Import/export transaction tracking with product, quantity, value, country, date, type

**URLs**: `/business/`

**Features**:
- Business idea pipeline management
- Market research documentation
- Business plan creation with financial projections
- Import/export record tracking

---

### 6. Journal App (`journal/`)
**Purpose**: Personal journaling, philosophy tracking, vision goals, and life lessons.

**Models**:
- `JournalEntry`: Daily journal entries with date, content, mood (excellent/good/okay/poor/terrible), energy_level (high/medium/low), tags
  - Unique constraint: one entry per user per date
- `Philosophy`: Personal philosophies with title, content, category (life/work/relationships/growth/values/other)
- `VisionGoal`: Long-term vision goals with title, description, category (career/education/business/personal/africa/financial/health/other), target_date, progress
- `LifeLesson`: Lessons learned with title, lesson, context, date_learned

**URLs**: `/journal/`

**Features**:
- Daily journaling with mood and energy tracking
- Personal philosophy documentation
- Vision goal setting and tracking
- Life lesson repository

---

### 7. Blog App (`blog/`)
**Purpose**: Blog post management with code snippets and tutorials.

**Models**:
- `BlogPost`: Blog posts with title, slug, content, category (django/python/ai/electronics/web/tutorial/project/other), published_date, featured flag, author
- `CodeSnippet`: Code examples linked to blog posts (optional) with title, language, code, description
- `Tutorial`: Tutorial series with title, slug, description, difficulty (beginner/intermediate/advanced), parts count

**URLs**: `/blog/`

**Features**:
- Blog post publishing with categories
- Code snippet embedding
- Tutorial series management
- Featured posts

---

## URL Structure

```
/                           → Portfolio home
/accounts/                  → Authentication (django-allauth)
  /login/
  /signup/
  /logout/
  /password/...
/academic/                  → Academic app
/productivity/              → Productivity app
/ai/                        → AI Assistant app
/business/                  → Business app
/journal/                   → Journal app
/blog/                      → Blog app
/admin/                     → Django admin
```

Each app has its own `urls.py` file that defines its specific routes.

## Authentication System

- **Method**: Email-based authentication (no username)
- **Library**: django-allauth 0.57+
- **Configuration**:
  - `ACCOUNT_LOGIN_METHODS = {'email'}`
  - `ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']`
  - Email verification: optional (configurable via `ACCOUNT_EMAIL_VERIFICATION`)
- **Login Redirect**: `/`
- **Logout Redirect**: `/`
- **Session**: Remembered by default

## Settings Configuration

### Environment Variables (via .env file)

**Required for basic functionality**:
- `SECRET_KEY`: Django secret key
- `DEBUG`: True/False
- `ALLOWED_HOSTS`: Comma-separated list

**Optional**:
- `DATABASE_URL`: PostgreSQL connection string (production)
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `EMAIL_BACKEND`: Email backend (default: console)
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `ACCOUNT_EMAIL_VERIFICATION`: 'mandatory', 'optional', or 'none'

**Production (AWS S3)**:
- `USE_S3`: True/False
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`

**File Upload Settings**:
- `FILE_UPLOAD_MAX_MEMORY_SIZE`: Default 10MB
- `DATA_UPLOAD_MAX_MEMORY_SIZE`: Same as above
- `DATA_UPLOAD_MAX_NUMBER_FIELDS`: Default 1000

### File Storage

**Development**: Local filesystem
- Static files: `static/` directory
- Media files: `media/` directory (with subdirectories per app)
- Profile photos: `media/profile_photos/`
- CV files: `media/profile/cv/`
- Project images: `media/projects/` and `media/projects/gallery/`
- Documents: `media/[app]/[type]/` (e.g., `media/academic/notes/`, `media/productivity/documents/`)

**Production**: AWS S3 (when `USE_S3=True`)

### Security Settings

Production mode (`DEBUG=False`) enables:
- `SECURE_SSL_REDIRECT`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SECURE_BROWSER_XSS_FILTER`
- `SECURE_CONTENT_TYPE_NOSNIFF`
- `X_FRAME_OPTIONS = 'DENY'`

## Template Structure

```
templates/
├── base.html                    # Main base template
├── home.html                    # Portfolio home page
├── components/                  # Reusable components
│   ├── navbar.html
│   ├── footer.html
│   └── ...
├── account/                     # Authentication templates (allauth)
├── portfolio/                   # Portfolio app templates
├── academic/                    # Academic app templates
├── productivity/                # Productivity app templates
├── ai_assistant/                # AI Assistant templates
├── business/                    # Business app templates
├── journal/                     # Journal app templates
└── blog/                        # Blog app templates
```

**Base Template Features**:
- Tailwind CSS styling
- Dark mode support
- Fixed navbar with responsive height
- Message/alerts system with auto-dismiss
- Flowbite JavaScript integration
- Font Awesome icons

## Static Files

- **Input CSS**: `static/css/input.css` (Tailwind source)
- **Output CSS**: `static/css/output.css` (compiled Tailwind)
- **Build Command**: `npm run build:css` (watches for changes)

## Database Models Summary

### User Relationships
All apps use `ForeignKey` or `OneToOneField` to Django's User model (`get_user_model()`), ensuring user-specific data isolation.

### Common Patterns
- **Timestamps**: Most models have `created_at` and `updated_at` fields
- **Ordering**: Models typically ordered by `-created_at` or `-updated_at`
- **Status Fields**: Many models use status choices (projects, courses, tasks, business ideas)
- **JSON Fields**: Used for flexible data (tech_stack, schedule_json, financial_data, social_links)

### Key Relationships
- Profile ↔ User: OneToOne
- BusinessPlan ↔ BusinessIdea: OneToOne
- All other relationships: ForeignKey (many-to-one)

## AI Integration Details

### OpenAI Configuration
- **Model**: GPT-4o-mini (default)
- **Client**: Initialized in `ai_assistant/services.py`
- **Error Handling**: All service functions raise exceptions with descriptive messages
- **Token Estimation**: Rough approximation (~4 characters per token)

### Available AI Services
1. **Chat Completions**: Generic chat with configurable model, temperature, max_tokens
2. **PDF Analysis**: Extract text and generate summaries with key points
3. **Study Help**: Question generation and study assistance
4. **Code Assistance**: Code review and debugging help
5. **Writing Assistance**: Text review and improvement suggestions
6. **Course Recommendations**: Personalized learning path recommendations

### Usage Pattern
```python
from ai_assistant.services import get_chat_completion

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "User question here"}
]
response = get_chat_completion(messages, max_tokens=1000)
```

## Development Workflow

### Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Install Node dependencies: `npm install`
3. Create `.env` file with required variables
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser` or use `create_superuser.py`
6. Collect static files: `python manage.py collectstatic` (production)
7. Run CSS watcher: `npm run build:css` (separate terminal)

### Running the Server
```bash
python manage.py runserver
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Code Patterns & Conventions

### Model Meta Options
- Consistent use of `verbose_name` and `verbose_name_plural`
- Standard ordering by creation/update dates
- Unique constraints where appropriate (e.g., JournalEntry user+date)

### View Patterns
- Function-based views (not class-based)
- Use of `get_object_or_404()` for detail views
- Django messages framework for user feedback
- Context dictionaries passed to templates

### Form Handling
- Separate `forms.py` in each app
- Django forms with validation
- File upload handling for images and documents

### File Uploads
- Validated file extensions (defined in settings)
- Organized by app and type in media directory
- ImageField for images, FileField for documents/PDFs
- Pillow required for image processing

## Key Features by App

1. **Portfolio**: Professional showcase, contact form, CV download
2. **Academic**: Course tracking, GPA calculation, flashcards, study sessions, AI question generator
3. **Productivity**: Tasks, habits, goals with milestones, documents, timetables, finance tracking
4. **AI Assistant**: Multi-type conversations, PDF analysis, study/code/writing help
5. **Business**: Idea pipeline, market research, business plans, import/export tracking
6. **Journal**: Daily entries with mood tracking, philosophies, vision goals, life lessons
7. **Blog**: Post management, code snippets, tutorial series

## Testing & Quality

- Test files exist in each app (`tests.py`) but may need implementation
- Linting and code quality tools not explicitly configured
- Manual testing recommended for features

## Deployment Considerations

1. Set `DEBUG=False` in production
2. Configure `ALLOWED_HOSTS` properly
3. Use PostgreSQL via `DATABASE_URL`
4. Set up AWS S3 for static/media files (optional)
5. Configure email backend for production
6. Set `OPENAI_API_KEY` for AI features
7. Run `collectstatic` before deployment
8. Use proper secret key management
9. Enable HTTPS and security headers (auto-enabled when DEBUG=False)

## Common Tasks for LLM Assistance

When working with this codebase, common tasks might include:

1. **Adding new features** to existing apps
2. **Creating new models** following existing patterns
3. **Implementing views** for CRUD operations
4. **Creating templates** using Tailwind CSS and base.html
5. **Integrating AI features** using services.py functions
6. **Adding URL routes** in app-specific urls.py files
7. **Handling file uploads** with proper validation
8. **Implementing user authentication** checks
9. **Adding form validation** and error handling
10. **Creating migrations** for model changes

## Notes for LLM Developers

- Always check if a feature already exists before creating new code
- Follow the existing patterns (function-based views, model structure, naming conventions)
- Use the base template and component structure
- Integrate with existing AI services when possible
- Ensure user authentication checks on protected views
- Use Django messages framework for user feedback
- Follow the file upload patterns for media handling
- Test with both authenticated and unauthenticated users where applicable
- Consider dark mode styling in templates
- Maintain consistent error handling patterns








