import importlib
from django.apps import AppConfig


class FolhaPontoConfig(AppConfig):
    name = "rh.folhaponto"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        pass
