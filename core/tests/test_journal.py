import pytest
from django.urls import reverse
from core.models import MoodEntry


@pytest.mark.django_db
def test_journal_view_get(client, journal_user):
    client.login(username='journaler', password='journalpass')
    response = client.get(reverse('journal_view'))
    assert response.status_code == 200
    assert b"Mood" in response.content


@pytest.mark.django_db
def test_journal_view_post(client, journal_user):
    client.login(username='journaler', password='journalpass')
    response = client.post(reverse('journal_view'), {
        'mood': 'sad',
        'notes': 'Rough day',
        'water_intake': 4,
        'exercised': False,
        'diet_summary': 'Junk food'
    })
    assert response.status_code == 302
    assert MoodEntry.objects.filter(user=journal_user, mood='sad').exists()


@pytest.mark.django_db
def test_journal_history_view(client, journal_user, mood_entry):
    client.login(username='journaler', password='journalpass')
    response = client.get(reverse('journal_history'))
    assert response.status_code == 200
    assert mood_entry.notes.encode() in response.content


@pytest.mark.django_db
def test_journal_edit_view(client, journal_user, mood_entry):
    client.login(username='journaler', password='journalpass')
    response = client.post(reverse('journal_edit', args=[mood_entry.pk]), {
        'mood': 'neutral',
        'notes': 'Changed note',
        'water_intake': 5,
        'exercised': False,
        'diet_summary': 'Okay'
    })
    mood_entry.refresh_from_db()
    assert mood_entry.notes == 'Changed note'
    assert response.status_code == 302


@pytest.mark.django_db
def test_journal_delete_view(client, journal_user, mood_entry):
    client.login(username='journaler', password='journalpass')
    response = client.post(reverse('journal_delete', args=[mood_entry.pk]))
    assert response.status_code == 302
    assert not MoodEntry.objects.filter(pk=mood_entry.pk).exists()
