import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from shop.models import Profile


@pytest.fixture
def create_user():
    def _create_user(username, password):
        return User.objects.create_user(username=username, password=password)

    return _create_user


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def create_profile():
    def _create_profile(
        user, full_name="Test User", email="test@example.com", phone="+79001234567"
    ):
        return Profile.objects.create(
            user=user, fullName=full_name, email=email, phone=phone
        )

    return _create_profile


@pytest.mark.django_db
def test_get_profile_authenticated(api_client, create_user, create_profile):
    user = create_user("testuser", "securepassword")
    create_profile(user)
    api_client.login(username="testuser", password="securepassword")
    url = reverse("api_profile")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["fullName"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["phone"] == "+79001234567"


@pytest.mark.django_db
def test_get_profile_unauthenticated(api_client):
    url = reverse("api_profile")
    response = api_client.get(url)
    assert response.status_code == 401
    assert response.json() == {"error": "User not authenticated"}


@pytest.mark.django_db
def test_post_profile_update(api_client, create_user, create_profile):
    user = create_user("testuser", "securepassword")
    create_profile(user)
    api_client.login(username="testuser", password="securepassword")
    url = reverse("api_profile")
    payload = {
        "fullName": "Updated User",
        "email": "updated@example.com",
        "phone": "+79111234567",
    }
    response = api_client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Profile updated successfully"}

    profile = Profile.objects.get(user=user)
    assert profile.fullName == "Updated User"
    assert profile.email == "updated@example.com"
    assert profile.phone == "+79111234567"


@pytest.mark.django_db
def test_post_profile_invalid_data(api_client, create_user):
    create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    url = reverse("api_profile")
    payload = {"email": "invalid-email", "phone": "123"}
    response = api_client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )

    assert response.status_code == 400
    data = response.json()
    assert "email" in data["errors"]
    assert "phone" in data["errors"]


@pytest.mark.django_db
def test_post_profile_password_success(api_client, create_user):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    url = reverse("api_profile_password")
    payload = {"currentPassword": "securepassword", "newPassword": "newpassword123"}
    response = api_client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Password updated successfully"}

    user.refresh_from_db()
    assert user.check_password("newpassword123")


@pytest.mark.django_db
def test_post_profile_password_invalid_current_password(api_client, create_user):
    create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    url = reverse("api_profile_password")
    payload = {"currentPassword": "wrongpassword", "newPassword": "newpassword123"}
    response = api_client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Current password is incorrect"}
