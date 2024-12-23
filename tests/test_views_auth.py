# tests/test_views_auth.py
import os

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(username, password, first_name):
        user = User.objects.create_user(
            username=username, password=password, first_name=first_name
        )
        return user

    return _create_user


@pytest.mark.django_db
def test_post_sign_up_success(api_client):
    url = reverse("api_sign_up")
    data = {
        "name": "Test User",
        "username": "testuser",
        "password": "securepassword123",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}
    assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_post_sign_up_username_taken(api_client, create_user):
    create_user("testuser", "securepassword123", "Existing User")

    url = reverse("api_sign_up")
    data = {"name": "New User", "username": "testuser", "password": "securepassword123"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert response.json() == {"error": "Username already taken"}


@pytest.mark.django_db
def test_post_sign_in_success(api_client, create_user):
    create_user("testuser", "securepassword123", "Test User")

    url = reverse("api_sign_in")
    data = {"username": "testuser", "password": "securepassword123"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}


@pytest.mark.django_db
def test_post_sign_in_invalid_credentials(api_client):
    url = reverse("api_sign_in")
    data = {"username": "wronguser", "password": "wrongpassword"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == 401
    assert response.json() == {"error": "Invalid username or password"}


@pytest.mark.django_db
def test_post_sign_out_success(api_client, create_user):
    user = create_user("testuser", "securepassword123", "Test User")
    api_client.force_authenticate(user=user)

    url = reverse("api_sign_out")
    response = api_client.post(url)

    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}


@pytest.mark.django_db
def test_post_sign_out_unauthenticated(api_client):
    url = reverse("api_sign_out")
    response = api_client.post(url)

    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}
