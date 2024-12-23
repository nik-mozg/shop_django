import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from shop.models import BasketItem, Order, Product, Profile


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
def create_order(create_user):
    def _create_order(user, total_cost=100.0, status="pending"):
        return Order.objects.create(
            user=user,
            full_name="Test User",
            email="test@example.com",
            delivery_type="standard",
            payment_type="online",
            total_cost=total_cost,
            city="Test City",
            address="Test Address",
            status=status,
        )

    return _create_order


@pytest.fixture
def create_product():
    def _create_product(
        title,
        price,
        count,
        description="Test description",
        full_description="Test full description",
    ):
        return Product.objects.create(
            title=title,
            price=price,
            count=count,
            description=description,
            full_description=full_description,
        )

    return _create_product


@pytest.mark.django_db
def test_get_orders(api_client, create_user, create_order):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    create_order(user)

    url = reverse("orders_view")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["fullName"] == "Test User"
    assert data[0]["status"] == "pending"


@pytest.mark.django_db
def test_post_orders(api_client, create_user, create_product, create_profile):
    user = create_user("testuser", "securepassword")
    create_profile(user)
    api_client.login(username="testuser", password="securepassword")

    product = create_product("Product 1", 100.0, 10)
    BasketItem.objects.create(user=user, product=product, quantity=2)

    url = reverse("orders_view")
    payload = [{"id": product.id, "count": 2}]
    response = api_client.post(
        url, json.dumps(payload), content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert "orderId" in data

    order = Order.objects.get(id=data["orderId"])
    assert order.total_cost == 200.0
    assert order.status == "pending"
    assert order.items.count() == 1
    assert BasketItem.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_get_order_by_id(api_client, create_user, create_order):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    order = create_order(user)

    url = reverse("order_view", args=[order.id])
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order.id
    assert data["status"] == "pending"


@pytest.mark.django_db
def test_post_order_update(api_client, create_user, create_order):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    order = create_order(user)

    url = reverse("order_view", args=[order.id])
    payload = {"status": "accepted"}
    response = api_client.post(
        url, json.dumps(payload), content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["orderId"] == order.id

    order.refresh_from_db()
    assert order.status == "accepted"


@pytest.mark.django_db
def test_get_history_order(api_client, create_user, create_order):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")
    create_order(user, total_cost=100.0, status="pending")

    url = reverse("get_history_order")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "Pending"
    assert float(data[0]["totalCost"]) == 100.0
