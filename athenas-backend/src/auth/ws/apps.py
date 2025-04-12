from django.apps import AppConfig


class WSAuthConfig(AppConfig):
    name = "auth.ws"
    default_auto_field = "django.db.models.BigAutoField"
    # label = 'auth.ws'
    # verbose_name = 'WS Auth Config'

    controllers = [
        "auth.ws.views",
    ]
