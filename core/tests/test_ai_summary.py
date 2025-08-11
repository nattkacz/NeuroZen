import pytest
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
from core.models import AISummary


@pytest.mark.django_db
@patch("openai.ChatCompletion.create")
def test_ai_summary_created_if_not_exists(mock_openai, client, user, task):
    mock_openai.return_value = {
        'choices': [
            {'message': {'content': "Mocked AI summary content"}}
        ]
    }

    client.login(username='testuser', password='testpass')
    response = client.get(reverse("daily_summary"))
    assert response.status_code == 200
    assert b"Mocked AI summary content" in response.content
    assert AISummary.objects.filter(user=user, date=timezone.localdate()).exists()


@pytest.mark.django_db
def test_ai_summary_if_existing(client, user):
    AISummary.objects.create(user=user, date=timezone.localdate(), content="Already generated summary")
    client.login(username='testuser', password='testpass')
    response = client.get(reverse("daily_summary"))
    assert response.status_code == 200
    assert b"Already generated summary" in response.content
