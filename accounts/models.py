from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from nanoid_field import NanoidField


# Main account class
class SwimProUser(AbstractUser):

    id = NanoidField(max_length=25, primary_key=True, unique=True, editable=False)
    pending_email = models.EmailField(blank=True, null=True)
    email_verification_pending = models.BooleanField(default=False)

    class Meta:
        db_table = "swim_pro_user"
