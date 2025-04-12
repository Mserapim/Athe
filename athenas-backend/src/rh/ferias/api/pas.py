# -*- coding: utf-8 -*-

import json

from contrib.controller import DefaultController
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, DateUtils
from contrib.decorator import login_required
from engine.mq.models import Task
from rh.ferias.models import PeriodoAquisitivo, PeriodoAquisitivoServidor

from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.conf import settings
from datetime import datetime
from functools import partial

import os


log = getLogger(__name__)


class FRSIndemnify(DefaultController):

    def indemnify_vacation(self, args=[]):
        obj = {"success": False}
        pas = PeriodoAquisitivoServidor.objects.get(pk=int(self.request.POST["pas"]))
        quantity = int(self.request.POST["quantity"])
        pas_recent = PeriodoAquisitivoServidor.objects.filter(
            servidor=pas.servidor, data_inicio_aquisicao__gt=pas.data_inicio_aquisicao
        )
        pas_old_with_days = PeriodoAquisitivoServidor.objects.filter(
            servidor=pas.servidor,
            data_inicio_aquisicao__lt=pas.data_inicio_aquisicao,
            estado=2,
        ).exclude(pk=pas.pk)
        is_old = True
        for p in pas_old_with_days:
            if p.dias_usufruidos + p.paid_days < p.quantidade_dias:
                is_old = False
                break

        if not pas_recent:
            obj.update(message="Não é possível indenizar o periodo atual.")
        elif pas.dias_agendados:
            obj.update(
                message="Os dias agendados devem ser cancelados antes do período ser indenizado."
            )
        elif not is_old:
            obj.update(
                message="Existem periodo(s) mais antigos que podem ser indenizados."
            )
        elif quantity > (pas.quantidade_dias - pas.dias_usufruidos - pas.paid_days):
            obj.update(
                message="Período selecionado não possui a quantidade disponível de dias solicitada para indenizar."
            )
        else:
            pas.paid_days = pas.paid_days + quantity
            try:
                pas.save()
                obj = {"success": True, "message": "Periodo indenizado com sucesso!"}
                if pas.paid_days + pas.dias_usufruidos == pas.quantidade_dias:
                    pas._indenizar()
            except Exception as e:
                log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))


class FRSEmployeeAcquisitionPeriod(RestfulDRY):

    _model = PeriodoAquisitivoServidor

    full_text_index = (
        "servidor__matricula__icontains",
        "servidor__pessoa_fisica__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.ferias.pas.EmployeeAcquisitionPeriodManage")'
        )

    @login_required("JSON")
    def create_automatic_book_vacation(self, args=[]):
        response = {"success": False, "message": "Nada foi feito ainda."}
        self._read_special_verb()
        try:
            pa = self.request.PUT.get("pa")
            self._model.create_automatic_book_vacation(pa=pa)
        except Exception as err:
            log.exception(err)
            response.update(message="%s" % err.args[0])
        else:
            response.update(
                success=True,
                message="Pedido de Marcação realizado com sucesso. Você será informado quando o processo finalizar.",
            )
        self.response["content-type"] = "text/javascript"
        self.renderer(response)

    @login_required(type="JSON")
    def file(self, args=[]):
        try:
            task = Task.objects.get(
                uuid=self.request.REQUEST.get("uuid"), owner=self.request.user
            )

            if task.state == "ready":
                filename = "%s/marcacao-%s.csv" % (settings.CACHE_PATH, task.uuid)
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.response["Content-Type"] = "application/pdf"
                self.response["Content-Disposition"] = (
                    'attachment; filename="marcacao-relatorio-%s.csv"' % now
                )
                with open(os.path.join(filename), "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)
                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo não está pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo para o usuário logado.</h1>"
            )

    def model_to_dict(self, instance):
        dict = super(FRSEmployeeAcquisitionPeriod, self).model_to_dict(instance)
        dict.update(
            {
                "status": instance.status,
                "dias_marcados": instance.dias_marcados,
                "dias_agendados": instance.dias_agendados,
                "dias_usufruidos": instance.dias_usufruidos,
                "dias_ausufruir": instance.dias_ausufruir,
                "dias_nao_marcados": instance.dias_nao_marcados,
                "usufruto_ini": "%s"
                % DateUtils.date_to_str(instance.data_inicio_usufruto),
                "usufruto_fim": (
                    "%s" % DateUtils.date_to_str(instance.data_fim_usufruto)
                    if instance.data_fim_usufruto
                    else "---"
                ),
                "situacao": "%s" % instance.situacao,
            }
        )
        return dict


class FRSEmployeeAcquisitionPeriodSpecialized(FRSEmployeeAcquisitionPeriod):

    def model_to_dict(self, instance):
        dict = super(FRSEmployeeAcquisitionPeriodSpecialized, self).model_to_dict(
            instance
        )
        dict.update(
            {
                "periodo_aquisitivo": "%s" % instance.periodo_aquisitivo,
                "servidor": "%s" % instance.servidor,
                "data_referencia": DateUtils.date_to_str(instance.data_referencia),
            }
        )
        return dict


class FRSAcquisitionPeriod(RestfulDRY):

    _model = PeriodoAquisitivo

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.pas.AcquisitionPeriodManage")')

    def period_display(self, instance):
        if instance.configuracao.modo == "CONTINUO":
            return "%d / %d" % (instance.ano_aquisicao - 1, instance.ano_aquisicao)
        else:
            ano_aquisicao = instance.ano_aquisicao
            periodo = instance.periodo_display()
            if instance.mes_fruicao != 14:
                periodo = instance.get_mes_fruicao_display()
            return "%s - %s" % (ano_aquisicao, periodo)

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)
        rst.update(period_display=self.period_display(instance))
        return rst

    @login_required(type="JSON")
    def file(self, args=[]):
        try:
            task = Task.objects.get(
                uuid=self.request.REQUEST.get("uuid"), owner=self.request.user
            )

            if task.state == "ready":
                filename = "%s/homologacao-%s.csv" % (settings.CACHE_PATH, task.uuid)
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.response["Content-Type"] = "application/pdf"
                self.response["Content-Disposition"] = (
                    'attachment; filename="homologacao-relatorio-%s.csv"' % now
                )
                with open(os.path.join(filename), "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)
                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo não está pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo para o usuário logado.</h1>"
            )
