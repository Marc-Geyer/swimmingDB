from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.settings import AUTH_USER_MODEL
from swimpro.models import TrainingGroup, Person


class TrainingGroupMembership(models.Model):
    class Role(models.TextChoices):
        SWIMMER = 'swimmer', _('Swimmer')
        TRAINER = 'trainer', _('Trainer')
        MANAGER = 'manager', _('Manager')

    training_group = models.ForeignKey(TrainingGroup, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, choices=Role, default=Role.SWIMMER)

    class Meta:
        db_table = 'training_group_membership'
        unique_together = ['training_group', 'person']


class UserPerson(models.Model):
    class Relation(models.TextChoices):
        SELF = 'self', _('Self')
        CHILD = 'child', _('Child')
        PARENT = 'parent', _('Parent')

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    relation = models.CharField(max_length=10, choices=Relation, default=Relation.SELF)

    class Meta:
        db_table = 'user_person'
        unique_together = ['user', 'person']
