# shop/views_basket.py
import datetime
import json
import logging  # noqa: F401

from django.db.models import Avg
from django.http import JsonResponse

from .models import BasketItem, Product, Sale

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


def get_basket(request):
    print(f"User: {request.user}, is_authenticated: {request.user.is_authenticated}")
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        basket_items = BasketItem.objects.filter(user=request.user)
        data = [
            {
                "id": item.product.id,
                "category": item.product.category.id if item.product.category else None,
                "price": float(get_price_with_discount(item.product)),
                "count": item.quantity,
                "date": item.product.date_added.strftime("%a %b %d %Y %H:%M:%S GMT%z"),
                "title": item.product.title,
                "description": item.product.description,
                "freeDelivery": item.product.free_delivery,
                "images": [
                    {"src": image.image.url, "alt": image.alt_text}
                    for image in item.product.images.all()
                ],
                "tags": [
                    {"id": tag.id, "name": tag.name} for tag in item.product.tags.all()
                ],
                "reviews": item.product.reviews.count(),
                "rating": item.product.reviews.aggregate(Avg("rate"))["rate__avg"]
                or 0.0,
            }
            for item in basket_items
        ]
        return JsonResponse(data, safe=False, status=200)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


# @csrf_exempt
def post_basket(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("id")
            count = data.get("count", 1)

            if not product_id or count <= 0:
                return JsonResponse(
                    {"error": "Invalid product ID or count"}, status=400
                )

            if not request.user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"error": "Product not found"}, status=404)
            basket_item, created = BasketItem.objects.get_or_create(
                user=request.user, product=product, defaults={"quantity": count}
            )

            if not created:
                basket_item.quantity += count
                basket_item.save()
            basket_items = BasketItem.objects.filter(user=request.user)
            data = [
                {
                    "id": item.product.id,
                    "category": (
                        item.product.category.id if item.product.category else None
                    ),
                    "price": float(get_price_with_discount(item.product)),
                    "count": item.quantity,
                    "date": item.product.date_added.strftime(
                        "%a %b %d %Y %H:%M:%S GMT%z"
                    ),
                    "title": item.product.title,
                    "description": item.product.description,
                    "freeDelivery": item.product.free_delivery,
                    "images": [
                        {"src": image.image.url, "alt": image.alt_text}
                        for image in item.product.images.all()
                    ],
                    "tags": [
                        {"id": tag.id, "name": tag.name}
                        for tag in item.product.tags.all()
                    ],
                    "reviews": item.product.reviews.count(),
                    "rating": item.product.reviews.aggregate(Avg("rate"))["rate__avg"]
                    or 0.0,
                }
                for item in basket_items
            ]
            return JsonResponse(data, safe=False, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def delete_basket(request):
    if request.method == "DELETE":
        try:
            data = json.loads(request.body)
            product_id = data.get("id")
            count = data.get("count", 1)

            if not product_id or count <= 0:
                return JsonResponse(
                    {"error": "Invalid product ID or count"}, status=400
                )

            if not request.user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            try:
                basket_item = BasketItem.objects.get(
                    user=request.user, product_id=product_id
                )
            except BasketItem.DoesNotExist:
                return JsonResponse({"error": "Item not found in basket"}, status=404)
            if basket_item.quantity <= count:
                basket_item.delete()
            else:
                basket_item.quantity -= count
                basket_item.save()
            basket_items = BasketItem.objects.filter(user=request.user)
            data = [
                {
                    "id": item.product.id,
                    "category": (
                        item.product.category.id if item.product.category else None
                    ),
                    "price": float(get_price_with_discount(item.product)),
                    "count": item.quantity,
                    "date": item.product.date_added.strftime(
                        "%a %b %d %Y %H:%M:%S GMT%z"
                    ),
                    "title": item.product.title,
                    "description": item.product.description,
                    "freeDelivery": item.product.free_delivery,
                    "images": [
                        {"src": image.image.url, "alt": image.alt_text}
                        for image in item.product.images.all()
                    ],
                    "tags": [
                        {"id": tag.id, "name": tag.name}
                        for tag in item.product.tags.all()
                    ],
                    "reviews": item.product.reviews.count(),
                    "rating": item.product.reviews.aggregate(Avg("rate"))["rate__avg"]
                    or 0.0,
                }
                for item in basket_items
            ]
            return JsonResponse(data, safe=False, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def basket_view(request):
    if request.method == "GET":
        return get_basket(request)
    elif request.method == "POST":
        return post_basket(request)
    elif request.method == "DELETE":
        return delete_basket(request)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)
