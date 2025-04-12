#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys, codecs
from django.db import transaction
from django.contrib.auth.models import User
from django.core.files.base import File as UploadFile
from django.template.defaultfilters import addslashes, slugify
from web.models import Post, Link, File, Area, ContentArea

SITE = "transparencia-test"
FILES_ROOT = "/media/storage/tests/python/export/files"
USER_SELECTOR = dict(username="tonyreis")
PAGES_AREA_SELECTOR = dict(parent__slug=SITE, slug="paginas")
MENU_AREA_SELECTOR = dict(parent__slug=SITE, slug="menu-esquerdo")
ROOT_LINK_SELECTOR = dict(
    areas__parent__slug="transparencia-test",
    areas__slug="menu-esquerdo",
    slug__icontains="relatorios",
)


def path_walker(basedir, parent=None, post=None):

    for item in os.listdir(basedir):
        path = os.path.join(basedir, item)
        if os.path.isdir(path):
            link = create_link(_whitespacefy(item.strip()), 0, "#", parent)
            if has_file(path):
                post = create_post(link.fullname.replace("/", "-"))
                link.url_embed = addslashes(post.slug)
                link.kind = 3
                link.save()
                path_walker(path, link, post)
            else:
                path_walker(path, link)
        else:
            if os.path.splitext(item)[1] == ".pdf":
                title = (
                    open("%s.fnd" % os.path.splitext(path)[0])
                    .read()
                    .decode("latin-1")
                    .split("#")[0]
                )
                upfile = UploadFile(open(path))
                upfile.content_type = "application/pdf"
                _file = create_file(_whitespacefy(title.strip()), upfile, post)
                print("%s - %s" % (parent.fullname, title))


def _whitespacefy(string):
    return string.replace("_", " ").replace("-", " ")


def has_file(path):
    for item in os.listdir(path):
        if os.path.isfile(os.path.join(path, item)):
            return True
    return False


def create_link(title, kind, url, parent=None):
    l = Link(title=addslashes(title.decode("u8")), kind=kind, url_embed=addslashes(url))
    if parent:
        l.parent = parent
    l.publish()
    l.save()

    if not l.areas.filter(**MENU_AREA_SELECTOR).exists():
        ContentArea(
            area=Area.objects.get(**MENU_AREA_SELECTOR), content=l.content_ptr
        ).save()

    return l


def create_post(title):
    p = Post(title=addslashes(title), as_link=True, credits="Web Exporter")
    p.publish()
    p.save()

    if not p.areas.filter(**PAGES_AREA_SELECTOR).exists():
        ContentArea(
            area=Area.objects.get(**PAGES_AREA_SELECTOR), content=p.content_ptr
        ).save()

    return p


def create_file(title, upfile, post):
    f = File(title=addslashes(title), credits="Web Exporter")
    f.save_file(upfile, User.objects.get(**USER_SELECTOR))
    f.publish()
    f.save()
    f.posts.add(post)
    post.check_attachments()
    post.save()

    return f


def main():
    print("starting export...")
    path_walker(FILES_ROOT, Link.objects.get(**ROOT_LINK_SELECTOR))
    print("\nexport finished.")


if __name__ == "__main__":
    sys.exit(main())
