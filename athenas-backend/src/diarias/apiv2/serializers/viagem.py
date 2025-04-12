from apiv2.baseserializers import BaseSerializer
from diarias.models import (
    HistoricoFluxoViagemBeneficiario,
    PassagemAeriaViagem,
    VeiculoPassageiro,
    Viagem,
    ViagemAnexo,
)
from rh.pvf.utils.chefe_imediato import get_aprovador
import requests
from rest_framework import serializers
from rest_framework import status
from django.db import transaction
from apiv2.const import MSG_SUCCESS_METHOD
from ged.models import Arquivo

from ged.apiv2.serializers import ArquivoSerializer

from contrib.utils import employee_from_user, getLogger

log = getLogger(__name__)


class ViagemSerializer(BaseSerializer):
    aprovador_atual = serializers.SerializerMethodField()
    tipo_viagem_display = serializers.SerializerMethodField()
    motivo_viagem_display = serializers.SerializerMethodField()
    finalidade_viagem_display = serializers.SerializerMethodField()
    situacao_solicitacao_display = serializers.SerializerMethodField()
    etapa_solicitacao_display = serializers.SerializerMethodField()
    etapa_fluxo = serializers.SerializerMethodField()
    situacao_etapa_atual = serializers.SerializerMethodField()
    solicitante = serializers.SerializerMethodField()
    solicitante_servidor = serializers.SerializerMethodField()
    solicitante_unicode = serializers.SerializerMethodField()
    data_solicitacao = serializers.SerializerMethodField()
    anexos = serializers.SerializerMethodField()
    qtd_beneficiarios = serializers.SerializerMethodField()
    tipo_solicitante_display = serializers.SerializerMethodField()
    chefes_imediatos = serializers.SerializerMethodField()
    servidores_beneficiarios = serializers.SerializerMethodField()
    servidores_beneficiarios_unicode = serializers.SerializerMethodField()
    possui_excedente = serializers.SerializerMethodField()
    link_informacao = serializers.SerializerMethodField()
    recebido_por = serializers.SerializerMethodField()

    class Meta:
        model = Viagem
        fields = "__all__"

    def get_aprovador_atual(self, obj):
        return "Aprovador"

    def get_solicitante(self, obj):
        return obj.solicitante

    def get_solicitante_servidor(self, obj):
        return obj.solicitante_servidor.id

    def get_solicitante_unicode(self, obj):
        solicitante = obj.created_by.servidor
        return f"{solicitante.matricula} - {solicitante.pessoa_fisica.social_name} - {obj.get_tipo_solicitante_display()}"

    def get_data_solicitacao(self, obj):
        return obj.data_solicitacao

    def get_tipo_viagem_display(self, obj):
        return obj.get_tipo_viagem_display() or ""

    def get_motivo_viagem_display(self, obj):
        return obj.get_motivo_viagem_display() or ""

    def get_finalidade_viagem_display(self, obj):
        return obj.get_finalidade_viagem_display() or ""

    def get_situacao_solicitacao_display(self, obj):
        fluxo = obj.fluxo_atual
        if fluxo:
            return fluxo.get_situacao_display() or ""
        return ""

    def get_etapa_solicitacao_display(self, obj):
        fluxo = obj.fluxo_atual
        if fluxo:
            return fluxo.get_etapa_display() or ""
        return ""

    def get_etapa_fluxo(self, obj):
        fluxo = obj.fluxo_atual
        if fluxo:
            return fluxo.etapa
        return None

    def get_situacao_etapa_atual(self, obj):
        return obj.situacao_etapa_atual

    def get_anexos(self, obj):
        anexos = [a.arquivo for a in obj.anexos_viagem.all()]
        return ArquivoSerializer(anexos, many=True).data

    def get_qtd_beneficiarios(self, obj):
        return obj.qtd_beneficiarios

    def get_tipo_solicitante_display(self, obj):
        tipo_solicitante = obj.tipo_solicitante
        if tipo_solicitante:
            return obj.get_tipo_solicitante_display() or ""
        return ""

    def get_chefes_imediatos(self, obj):
        chefes_imediatos = []

        for beneficiario in obj.beneficiarios.all():
            if beneficiario.chefe_imediato:
                chefes_imediatos.append(beneficiario.chefe_imediato.id)
            else:
                try:
                    chefe_imediato = get_aprovador(beneficiario.servidor)
                except Exception as e:
                    log.error(
                        f"Erro ao tentar buscar o chefe imediato no serializer de viagem: {e}"
                    )
                    chefe_imediato = None
                if chefe_imediato:
                    chefes_imediatos.append(chefe_imediato.id)

        return chefes_imediatos if chefes_imediatos else None

    def get_servidores_beneficiarios(self, obj):
        return [beneficiario.servidor.id for beneficiario in obj.beneficiarios.all()]

    def get_servidores_beneficiarios_unicode(self, obj):
        return [
            f"{beneficiario.servidor.matricula} - {beneficiario.servidor.pessoa_fisica.social_name}"
            for beneficiario in obj.beneficiarios.all()
        ]

    def get_possui_excedente(self, obj):
        return obj.possui_excedente

    def get_link_informacao(self, obj):
        if obj.fluxo:
            return obj.fluxo.link_informacao
        return ""

    def get_recebido_por(self, obj):
        fluxo_nota = 47
        fluxo_empenho = [49, 50]
        fluxo_ordem = 51
        fluxos_validos = {fluxo_nota, fluxo_ordem} | set(fluxo_empenho)

        user = obj.modified_by
        servidor = employee_from_user(user)
        return (
            servidor.pessoa_fisica.nome
            if obj.fluxo and obj.fluxo.id in fluxos_validos
            else None
        )

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:

            with transaction.atomic():
                self.is_valid(raise_exception=True)
                self.save()

                request = self.context.get("request")
                anexos = request.data.get("anexos", None)

                if anexos:
                    for anexo_id in anexos:
                        arquivo = Arquivo.objects.get(pk=anexo_id)

                        anexo, _ = ViagemAnexo.objects.get_or_create(
                            viagem=self.instance, arquivo=arquivo
                        )

                rst.update(
                    {
                        "success": True,
                        "message": MSG_SUCCESS_METHOD["post"],
                        "data": self.data,
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst

    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            with transaction.atomic():
                self.is_valid(raise_exception=True)
                self.save()

                request = self.context.get("request")
                anexos = request.data.get("anexos", None)

                if anexos:
                    for anexo_id in anexos:
                        arquivo = Arquivo.objects.get(pk=anexo_id)

                        anexo, _ = ViagemAnexo.objects.get_or_create(
                            viagem=self.instance, arquivo=arquivo
                        )

                rst.update(
                    {
                        "success": True,
                        "message": MSG_SUCCESS_METHOD["put"],
                        "data": self.data,
                    }
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


class HistoricoFluxoViagemBeneficiarioSerializer(BaseSerializer):
    anexos = serializers.SerializerMethodField()
    numero_empenho = serializers.SerializerMethodField()
    numero_nota_liquidacao = serializers.SerializerMethodField()
    numero_ordem_bancaria = serializers.SerializerMethodField()
    qtd_total_diarias_deferido = serializers.SerializerMethodField()
    acomp_autoridade_deferimento = serializers.SerializerMethodField()
    gedoc = serializers.SerializerMethodField()

    class Meta:
        model = HistoricoFluxoViagemBeneficiario
        fields = [
            "obs",
            "numero_empenho",
            "numero_nota_liquidacao",
            "numero_ordem_bancaria",
            "anexos",
            "qtd_total_diarias_deferido",
            "acomp_autoridade_deferimento",
            "gedoc",
            "feedback",
        ]

    def get_anexos(self, obj):
        anexos = [a.arquivo for a in obj.anexos.all()]
        return ArquivoSerializer(anexos, many=True).data

    def get_numero_empenho(self, obj):
        if (
            obj.fluxo.situacao == 1
            and obj.fluxo.etapa == 3
            and obj.decisao == "deferido"
        ):  # Aguardando empenho - DEPLAN-  Executor
            return obj.beneficiario.numero_empenho if obj.beneficiario else None

    def get_numero_nota_liquidacao(self, obj):
        if (
            obj.fluxo.situacao == 5
            and obj.fluxo.etapa == 11
            and obj.decisao == "deferido"
        ):  # Aguardando Nota Liquidação - DEFIN- Gerencia Financeira
            return obj.beneficiario.numero_nota_liquidacao if obj.beneficiario else None

    def get_numero_ordem_bancaria(self, obj):
        if (
            obj.fluxo.situacao == 6
            and obj.fluxo.etapa == 11
            and obj.decisao == "deferido"
        ):  # Aguardando Ordem Bancária - DEFIN- Gerencia Financeira
            return obj.beneficiario.numero_ordem_bancaria if obj.beneficiario else None

    def get_qtd_total_diarias_deferido(self, obj):
        if (
            obj.fluxo.id in [6, 24, 27, 28, 30, 31, 33]
            and obj.decisao  # "Assessoria da DG - Aguardando análise" ou "Aguardando análise - Assessoria do SUB JUR" ou "Aguardando análise - Assessoria do PGJ" ou "DEFIN - Excedente"
            in ["deferido", "encaminhado"]
            and obj.beneficiario.calculos_diarias_consolidados
        ):
            return (
                obj.beneficiario.calculos_diarias_consolidados.qtd_total_diarias_deferido
            )
        return None

    def get_acomp_autoridade_deferimento(self, obj):
        if (
            obj.fluxo.id == 6 and obj.decisao == "deferido"
        ):  # "Aguardando análise - Assessoria da DG"
            return obj.beneficiario.acomp_autoridade_deferimento

    def get_gedoc(self, obj):
        if obj.fluxo.id == 27:  # Fluxo: "DEFIN - Excedente"
            return obj.beneficiario.gedoc_numero


class PassagemAereaViagemSerializer(BaseSerializer):
    anexos = serializers.SerializerMethodField()

    class Meta:
        model = PassagemAeriaViagem
        fields = "__all__"

    def get_anexos(self, obj):
        anexos = [a.arquivo for a in obj.anexos.all()]
        return ArquivoSerializer(anexos, many=True).data


class VeiculoPassageiroSerializer(BaseSerializer):
    motorista = serializers.SerializerMethodField()
    veiculo_placa = serializers.SerializerMethodField()
    veiculo_marca = serializers.SerializerMethodField()
    veiculo_modelo = serializers.SerializerMethodField()
    veiculo_capacidade_passageiros = serializers.SerializerMethodField()
    data_daa = serializers.SerializerMethodField()

    class Meta:
        model = VeiculoPassageiro
        fields = "__all__"

    def get_motorista(self, obj):
        motorista = obj.motorista_veiculo
        if motorista:
            servidor = motorista.servidor
            return f"{servidor.matricula} - {servidor.pessoa_fisica.social_name}"
        return None

    def get_veiculo_placa(self, obj):
        if obj.veiculo:
            return obj.veiculo.placa
        return None

    def get_veiculo_marca(self, obj):
        if obj.veiculo:
            return obj.veiculo.marca
        return None

    def get_veiculo_modelo(self, obj):
        if obj.veiculo:
            return obj.veiculo.modelo
        return None

    def get_veiculo_capacidade_passageiros(self, obj):
        if obj.veiculo:
            return obj.veiculo.capacidade_passageiros
        return None

    def get_data_daa(self, obj):
        if obj.passageiro:
            return obj.passageiro.data_daa
        return None
