from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Person

@receiver(post_save, sender=User)
def create_person_for_user(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance, name=instance.username)