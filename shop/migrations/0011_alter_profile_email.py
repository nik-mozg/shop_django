# Generated by Django 5.1.1 on 2024-12-17 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0010_order_orderitem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
