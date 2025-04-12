#!/usr/bin/env python
# -*- coding:utf-8 -*-

from web import models as web


def get_sites():
    return web.Area.objects.filter(active=True, parent__isnull=True)


def get_default_modules():
    return web.Module.objects.filter(slug__in=["links", "posts"])


def fix_kind_of_contents():
    get_sites().update(kind_of_content="area")
    web.Area.objects.filter(kind_of_content="Post").update(kind_of_content="post")
    web.Area.objects.filter(kind_of_content="Link").update(kind_of_content="link")


def create_modules():
    modules = [
        {"slug": "posts", "name": "Posts"},
        {"slug": "links", "name": "Links"},
        {"slug": "polls", "name": "Polls"},
        {"slug": "pgj-actions", "name": "PGJ Actions"},
    ]

    for module in modules:
        qs = web.Module.objects.filter(slug=module["slug"])
        if not qs.exists():
            web.Module.objects.create(**module)


def fix_wrong_enabled_modules():
    for area in web.Area.objects.filter(active=True, parent__isnull=False):
        area.modules.clear()
        print(
            area.name,
            "\n\tEnabled modules =>",
            area.modules.all().values_list("slug", flat=True),
        )


def enable_default_modules_on_sites():
    sites = get_sites()
    modules = get_default_modules()
    for site in sites:
        for module in modules:
            if not site.modules.filter(slug=module.slug).exists():
                site.modules.add(module)


def print_sites_and_enabled_modules():
    sites = get_sites()
    for site in sites:
        print(
            site.name,
            "\n\tEnabled modules =>",
            site.modules.all().values_list("slug", flat=True),
            "\n",
        )


def main():
    create_modules()
    fix_kind_of_contents()
    enable_default_modules_on_sites()
    print_sites_and_enabled_modules()


if __name__ == "__main__":
    main()
