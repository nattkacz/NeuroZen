from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from core.forms import UserRegisterForm, TaskForm
from core.models import Task, DailyQuote, MoodEntry, PomodoroSession, Category, BreathingExercise
from datetime import date
from collections import defaultdict
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

@login_required
def task_categories(request):
    user = request.user
    categories = Category.objects.filter(user=user, is_active=True)

    category_data = []
    for category in categories:
        task_count = Task.objects.filter(user=user, category=category).count()
        category_data.append({'category': category, 'task_count': task_count})

    context = {
        'category_data': category_data
    }
    return render(request, 'core/task_categories.html', context)

@login_required
def tasks_by_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    tasks = Task.objects.filter(user=request.user, category=category).order_by('due_date')

    context = {
        'category': category,
        'tasks': tasks
    }
    return render(request, 'core/tasks_by_category.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('tasks_by_category', pk=task.category.pk)
    else:
            form = TaskForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'core/task_form.html', context)


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('tasks_by_category', pk=task.category.pk)
    else:
        form = TaskForm(instance=task, user=request.user)

    context = {
        'form': form,
        'task': task,
    }
    return render(request, 'core/task_form.html', context)

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.delete()
        return redirect('tasks_by_category', pk=task.category.pk)

    context = {
        'task': task,
    }
    return render(request, 'core/task_confirm_delete.html', context)


@login_required
def pomodoro_view(request):
    tasks = Task.objects.filter(user=request.user).order_by('-due_date')
    return render(request, 'core/pomodoro.html', {'tasks': tasks})

@login_required
def start_pomodoro(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = Task.objects.filter(id=task_id, user=request.user).first() if task_id else None

        session = PomodoroSession.objects.create(
            user=request.user,
            task=task,
            start_time=timezone.now().time(),
            duration=25
        )
        return JsonResponse({'session_id': session.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def end_pomodoro(request):
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        note = request.POST.get('note', '')

        session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)
        session.end_time = timezone.now().time()
        session.completed = True
        if note:
            session.notes = note
        session.save()
        return JsonResponse({'status': 'saved'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
