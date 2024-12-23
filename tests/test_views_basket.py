# tests/test_views_basket.py
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from shop.models import BasketItem, Category, Product, Sale


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(username, password):
        user = User.objects.create_user(username=username, password=password)
        return user

    return _create_user


@pytest.fixture
def create_category():
    def _create_category(name):
        return Category.objects.create(name=name)

    return _create_category


@pytest.fixture
def create_product(create_category):
    def _create_product(
        title,
        price,
        count,
        category_name=None,
        free_delivery=False,
        description="Test description",
        full_description="Test full description",
    ):
        category = create_category(category_name) if category_name else None
        return Product.objects.create(
            title=title,
            price=price,
            count=count,
            category=category,
            free_delivery=free_delivery,
            description=description,
            full_description=full_description,
        )

    return _create_product


@pytest.fixture
def create_sale():
    def _create_sale(product, sale_price, date_from, date_to):
        return Sale.objects.create(
            product=product, sale_price=sale_price, date_from=date_from, date_to=date_to
        )

    return _create_sale


@pytest.mark.django_db
def test_get_basket(api_client, create_user, create_product):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")

    print(f"Authenticated user: {user.username}")
    product = create_product("Test Product", 100.0, 10)
    BasketItem.objects.create(user=user, product=product, quantity=2)

    url = reverse("basket_view")
    response = api_client.get(url)

    print(f"Response data: {response.content}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Product"
    assert data[0]["count"] == 2


@pytest.mark.django_db
def test_post_basket(api_client, create_user, create_product):
    create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")  # Используем login

    product = create_product("Test Product", 100.0, 10)

    url = reverse("basket_view")
    payload = {"id": product.id, "count": 2}
    response = api_client.post(url, payload, format="json")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Product"
    assert data[0]["count"] == 2


@pytest.mark.django_db
def test_post_basket_invalid_data(api_client, create_user):
    create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")  # Используем login

    url = reverse("basket_view")
    payload = {"id": None, "count": 2}  # Invalid product ID
    response = api_client.post(url, payload, format="json")

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid product ID or count"}


@pytest.mark.django_db
def test_delete_basket(api_client, create_user, create_product):
    user = create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")  # Используем login

    product = create_product("Test Product", 100.0, 10)
    BasketItem.objects.create(user=user, product=product, quantity=2)

    url = reverse("basket_view")
    payload = {"id": product.id, "count": 1}
    response = api_client.delete(url, payload, format="json")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["count"] == 1  # Remaining count after deletion


@pytest.mark.django_db
def test_delete_basket_nonexistent_item(api_client, create_user):
    create_user("testuser", "securepassword")
    api_client.login(username="testuser", password="securepassword")  # Используем login

    url = reverse("basket_view")
    payload = {"id": 999, "count": 1}  # Non-existent product ID
    response = api_client.delete(url, payload, format="json")

    assert response.status_code == 404
    assert response.json() == {"error": "Item not found in basket"}
