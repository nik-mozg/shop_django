# tests/tesrs_views_catalog.py
import datetime
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from shop.models import Banner, Category, Product, Sale


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_category():
    def _create_category(name, parent=None):
        return Category.objects.create(name=name, parent=parent)

    return _create_category


@pytest.fixture
def create_product(create_category):
    def _create_product(
        title,
        price,
        count,
        category=None,
        free_delivery=False,
        description="Description",
    ):
        return Product.objects.create(
            title=title,
            price=price,
            count=count,
            category=category,
            free_delivery=free_delivery,
            description=description,
            full_description=f"{description} Full",
        )

    return _create_product


@pytest.fixture
def create_sale():
    def _create_sale(product, sale_price, date_from, date_to):
        return Sale.objects.create(
            product=product, sale_price=sale_price, date_from=date_from, date_to=date_to
        )

    return _create_sale


@pytest.fixture
def create_banner():
    def _create_banner(product, title, description="Banner description"):
        return Banner.objects.create(
            product=product, title=title, description=description, image=None
        )

    return _create_banner


@pytest.mark.django_db
def test_get_categories(api_client, create_category):
    parent_category = create_category("Parent Category")
    create_category("Child Category 1", parent=parent_category)
    create_category("Child Category 2", parent=parent_category)

    url = reverse("get_categories")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["subcategories"]) == 2
    assert data[0]["title"] == "Parent Category"


@pytest.mark.django_db
def test_get_catalog(api_client, create_product):
    product1 = create_product("Product 1", 100.0, 10)
    product2 = create_product("Product 2", 200.0, 5)

    url = f"{reverse('get_catalog')}?sort=date&sortType=asc"
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["title"] == product1.title
    assert data["items"][1]["title"] == product2.title


@pytest.mark.django_db
def test_get_products_popular(api_client, create_product):
    product1 = create_product("Product 1", 100.0, 10)
    product2 = create_product("Product 2", 200.0, 5)
    product1.reviews.create(
        rate=5, text="Great product", author="Author 1", email="author1@example.com"
    )
    product1.reviews.create(
        rate=4, text="Another review", author="Author 3", email="author3@example.com"
    )
    product2.reviews.create(
        rate=4, text="Good product", author="Author 2", email="author2@example.com"
    )

    url = reverse("get_products_popular")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Product 1"
    assert data[1]["title"] == "Product 2"


@pytest.mark.django_db
def test_get_products_limited(api_client, create_product):
    create_product("Product 1", 100.0, 100)
    create_product("Product 2", 200.0, 5)

    url = reverse("get_products_limited")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Product 2"


@pytest.mark.django_db
def test_get_sales(api_client, create_product, create_sale):
    product = create_product("Product 1", 100.0, 10)
    create_sale(
        product,
        80.0,
        datetime.date.today(),
        datetime.date.today() + datetime.timedelta(days=1),
    )

    url = reverse("get_sales")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["salePrice"] == 80.0


@pytest.fixture
def create_banner():  # noqa: F811
    def _create_banner(product, title):
        image = io.BytesIO()
        img = Image.new("RGB", (100, 100), color="red")
        img.save(image, format="JPEG")
        image.seek(0)
        uploaded_image = SimpleUploadedFile(
            name="test_image.jpg", content=image.read(), content_type="image/jpeg"
        )

        return Banner.objects.create(product=product, title=title, image=uploaded_image)

    return _create_banner


@pytest.mark.django_db
def test_get_banners(api_client, create_product, create_banner):
    product = create_product("Product 1", 100.0, 10)
    create_banner(product, "Banner 1")

    url = reverse("get_banners")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Banner 1"
    assert "src" in data[0]["images"][0]
    assert data[0]["images"][0]["alt"] == "Banner 1"
