from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers
from diarias.models import Beneficiario, DadosBancariosImportacao
from diarias.utils.fluxo_condicionais import benef_acomp_autoridade

from contrib.utils import getLogger
import rest_framework.serializers
from rh.models import MovimentacaoPosse, ServidorLotacao
from rh.pvf.utils.chefe_imediato import get_aprovador
from diarias.apiv2.serializers.viagem import ViagemSerializer
from diarias.apiv2.serializers.evento import EventoSerializer
from diarias.apiv2.serializers.destino import DestinoSerializer

log = getLogger(__name__)


class BeneficiarioSerializer(BaseSerializer):

    fluxo_unicode = serializers.SerializerMethodField()
    etapa_fluxo = serializers.SerializerMethodField()
    servidor_unicode = serializers.SerializerMethodField()
    servidor_matricula = serializers.SerializerMethodField()
    servidor_nome = serializers.SerializerMethodField()
    servidor_cpf = serializers.SerializerMethodField()
    lotacao = serializers.SerializerMethodField()
    categoria_funcional = serializers.SerializerMethodField()
    conta_bancaria_unicode = serializers.SerializerMethodField()
    conta_bancaria_tipo = serializers.SerializerMethodField()
    cargo = serializers.SerializerMethodField()
    qtd_destinos = serializers.SerializerMethodField()
    qtd_eventos = serializers.SerializerMethodField()
    codigo_os = serializers.SerializerMethodField()
    codigo_os_viagem_original = serializers.SerializerMethodField()
    codigo_os_excedente = serializers.SerializerMethodField()
    total_distancia_destinos = serializers.SerializerMethodField()
    chefe_imediato = serializers.SerializerMethodField()
    qtd_total_diarias = serializers.SerializerMethodField()
    qtd_total_diarias_deferido = serializers.SerializerMethodField()
    pode_editar_valor_deferido = serializers.SerializerMethodField()
    reanalise = serializers.SerializerMethodField()
    acomp_autoridade = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiario
        fields = "__all__"

    def get_servidor_unicode(self, obj):
        return f"{obj.servidor.matricula} - {obj.servidor.pessoa_fisica.social_name}"

    def get_servidor_matricula(self, obj):
        return f"{obj.servidor.matricula}"

    def get_servidor_nome(self, obj):
        return f"{obj.servidor.pessoa_fisica.social_name}"

    def get_servidor_cpf(self, obj):
        return f'{obj.servidor.pessoa_fisica.cpf or ""}'

    def get_conta_bancaria_unicode(self, obj):

        if obj.viagem.importada:
            dados_importacao = DadosBancariosImportacao.objects.filter(
                beneficiario=obj
            ).first()
            if dados_importacao:
                return f'{dados_importacao.banco or ""} - {dados_importacao.agencia or ""} - {dados_importacao.conta or ""}'
            return ""

        if (
            obj.conta_bancaria_pgto.agencia_numero
            and obj.conta_bancaria_pgto.conta_numero
        ):

            ag = obj.conta_bancaria_pgto.agencia_numero
            conta = obj.conta_bancaria_pgto.conta_numero

            if (
                obj.conta_bancaria_pgto.agencia_dv
                and obj.conta_bancaria_pgto.agencia_dv != ""
            ):
                ag += obj.conta_bancaria_pgto.agencia_dv
            if (
                obj.conta_bancaria_pgto.conta_dv
                and obj.conta_bancaria_pgto.conta_dv != ""
            ):
                conta += obj.conta_bancaria_pgto.conta_dv

            return f"{obj.conta_bancaria_pgto.banco} - {ag} - {conta}"

        return f"{obj.conta_bancaria_pgto.banco} - {obj.conta_bancaria_pgto.agencia} - {obj.conta_bancaria_pgto.conta_corrente_completa}"

    def get_conta_bancaria_tipo(self, obj):

        if obj.viagem.importada:
            return ""
        return obj.conta_bancaria_pgto.get_tipo_conta_display()

    def get_fluxo_unicode(self, obj):

        return f"{obj.fluxo.get_etapa_display()} - {obj.fluxo.get_situacao_display()}"

    def get_etapa_fluxo(self, obj):
        return obj.fluxo.etapa

    def get_cargo(self, obj):

        mov_posse = MovimentacaoPosse.objects.filter(
            servidor=obj.servidor, ativo=True
        ).last()
        if mov_posse and mov_posse.quadro.cargo:
            return f"{mov_posse.quadro.cargo}"

        return obj.cargo.nome if obj.cargo else ""

    def get_qtd_destinos(self, obj):
        return obj.destinos.count()

    def get_qtd_eventos(self, obj):
        return obj.eventos.count()

    def get_lotacao(self, obj):
        lotacoes = ServidorLotacao.objects.filter(
            servidor=obj.servidor, designacao=False, ativo=True
        )
        if lotacoes.exists():
            return lotacoes.last().lotacao.nome
        return ""

    def get_categoria_funcional(self, obj):
        return obj.servidor.get_type_by_possession_display()

    def get_codigo_os(self, obj):
        return obj.codigo_os

    def get_codigo_os_viagem_original(self, obj):
        return obj.codigo_os_viagem_original

    def get_codigo_os_excedente(self, obj):
        return obj.codigo_os_excedente

    def get_total_distancia_destinos(self, obj):
        return obj.total_distancia_destinos

    def get_chefe_imediato(self, obj):
        try:
            if obj.chefe_imediato:
                return obj.chefe_imediato.id
            else:
                chefe_imediato = get_aprovador(obj.servidor)
                if chefe_imediato:
                    return chefe_imediato.id
        except Exception as e:
            log.error(f"Erro ao buscar chefe imediato: {e}")
        return None

    def get_qtd_total_diarias(self, obj):
        if hasattr(obj, "calculos_diarias_consolidados"):
            return obj.calculos_diarias_consolidados.qtd_total_diarias
        return None

    def get_qtd_total_diarias_deferido(self, obj):
        if hasattr(obj, "calculos_diarias_consolidados"):
            return obj.calculos_diarias_consolidados.qtd_total_diarias_deferido
        return None

    def get_pode_editar_valor_deferido(self, obj):
        return obj.pode_editar_valor_deferido

    def get_reanalise(self, obj):
        if hasattr(obj, "calculos_diarias_consolidados"):
            return obj.calculos_diarias_consolidados.reanalise
        return False

    def get_acomp_autoridade(self, obj):
        return benef_acomp_autoridade(obj)


class BeneficiarioConsolidadSerializer(BaseSerializer):

    servidor_unicode = serializers.SerializerMethodField()
    codigo_os = serializers.SerializerMethodField()
    qtd_total_diarias = serializers.SerializerMethodField()
    qtd_total_diarias_deferido = serializers.SerializerMethodField()

    viagem = serializers.SerializerMethodField()
    eventos = serializers.SerializerMethodField()
    destinos = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiario
        fields = "__all__"

    def get_servidor_unicode(self, obj):
        return f"{obj.servidor.matricula} - {obj.servidor.pessoa_fisica.social_name}"

    def get_codigo_os(self, obj):
        return obj.codigo_os

    def get_qtd_total_diarias(self, obj):
        if hasattr(obj, "calculos_diarias_consolidados"):
            return obj.calculos_diarias_consolidados.qtd_total_diarias
        return None

    def get_qtd_total_diarias_deferido(self, obj):
        if hasattr(obj, "calculos_diarias_consolidados"):
            return obj.calculos_diarias_consolidados.qtd_total_diarias_deferido
        return None

    def get_viagem(self, obj):
        viagem_data = ViagemSerializer(obj.viagem).data
        # Remova os campos indesejados
        campos_a_remover = [
            "justificativa",
            "resumo",
        ]  # Substitua pelos nomes dos campos a remover
        for campo in campos_a_remover:
            viagem_data.pop(campo, None)  # Remove o campo, se existir
        return viagem_data

    def get_eventos(self, obj):
        return EventoSerializer(obj.eventos.all(), many=True).data

    def get_destinos(self, obj):
        return DestinoSerializer(obj.destinos.all(), many=True).data
