import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from shop.models import Category, Product, Tag


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_category():
    def _create_category(name):
        return Category.objects.create(name=name)

    return _create_category


@pytest.fixture
def create_product():
    def _create_product(
        title, category=None, price=0.0, count=1, description="", full_description=""
    ):
        return Product.objects.create(
            title=title,
            category=category,
            price=price,
            count=count,
            description=description,
            full_description=full_description,
        )

    return _create_product


@pytest.fixture
def create_tag():
    def _create_tag(name, products=None):
        tag = Tag.objects.create(name=name)
        if products:
            tag.products.add(*products)
        return tag

    return _create_tag


@pytest.mark.django_db
def test_get_all_tags(api_client, create_tag):
    create_tag("Tag1")
    create_tag("Tag2")
    url = reverse("get_tags")
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Tag1"
    assert data[1]["name"] == "Tag2"


@pytest.mark.django_db
def test_get_tags_by_category(api_client, create_category, create_product, create_tag):
    category = create_category("Category1")
    product1 = create_product(
        title="Product1",
        category=category,
        price=100.0,
        count=10,
        description="Short description for Product1",
        full_description="Detailed description for Product1",
    )
    product2 = create_product(
        title="Product2",
        category=category,
        price=150.0,
        count=5,
        description="Short description for Product2",
        full_description="Detailed description for Product2",
    )

    tag1 = create_tag("Tag1", products=[product1, product2])
    tag2 = create_tag("Tag2", products=[product1])
    url = reverse("get_tags") + f"?category={category.id}"
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert {"id": tag1.id, "name": tag1.name} in data
    assert {"id": tag2.id, "name": tag2.name} in data


@pytest.mark.django_db
def test_get_tags_invalid_category(api_client):
    url = reverse("get_tags") + "?category=invalid"
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid category ID"}


@pytest.mark.django_db
def test_get_tags_no_category(api_client, create_tag):
    tag1 = create_tag("Tag1")
    tag2 = create_tag("Tag2")
    url = reverse("get_tags")
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {"id": tag1.id, "name": tag1.name} in data
    assert {"id": tag2.id, "name": tag2.name} in data
