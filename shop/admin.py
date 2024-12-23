from django.contrib import admin

from .models import (
    Banner,
    BasketItem,
    Category,
    Order,
    OrderItem,
    Product,
    ProductImage,
    Profile,
    Review,
    Sale,
    Tag,
)

admin.site.site_header = "Административный раздел магазина"
admin.site.site_title = "Админка магазина"
admin.site.index_title = "Добро пожаловать в административный раздел"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "fullName", "email", "phone")
    search_fields = ("fullName", "email", "phone")
    list_filter = ("user__is_staff",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "count", "category", "date_added")
    search_fields = ("title", "description")
    list_filter = ("category", "free_delivery")
    prepopulated_fields = {"title": ("description",)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image", "alt_text")
    search_fields = ("product__title",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "author", "email", "rate", "date")
    search_fields = ("author", "email", "product__title")
    list_filter = ("rate",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("product", "sale_price", "date_from", "date_to")
    search_fields = ("product__title",)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("product", "title", "date_added")
    search_fields = ("title", "description")


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "added_at")
    search_fields = ("user__username", "product__title")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "status", "total_cost")
    search_fields = ("user__username", "email", "full_name")
    list_filter = ("status", "delivery_type", "payment_type")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")
    search_fields = ("order__id", "product__title")
