# -*- coding: utf-8 -*-
import os
import django

os.environ.update(DJANGO_SETTINGS_MODULE="app.settings")

django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from app.asgi.routing.py3 import websocket_urlpatterns
from asgiref.compatibility import guarantee_single_callable

application = guarantee_single_callable(
    ProtocolTypeRouter(
        {
            "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        }
    )
)
