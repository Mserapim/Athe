# -*- coding: utf-8 -*-
from functools import partial
import json
import os
import pathlib

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponseServerError

from contrib.controller import DefaultController
from contrib.utils import getLogger
from edocs.protocolo.models import Protocolo as Protocol
from edocs.protocolo.task import flowchart
from engine.mq.models import Task


log = getLogger()


class EDOCFlowchart(DefaultController):

    def download(self, *args):
        try:
            cache_dir = getattr(settings, "CACHE", {}).get("flowchart", None)
            if not cache_dir:
                html = (
                    "<h1>Não foi possível recuperar o caminho do "
                    'diretório de cache para "flowchart"</h1>'
                )
                self.response = HttpResponseServerError(html)
                return

            try:
                task = Task.objects.get(
                    uuid=self.request.REQUEST.get("uuid"), owner=self.request.user
                )
            except Task.DoesNotExist:
                html = f"<h1>Não existe este pedido de fluxograma para o usuário logado</h1>"
                self.response = HttpResponseNotFound(html)
                return

            if task.state != "ready":
                html = (
                    f"<h1>O fluxograma ainda não está pronto, ou não foi "
                    "solicitado, ou não está mais disponível</h1>"
                )
                self.response = HttpResponseNotFound(html)
                return

            # Se este dict for atualizado, atualize também a lista
            # flowchart.supported_output_formats, e vice-versa.
            formats = {
                "svg": "image/svg+xml",
                "png": "image/png",
                "jpg": "image/jpeg",
                "pdf": "application/pdf",
            }

            mimetype = formats.get(
                self.request.REQUEST.get("output_format", "svg").lower(),
                "application/octstream",
            )
            filename = task.data
            abs_path = os.path.join(cache_dir, filename)
            self.response["Content-Type"] = mimetype
            self.response["Content-Disposition"] = f'attachment; filename="{filename}"'

            with open(abs_path, "rb") as fd:
                for chunk in iter(partial(fd.read, 8192), b""):
                    self.response.write(chunk)

            try:
                pathlib.Path(abs_path).unlink()
            except FileNotFoundError:
                pass  # Same behavior as the POSIX rm -f command.
            except Exception as e:
                log.exception(f'Erro ao excluir o arquivo "{abs_path}": {str(e)}')

            task.state = "downloaded"
            task.save()
        except Exception as e:
            msg = (
                f"<h1>Não foi possível preparar o arquivo para "
                "download devido a um erro interno</h1>"
            )
            log.exception(f"{msg}: {str(e)}")
            self.response = HttpResponseServerError(msg)

    def generate(self, *args):
        response = {"success": False, "message": "Nothing done yet."}

        try:
            protocol = self.request.REQUEST.get("protocol")
            if not protocol:
                raise Exception(f"Forneça um id de protocolo válido.")

            output_format = self.request.REQUEST.get("output_format")
            if output_format not in flowchart.supported_output_formats:
                raise Exception(
                    f"O formato de saída fornecido é inválido. Formatos "
                    f"válidos: {flowchart.supported_output_formats}"
                )

            try:
                protocol_obj = Protocol.objects.get(pk=protocol)
            except Protocol.DoesNotExist:
                msg = f"Não foi possível encontrar o protocolo de id {protocol}."
                raise ObjectDoesNotExist(msg)

            if not protocol_obj.can_read:
                raise Exception(
                    "Não foi possível concluir a operação pois o protocolo "
                    f"{protocol_obj.codigo} está classificado com nível de acesso."
                )

            log.info(f"{self.__class__}: Criando uma task para gerar o fluxograma.")

            Task.start(
                flowchart.generate,
                protocol=protocol,
                output_format=output_format.lower(),
            )
        except Exception as e:
            log.exception(str(e))
            response.update(message=str(e))
        else:
            response.update(
                {
                    "success": True,
                    "message": (
                        "O fluxograma foi requisitado com sucesso. Você "
                        "será notificado quando tudo estiver pronto."
                    ),
                }
            )

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(response))
