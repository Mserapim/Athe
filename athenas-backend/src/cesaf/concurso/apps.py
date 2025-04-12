# -*- coding:utf-8 -*-

from django.apps import AppConfig


class ConcursoConfig(AppConfig):
    name = "cesaf.concurso"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "cesaf.concurso.views",
    ]
