# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import json
from django.db.models import Count
from django.db.models import Q
from contrib.controller import JsonResponseController

from contrib.newrest import RestfulDRY
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger, get_json_engine, DateUtils
from reports.data.mpmt.pvf.approversvdf import get_approver_vdf
from rh.models import (
    CargaHoraria,
    Servidor,
    MovimentacaoPosse,
    MovimentacaoTeletrabalho,
)
from rh.pvf.models import PortalRequest
from rh.registerpoint.const import TIPO_JUSTIFICATIVA_MAP
from standard.models import Choice, JustificationItem
from contrib.nil import nil_datetime, nil_pk, nil_unicode
from rh.registerpoint.models import MarkPoint


log = getLogger(__name__)
json_engine = get_json_engine()


class RHGestorBatidas(RestfulDRY):

    _model = MarkPoint

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gestorbatida.Manage")')

    def get_tipo_justificativa(self, args=[]):
        servidor = Servidor.objects.get(matricula=args[0])
        posse = servidor.type_by_possession

        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            justification_items = JustificationItem.objects.filter(
                type_by_possession__contains=posse
            )

            choices_list = [
                {"pk": int(item.value), "description": item.name}
                for item in justification_items
            ]

            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(choices_list),
                collection=choices_list,
            )

        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def model_to_dict(self, instance):
        tipo_justificativa_configs = JustificationItem.get_config_for(
            "folha_ponto_justificativas"
        )
        choices_dict = {item[0]: item[1] for item in tipo_justificativa_configs}

        tipo_justificativa_label = None
        tipo_justificativa = None

        if instance.tipo_justificativa:
            tipo_justificativa = instance.tipo_justificativa
            tipo_justificativa_label = choices_dict.get(tipo_justificativa, None)
        elif instance.tipo_justificativa_origem:
            tipo_justificativa_convertido = TIPO_JUSTIFICATIVA_MAP.get(
                int(instance.tipo_justificativa_origem), None
            )
            tipo_justificativa_label = choices_dict.get(
                tipo_justificativa_convertido, None
            )
            tipo_justificativa = tipo_justificativa_convertido

        rst = {
            "date_time": instance.get_date,
            "employee_name": instance.get_name,
            "employee_register": instance.get_register,
            "employee_matricula": instance.get_matricula,
            "workplace": instance.get_workplace,
            "ip": instance.ip,
            "marcacao": (
                instance.marcacao.strftime("%d-%m-%Y %H:%M:%S")
                if instance.marcacao
                else None
            ),
            "marcacao_valida": instance.marcacao_valida,
            "tipo_justificativa": tipo_justificativa,
            "tipo_justificativa_label": tipo_justificativa_label,
            "justificativa": instance.justificativa,
            "tabela_import": instance.tabela_import,
            "codigo_import": instance.codigo_import,
            "id": instance.pk,
        }
        return rst

    def salvarbatida(self, request, *args, **kwargs):
        data = self.request.POST.dict()
        try:
            employee_id = data.get("employee")
            data_inicio = datetime.strptime(data.get("data_inicio"), "%Y-%m-%d").date()
            data_fim = (
                datetime.strptime(data.get("data_fim"), "%Y-%m-%d").date()
                if data.get("data_fim")
                else data_inicio
            )
            tipo_justificativa = data.get("tipo_justificativa")
            justificativa = data.get("justificativa")

            if MarkPoint.objects.filter(
                employee_id=employee_id,
                marcacao__date__range=(data_inicio, data_fim),
                marcacao_valida=True,
            ).exists():
                mensagem_erro = "Já existe batida de ponto para um ou mais dias no intervalo selecionado."
                self.response.write(
                    json.dumps({"success": False, "message": mensagem_erro})
                )
                return self.response

            data = data_inicio
            while data <= data_fim:
                if data.weekday() >= 5:
                    data += timedelta(days=1)
                    continue

                MarkPoint.objects.create(
                    employee_id=employee_id,
                    marcacao=data,
                    tipo_justificativa=tipo_justificativa,
                    justificativa=justificativa,
                    marcacao_valida=True,
                )

                data += timedelta(days=1)

            self.response.write(
                json.dumps(
                    {"success": True, "message": "Batidas de ponto salvas com sucesso."}
                )
            )
            return self.response

        except Exception as e:
            self.response.write(
                json.dumps(
                    {
                        "success": False,
                        "message": f"Erro ao salvar justificativa: {str(e)}",
                    }
                )
            )
            return self.response

    def invalidar_marcacoes(self, request, *args, **kwargs):
        ids = self.request.POST.getlist("ids")
        try:
            MarkPoint.objects.filter(pk__in=ids).update(marcacao_valida=False)
            self.response.write(
                json.dumps({"success": True, "message": "Item removido com sucesso."})
            )
        except MarkPoint.DoesNotExist:
            self.response.write(
                json.dumps({"success": False, "message": "Item não encontrado."})
            )
        except Exception as e:
            self.response.write(json.dumps({"success": False, "message": str(e)}))
            return self.response


class ServidorGestorBatida(RestfulDRY):

    _model = Servidor

    full_text_index = (
        "matricula__iexact",
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__cpf__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new rh.gestorbatida.servidor.Manage")

    def get_query(self):
        queryset = super(ServidorGestorBatida, self).get_query()

        current_user = employee_from_user(get_current_user())
        request = PortalRequest()

        if not current_user.user.groups.filter(
            name="mpmt-perfil-vdf-aprovador-servidores"
        ).exists():
            queryset = queryset.filter(
                Q(ativo=True),
                Q(
                    type_by_possession__in=[
                        "EFE",
                        "CMS",
                        "REQ",
                        "REX",
                        "ECM",
                        "RCM",
                        "RFC",
                        "EST",
                        "VOL",
                        "EXT",
                        "RES",
                        "EFC",
                    ]
                )
                & (
                    Q(chefe_imediato=current_user)
                    | Q(lotacoes__responsavel=current_user)
                    | Q(lotacoes__pai__responsavel=current_user)
                ),
            ).distinct()

            servidores_filtrados = [
                servidor.pk
                for servidor in queryset
                if get_approver_vdf(request, servidor)
                == current_user.pessoa_fisica.nome
            ]

            queryset = queryset.filter(pk__in=servidores_filtrados)
        return queryset

    def model_to_dict(self, instance):
        rst = super(ServidorGestorBatida, self).model_to_dict(instance)

        departures = instance.departures().first()
        effective, commission = self.get_effective_and_commission(instance)

        q_mov_posse = MovimentacaoPosse.objects.filter(servidor=instance)
        dt_posse = q_mov_posse.last().data_posse if q_mov_posse.exists() else None

        lotacao = instance.lotacoes.filter(ativo=True).first()
        if lotacao:
            nome_lotacao = lotacao.lotacao.nome
        else:
            nome_lotacao = "Sem lotação"

        carga_horaria = CargaHoraria.objects.filter(
            servidor=instance, active=True
        ).first()

        if carga_horaria:
            jornada_trabalho = str(carga_horaria.jornada_trabalho)
            duracao = carga_horaria.duration
            horas = duracao // 60
            duracao = f"{horas} horas"
        else:
            jornada_trabalho = "Não definida"
            duracao = 0

        rst.update(
            servidor_pk=instance.pk,
            ativo=instance.ativo,
            matricula=instance.matricula,
            pessoa_fisica_unicode=instance.pessoa_fisica.nome,
            type_by_possession_display=instance.get_type_by_possession_display(),
            departure_unicode=departures.__str_restful__() if departures else "",
            effective_unicode=str(effective),
            commission_unicode=str(commission),
            in_telework=(
                "SIM"
                if MovimentacaoTeletrabalho.objects.filter(
                    servidor=instance, ativo=True
                )
                else "NÃO"
            ),
            servidor_created_by_unicode=nil_unicode(instance.created_by, None),
            servidor_created_at=DateUtils.date_to_str(instance.created_at),
            servidor_modified_by_unicode=nil_unicode(instance.modified_by, None),
            servidor_modified_at=DateUtils.date_to_str(instance.modified_at),
            dt_posse=DateUtils.date_to_str(dt_posse) if dt_posse else "",
            lotacao=nome_lotacao,
            jornada_trabalho=jornada_trabalho,
            duracao=duracao,
        )

        return rst

    def get_effective_and_commission(self, instance):
        effective = ""
        commission = ""

        possessions = instance.posses_ativas
        if not instance.ativo:
            possessions = instance.posses

        effectives = possessions.filter(quadro__cargo__tipo_lei_cargo="EF")
        if effectives.exists():
            ef = effectives.latest("data_exercicio")
            effective = ef.quadro
        if instance.ativo or (not effective):
            commissions = possessions.filter(
                quadro__cargo__tipo_lei_cargo__in=("CM", "FC")
            )
            if commissions.exists():
                cm = commissions.latest("data_exercicio")
                commission = cm.quadro

        if not effective:
            effective = "Não encontrado"
        if not commission:
            commission = "Não encontrado"

        return effective, commission
