#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.template.defaultfilters import slugify
from web.scripts import web_modules, pgj_actions_markers
from web.models import Area


def get_site():
    name = "Portal"
    qs = Area.objects.filter(active=True, parent__isnull=True, slug=slugify(name))
    if not qs.exists():
        return Area.objects.create(name=name)
    return qs[0]


def create_prosecutor_areas():
    site = get_site()
    areas = [
        "Educação",
        "Segurança",
        "Criança e Adolescente",
        "Saúde",
        "Patrimônio Público",
        "Idoso",
        "Meio Ambiente",
        "Maria da Penha",
        "Outros",
    ]

    for area in areas:
        qs = Area.objects.filter(
            name=area, parent_id=site.id, kind_of_content="pgj-actions"
        )
        if not qs.exists():
            Area.objects.create(
                name=area,
                as_link=True,
                can_share=False,
                parent_id=site.id,
                kind_of_content="pgj-actions",
            )


def main():
    create_prosecutor_areas()
    # web_modules.main()
    pgj_actions_markers.main()
