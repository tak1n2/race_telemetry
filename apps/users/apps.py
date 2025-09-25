from django.apps import AppConfig



class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users" # python path
    label = "users"
    verbose_name = "Users"