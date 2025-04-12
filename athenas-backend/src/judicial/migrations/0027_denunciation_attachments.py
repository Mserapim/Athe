# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models
from judicial.models import AssessmentNoticeOffice, Denunciation, Attached
from contrib.middleware import set_current_user


def up_fn(*args, **kwargs):
    print(" ", end="")

    for Entity in [Denunciation, AssessmentNoticeOffice]:
        print(
            " (%d) "
            % Entity.objects.filter(lawsuit__origin__attachments__isnull=False).count(),
            end="",
        )
        sys.stdout.flush()

        for entity in Entity.objects.filter(lawsuit__origin__attachments__isnull=False):
            query = entity.lawsuit.origin.attachments.exclude(
                attach__in=entity.attaches.filter().values("file_descriptor")
            )

            print(" [%d] " % query.count(), end="")
            sys.stdout.flush()

            for attach in query:
                a = Attached(
                    attached_document=entity,
                    title=attach.title[:100],
                    file_descriptor=attach.attach,
                )
                a.skip_read_only_validate = True
                a.save()
                a.process_renderer_pages()

                print(".", end="")
                sys.stdout.flush()

                a.save()

    print(" ", end="")
    sys.stdout.flush()


def down_fn(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0026_normalize_ordinacereformulated_post_sign"),
    ]

    operations = [migrations.RunPython(up_fn, down_fn)]
