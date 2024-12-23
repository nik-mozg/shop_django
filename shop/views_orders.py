# shop/views_orders.py
import json
import logging  # noqa: F401
from datetime import date

from django.db import transaction
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import BasketItem, Order, OrderItem, Product, Profile, Sale

# logger = logging.getLogger('custom_logger')


def orders_view(request):
    if request.method == "GET":
        return get_orders(request)
    elif request.method == "POST":
        return post_orders(request)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_orders(request):
    if request.method == "GET":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        orders = Order.objects.filter(user=user, status__in=["pending", "accepted"])
        data = []
        for order in orders:
            data.append(
                {
                    "id": order.id,
                    "createdAt": order.created_at.strftime("%Y-%m-%d %H:%M"),
                    "fullName": order.full_name,
                    "email": order.email,
                    "phone": order.phone,
                    "deliveryType": order.delivery_type,
                    "paymentType": order.payment_type,
                    "totalCost": float(order.total_cost),
                    "status": order.status,
                    "city": order.city,
                    "address": order.address,
                    "products": [
                        {
                            "id": item.product.id,
                            "category": (
                                item.product.category.id
                                if item.product.category
                                else None
                            ),
                            "price": float(item.price),
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
                            "rating": item.product.reviews.aggregate(Avg("rate"))[
                                "rate__avg"
                            ]
                            or 0.0,
                        }
                        for item in order.items.all()
                    ],
                }
            )
        return JsonResponse(data, safe=False, status=200)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_price_with_discount(product):
    """Возвращает цену продукта с учетом активной скидки, если она есть."""
    try:
        sale = product.sale
        if sale.date_from <= date.today() <= sale.date_to:
            return float(sale.sale_price)
    except Sale.DoesNotExist:
        pass
    return float(product.price)


def post_orders(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)
            total_cost = 0
            order_items = []
            for item in data:
                try:
                    product = Product.objects.get(id=item["id"])
                    price = get_price_with_discount(product)
                    total_cost += price * item["count"]
                    order_items.append(
                        {"product": product, "count": item["count"], "price": price}
                    )

                except Product.DoesNotExist:
                    print(f"Product with id {item['id']} not found")
                    return JsonResponse({"error": "Product not found"}, status=404)
                except KeyError as e:
                    print(f"Missing key in item data: {e}")
                    return JsonResponse(
                        {"error": f"Missing key in item data: {e}"}, status=400
                    )
            profile, _ = Profile.objects.get_or_create(user=user)

            if not profile.fullName or not profile.email:
                return JsonResponse(
                    {
                        "error": (
                            "Profile is missing necessary information "
                            "(fullName, email)"
                        )
                    },
                    status=400,
                )
            order = Order.objects.create(
                user=user,
                full_name=profile.fullName,
                email=profile.email,
                delivery_type="standard",
                payment_type="online",
                total_cost=total_cost,
                city="Moscow",
                address="Default address",
                status="pending",
            )
            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["count"],
                    price=item["price"],
                )
                item["product"].count -= item["count"]
                item["product"].save()
            BasketItem.objects.filter(user=user).delete()
            response = {"orderId": order.id}
            return JsonResponse(response, status=200)
        except Exception as e:
            print("Error during order creation:", e)
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_order_by_id(request, id):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        order = get_object_or_404(Order, id=id, user=request.user)
        data = {
            "id": order.id,
            "createdAt": order.created_at.strftime("%Y-%m-%d %H:%M"),
            "fullName": order.full_name,
            "email": order.email,
            "phone": order.phone,
            "deliveryType": order.delivery_type,
            "paymentType": order.payment_type,
            "totalCost": float(order.total_cost),
            "status": order.status,
            "city": order.city,
            "address": order.address,
            "products": [
                {
                    "id": item.product.id,
                    "category": (
                        item.product.category.id if item.product.category else None
                    ),
                    "price": float(item.price),
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
                for item in order.items.all()
            ],
        }

        return JsonResponse(data, status=200)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def post_order_update(request, id):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        try:
            data = json.loads(request.body)
            status = data.get("status")

            if not status:
                print(
                    f"No status provided, setting status to 'accepted' for order {id}"
                )
                status = "accepted"
            order = get_object_or_404(Order, id=id, user=request.user)
            with transaction.atomic():
                order.status = status
                order.save()
            response_data = {"orderId": order.id}

            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def order_view(request, id):
    if request.method == "GET":
        return get_order_by_id(request, id)
    elif request.method == "POST":
        return post_order_update(request, id)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_history_order(request):
    if request.method == "GET":
        try:
            orders = Order.objects.filter(user=request.user).order_by("-created_at")
            orders_data = [
                {
                    "id": order.id,
                    "createdAt": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "deliveryType": order.delivery_type,
                    "paymentType": order.payment_type,
                    "totalCost": order.total_cost,
                    "status": order.get_status_display(),
                    "paymentError": order.payment_error or None,
                }
                for order in orders
            ]

            return JsonResponse(orders_data, safe=False)
        except Exception as e:
            print(f"Ошибка при получении истории заказов: {e}")
            return JsonResponse(
                {"error": "Произошла ошибка при получении истории заказов."}, status=500
            )
    else:
        return JsonResponse({"error": "Метод не поддерживается."}, status=405)
