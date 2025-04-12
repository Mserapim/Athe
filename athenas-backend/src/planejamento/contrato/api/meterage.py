# -*- coding: utf-8 -*-
from django.db.models import Q, Sum
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, DateUtils
from contrib.middleware import get_current_user
from planejamento.contrato.models import Medicao as Meterage, AgreementSupervisor
from rh.models import Servidor
from django.template import loader
import locale
import json

log = getLogger(__name__)


class PHAMeterage(RestfulDRY):

    _model = Meterage

    full_text_index = ("nota_empenho__numero_ne__icontains",)

    # Gera o despacho no formato texto para ser colado no SEI
    def dispatch(self, pks):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        meterages = self._model.objects.filter(id__in=pks)

        obj.update(success=True, message=self.render_meterages(meterages))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def render_meterages(self, meterages):
        tpl = loader.get_template("meterage/meterage.html")
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        return tpl.render(
            {
                "meterages": meterages,
                "meterage": {
                    "processo": meterages.last().contrato.numero_processo,
                    "contrato": meterages.last().contrato.numero,
                    "quantidade": meterages.count(),
                    "total": meterages.aggregate(valor=Sum("valor"))["valor"],
                },
            }
        )

    # Registra a ordem bancária de uma solicitação de pagamento
    def pay(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            m = Meterage.objects.get(pk=self.request.POST.get("pk"))
            if m.ordem_bancaria:
                obj.update(
                    message="Já há uma ordem bancária cadastrada. Para alterar, reverta o pagamento"
                )
            else:
                m.ordem_bancaria = self.request.POST.get("ordem_bancaria")
                m.data_pagamento = DateUtils.str_to_date(
                    self.request.POST.get("data_pagamento")
                )
                m._action = "pay"
                m.save()
                obj.update(success=True, message="Pagamento realizada com sucesso.")
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    # # Apagar a ordem bancária de uma solicitação de pagamento
    def unpay(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        try:
            m = Meterage.objects.get(pk=self.request.POST.get("pk"))
            m._action = "unpay"
            if not m.ordem_bancaria:
                obj.update(
                    message="Não há uma ordem bancária cadastrada. Para alterar, reverta o pagamento"
                )
            else:
                m.save()
                obj.update(success=True, message="Pagamento desfeito com sucesso.")
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_logged_employee_id(self, *args):
        obj = {}
        contrato = self.request.POST.get("contrato")
        user = get_current_user()
        try:
            supervisor = AgreementSupervisor.objects.get(
                Q(agreement=contrato) & Q(employee__user=user) & Q(end=None)
            )
            if supervisor:
                obj["logged_employee_id"] = supervisor.employee.id
            else:
                obj["logged_employee_id"] = 0
        except AgreementSupervisor.DoesNotExist:
            obj["logged_employee_id"] = 0

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        if instance.modified_by:
            self.responsavel = instance.modified_by
        else:
            self.responsavel = instance.created_by

        servidor = Servidor.objects.get(user=self.responsavel)

        if instance.inicio_periodo_referencia and instance.fim_periodo_referencia:
            periodo = (
                instance.inicio_periodo_referencia.strftime("%d/%m/%Y")
                + " até "
                + instance.fim_periodo_referencia.strftime("%d/%m/%Y")
            )

        rst.update(
            icons=instance.get_state(),
            user_display=servidor.pessoa_fisica.nome,
            nota_empenho_display=instance.nota_empenho.numero_ne,
            periodo_display=periodo,
        )

        return rst
