from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SwimproConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'swimpro'
    verbose_name = _('Swim Pro')

    def ready(self):
        import swimpro.signals
