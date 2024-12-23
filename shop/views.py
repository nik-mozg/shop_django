# shop/views.py
import logging  # noqa: F401

from django.http import JsonResponse

from .models import Product, Tag

# logger = logging.getLogger('custom_logger')


def get_tags(request):
    """
    Эндпоинт для получения тегов.
    Если передан параметр categoryId, фильтрует теги по категории.
    """
    category_id = request.GET.get("category")

    if category_id:
        try:
            products = Product.objects.filter(category_id=category_id)
            tags = Tag.objects.filter(products__in=products).distinct()
        except ValueError:
            return JsonResponse({"error": "Invalid category ID"}, status=400)
    else:
        tags = Tag.objects.all()
    tag_list = [{"id": tag.id, "name": tag.name} for tag in tags]
    return JsonResponse(tag_list, safe=False, status=200)
