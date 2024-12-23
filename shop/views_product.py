# shop/views_product.py
import json
import logging  # noqa: F401

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from .models import Product, Review, Sale

# logger = logging.getLogger('custom_logger')


def get_product_item(request, id):
    try:
        product = get_object_or_404(Product, id=id)
        sale_price = None
        try:
            sale = product.sale
            if sale.date_from <= now().date() <= sale.date_to:
                sale_price = sale.sale_price
        except Sale.DoesNotExist:
            pass

        # Формирование ответа
        response_data = {
            "id": product.id,
            "category": product.category.id if product.category else None,
            "price": sale_price if sale_price else product.price,
            "originalPrice": product.price,
            "salePrice": sale_price,
            "count": product.count,
            "date": product.date_added.strftime("%a %b %d %Y %H:%M:%S GMT%z (%Z)"),
            "title": product.title,
            "description": product.description,
            "fullDescription": product.full_description,
            "freeDelivery": product.free_delivery,
            "images": [
                {"src": image.image.url, "alt": image.alt_text}
                for image in product.images.all()
            ],
            "tags": [tag.name for tag in product.tags.all()],
            "reviews": [
                {
                    "author": review.author,
                    "email": review.email,
                    "text": review.text,
                    "rate": review.rate,
                    "date": review.date.strftime("%Y-%m-%d %H:%M"),
                }
                for review in product.reviews.all()
            ],
        }
        return JsonResponse(response_data, status=200)
    except Http404:
        return JsonResponse({"error": "Product not found"}, status=404)


def post_product_review(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            author = data.get("author")
            email = data.get("email")
            text = data.get("text")
            rate = data.get("rate")

            if not all([author, email, text, rate]):
                return JsonResponse({"error": "All fields are required"}, status=400)
            product = get_object_or_404(Product, id=id)
            current_time = now()
            Review.objects.create(
                product=product,
                author=author,
                email=email,
                text=text,
                rate=rate,
                date=current_time,
            )
            reviews = Review.objects.filter(product=product).values(
                "author", "email", "text", "rate", "date"
            )
            return JsonResponse(list(reviews), safe=False, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)
