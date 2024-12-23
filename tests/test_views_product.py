import json
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.test import APIClient

from shop.models import Product, Review, Sale


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_product():
    def _create_product(title, price, count):
        return Product.objects.create(
            title=title,
            price=price,
            count=count,
            description="Test description",
            full_description="Full test description",
            free_delivery=True,
        )

    return _create_product


@pytest.fixture
def create_sale():
    def _create_sale(product, sale_price, date_from=None, date_to=None):
        date_from = date_from or now().date()
        date_to = date_to or (date_from + timedelta(days=10))
        return Sale.objects.create(
            product=product,
            sale_price=sale_price,
            date_from=date_from,
            date_to=date_to,
        )

    return _create_sale


@pytest.fixture
def create_review():
    def _create_review(product, author, email, text, rate):
        return Review.objects.create(
            product=product,
            author=author,
            email=email,
            text=text,
            rate=rate,
            date=now(),
        )

    return _create_review


@pytest.mark.django_db
def test_get_product_item(api_client, create_product, create_sale, create_review):
    product = create_product("Test Product", 100.0, 10)
    create_sale(
        product,
        sale_price=80.0,
        date_from=now().date(),
        date_to=now().date() + timedelta(days=1),
    )

    create_review(product, "Test Author", "test@example.com", "Great product!", 5)
    url = reverse("get_product_item", args=[product.id])
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product.id
    assert data["price"] == "80.00"
    assert len(data["reviews"]) == 1
    assert data["reviews"][0]["author"] == "Test Author"


@pytest.mark.django_db
def test_get_product_item_not_found(api_client):
    url = reverse("get_product_item", args=[999])
    response = api_client.get(url)

    assert response.status_code == 404
    assert response.json() == {"error": "Product not found"}


@pytest.mark.django_db
def test_post_product_review(api_client, create_product):
    product = create_product("Test Product", 100.0, 10)

    url = reverse("post_product_review", args=[product.id])
    payload = {
        "author": "Test Author",
        "email": "test@example.com",
        "text": "Great product!",
        "rate": 5,
    }

    response = api_client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"] == "Test Author"


@pytest.mark.django_db
def test_post_product_review_missing_fields(api_client, create_product):
    product = create_product("Test Product", 100.0, 10)

    url = reverse("post_product_review", args=[product.id])
    payload = {
        "author": "Test Author",
        "email": "test@example.com",
        "rate": 5,
    }

    response = api_client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 400
    assert response.json() == {"error": "All fields are required"}


@pytest.mark.django_db
def test_post_product_review_invalid_json(api_client, create_product):
    product = create_product("Test Product", 100.0, 10)

    url = reverse("post_product_review", args=[product.id])
    invalid_payload = "Invalid JSON"

    response = api_client.post(
        url, data=invalid_payload, content_type="application/json"
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid JSON"}
