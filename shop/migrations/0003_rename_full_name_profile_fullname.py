# Generated by Django 5.1.3 on 2024-12-07 05:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_alter_profile_avatar_alter_profile_phone"),
    ]

    operations = [
        migrations.RenameField(
            model_name="profile",
            old_name="full_name",
            new_name="fullname",
        ),
    ]