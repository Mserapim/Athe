#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys, codecs  # , shutil
from django.db import transaction
from django.contrib.auth.models import User
from django.core.files.base import File as UploadFile
from django.template.defaultfilters import addslashes, slugify
from web.models import Post, Link, File

SITE = "transparencia"
FILES_ROOT = "/media/storage/tests/python/export"
USER_SELECTOR = dict(username="tonyreis")
ROOT_LINK_SELECTOR = dict(
    areas__parent__slug=SITE, areas__slug="menu-esquerdo", title="Recursos Humanos"
)


def _whitespacefy(string):
    return string.replace("_", " ").replace("-", " ")


def normalize_folder_names(basedir):
    for item in os.listdir(basedir):
        path = os.path.join(basedir, item)
        if os.path.isdir(path):
            new_path = os.path.join(basedir, slugify(item))
            os.rename(path, new_path)
            normalize_folder_names(new_path)


# @transaction.commit_on_success
def create_file(title, upfile, post):

    new_file = File(title=addslashes(title), credits="Web Exporter")
    new_file.save_file(upfile, User.objects.get(**USER_SELECTOR))
    new_file.publish()
    new_file.save()
    new_file.posts.add(post)
    post.check_attachments()
    post.save()

    return new_file


def redo_files(post):

    basedir = os.path.join(
        FILES_ROOT, "/".join([slugify(piece) for piece in post.title.split(" - ")])
    )
    print(basedir, os.path.exists(basedir))
    if os.path.exists(basedir):
        for item in os.listdir(basedir):
            path = os.path.join(basedir, item)
            filename, ext = os.path.splitext(path)

            if ext == ".fnd":
                title = open("%s.fnd" % filename).read().decode("latin-1").split("#")[0]
                upfile = UploadFile(open("%s.pdf" % filename))
                upfile.content_type = "application/pdf"
                _file = create_file(_whitespacefy(title.strip()), upfile, post)
                print(_file.slug)


def search_posts(link):
    for l in link.children.filter(active=True):
        print("checking link: %s" % l.title)
        if l.kind == 3:
            print("is to page")
            post = Post.objects.filter(slug=l.url_embed, active=True)
            if post.exists():
                post = post[0]
                for f in post.files.all():
                    f.posts.clear()
                    f.delete()
                redo_files(post)
        search_posts(l)


def main():
    print("redoing attachments...")
    normalize_folder_names(os.path.join(FILES_ROOT, "relatorios"))
    search_posts(Link.objects.get(**ROOT_LINK_SELECTOR))
    print("\nredo attachments finished.")


if __name__ == "__main__":
    sys.exit(main())
