import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Category, Task, MoodEntry, AISummary, PomodoroSession, Rewards

User = get_user_model()



@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def dashboard_user(db):
    return User.objects.create_user(
        username='dashboarder',
        password='testpass',
        points=42,
        streak_days=3,
        reminder_frequency='30min',
        enable_notifications=True,
        enable_sound=False
    )

@pytest.fixture
def journal_user(db):
    return User.objects.create_user(username='journaler', password='journalpass')

@pytest.fixture
def reward_user(db):
    return User.objects.create_user(username='rewarder', password='rewardpass', points=20)

@pytest.fixture
def pomodoro_user(db):
    return User.objects.create_user(
        username='pomodoro',
        password='focuspass',
        focus_time=25,
        break_time=5
    )

@pytest.fixture
def settings_user(db):
    return User.objects.create_user(
        username='settings_user',
        password='settingpass',
        reminder_frequency='30min',
        enable_notifications=False,
        enable_sound=True
    )


@pytest.fixture
def category(user):
    return Category.objects.create(user=user, name='Work', is_active=True)

@pytest.fixture
def dashboard_category(dashboard_user):
    return Category.objects.create(user=dashboard_user, name='Work', is_active=True)

@pytest.fixture
def pomodoro_category(pomodoro_user):
    return Category.objects.create(user=pomodoro_user, name='Work', is_active=True)


@pytest.fixture
def task(user, category):
    return Task.objects.create(
        user=user,
        category=category,
        title="Test Task",
        status="todo",
        due_date=timezone.now()
    )

@pytest.fixture
def today_task(dashboard_user, dashboard_category):
    return Task.objects.create(
        user=dashboard_user,
        title='Today task',
        category=dashboard_category,
        due_date=timezone.now(),
        priority='medium',
        status='todo',
        points=10
    )

@pytest.fixture
def completed_task(dashboard_user, dashboard_category):
    return Task.objects.create(
        user=dashboard_user,
        title='Completed task',
        category=dashboard_category,
        due_date=timezone.now(),
        completed_at=timezone.now(),
        priority='high',
        status='completed',
        points=20
    )

@pytest.fixture
def pomodoro_task(pomodoro_user, pomodoro_category):
    return Task.objects.create(
        user=pomodoro_user,
        category=pomodoro_category,
        title='Pomodoro Task',
        status='todo',
        due_date=timezone.now()
    )


@pytest.fixture
def mood_entry(journal_user):
    return MoodEntry.objects.create(
        user=journal_user,
        date=timezone.localdate(),
        mood='neutral',
        notes='Wrote a test',
        water_intake=6,
        exercised=True,
        diet_summary='Clean eating',
    )

@pytest.fixture
def pomodoro_session(pomodoro_user):
    return PomodoroSession.objects.create(
        user=pomodoro_user,
        start_time=timezone.now(),
        duration=25,
        completed=True
    )

@pytest.fixture
def reward(reward_user):
    return Rewards.objects.create(
        user=reward_user,
        title="Test Reward",
        points=10,
        is_active=True,
        is_claimed=False
    )
