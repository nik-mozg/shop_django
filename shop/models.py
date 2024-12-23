# shop/models.py
import re
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def user_avatar_directory_path(instance, filename):
    """Генерирует путь для загрузки аватара: media/{id пользователя}/avatar/{filename}"""
    return f"{instance.user.id}/avatar/{filename}"


def normalize_phone(phone):
    """Нормализация номера телефона в формате +7XXXXXXXXXX."""
    if phone.startswith("8"):
        return f"+7{phone[1:]}"
    return phone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    fullName = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(
        upload_to=user_avatar_directory_path, null=True, blank=True
    )

    def clean(self):
        if not self.email:
            raise ValidationError({"email": "Email is required."})
        if self.phone:
            phone_pattern = r"^(\+7|8)\d{10}$"
            if not re.match(phone_pattern, self.phone):
                raise ValidationError(
                    {
                        "phone": (
                            "Phone number must be in format +7XXXXXXXXXX or 8XXXXXXXXXX."
                        )
                    }
                )
            self.phone = normalize_phone(self.phone)
            if Profile.objects.filter(phone=self.phone).exclude(pk=self.pk).exists():
                raise ValidationError({"phone": "This phone number is already in use."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    image = models.ImageField(upload_to="category_images/", null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    full_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    free_delivery = models.BooleanField(default=False)
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )

    def clean(self):
        if self.price < 0:
            raise ValidationError({"price": "Price cannot be less than zero."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="Product_images/")
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.product.title}"


class Tag(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, related_name="tags")


class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    author = models.CharField(max_length=100)
    email = models.EmailField()
    text = models.TextField()
    rate = models.PositiveSmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)


class Sale(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="sale"
    )
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_from = models.DateField()
    date_to = models.DateField()

    def clean(self):
        # Проверка, что `sale_price` больше нуля
        if self.sale_price <= 0:
            raise ValidationError(
                {"sale_price": "Sale price must be greater than zero."}
            )

        # Проверка формата дат - Django DateField уже выполняет валидацию формата

        # Проверка, что `date_from` не в прошлом
        if self.date_from < date.today():
            raise ValidationError({"date_from": "Start date cannot be in the past."})

        # Проверка, что `date_to` не в прошлом и не превышает одного года от текущей даты
        if self.date_to < date.today():
            raise ValidationError({"date_to": "End date cannot be in the past."})
        if self.date_to > date.today() + timedelta(days=365):
            raise ValidationError(
                {"date_to": "End date cannot be more than one year from today."}
            )

        # Проверка, что `date_to` >= `date_from`
        if self.date_to < self.date_from:
            raise ValidationError(
                {"date_to": "End date cannot be earlier than start date."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Запускаем валидацию перед сохранением
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale for {self.product.title}"


class Banner(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="banners"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="banner_images/")
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BasketItem(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="basket_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="basket_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.quantity})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
        ("paid", "Paid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    delivery_type = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_error = models.TextField(blank=True, null=True)  # Новое поле
    city = models.CharField(max_length=100)
    address = models.TextField()

    def clean(self):
        if not self.email:
            raise ValidationError({"email": "Email is required."})

        # Проверка формата phone
        if self.phone:
            phone_pattern = (
                r"^(\+7|8)\d{10}$"  # Допустимые форматы: +79201234567 или 89201234567
            )
            if not re.match(phone_pattern, self.phone):
                raise ValidationError(
                    {
                        "phone": (
                            "Phone number must be in format +7XXXXXXXXXX or 8XXXXXXXXXX."
                        )
                    }
                )

            # Нормализация телефона
            self.phone = normalize_phone(self.phone)

            # Проверка уникальности нормализованного номера телефона
            if Profile.objects.filter(phone=self.phone).exclude(pk=self.pk).exists():
                raise ValidationError({"phone": "This phone number is already in use."})

    def save(self, *args, **kwargs):
        self.full_clean()  # Запускаем валидацию перед сохранением
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.price < 0:
            raise ValidationError({"price": "Price cannot be less than zero."})

    def save(self, *args, **kwargs):
        self.full_clean()  # Запускаем валидацию перед сохранением
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.id} - {self.product.title} ({self.quantity})"
