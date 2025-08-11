from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from core.forms import UserRegisterForm, TaskForm, MoodEntryForm, RewardForm, SettingsForm
from core.models import Task, DailyQuote, MoodEntry, PomodoroSession, Category, BreathingExercise, Rewards, AISummary
from datetime import timedelta
from collections import defaultdict
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import localdate
from django.conf import settings
import openai



def home(request):
    """Render the home page."""
    return render(request, 'core/home.html')

def register(request):
    """Handle user registration and redirect to the dashboard on success."""
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
    """Authenticate and log in the user, then redirect to the dashboard."""
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
    """Log out the user and redirect to the home page."""
    logout(request)
    return redirect('home')

@login_required
def user_settings(request):
    """Display and update user account settings."""

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
    """
     Display the user's dashboard with today's tasks, statistics,
     motivational quote, and mood tracking.

    """
    user = request.user
    today = localdate()

    latest_completed = Task.objects.filter(
        user=user,
        status='completed'
    ).order_by('-completed_at').first()

    if latest_completed and latest_completed.completed_at and latest_completed.completed_at.date() == today:
        if user.last_active_date == today - timedelta(days=1):
            user.streak_days += 1
        elif user.last_active_date != today:
            user.streak_days = 1

        user.last_active_date = today
        user.save()

    today_tasks_qs = Task.objects.filter(
        category__user=user,
        due_date__date=today
    ).order_by('priority', 'due_date')


    completed_today = today_tasks_qs.filter(status='completed')
    pending_overall = Task.objects.filter(category__user=user).exclude(status='completed')

    pomodoro_today = PomodoroSession.objects.filter(
        user=user,
        start_time__date=today
    ).count()

    mood_entry = MoodEntry.objects.filter(user=user, date=today).order_by('-time').first()
    breathing_exercise = BreathingExercise.objects.filter(is_active=True).order_by('?').first()
    quote = DailyQuote.objects.filter(is_active=True).order_by('?').first()


    context = {
        'today_tasks_count': today_tasks_qs.count(),
        'completed_today_count': completed_today.count(),
        'pending_tasks_count': pending_overall.count(),

        'total_points': user.points,
        'pomodoro_sessions': pomodoro_today,
        'streak_days': user.streak_days,
        'mood_entry': mood_entry,
        'quote': quote,
        'breathing_exercise': breathing_exercise,
        'reminder_frequency': request.user.reminder_frequency,
        'enable_notifications': request.user.enable_notifications,
        'enable_sound': request.user.enable_sound,
    }

    return render(request, 'core/dashboard.html', context)

@login_required
def all_tasks_view(request):
    """
       Display a list of all tasks with filtering and grouping options.
    """
    user = request.user
    tasks = Task.objects.filter(user=user).select_related('category')


    search = request.GET.get('q')
    selected_status = request.GET.getlist('status')
    selected_categories = request.GET.getlist('category')
    selected_date = request.GET.get('date')
    group_by_category = request.GET.get('group') == 'on'


    if search:
        tasks = tasks.filter(title__icontains=search)


    if selected_status:
        tasks = tasks.filter(status__in=selected_status)


    if selected_categories:
        tasks = tasks.filter(category__id__in=selected_categories)


    if selected_date:
        tasks = tasks.filter(due_date__date=selected_date)


    categories = Category.objects.filter(user=user, is_active=True)


    grouped_tasks = {}
    if group_by_category:
        for cat in categories:
            grouped_tasks[cat.name] = tasks.filter(category=cat)


    context = {
        'tasks': tasks,
        'search': search,
        'selected_status': selected_status,
        'selected_categories': selected_categories,
        'selected_date': selected_date,
        'group_by_category': group_by_category,
        'grouped_tasks': grouped_tasks,
        'categories': categories,
        'status_options': [
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("completed", "Completed")
        ],
    }
    return render(request, 'core/all_tasks.html', context)



@login_required
def tasks_by_category(request, pk):
    """Display tasks for a specific category, grouped by status."""

    category = get_object_or_404(Category, pk=pk, user=request.user)
    search_query = request.GET.get('q', '')

    tasks = Task.objects.filter(user=request.user, category=category)

    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    grouped_tasks = {
        'To Do': tasks.filter(status='todo').order_by('due_date'),
        'In Progress': tasks.filter(status='in_progress').order_by('due_date'),
        'Completed': tasks.filter(status='completed').order_by('due_date'),
    }

    context = {
        'category': category,
        'grouped_tasks': grouped_tasks,
        'search_query': search_query
    }
    return render(request, 'core/tasks_by_category.html', context)


@login_required
def task_create(request):
    """Create a new task, optionally pre-setting the category."""
    category_id = request.GET.get('category')

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('all_tasks')
    else:
        form = TaskForm(user=request.user)
        if category_id:
            form.fields['category'].initial = category_id

    context = {
        'form': form,
    }
    return render(request, 'core/task_form.html', context)


@login_required
def task_edit(request, pk):
    """Edit an existing task."""

    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('all_tasks')
    else:
        form = TaskForm(instance=task, user=request.user)

    context = {
        'form': form,
        'task': task,
    }
    return render(request, 'core/task_form.html', context)


@login_required
def task_delete(request, pk):
    """Delete a task after user confirmation."""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.delete()
        return redirect('all_tasks')

    context = {
        'task': task,
    }
    return render(request, 'core/task_confirm_delete.html', context)


@login_required
def task_complete(request, pk):
    """
    Mark a task as completed, update user points and stats,
    and display success or info message.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if task.status != 'completed':
        task.status = 'completed'
        task.save()

        request.user.points += task.points
        request.user.total_completed_tasks += 1
        request.user.save()
        if request.htmx:
            return HttpResponse(
                "<div class='alert alert-success w-100'> Completed</div>"

            )
        messages.success(request, f"Task completed! You earned {task.points} points.")
    else:
        if request.htmx:
            return HttpResponse(
                "div class='alert alert-info w-100'> Already completed</div>"
            )
        messages.info(request, "This task is already completed.")

    return redirect('tasks_by_category', pk=task.category.pk)

@login_required
def tasks_in_work_hours(request):
    """Display tasks scheduled within the user's preferred working hours."""

    user = request.user
    today = localdate()

    tasks = Task.objects.filter(
        user=user,
        due_date__date=today
    )


    if user.preferred_working_hours_start and user.preferred_working_hours_end:
        tasks = tasks.filter(
            due_date__time__gte=user.preferred_working_hours_start,
            due_date__time__lte=user.preferred_working_hours_end
        )

    tasks = tasks.order_by('due_date')

    return render(request, 'core/tasks_work_hours.html', {
        'tasks': tasks
    })

@login_required
def pomodoro_view(request):
    """Render the Pomodoro timer view with user-configured durations."""

    user = request.user
    context = {
        'tasks': Task.objects.filter(user=user).exclude(status='completed').order_by('-due_date'),
        'focus_time': user.focus_time,
        'break_time': user.break_time,
    }
    return render(request, 'core/pomodoro.html', context)

@login_required
def start_pomodoro(request):
    """
       Start a new Pomodoro session linked to a task (optional).
       Returns session ID as JSON.
    """
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
    """
    End a Pomodoro session, save optional notes,
    and return confirmation as JSON.
    """
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
    """Display a grouped history of completed Pomodoro sessions."""

    sessions = PomodoroSession.objects.filter(user=request.user, completed=True).order_by('-start_time')

    history = defaultdict(list)
    for session in sessions:
        session_date = session.start_time.strftime('%Y-%m-%d')
        history[session_date].append(session)

    sorted_history = dict(sorted(history.items(), reverse=True))

    return render(request, 'core/pomodoro_history.html', {'history': sorted_history})


@login_required
def journal_view(request):
    """Create or update today's mood journal entry."""
    today = localdate()
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
    """Display the history of all journal entries."""

    entries = MoodEntry.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'core/journal_history.html', {'entries': entries})


@login_required
def journal_edit(request, pk):
    """Edit a specific journal entry."""

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
    """Delete a journal entry after confirmation."""

    journal = get_object_or_404(MoodEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        journal.delete()
        return redirect('journal_history')

    return render(request, 'core/journal_delete.html', {'journal': journal})


@login_required
def reward_create(request):
    """Create a new reward that users can redeem with points."""

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
    """Display all active rewards available to the user."""
    rewards = Rewards.objects.filter(user=request.user, is_active=True)
    return render(request, 'core/reward_list.html', {'rewards': rewards})


@login_required
def reward_edit(request, pk):
    """Edit an existing reward."""

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
    """Delete a reward after confirmation."""

    reward = get_object_or_404(Rewards, pk=pk, user=request.user)
    if request.method == 'POST':
        reward.delete()
        return redirect('reward_list')
    return render(request, 'core/reward_delete.html', {'reward': reward})


@login_required
def reward_claim(request, pk):
    """
    Claim a reward if the user has enough points.
    Deduct points and mark reward as claimed.
    """

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
    """
    Generate and display an AI-written summary of the user's day
    based on task completion, Pomodoros, and mood.
    """

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
    • Journal note: {mood_entry.notes if mood_entry else '—'}

    Now please:
    1. Write a warm, emotionally supportive summary using the user's name.
    2. Celebrate even small wins.
    3. Encourage without judgment.
    4. Offer one kind, actionable suggestion for tomorrow.

    The tone should feel like it’s coming from a close, trusted friend or coach who truly cares.
    """

    openai.api_key = settings.OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4.1-nano",
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



@login_required
def summary_history(request):
    """Display a history of daily AI-generated summaries."""

    summaries = AISummary.objects.filter(user=request.user).order_by('-date')

    date = request.GET.get('date')
    if date:
        summaries = summaries.filter(date=date)

    return render(request, 'core/summary_history.html', {
        'summaries': summaries,
        'date': date
    })