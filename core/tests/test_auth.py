import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_register_view_creates_user(client):
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'Testpass123!',
        'password2': 'Testpass123!',
    })
    assert response.status_code == 302
    assert User.objects.filter(username='testuser').exists()


@pytest.mark.django_db
def test_login_view_success(client, user):
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 302
    assert response.url == reverse('dashboard')


@pytest.mark.django_db
def test_login_view_fail(client):
    response = client.post(reverse('login'), {
        'username': 'wronguser',
        'password': 'wrongpass',
    })
    assert response.status_code == 200
    assert b"correct username and password" in response.content


@pytest.mark.django_db
def test_logout(client, user):
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('logout'))
    assert response.status_code == 302
    assert response.url == reverse('home')


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert "/login" in response.url
