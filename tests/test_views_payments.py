import json
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from shop.models import Order, Profile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_profile(create_user):
    def _create_profile(user):
        return Profile.objects.create(
            user=user, fullName="Test User", email="test@example.com"
        )

    return _create_profile


@pytest.fixture
def create_user():
    def _create_user(username, password):
        return User.objects.create_user(username=username, password=password)

    return _create_user


@pytest.fixture
def create_order():
    def _create_order(user, total_cost, status="pending", payment_id=None):
        return Order.objects.create(
            user=user,
            total_cost=total_cost,
            full_name="Test User",
            email="testuser@example.com",
            delivery_type="standard",
            payment_type="online",
            city="Test City",
            address="Test Address",
            status=status,
            payment_id=payment_id,
        )

    return _create_order


@pytest.mark.django_db
def test_post_payment_valid_data(api_client, create_user, create_order):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    order = create_order(user, total_cost=100.0, status="pending")

    url = reverse("post_payment", args=[order.id])
    payload = {
        "number": "1234567812345678",
        "name": "Test User",
        "month": "12",
        "year": "25",
        "code": "123",
    }

    response = api_client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Payment processed successfully"
    assert data["order_id"] == order.id

    order.refresh_from_db()
    assert order.status == "paid"


@pytest.mark.django_db
def test_post_payment_invalid_card_number(api_client, create_user, create_order):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    order = create_order(user, total_cost=100.0, status="pending")

    url = reverse("post_payment", args=[order.id])
    payload = {
        "number": "1234",
        "name": "Test User",
        "month": "12",
        "year": "25",
        "code": "123",
    }

    response = api_client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 400
    assert (
        response.json()["error"]
        == "Invalid card number. It should be a 16-digit number."
    )


@pytest.mark.django_db
@patch("yookassa.Payment.create")
def test_create_payment(mock_payment_create, api_client, create_user, create_order):
    mock_payment_create.return_value = {
        "id": "test_payment_id",
        "confirmation": {"confirmation_url": "http://test-confirmation-url.com"},
    }

    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    order = create_order(user, total_cost=100.0, status="pending")

    url = reverse("create_payment", args=[order.id])
    response = api_client.get(url)
    assert response.status_code == 302
    assert response.url == "http://test-confirmation-url.com"

    order.refresh_from_db()
    assert order.payment_id == "test_payment_id"


@pytest.mark.django_db
@patch("shop.views_payments.Payment.find_one")
def test_payment_success(mock_find_one, api_client, create_user, create_order):
    mock_find_one.return_value = MagicMock(id="test_payment_id", status="succeeded")

    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    order = create_order(
        user, total_cost=100.0, status="pending", payment_id="test_payment_id"
    )
    url = reverse("payment_success") + f"?order_id={order.id}"
    response = api_client.get(url)
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "paid"


@pytest.mark.django_db
def test_retry_payment(api_client, create_user, create_order):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    order = create_order(user, total_cost=100.0, status="pending")

    url = reverse("retry_payment", args=[order.id])
    response = api_client.get(url)

    assert response.status_code == 302  # Redirect to create_payment
    assert response.url == reverse("create_payment", args=[order.id])
