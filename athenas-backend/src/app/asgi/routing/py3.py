# -*- coding: utf-8 -*-
from django.urls import re_path
from app.asgi.consumer.py3 import DefaultConsumer

websocket_urlpatterns = [re_path(r"ws/?", DefaultConsumer.as_asgi())]
