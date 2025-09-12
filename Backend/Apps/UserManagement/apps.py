from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.UserManagement"
    verbose_name = "User Management"

    def ready(self):
        import Apps.UserManagement.signals
