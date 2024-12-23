# shop/views.py
import json
import logging  # noqa: F401
import re
import uuid

from django.http import HttpResponseRedirect, JsonResponse

# logger = logging.getLogger('custom_logger')
from django.shortcuts import get_object_or_404, redirect, render
from yookassa import Configuration, Payment

from .models import Order

Configuration.account_id = "1001674"
Configuration.secret_key = "test_AX2vIdQrcGW0dwjLkIhAo7KecbtPvghXFfAqskjQ9yg"


def post_payment(request, id):
    if request.method == "POST":
        try:
            print(f"Received POST request for payment processing on order {id}")
            try:
                data = json.loads(request.body)
                print(f"Request body successfully parsed: {data}")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            number = data.get("number")
            name = data.get("name")
            month = data.get("month")
            year = data.get("year")
            code = data.get("code")
            if not number or not re.match(r"^\d{16}$", number):
                return JsonResponse(
                    {"error": "Invalid card number. It should be a 16-digit number."},
                    status=400,
                )
            if (
                not year
                or not re.match(r"^\d{2}$", year)
                or not (15 <= int(year) <= 40)
            ):
                return JsonResponse(
                    {
                        "error": (
                            "Invalid year. It should be a two-digit number "
                            "between 15 and 40."
                        )
                    },
                    status=400,
                )
            if not month or not re.match(r"^(0[1-9]|1[0-2])$", month):
                return JsonResponse(
                    {
                        "error": (
                            "Invalid month. It should be a two-digit number "
                            "between 01 and 12."
                        )
                    },
                    status=400,
                )
            if not code or not re.match(r"^\d{3}$", code):
                return JsonResponse(
                    {"error": "Invalid code. It should be a 3-digit number."},
                    status=400,
                )
            if not all([name, number, month, year, code]):
                return JsonResponse({"error": "Missing required fields"}, status=400)
            # Пример логики (например, сохранение платежа)
            # payment = Payment.objects.create(number=number, name=name,
            # month=month, year=year, code=code)
            # print(f"Payment object created: {payment}")
            try:
                order = Order.objects.get(id=id)
            except Order.DoesNotExist:
                print(f"Error: Order with id {id} does not exist.")
                return JsonResponse({"error": "Order not found"}, status=404)
            order.status = "paid"
            order.save()
            print(f"Order {id} status updated to 'paid'.")
            print(f"Payment for order {id} processed successfully.")
            return JsonResponse(
                {"message": "Payment processed successfully", "order_id": id},
                status=200,
            )

        except json.JSONDecodeError:
            print("Error: Invalid JSON in the request.")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        print(f"Error: Method {request.method} not allowed for payment processing.")
        return JsonResponse({"error": "Method not allowed"}, status=405)


def create_payment(request, id):
    """
    Функция для создания платежа в YooKassa и изменения статуса заказа.
    """
    order = get_object_or_404(Order, id=id)

    try:
        payment = Payment.create(
            {
                "amount": {
                    "value": str(order.total_cost),
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": (
                        f"http://127.0.0.1:8000/payment-success/"
                        f"?order_id={order.id}"
                    ),
                },
                "capture": True,
                "description": f"Заказ №{order.id} - Оплата заказа",
            },
            uuid.uuid4(),
        )

        order.payment_id = payment["id"]
        order.save()

        redirect_url = payment["confirmation"]["confirmation_url"]
        return HttpResponseRedirect(redirect_url)  # Возвращаем редирект (302)

    except Exception as e:
        print(f"Ошибка при создании платежа: {e}")
        return JsonResponse(
            {"status": "error", "message": f"Ошибка при создании платежа: {e}"},
            status=500,
        )


def payment_success(request):
    order_id = request.GET.get("order_id")
    if not order_id:
        return render(
            request,
            "payment_success.html",
            {"error": "Не удалось получить идентификатор заказа."},
        )
    try:
        order = Order.objects.get(id=order_id)
        if not order.payment_id:
            return render(
                request,
                "payment_error.html",
                {"error": "Платежный идентификатор отсутствует для данного заказа."},
            )
        payment = Payment.find_one(order.payment_id)
        print(f"Найден платеж с ID: {payment.id}, Статус: {payment.status}")

        if payment.status == "succeeded":
            order.status = "paid"
            order.save()
            return render(
                request, "payment_success.html", {"order": order, "status": "success"}
            )

        else:
            print(f"Платеж не завершен. Статус: {payment.status}")
            return render(
                request,
                "payment_error.html",
                {
                    "error": f"Платеж не завершен. Статус: {payment.status}",
                    "order": order,
                },
            )

    except Order.DoesNotExist:
        print("Ошибка: Заказ не найден")
        return render(request, "payment_error.html", {"error": "Заказ не найден"})

    except Exception as e:
        print(f"Ошибка при обработке платежа: {str(e)}")
        return render(request, "payment_error.html", {"error": f"Ошибка: {str(e)}"})


def retry_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        return redirect("create_payment", id=order.id)

    except Order.DoesNotExist:
        return render(request, "payment_error.html", {"error": "Заказ не найден"})
