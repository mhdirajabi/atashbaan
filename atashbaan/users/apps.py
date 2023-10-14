from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "atashbaan.users"
    verbose_name = "کاربر ها"

    def ready(self):
        try:
            import atashbaan.users.signals  # noqa: F401
        except ImportError:
            pass
