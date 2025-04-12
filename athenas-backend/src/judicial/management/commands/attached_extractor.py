# -*- coding: utf-8 -*-
import sys
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q
from optparse import make_option
from judicial.models import Attached
from subprocess import call


class Command(BaseCommand):

    _model = Attached

    @property
    def Model(self):
        return self._model

    def add_arguments(self, parser):
        parser.add_argument("pkset", help="Id or file hash of Attached", nargs="*")
        parser.add_argument(
            "--search-not-extracted",
            help="Search for not extracted files and proccess this.",
            action="store_true",
        )
        parser.add_argument(
            "--recovery",
            help="Run recovery with pdftocairo for fix pdf currupted.",
            action="store_true",
        )
        parser.add_argument("--dry-run", help="Simulate only.", action="store_true")

    def is_empty(self, path):
        return not os.path.exists(path) or not os.listdir(path)

    def handle(
        self,
        pkset=[],
        recovery=False,
        search_not_extracted=False,
        dry_run=False,
        *args,
        **kwargs
    ):
        query = self.Model.objects.none()

        if not search_not_extracted:
            query = self.Model.objects.filter(file_descriptor__file__in=pkset)
        else:
            cachedir = os.path.join(getattr(settings, "CACHE_BASE", ""), "ejud")

            pdf_mimes = (
                "application/pdf",
                "application/force-download",
                "application/octet-stream",
                "adobe/pdf",
                "adobe/force-download",
                "adobe/octet-stream",
            )

            query = self.Model.objects.filter(
                pk__in=[
                    a.pk
                    for a in self.Model.objects.filter(
                        file_descriptor__mimetype__in=pdf_mimes
                    )
                    if self.is_empty(os.path.join(cachedir, a.file_descriptor.file))
                ]
            )

        print("Foram encontrados %d itens" % query.count())
        message = ""
        count = 0
        total = query.count()

        if recovery:
            for attached in query:
                self.recovery(attached)

        for attached in query:
            count += 1
            print("\b" * len(message), end="")
            message = "Processando %d de %d {%s}" % (
                count,
                total,
                attached.file_descriptor.file,
            )
            print(message, end="")
            sys.stdout.flush()

            if not dry_run:
                try:
                    attached.process_renderer_pages()
                except Exception as e:
                    pass

        print("")

    def recovery(self, attached):
        src = attached.file_descriptor.absolute_path
        dst = "%s.recovered" % src

        cmd = ["/usr/bin/pdftocairo", "-pdf", src, dst]

        print(" · recuperando %s para %s ... " % (src, dst), end="")
        if not os.path.exists(dst):
            call(cmd, shell=False)
            print("pronto")
        else:
            print("ignorado")
