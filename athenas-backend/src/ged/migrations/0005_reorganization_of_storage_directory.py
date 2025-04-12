# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os
import shutil
import time

from django.db import migrations, models


def up_fn(apps, schema_editor):
    from ged.models import Arquivo as FileObject

    query = FileObject.objects.filter()
    # query = FileObject.objects.filter(pk__lt=1000)
    # query = FileObject.objects.order_by('-pk')[:1000]

    total = query.count()
    pos = 0
    message = ""
    t_start = time.time()
    for fobj in query:
        pos += 1
        t_end = time.time()
        t1 = t_end - t_start
        t2 = (t1 * (total - pos)) / pos

        sys.stdout.write("\b" * len(message))
        message = " %d de %d (decorrido %d s; estimado %d s)" % (pos, total, t1, t2)
        sys.stdout.write(message)
        sys.stdout.flush()

        if not os.path.exists(fobj.absolute_directory):
            os.makedirs(fobj.absolute_directory)

        if os.path.exists(fobj.older_absolute_path):
            shutil.move(fobj.older_absolute_path, fobj.absolute_path)

        if os.path.exists("%s.img-cache" % fobj.older_absolute_path):
            shutil.move(
                "%s.img-cache" % fobj.older_absolute_path,
                "%s.img-cache" % fobj.absolute_path,
            )

        if os.path.exists("%s.cache" % fobj.older_absolute_path):
            shutil.move(
                "%s.cache" % fobj.older_absolute_path, "%s.cache" % fobj.absolute_path
            )

        if os.path.exists("%s.recovered" % fobj.older_absolute_path):
            shutil.move(
                "%s.recovered" % fobj.older_absolute_path,
                "%s.recovered" % fobj.absolute_path,
            )

    sys.stdout.write(" ")
    sys.stdout.flush()


def down_fn(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("ged", "0004_auto_20180201_1933"),
    ]

    operations = [migrations.RunPython(up_fn, down_fn)]
