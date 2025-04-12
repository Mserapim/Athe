# -*- coding: utf-8 -*-
from django.db.models import Q

from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.nil import nil_display
from contrib.utils import getLogger
from planejamento.contrato.models import Contrato as Agreement, MinuteSolicitation
from standard.models import Choice

log = getLogger(__name__)


class PHAAgreement(RestfulDRY):

    _model = Agreement

    full_text_index = (
        "numero__icontains",
        "numero_processo__icontains",
        "agreementsupervisors__employee__pessoa_fisica__nome__icontains",
        "agreementsupervisors__employee__user__username__icontains",
        "objeto_contrato__icontains",
        "numero_processo_mae__icontains",
        "pessoa__nome__icontains",
        "pessoa__pessoajuridica__razao_social__icontains",
        "pessoa__pessoajuridica__cnpj__icontains",
        "pessoa__pessoafisica__social_name__icontains",
    )

    force_upper = False

    def generate_from_solicitations(self, *args):
        obj = {"success": True, "message": "Nada feito ainda."}

        try:
            solicitations = MinuteSolicitation.objects.filter(
                pk__in=self.request.POST.getlist("solicitation_set")
            )

            minute = solicitations.first().minute

            parameter_number = self.request.POST.get("numero_contrato")
            parameter_start_date = self.request.POST.get("data_inicio")
            parameter_end_date = self.request.POST.get("data_fim")
            copy_supervisor = self.request.POST.get("copiar_fiscais", "off") == "on"
            agreement_type = self.request.POST.get("tipo_contrato")

            inst = self._model.create_from_minute(
                minute,
                solicitations,
                parameter_number,
                parameter_start_date,
                parameter_end_date,
                copy_supervisor,
                agreement_type,
            )
        except Exception as e:
            obj.update(success=False, message=str(e))
        else:
            obj.update(
                instance=self.model_to_dict(inst),
                message="Contrato gerado com sucesso.",
            )
        self.renderer(obj)

    def get_query(self):
        query = super(PHAAgreement, self).get_query().distinct()
        query = query.order_by("data_vencimento_flag")

        user = get_current_user()

        group_views = {
            1: "hiring-agreement-supervisor",
            2: "hiring-agreement-view-all",
            3: "hiring-agreement-manager",
            5: "hiring-agreement-financial",
        }

        # Se for gestor geral ou financeiro, visualiza todos
        if user.groups.filter(
            Q(name=group_views.get(2))
            | Q(name=group_views.get(3))
            | Q(name=group_views.get(5))
        ).exists():
            query = query.filter()

        # Se for fiscal, visualiza os que ele é gestor ou responsável
        elif user.groups.filter(name=group_views.get(1)).exists():
            subordinates = user.servidor.subordinados.filter()
            query = query.filter(
                Q(agreementsupervisors__employee__user=user)
                | Q(agreementsupervisors__employee__in=subordinates),
                Q(agreementsupervisors__end=None),
            )

        # Se for de tipo algum, não recebe nada
        else:
            query = query.none()

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("planning.hiring.agreement.Manage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            tipo_contrato_display=nil_display(instance, "tipo_contrato", None),
            valor=str(instance._valor_contrato),
            main_agreementsupervisors=instance.main_agreementsupervisors_list(),
        )

        return rst

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem informações", "appends": []},
        }

        try:
            query = self.get_query().filter(pk=args[0]).distinct()
            agree = query.last()
            # agree = (self.get_query().get(pk=args[0]))

            rst.update(
                success=True, document={"content": agree.rendered, "appends": []}
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def tipo_ordem_contrato(self, *args):
        result = {
            "success": False,
            "message": "Nothing done yet.",
            "count": 0,
            "collection": [],
        }

        try:
            agreement = self.get_query().get(pk=self.request.REQUEST.get("pk", 0))
        except self.Model.DoesNotExist:
            try:
                values = [
                    {"label": choice[1], "value": choice[0]}
                    for choice in Choice.get_choices_for(
                        "contrato", "TIPO_ORDEM_CONTRATO", query_dict={"active": True}
                    )
                ]
            except Exception as e:
                result.update(message=str(e))
            else:
                result = {
                    "success": True,
                    "message": "Retornando todos os choices para contrato.TIPO_ORDEM_CONTRATO",
                    "count": len(values),
                    "collection": values,
                }
        else:
            try:
                result = {
                    "success": True,
                    "message": "Retornando apenas o campo 'ordem' de todos os valores de contrato.",
                    "count": agreement.valores_contrato.count(),
                    "collection": [
                        {"label": value.get_ordem_display(), "value": value.ordem}
                        for value in agreement.valores_contrato.all()
                    ],
                }
            except Exception as e:
                result.update(message=str(e))

        self.renderer(result)


class PHAContractOutsourcedRestful(PHAAgreement):

    _model = Agreement

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("planning.agreement.outsourced.ContractOutsourcedManage")'
        )
