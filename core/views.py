from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from core.forms import UserRegisterForm, TaskForm, MoodEntryForm, RewardForm, SettingsForm
from core.models import Task, DailyQuote, MoodEntry, PomodoroSession, Category, BreathingExercise, Rewards, AISummary
from datetime import date
from collections import defaultdict
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import localdate
from django.db.models import Sum
from django.conf import settings
import openai
from django.core.mail import send_mail
from django.http import HttpResponse





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
def user_settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings saved successfully.")
            return redirect('user_settings')
    else:
        form = SettingsForm(instance=request.user)
    return render(request, 'core/user_settings.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    today = localdate()


    today_tasks_qs = Task.objects.filter(
        category__user=user,
        due_date__date=today
    ).order_by('priority', 'due_date')

    today_tasks = today_tasks_qs[:5]

    completed_today = today_tasks_qs.filter(status='completed')
    pending_overall = Task.objects.filter(category__user=user).exclude(status='completed')

    pomodoro_today = PomodoroSession.objects.filter(
        user=user,
        start_time__date=today
    ).count()

    mood_entry = MoodEntry.objects.filter(user=user, date=today).order_by('-time').first()
    breathing_exercise = BreathingExercise.objects.filter(is_active=True).order_by('?').first()
    quote = DailyQuote.objects.filter(is_active=True).order_by('?').first()
    categories = Category.objects.filter(user=user, is_active=True)

    context = {
        'today_tasks': today_tasks,
        'today_tasks_count': today_tasks_qs.count(),
        'completed_today_count': completed_today.count(),
        'pending_tasks_count': pending_overall.count(),  # ogólna liczba zadań oczekujących

        'total_points': user.points,  # ogólna suma punktów
        'pomodoro_sessions': pomodoro_today,
        'streak_days': user.streak_days,
        'mood_entry': mood_entry,
        'quote': quote,
        'categories': categories,
        'breathing_exercise': breathing_exercise,
        'reminder_frequency': request.user.reminder_frequency,
        'enable_notifications': request.user.enable_notifications,
        'enable_sound': request.user.enable_sound,
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

    tasks = Task.objects.filter(user=request.user, category=category)

    grouped_tasks = {
        'To Do': tasks.filter(status='todo').order_by('due_date'),
        'In Progress': tasks.filter(status='in_progress').order_by('due_date'),
        'Completed': tasks.filter(status='completed').order_by('due_date'),
    }

    context = {
        'category': category,
        'grouped_tasks': grouped_tasks
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
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if task.status != 'completed':
        task.status = 'completed'
        task.save()

        request.user.points += task.points
        request.user.total_completed_tasks += 1
        request.user.save()

        messages.success(request, f"Task completed! You earned {task.points} points.")
    else:
        messages.info(request, "This task is already completed.")

    return redirect('tasks_by_category', pk=task.category.pk)



@login_required
def pomodoro_view(request):
    user = request.user
    context = {
        'tasks': Task.objects.filter(user=user).exclude(status='completed').order_by('-due_date'),
        'focus_time': user.focus_time,
        'break_time': user.break_time,
    }
    return render(request, 'core/pomodoro.html', context)

@login_required
def start_pomodoro(request):
    user = request.user
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = Task.objects.filter(id=task_id, user=request.user).first() if task_id else None

        session = PomodoroSession.objects.create(
            user=request.user,
            task=task,
            start_time=timezone.now(),
            duration=user.focus_time,
        )
        return JsonResponse({'session_id': session.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def end_pomodoro(request):
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        note = request.POST.get('note', '')

        session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)
        session.end_time = timezone.now()
        session.completed = True
        if note:
            session.notes = note
        session.save()
        return JsonResponse({'status': 'saved'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def pomodoro_history(request):
    sessions = PomodoroSession.objects.filter(user=request.user, completed=True).order_by('-start_time')

    history = defaultdict(list)
    for session in sessions:
        session_date = session.start_time.strftime('%Y-%m-%d')
        history[session_date].append(session)

    sorted_history = dict(sorted(history.items(), reverse=True))

    return render(request, 'core/pomodoro_history.html', {'history': sorted_history})


@login_required
def journal_view(request):
    today = timezone.now().date()
    mood_entry, _ = MoodEntry.objects.get_or_create(user=request.user, date=today)

    if request.method == 'POST':
        form = MoodEntryForm(request.POST, instance=mood_entry)
        if form.is_valid():
            form.save()
            return redirect('journal_history')

    else:
        form = MoodEntryForm(instance=mood_entry)

    return render(request, 'core/journal.html', {'form': form})


@login_required
def journal_history(request):
    entries = MoodEntry.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'core/journal_history.html', {'entries': entries})


@login_required
def journal_edit(request, pk):
    entry = get_object_or_404(MoodEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MoodEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('journal_history')
    else:
        form = MoodEntryForm(instance=entry)

    return render(request, 'core/journal.html', {'form': form})

@login_required
def journal_delete(request, pk):
    journal = get_object_or_404(MoodEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        journal.delete()
        return redirect('journal_history')

    return render(request, 'core/journal_delete.html', {'journal': journal})



@login_required
def reward_create(request):
    if request.method == 'POST':
        form = RewardForm(request.POST)
        if form.is_valid():
            reward = form.save(commit=False)
            reward.user = request.user
            reward.save()
            return redirect('reward_list')
    else:
        form = RewardForm()
    return render(request, 'core/reward_form.html', {'form': form})

@login_required
def reward_list(request):
    rewards = Rewards.objects.filter(user=request.user, is_active=True)
    return render(request, 'core/reward_list.html', {'rewards': rewards})


@login_required
def reward_edit(request, pk):
    reward = get_object_or_404(Rewards, pk=pk, user=request.user)
    if request.method == 'POST':
        form = RewardForm(request.POST, instance=reward)
        if form.is_valid():
            form.save()
            return redirect('reward_list')
    else:
        form = RewardForm(instance=reward)
    return render(request, 'core/reward_form.html', {'form': form})


@login_required
def reward_delete(request, pk):
    reward = get_object_or_404(Rewards, pk=pk, user=request.user)
    if request.method == 'POST':
        reward.delete()
        return redirect('reward_list')
    return render(request, 'core/reward_delete.html', {'reward': reward})

@login_required
def reward_claim(request, pk):
    reward = get_object_or_404(Rewards, pk=pk, user=request.user)

    if reward.is_claimed:
        messages.info(request, "You already claimed this reward.")
    elif request.user.points >= reward.points:
        request.user.points -= reward.points
        request.user.save()

        reward.is_claimed = True

        reward.claimed_at = timezone.now()
        reward.save()

        messages.success(request, "ENJOY")
    else:
        messages.error(request, "Not enough points to claim this reward.")

    return redirect('reward_list')



@login_required
def daily_summary_ai(request):
    user = request.user
    today = timezone.localdate()


    existing = AISummary.objects.filter(user=user, date=today).first()
    if existing:
        return render(request, 'core/daily_summary.html', {
            'ai_summary': existing.content,
        })


    tasks_today = Task.objects.filter(category__user=user, due_date__date=today)
    completed = tasks_today.filter(status='completed')
    pending = tasks_today.exclude(status='completed')
    pomodoros = PomodoroSession.objects.filter(user=user, start_time__date=today).count()
    mood_entry = MoodEntry.objects.filter(user=user, date=today).first()

    prompt = f"""
    The user's name is {user.username}. Please include it at the beginning of the summary to make it feel personal and direct.

    Here's how their day went on {today.strftime('%B %d, %Y')}:

    • Tasks scheduled: {tasks_today.count()}
    • Completed: {completed.count()}
    • Still pending: {pending.count()}
    • Pomodoro sessions done: {pomodoros}
    • Mood: {mood_entry.mood if mood_entry else 'No entry'}
    • Journal note: {mood_entry.note if mood_entry else '—'}

    Now please:
    1. Write a warm, emotionally supportive summary using the user's name.
    2. Celebrate even small wins.
    3. Encourage without judgment.
    4. Offer one kind, actionable suggestion for tomorrow.

    The tone should feel like it’s coming from a close, trusted friend or coach who truly cares.
    """

    openai.api_key = settings.OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are the best, caring, supportive coach."},
            {"role": "user", "content": prompt}
        ]
    )

    ai_summary = response['choices'][0]['message']['content']


    AISummary.objects.create(user=user, date=today, content=ai_summary)

    return render(request, 'core/daily_summary.html', {
        'ai_summary': ai_summary,
    })


def test_email(request):
    try:
        send_mail(
            subject='Test NeuroZen Email',
            message='If you see this, your email config works.',
            from_email=None,  # domyślnie DEFAULT_FROM_EMAIL
            recipient_list=['neurozen1234app@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse("✅ Email sent successfully.")
    except Exception as e:
        return HttpResponse(f"❌ Email failed: {e}")