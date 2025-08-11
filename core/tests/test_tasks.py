import pytest
from django.urls import reverse
from django.utils.timezone import now
from core.models import Task


@pytest.mark.django_db
def test_all_tasks_view(client, user, task):
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('all_tasks'))
    assert response.status_code == 200
    assert b'Test Task' in response.content


@pytest.mark.django_db
def test_tasks_by_category(client, user, category, task):
    client.login(username='testuser', password='testpass')
    url = reverse('tasks_by_category', args=[category.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert task in response.context['grouped_tasks']['To Do']


@pytest.mark.django_db
def test_task_create(client, user, category):
    client.login(username='testuser', password='testpass')
    response = client.post(reverse('task_create'), {
        'title': 'New Task',
        'category': category.pk,
        'due_date': now().strftime('%Y-%m-%dT%H:%M'),
        'priority': 'low',
        'status': 'todo',
        'points': 5,
    })
    assert response.status_code == 302
    assert Task.objects.filter(title='New Task').exists()


@pytest.mark.django_db
def test_task_edit(client, user, task):
    client.login(username='testuser', password='testpass')
    url = reverse('task_edit', args=[task.pk])
    response = client.post(url, {
        'title': 'Edited Task',
        'category': task.category.pk,
        'due_date': now().strftime('%Y-%m-%dT%H:%M'),
        'priority': 'high',
        'status': 'in_progress',
        'points': 15,
    })
    assert response.status_code == 302
    task.refresh_from_db()
    assert task.title == 'Edited Task'
    assert task.points == 15


@pytest.mark.django_db
def test_task_delete(client, user, task):
    client.login(username='testuser', password='testpass')
    url = reverse('task_delete', args=[task.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert not Task.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
def test_task_complete(client, user, task):
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('task_complete', args=[task.pk]))
    assert response.status_code == 302
    task.refresh_from_db()
    user.refresh_from_db()
    assert task.status == 'completed'
    assert user.points == task.points


@pytest.mark.django_db
def test_tasks_in_work_hours(client, user, task):
    user.preferred_working_hours_start = task.due_date.time()
    user.preferred_working_hours_end = task.due_date.time()
    user.save()
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('tasks_in_work_hours'))
    assert response.status_code == 200
    assert b'Test Task' in response.content
