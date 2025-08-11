# 🧠 NeuroZen – Productivity & Mental Wellness Web App

**NeuroZen** is a modern Django-based web application designed to help users improve productivity while maintaining mental balance. It integrates task planning, Pomodoro sessions, mood journaling, and AI-generated summaries — all in one intuitive dashboard.

---

##  Key Features

###  Task Management
- Add, edit, delete, and complete tasks
- Task categorization (e.g., Work, Study, Personal, etc.)
- Filter tasks by status, date, and category
- Grouping and searching with advanced filters
- Point system for completed tasks

###  Pomodoro Sessions
- Log focused work sessions
- Track daily Pomodoros and focus statistics
- Display focus-based tasks for current working hours

###  Mood Journal
- Log daily moods, water intake, diet, and exercise
- Write reflective notes and view mood history
- Auto-create one journal entry per day

###  Breathing Exercises
- Suggested relaxation exercises
- Adjustable inhale, hold, and exhale timing

###  AI Daily Summary
- Automatically generate daily summaries using OpenAI
- Personalized text based on task performance and mood
- View summary history with filters

###  Progress & Goals
- Daily goal tracking
- Task streak counter with active day detection


## Tech Stack

- **Backend**: Django 5, Python 3.13
- **Frontend**: Bootstrap 5, HTML, custom templates, JavaScript
- **Database**: PostgreSQL
- **APIs**: OpenAI API for AI summaries
- **Testing**: Pytest + Django test framework
- **Other**: Django Forms, Messages, Authentication, ORM

---

##  Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/neurozen.git
cd neurozen
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file or set variables in `settings.py`:
```env
OPENAI_API_KEY=your_openai_key_here
DEBUG=True
SECRET_KEY=your_django_secret_key
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create a superuser
```bash
python manage.py createsuperuser
```

### 7. Launch the development server
```bash
python manage.py runserver
```

