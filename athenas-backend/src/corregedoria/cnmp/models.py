# -*- coding:utf-8 -*-
from datetime import datetime
import json
from django.db import models
from standard.models import AuditTimestampModel, Choice
from contrib.utils import getLogger
from corregedoria.cnmp.workflow import ExportDataEmployee
from rh.models import Servidor

log = getLogger(__name__)


class Communication(models.Model):
    employee = models.ForeignKey(Servidor, related_name="+", on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(default=1)
    message = models.TextField(blank=True)
    content = models.TextField(blank=True)
    send_at = models.DateTimeField(blank=True, null=True)
    finalized = models.BooleanField(default=False)

    class Meta:
        ordering = ["employee"]
        verbose_name = "Tabela de Controle de envio"
        permissions = (("is_administrator", "Administrador"),)

    def get_status(self):
        """
        pendding: Pendente de envio.
        success: Enviado com sucesso, sem retorno de error ou warning. Dados gravados no destino.
        warning: Enviado com sucesso, retornando warning. Parte dos dados são gravados no destino.
        error: Enviado com sucesso, retornando error. Dados não são gravados no destino.
        fail: Não enviado ou Enviado mas sem resposta.
        """
        return {1: "pendding", 2: "success", 3: "warning", 4: "error", 5: "fail"}.get(
            self.status
        )

    def rendered(self):
        return self.message

    @property
    def icon_status(self):

        return {
            1: {
                "iconCls": "icon-crgmpe icon-crgmpe-waiting",
                "title": "Aguardando envio..",
            },
            2: {
                "iconCls": "icon-crgmpe icon-crgmpe-confirmed",
                "title": "Enviado com sucesso",
            },
            3: {
                "iconCls": "icon-crgmpe icon-crgmpe-warn",
                "title": "Informações enviadas apresentam pendência",
            },
            4: {
                "iconCls": "icon-crgmpe icon-crgmpe-exclamation-red",
                "title": "Informações enviadas apresentam erros",
            },
            5: {
                "iconCls": "icon-crgmpe icon-crgmpe-exclamation-black",
                "title": "Falha ao enviar",
            },
        }.get(self.status)

    @property
    def icons(self):

        return [self.icon_status]

    def load_data(self):
        self.content = ""

    def send(self):
        resp = None
        if self.finalized:
            raise Exception(
                "Comunicacao encontra-se finalizada. Crie outra Comunicacao."
            )
        else:
            try:
                resp = ExportDataEmployee.run(self.employee.pk, production=True)

                if resp is None:
                    self.status = 5
                    self.message = "Sem retorno"
                else:
                    self.message = str(resp)

                    if resp[0].get("erros") or resp[0].get("impedimentos"):
                        self.status = 4
                    elif resp[0].get("informativos"):
                        self.status = 3
                    else:
                        self.status = 2

            except Exception as e:
                self.status = 5
                self.message = str(e)
                raise e
            finally:
                self.send_at = datetime.now()
                self.save()

    def validate_employee(self):
        if getattr(self.employee, "tipo", None) != "M":
            raise Exception("Servidor indicado não é Membro.")

    @classmethod
    def bulk_generate(cls):
        info = []
        for employee in Servidor.objects.filter(tipo="M", ativo=True):
            try:
                cls.generate(employee)
            except Exception as e:
                log.info(str(e))
                info.append(str(e))

        return info

    @classmethod
    def generate(cls, employee=None):
        try:
            cls(employee=employee).save()
        except Exception as e:
            raise e

    def save(self, *args, **kwargs):
        skip = False

        self.validate_employee()

        if self.pk is None:
            if self.__class__.objects.filter(
                employee=self.employee, status__in=[1, 3, 4, 5]
            ).exists():
                skip = True
        else:
            old = self.__class__.objects.get(pk=self.pk)
            if old.employee.pk != self.employee.pk:
                raise Exception("Operacao não permitida.")

            self.finalized = True if self.status == 2 else False

        if not skip:
            super(Communication, self).save(*args, **kwargs)
        else:
            raise Exception(
                "Os dados de {} ja encontra-se disponivel para analise e envio. ".format(
                    str(self.employee)
                )
            )
