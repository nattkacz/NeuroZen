from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from core.forms import UserRegisterForm
from core.models import Task, DailyQuote, MoodEntry, PomodoroSession, Category, BreathingExercise
from datetime import date
from django.utils import timezone



def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    user = request.user
    today = date.today()

    today_tasks = Task.objects.filter(
        category__user=user,
        due_date=today
    ).order_by('priority', 'due_date')[:5]

    all_tasks = Task.objects.filter(category__user=user)
    completed_tasks = all_tasks.filter(status='completed').count()
    pending_tasks = all_tasks.exclude(status='completed').count()


    pomodoro_today = PomodoroSession.objects.filter(
        user=user,
        start_time__lte=timezone.now()
    ).count()


    mood_entry = MoodEntry.objects.filter(user=user, date=today).order_by('-time').first()

    breathing_exercise = BreathingExercise.objects.filter(is_active=True).order_by('?').first()
    quote = DailyQuote.objects.filter(is_active=True).order_by('?').first()
    categories = Category.objects.filter(user=user, is_active=True)

    context = {
        'tasks': today_tasks,
        'all_tasks_count': all_tasks.count(),
        'completed_tasks_count': completed_tasks,
        'pending_tasks_count': pending_tasks,
        'pomodoro_sessions': pomodoro_today,
        'streak_days': user.streak_days,
        'mood_entry': mood_entry,
        'quote': quote,
        'categories': categories,
        'breathing_exercise': breathing_exercise,
    }

    return render(request, 'core/dashboard.html', context)
