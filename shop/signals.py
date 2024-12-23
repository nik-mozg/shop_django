from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(instance, created):
    if created:
        Profile.objects.create(
            user=instance,
            fullName=instance.username,
            email=instance.email or f"{instance.username}@example.com",
        )


@receiver(post_save, sender=User)
def save_user_profile(instance):
    instance.profile.save()
