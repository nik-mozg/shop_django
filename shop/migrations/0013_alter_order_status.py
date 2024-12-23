# Generated by Django 5.1.1 on 2024-12-17 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0012_remove_productimage_url_productimage_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("accepted", "Accepted"),
                    ("shipped", "Shipped"),
                    ("delivered", "Delivered"),
                    ("canceled", "Canceled"),
                    ("paid", "Paid"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]