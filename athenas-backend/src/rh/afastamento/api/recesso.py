# -*- coding: utf-8 -*-


import csv
import json
import os
from collections import namedtuple
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from functools import partial

from engine.mq.models import Task
from ged.models import Arquivo as File
from rh.afastamento.api.baselicencaafastamento import AFABaseLicencaAfastamentoRestful
from rh.afastamento.models import Recesso
from rh.task.afastamento.recess_batch import create_batch_recess_task

log = getLogger(__name__)


class AFARecessoRestful(AFABaseLicencaAfastamentoRestful):

    full_text_index = () + AFABaseLicencaAfastamentoRestful.full_text_index

    exclude_fields = [] + AFABaseLicencaAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFABaseLicencaAfastamentoRestful.force_persist_boolean_fields
    )

    _model = Recesso

    def create_batch_recess(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda!"}

        start_date = self.request.POST.get("start_date")
        end_date = self.request.POST.get("end_date")
        employee_type = self.request.POST.get("employee_type")

        try:
            file_csv = File.objects.get(pk=self.request.POST.get("registry_file"))
        except File.DoesNotExist:
            obj.update(message="Arquivo não encontrado!")
        else:
            filename, file_extension = os.path.splitext(file_csv.filename)
            if file_extension == ".csv":
                exclude_registry = []
                insert_registry = {}
                with transaction.atomic():
                    try:
                        with open(file_csv.absolute_path, "r") as csv_file:
                            f_csv = csv.reader(csv_file, delimiter=";")
                            headings = next(f_csv)
                            Row = namedtuple("Row", headings)
                            for r in f_csv:
                                row = Row(*r)
                                if row.datainicio != "" and row.datafim != "":
                                    period = [row.datainicio, row.datafim]

                                    if row.matricula not in list(
                                        insert_registry.keys()
                                    ):
                                        insert_registry[row.matricula] = []
                                        insert_registry[row.matricula] = [period]
                                    else:
                                        insert_registry[row.matricula].append(period)

                                else:
                                    exclude_registry.append(int(row.matricula))
                    except Exception as e:
                        obj.update(message="{}".format(e))
                    else:
                        Task.start(
                            create_batch_recess_task,
                            start_date=start_date,
                            end_date=end_date,
                            employee_type=employee_type,
                            insert_registry=insert_registry,
                            exclude_registry=exclude_registry,
                            user=get_current_user().pk,
                            success="""<p>Arquivo de resumo foi gerado com sucesso.
                            Para fazer o download clique no <a href="/athenas/AFARecessoRestful/download_file/?uuid=%(uuid)s">link</a>.
                            </p>
                            <p>Este arquivo está disponível para download até dia <span style="font-weight:bold">%(deadline)s</span></p>""",
                        )
                        obj.update(
                            success=True,
                            message="A criação de recessos foi iniciada...",
                        )
            else:
                obj.update(message="O arquivo não possui extensão CSV.")

        self.renderer(obj)

    def download_file(self, args=[]):
        cache_path = os.path.join(settings.CACHE_PATH, "afastamento")

        try:
            task = Task.objects.get(
                uuid=self.request.GET.get("uuid"), owner=self.request.user
            )
            if task.state == "ready":
                data = json.loads(task.data)
                filename = data.get("filename")

                self.response["Content-Type"] = "application/pdf"
                self.response["Content-Disposition"] = (
                    'attachment; filename="%s"' % filename
                )
                with open(os.path.join(cache_path, filename), "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)

                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo do resumo dos recessos criados não está pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo do resumo dos recessos criados para o usuário logado.</h1>"
            )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.recesso.Manage")')
