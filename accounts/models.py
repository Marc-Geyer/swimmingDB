from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class SwimProUser(AbstractUser):
    pending_email = models.EmailField(blank=True, null=True)
    email_verification_pending = models.BooleanField(default=False)