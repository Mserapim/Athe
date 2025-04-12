#!/usr/bin/env python
# -*- coding:utf-8 -*-

from web.models import *
from django.contrib.auth.models import User


SITE_SLUG = "portal"
KIND_OF_CONTENT = "pgj-actions"
USERNAMES = ["williamgomes", "alaylaramos", "joseotsuka"]


def get_areas(site_slug, kind_of_content):
    return Area.objects.filter(
        active=True, parent__slug=site_slug, kind_of_content=kind_of_content
    )


def get_users(usernames):
    return User.objects.filter(username__in=usernames)


def relate_users(site_slug, kind_of_content, usernames):
    areas = get_areas(site_slug, kind_of_content)
    users = get_users(usernames)
    print("===Areas===\n%s\n===========\n" % areas)
    print("===Users===\n%s\n===========\n" % users)

    for area in areas:

        group = WebGroup.objects.filter(area__id=area.id)
        if not group.exists():
            group = WebGroup.objects.create(
                area=area,
                name="Administração %s" % area,
                can_add=True,
                can_change=True,
                can_delete=True,
                can_publish=True,
            )
        else:
            group = group[0]

        for user in users:
            # print(group)
            # print dir(group)
            if not group.users.filter(id=user.id).exists():
                print("Relating %s to %s" % (user, area))
                group.users.add(user)
            else:
                print("%s already related with %s" % (user, area))
        print("")


def main(site_slug=SITE_SLUG, kind_of_content=KIND_OF_CONTENT, usernames=USERNAMES):
    relate_users(site_slug, kind_of_content, usernames)


if __name__ == "__main__":
    main()
