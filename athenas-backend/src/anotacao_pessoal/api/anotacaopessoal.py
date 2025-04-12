# -*- coding: utf-8 -*-
from django.db.models import Count

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, get_json_engine, DateUtils
from contrib.middleware import get_current_user
from django.contrib.auth.models import Permission, User
from anotacao_pessoal.models import AnotacaoPessoal
from rh.models import Servidor, MovimentacaoPosse, MovimentacaoTeletrabalho
from standard.models import Choice
from contrib.nil import nil_datetime, nil_pk, nil_unicode

log = getLogger(__name__)
json_engine = get_json_engine()


class AnotacaoPessoalCadRF(RestfulDRY):

    _model = AnotacaoPessoal

    force_upper = False

    full_text_index = (
        "documento_numero__icontains",
        "documento_ano__icontains",
    )

    def json(self, args=[]):
        q_choice_tipo_anotacao = (
            Choice.objects.values_list("value", "label")
            .filter(
                app_label="rh",
                name="TIPO_ANOTACAO",
            )
            .order_by("label")
        )
        tipos_anotacao = [
            {"id": x[0], "tipo_anotacao": x[1].title()} for x in q_choice_tipo_anotacao
        ]

        q_choice_tipo_doc = (
            Choice.objects.values_list("value", "label")
            .filter(
                app_label="rh",
                name="TIPO_DOCUMENTO",
            )
            .order_by("label")
        )
        tipos_doc = [{"id": x[0], "tipo_doc": x[1].title()} for x in q_choice_tipo_doc]

        params = {
            "tipos_documento": tipos_doc,
            "tipos_anotacao": tipos_anotacao,
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(
            f"Ext._create('anotacao_pessoal.anotacao.Manage', {params})"
        )

    def ocultar_anotacao(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        usuario = get_current_user()
        permissao = Permission.objects.get(
            pk=6184
        )  # Permissão para deletar Anotação Pessoal

        if usuario.groups.filter(permissions=permissao) or usuario.is_superuser:
            try:
                anotacao_pk = self.request.POST.get("anotacao_pk")

                anotacao = AnotacaoPessoal.objects.get(pk=anotacao_pk)
                anotacao.delete()

                obj["message"] = f"Anotação Pessoal Ocultada {anotacao_pk}"
            except:
                obj["success"] = False
                obj["message"] = "Erro ao tentar ocultar a Anotação Pessoal."
        else:
            obj["success"] = False
            obj["message"] = "Você não tem permissão para ocultar a Anotação Pessoal."

        self.response.write(json_engine.encode(obj))

    def model_to_dict(self, instance):
        rst = super(AnotacaoPessoalCadRF, self).model_to_dict(instance)

        dt_publicacao = ""
        if instance.publicacao and instance.publicacao.data_publicacao:
            dt_publicacao = DateUtils.date_to_str(instance.publicacao.data_publicacao)

        data_publicacao_exp = ""
        if instance.publicacao and instance.publicacao.data_expedicao:
            data_publicacao_exp = DateUtils.date_to_str(
                instance.publicacao.data_expedicao
            )

        rst.update(
            data_publicacao=dt_publicacao,
            data_publicacao_exp=data_publicacao_exp,
        )

        return rst


class ServidorAnotacaoPessoalRF(RestfulDRY):

    _model = Servidor

    full_text_index = (
        "matricula__iexact",
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__cpf__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("anotacao_pessoal.anotacao.servidor.Manage")')

    def model_to_dict(self, instance):
        rst = super(ServidorAnotacaoPessoalRF, self).model_to_dict(instance)

        departures = instance.departures().first()
        effective, commission = self.get_effective_and_commission(instance)

        q_mov_posse = MovimentacaoPosse.objects.filter(servidor=instance)
        dt_posse = q_mov_posse.last().data_posse if q_mov_posse.exists() else None

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
