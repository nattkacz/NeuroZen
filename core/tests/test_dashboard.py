import pytest
from django.urls import reverse
from django.utils.timezone import now, localdate
from datetime import timedelta
from core.models import MoodEntry, DailyQuote, BreathingExercise, PomodoroSession, Task


@pytest.mark.django_db
def test_dashboard_for_logged_user(client, dashboard_user):
    client.login(username='dashboarder', password='testpass')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert b"Welcome" in response.content


@pytest.mark.django_db
def test_dashboard_has_today_task_count(client, dashboard_user, today_task):
    client.login(username='dashboarder', password='testpass')
    response = client.get(reverse('dashboard'))
    assert response.context['today_tasks_count'] == 1


@pytest.mark.django_db
def test_dashboard_completed_and_pending_counts(client, dashboard_user, today_task, completed_task):
    client.login(username='dashboarder', password='testpass')
    response = client.get(reverse('dashboard'))
    context = response.context
    assert context['today_tasks_count'] >= 1
    assert context['completed_today_count'] >= 1
    assert context['pending_tasks_count'] >= 0


@pytest.mark.django_db
def test_dashboard_user_context_data(client, dashboard_user):
    client.login(username='dashboarder', password='testpass')

    PomodoroSession.objects.create(
        user=dashboard_user,
        start_time=now(),
        duration=25,
        completed=True
    )

    response = client.get(reverse('dashboard'))
    context = response.context

    assert context['total_points'] == 42
    assert context['streak_days'] == 3
    assert context['pomodoro_sessions'] == 1
    assert context['reminder_frequency'] == '30min'
    assert context['enable_notifications'] is True
    assert context['enable_sound'] is False


@pytest.mark.django_db
def test_dashboard_without_mood_entry(client, dashboard_user):
    client.login(username='dashboarder', password='testpass')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert response.context['mood_entry'] is None


@pytest.mark.django_db
def test_dashboard_with_mood_entry(client, dashboard_user):
    MoodEntry.objects.create(user=dashboard_user, date=localdate(), mood='neutral', notes='test')
    client.login(username='dashboarder', password='testpass')
    response = client.get(reverse('dashboard'))
    mood_entry = response.context['mood_entry']
    assert mood_entry is not None
    assert mood_entry.notes == 'test'


@pytest.mark.django_db
def test_dashboard_with_quote(client, dashboard_user):
    DailyQuote.objects.create(quote="Stay strong", author="Coach Zen", is_active=True)
    client.login(username='dashboarder', password='testpass')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert response.context['quote'] is not None
    assert b"Stay strong" in response.content


@pytest.mark.django_db
def test_dashboard_with_breathing_exercise(client, dashboard_user):
    BreathingExercise.objects.create(
        title="4-4-4",
        inhale_duration=4,
        hold_duration=4,
        exhale_duration=4,
        is_active=True
    )
    client.login(username='dashboarder', password='testpass')
    response = client.get(reverse('dashboard'))
    assert response.context['breathing_exercise'] is not None
    assert b"4-4-4" in response.content


@pytest.mark.django_db
def test_streak_increases_if_active_two_days(client, dashboard_user, dashboard_category):
    yesterday = localdate() - timedelta(days=1)
    dashboard_user.last_active_date = yesterday
    dashboard_user.streak_days = 1
    dashboard_user.save()

    Task.objects.create(
        user=dashboard_user,
        title="Completed streak task",
        category=dashboard_category,
        due_date=now(),
        completed_at=now(),
        priority="high",
        status="completed",
        points=10
    )

    client.login(username='dashboarder', password='testpass')
    client.get(reverse('dashboard'))

    dashboard_user.refresh_from_db()
    assert dashboard_user.streak_days == 2
    assert dashboard_user.last_active_date == localdate()