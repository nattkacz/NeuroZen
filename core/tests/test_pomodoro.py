import pytest
from django.urls import reverse
from django.utils import timezone
from core.models import PomodoroSession


@pytest.mark.django_db
def test_pomodoro_view_renders(client, pomodoro_user, pomodoro_task):
    client.login(username='pomodoro', password='focuspass')
    response = client.get(reverse('pomodoro'))
    assert response.status_code == 200
    assert pomodoro_task.title.encode() in response.content


@pytest.mark.django_db
def test_start_pomodoro_creates_session(client, pomodoro_user, pomodoro_task):
    client.login(username='pomodoro', password='focuspass')
    response = client.post(reverse('start_pomodoro'), {
        'task_id': pomodoro_task.id
    })
    assert response.status_code == 200
    data = response.json()
    assert 'session_id' in data
    assert PomodoroSession.objects.filter(id=data['session_id']).exists()


@pytest.mark.django_db
def test_end_pomodoro_completes_session(client, pomodoro_user):
    session = PomodoroSession.objects.create(
        user=pomodoro_user,
        start_time=timezone.now(),
        duration=25,
        completed=False
    )
    client.login(username='pomodoro', password='focuspass')
    response = client.post(reverse('end_pomodoro'), {
        'session_id': session.id,
        'note': 'Great work'
    })
    assert response.status_code == 200
    session.refresh_from_db()
    assert session.completed is True
    assert session.notes == 'Great work'
    assert session.end_time is not None


@pytest.mark.django_db
def test_pomodoro_history_view(client, pomodoro_user, pomodoro_session):
    client.login(username='pomodoro', password='focuspass')
    response = client.get(reverse('pomodoro_history'))
    assert response.status_code == 200

    date_key = pomodoro_session.start_time.strftime('%Y-%m-%d')
    assert pomodoro_session in response.context['history'][date_key]
