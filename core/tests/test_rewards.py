import pytest
from django.urls import reverse
from core.models import Rewards


@pytest.mark.django_db
def test_reward_list(client, reward_user, reward):
    client.login(username='rewarder', password='rewardpass')
    response = client.get(reverse('reward_list'))
    assert response.status_code == 200
    assert reward.title.encode() in response.content


@pytest.mark.django_db
def test_reward_create(client, reward_user):
    client.login(username='rewarder', password='rewardpass')
    response = client.post(reverse('reward_create'), {
        'title': 'New Reward',
        'points': 5,
        'is_active': True
    })
    assert response.status_code == 302
    assert Rewards.objects.filter(title='New Reward').exists()


@pytest.mark.django_db
def test_reward_edit(client, reward_user, reward):
    client.login(username='rewarder', password='rewardpass')
    response = client.post(reverse('reward_edit', args=[reward.pk]), {
        'title': 'Edited Reward',
        'points': 8,
        'is_active': True
    })
    reward.refresh_from_db()
    assert reward.title == 'Edited Reward'
    assert reward.points == 8
    assert response.status_code == 302


@pytest.mark.django_db
def test_reward_delete(client, reward_user, reward):
    client.login(username='rewarder', password='rewardpass')
    response = client.post(reverse('reward_delete', args=[reward.pk]))
    assert response.status_code == 302
    assert not Rewards.objects.filter(pk=reward.pk).exists()


@pytest.mark.django_db
def test_reward_claim_success(client, reward_user, reward):
    client.login(username='rewarder', password='rewardpass')
    response = client.get(reverse('reward_claim', args=[reward.pk]))
    reward_user.refresh_from_db()
    reward.refresh_from_db()
    assert reward.is_claimed is True
    assert reward_user.points == 10  # 20 - 10
    assert response.status_code == 302


@pytest.mark.django_db
def test_reward_claim_insufficient_points(client, reward_user):
    reward = Rewards.objects.create(user=reward_user, title="Too Expensive", points=50, is_active=True)
    client.login(username='rewarder', password='rewardpass')
    response = client.get(reverse('reward_claim', args=[reward.pk]))
    reward.refresh_from_db()
    assert reward.is_claimed is False
    assert reward_user.points == 20
