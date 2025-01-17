# Generated by Django 5.1.3 on 2024-12-07 12:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0006_category_image_category_parent"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sale",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sale_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("date_from", models.DateField()),
                ("date_to", models.DateField()),
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sale",
                        to="shop.product",
                    ),
                ),
            ],
        ),
    ]
