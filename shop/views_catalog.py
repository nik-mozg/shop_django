# shop/views_catalog.py
import datetime
import logging  # noqa: F401

from django.core.paginator import Paginator
from django.db.models import Avg, Count, FloatField
from django.http import JsonResponse

from .models import Banner, Category, Product, Sale

# logger = logging.getLogger('custom_logger')


def get_price_with_discount(product):
    """Возвращает цену продукта с учетом активной скидки, если она есть."""
    try:
        sale = product.sale
        if sale.date_from <= datetime.date.today() <= sale.date_to:
            return sale.sale_price
    except Sale.DoesNotExist:
        pass
    return product.price


def get_categories(request):
    """
    Эндпоинт для получения категорий и подкатегорий.
    """
    categories = Category.objects.filter(parent__isnull=True)

    category_list = []
    for category in categories:
        subcategories = category.subcategories.all()
        category_data = {
            "id": category.id,
            "title": category.name,
            "image": {
                "src": category.image.url if category.image else None,
                "alt": category.name,
            },
            "subcategories": [
                {
                    "id": sub.id,
                    "title": sub.name,
                    "image": {
                        "src": sub.image.url if sub.image else None,
                        "alt": sub.name,
                    },
                }
                for sub in subcategories
            ],
        }
        category_list.append(category_data)

    return JsonResponse(category_list, safe=False, status=200)


def get_catalog(request):
    filter_params = request.GET.get("filter")
    current_page = int(request.GET.get("currentPage", 1))
    category_id = request.GET.get("category")
    sort = request.GET.get("sort", "date")
    sort_type = request.GET.get("sortType", "dec")
    limit = int(request.GET.get("limit", 20))
    tags = request.GET.getlist("tags")
    filter_data = {}
    if filter_params:
        import json

        try:
            filter_data = json.loads(filter_params)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid filter format"}, status=400)
    products = Product.objects.all()
    if "name" in filter_data:
        products = products.filter(title__icontains=filter_data["name"])
    if "minPrice" in filter_data:
        products = products.filter(price__gte=filter_data["minPrice"])
    if "maxPrice" in filter_data:
        products = products.filter(price__lte=filter_data["maxPrice"])
    if "freeDelivery" in filter_data:
        products = products.filter(free_delivery=filter_data["freeDelivery"])
    if "available" in filter_data:
        products = products.filter(count__gt=0)
    if category_id:
        products = products.filter(category_id=category_id)
    if tags:
        products = products.filter(tags__id__in=tags).distinct()
    products = products.annotate(
        rating=Avg("reviews__rate", output_field=FloatField()),
        reviews_count=Count("reviews"),
    )
    sort_prefix = "-" if sort_type == "dec" else ""
    if sort in ["rating", "price", "reviews", "date_added"]:
        products = products.order_by(f"{sort_prefix}{sort}")
    else:
        products = products.order_by(f"{sort_prefix}date_added")
    paginator = Paginator(products, limit)
    page_obj = paginator.get_page(current_page)
    items = []
    for product in page_obj.object_list:
        price = get_price_with_discount(product)
        items.append(
            {
                "id": product.id,
                "category": product.category.id if product.category else None,
                "price": float(price),
                "count": product.count,
                "date": product.date_added.isoformat(),
                "title": product.title,
                "description": product.description,
                "freeDelivery": product.free_delivery,
                "images": [
                    {"src": img.image.url, "alt": img.alt_text}
                    for img in product.images.all()
                ],
                "tags": [
                    {"id": tag.id, "name": tag.name} for tag in product.tags.all()
                ],
                "reviews": product.reviews_count,
                "rating": product.rating or 0.0,
            }
        )

    response = {
        "items": items,
        "currentPage": current_page,
        "lastPage": paginator.num_pages,
    }
    return JsonResponse(response, safe=False)


def get_products_popular(request):
    if request.method == "GET":
        popular_products = Product.objects.annotate(
            review_count=Count("reviews")
        ).order_by("-review_count")[:10]
        data = []
        for product in popular_products:
            print(f"Product: {product.title}, Review count: {product.review_count}")
            price = get_price_with_discount(product)
            data.append(
                {
                    "id": product.id,
                    "category": product.category.id if product.category else None,
                    "price": float(price),
                    "count": product.count,
                    "date": product.date_added.strftime("%a %b %d %Y %H:%M:%S GMT%z"),
                    "title": product.title,
                    "description": product.description,
                    "freeDelivery": product.free_delivery,
                    "images": [
                        {"src": img.image.url, "alt": img.alt_text}
                        for img in product.images.all()
                    ],
                    "tags": [
                        {"id": tag.id, "name": tag.name} for tag in product.tags.all()
                    ],
                    "reviews": product.reviews.count(),
                    "rating": product.reviews.aggregate(Avg("rate"))["rate__avg"]
                    or 0.0,
                }
            )
        return JsonResponse(data, safe=False, status=200)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_products_limited(request):
    if request.method == "GET":
        LIMIT_THRESHOLD = 10
        limited_products = Product.objects.filter(count__lte=LIMIT_THRESHOLD)
        data = []
        for product in limited_products:
            price = get_price_with_discount(product)
            data.append(
                {
                    "id": product.id,
                    "category": product.category.id if product.category else None,
                    "price": float(price),
                    "count": product.count,
                    "date": product.date_added.strftime("%a %b %d %Y %H:%M:%S GMT%z"),
                    "title": product.title,
                    "description": product.description,
                    "freeDelivery": product.free_delivery,
                    "images": [
                        {"src": image.image.url, "alt": image.alt_text}
                        for image in product.images.all()
                    ],
                    "tags": [
                        {"id": tag.id, "name": tag.name} for tag in product.tags.all()
                    ],
                    "reviews": product.reviews.count(),
                    "rating": product.reviews.aggregate(Avg("rate"))["rate__avg"]
                    or 0.0,
                }
            )
        return JsonResponse(data, safe=False, status=200)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_sales(request):
    if request.method == "GET":
        current_page = int(request.GET.get("currentPage", 1))
        items_per_page = 10
        start = (current_page - 1) * items_per_page
        end = start + items_per_page

        sales = Sale.objects.filter(
            date_from__lte=datetime.date.today(), date_to__gte=datetime.date.today()
        )[start:end]
        total_sales = Sale.objects.filter(
            date_from__lte=datetime.date.today(), date_to__gte=datetime.date.today()
        ).count()

        data = {
            "items": [
                {
                    "id": sale.product.id,
                    "price": float(sale.product.price),
                    "salePrice": float(sale.sale_price),
                    "dateFrom": sale.date_from.strftime("%m-%d"),
                    "dateTo": sale.date_to.strftime("%m-%d"),
                    "title": sale.product.title,
                    "images": [
                        {"src": img.image.url, "alt": img.alt_text}
                        for img in sale.product.images.all()
                    ],
                }
                for sale in sales
            ],
            "currentPage": current_page,
            "lastPage": (total_sales + items_per_page - 1) // items_per_page,
        }
        return JsonResponse(data, safe=False, status=200)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_banners(request):

    if request.method == "GET":
        banners = Banner.objects.all().order_by("-date_added")
        data = [
            {
                "id": banner.id,
                "category": (
                    banner.product.category.id if banner.product.category else None
                ),
                "price": float(banner.product.price),
                "count": banner.product.count,
                "date": banner.date_added.strftime("%a %b %d %Y %H:%M:%S GMT%z"),
                "title": banner.title,
                "description": banner.description,
                "freeDelivery": banner.product.free_delivery,
                "images": [{"src": banner.image.url, "alt": banner.title}],
                "tags": [
                    {"id": tag.id, "name": tag.name}
                    for tag in banner.product.tags.all()
                ],
                "reviews": banner.product.reviews.count(),
                "rating": banner.product.reviews.aggregate(Avg("rate"))["rate__avg"]
                or 0.0,
            }
            for banner in banners
        ]
        return JsonResponse(data, safe=False, status=200)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)
