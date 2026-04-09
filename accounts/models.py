from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from nanoid_field import NanoidField


# Main account class
class SwimProUser(AbstractUser):

    id = NanoidField(max_length=25, primary_key=True, unique=True, editable=False)

    class Role(models.TextChoices):
        SWIMMER = "swimmer", _("Swimmer")
        PARENT = "parent", _("Parent")

    role = models.CharField(max_length=50, choices=Role, default=Role.SWIMMER)
    privilege_level = models.PositiveSmallIntegerField(
        choices=[
            (1, "Viewer"),
            (2, "Editor"),
            (3, "Manager"),
            (4, "Admin"),
        ],
        default=1,
    )

    pending_email = models.EmailField(blank=True, null=True)
    email_verification_pending = models.BooleanField(default=False)

    class Meta:
        db_table = "swim_pro_user"
