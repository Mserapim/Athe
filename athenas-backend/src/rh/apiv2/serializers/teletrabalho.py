from rest_framework import serializers
from rh.models import MetaTeletrabalho, MovimentacaoTeletrabalho
from contrib.utils import getLogger
from datetime import timedelta


log = getLogger(__name__)


class MetaTeletrabalhoSerializer(serializers.ModelSerializer):
    periodicidade = serializers.IntegerField(source="periodicity")
    periodicidade_display = serializers.SerializerMethodField()
    ativo = serializers.BooleanField(source="active")

    class Meta:
        model = MetaTeletrabalho
        fields = [
            "id",
            "data_inicio",
            "data_fim",
            "descricao",
            "meta",
            "periodicidade",
            "periodicidade_display",
            "ativo",
        ]

    def get_periodicidade_display(self, obj):
        if obj.periodicity:
            return obj.get_periodicity_display()
        return None


class MovimentacaoTeletrabalhoSerializer(serializers.ModelSerializer):

    servidor = serializers.SerializerMethodField()
    servidor_id = serializers.SerializerMethodField()
    aprovador = serializers.SerializerMethodField()
    aprovador_id = serializers.SerializerMethodField()
    tipo_ato_display = serializers.SerializerMethodField()
    tipo_pedido_display = serializers.SerializerMethodField()
    publicacao_movimentacao = serializers.SerializerMethodField()
    publicacao_movimentacao_id = serializers.SerializerMethodField()
    lotacao = serializers.SerializerMethodField()
    lotacao_id = serializers.SerializerMethodField()
    data_renovacao = serializers.SerializerMethodField()
    criado_em = serializers.DateTimeField(source="created_at")
    modificado_em = serializers.DateTimeField(source="modified_at")
    criado_por = serializers.SerializerMethodField()
    modificado_por = serializers.SerializerMethodField()
    metas = serializers.SerializerMethodField()

    class Meta:
        model = MovimentacaoTeletrabalho
        fields = [
            "id",
            "servidor",
            "servidor_id",
            "aprovador",
            "aprovador_id",
            "tipo_ato",
            "tipo_ato_display",
            "tipo_pedido",
            "tipo_pedido_display",
            "publicacao_movimentacao",
            "publicacao_movimentacao_id",
            "lotacao",
            "lotacao_id",
            "data_inicio",
            "data_fim",
            "data_renovacao",
            "criado_em",
            "modificado_em",
            "criado_por",
            "modificado_por",
            "gedoc",
            "presencial",
            "ativo",
            "metas",
        ]

    def get_servidor(self, obj):
        return obj.servidor.__str__()

    def get_servidor_id(self, obj):
        return obj.servidor.pk

    def get_aprovador(self, obj):
        if obj.aprovador:
            return obj.aprovador.__str__()
        return None

    def get_aprovador_id(self, obj):
        if obj.aprovador:
            return obj.aprovador.pk
        return None

    def get_tipo_ato_display(self, obj):
        return obj.get_tipo_ato_display()

    def get_tipo_pedido_display(self, obj):
        return obj.get_tipo_pedido_display()

    def get_publicacao_movimentacao(sel, obj):
        if obj.publicacao_movimentacao:
            return obj.publicacao_movimentacao.__str__()
        return None

    def get_publicacao_movimentacao_id(sel, obj):
        if obj.publicacao_movimentacao:
            return obj.publicacao_movimentacao.pk
        return None

    def get_lotacao(sel, obj):
        if obj.lotacao:
            return obj.lotacao.lotacao.nome
        return None

    def get_lotacao_id(sel, obj):
        if obj.lotacao:
            return obj.lotacao.lotacao.pk
        return None

    def get_data_renovacao(self, obj):
        if obj.data_fim:
            return obj.data_fim + timedelta(days=1)
        return None

    def get_criado_por(self, obj):
        return obj.created_by.username

    def get_modificado_por(self, obj):
        return obj.modified_by.username

    def get_metas(self, obj):
        metas = MetaTeletrabalho.objects.filter(mov_teletrabalho=obj)
        return MetaTeletrabalhoSerializer(metas, many=True).data
