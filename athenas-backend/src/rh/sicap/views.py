# -*- coding: utf-8 -*-

import json
import os

from django.http import HttpResponseBadRequest, HttpResponseNotFound

from contrib.controller import DefaultController
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from rh.sicap.utils import SicapUtil
from rh.task.sicapap import sicap_generator
from functools import partial

log = getLogger(__name__)


class RHSicapApWindowGenerator(DefaultController):

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write("new toolkit.rh.sicap.WindowGenerator()")

    def renderer(self, data):
        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(data))

    @login_required(type="JSON")
    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            Task.start(
                sicap_generator,
                year=self.request.POST.get("year"),
                months=[int(self.request.POST.get("month"))],
                user=get_current_user().pk,
                success="""<p>Arquivo <span style="font-weight:bold">SICAP AP %(sicapap)s</span> foi gerado com sucesso.
                Para fazer o download clique no <a href="/athenas/RHSicapApWindowGenerator/file/?uuid=%(uuid)s">link</a>.
    </p>
    <p>Este arquivo está disponível para download até dia <span style="font-weight:bold">%(deadline)s</span></p>""",
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Arquivo do SICAP AP %s-%s requisitado com sucesso, você será avisado quando o mesmo for concluído."
                % (
                    SicapUtil._months_to_unicode(
                        [int(self.request.POST.get("month", []))]
                    ),
                    self.request.POST.get("year"),
                ),
            )
        self.renderer(rst)

    def file(self, args=[]):
        cache_path = SicapUtil.directory_tmp()
        try:
            task = Task.objects.get(
                uuid=self.request.GET.get("uuid"), owner=self.request.user
            )

            if task.state == "ready":
                data = json.loads(task.data)
                filename = data.get("filename")

                self.response["Content-Type"] = "application/zip"
                self.response["Content-Disposition"] = (
                    'attachment; filename="%s"' % filename
                )
                with open(os.path.join(cache_path, filename), "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)

                # task.state = 'downloaded'
                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo do SICAP AP não está pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo do SICAP AP para o usuário logado.</h1>"
            )
