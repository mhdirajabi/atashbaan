from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "atashbaan.images"
    verbose_name = "تصویر"
    verbose_name_plural = "تصویر ها"
