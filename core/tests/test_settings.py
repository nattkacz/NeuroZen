import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_user_settings_get(client, settings_user):
    client.login(username='settings_user', password='settingpass')
    response = client.get(reverse('user_settings'))
    assert response.status_code == 200
    assert b"Settings" in response.content or b"form" in response.content


@pytest.mark.django_db
def test_user_settings_post(client, settings_user):
    client.login(username='settings_user', password='settingpass')
    response = client.post(reverse('user_settings'), {
        'reminder_frequency': '15min',
        'enable_notifications': 'on',
        'focus_time': 30,
        'break_time': 5,
        'daily_goal': 4,
    })

    settings_user.refresh_from_db()
    assert response.status_code == 302
    assert settings_user.reminder_frequency == '15min'
    assert settings_user.enable_notifications is True
