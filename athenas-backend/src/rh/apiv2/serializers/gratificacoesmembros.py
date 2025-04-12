from rest_framework import serializers
from rh.models import Gratificacao, ServidorLotacao
from standard.models import Choice


class LotacaoGratificacaoSerializer(serializers.ModelSerializer):

    lotacao = serializers.SerializerMethodField()
    ato_portaria = serializers.SerializerMethodField()
    data_publicacao = serializers.SerializerMethodField()

    class Meta:
        model = ServidorLotacao
        fields = ["lotacao", "ato_portaria", "data_publicacao"]

    def get_ato_portaria(self, obj):
        if obj.publicacao:
            return obj.publicacao.__str__()
        return None

    def get_data_publicacao(self, obj):
        if obj.publicacao:
            return obj.publicacao.data_publicacao
        return None

    def get_lotacao(self, obj):
        if obj.lotacao:
            return obj.lotacao.nome
        return None


class GratificacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Gratificação
    """

    matricula = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    gratificacao = serializers.SerializerMethodField()
    lotacoes = serializers.SerializerMethodField()

    class Meta:
        model = Gratificacao
        fields = ["matricula", "nome", "gratificacao", "lotacoes"]

    def get_matricula(self, obj):
        return obj.grat_membro.servidor.matricula

    def get_nome(self, obj):
        return obj.grat_membro.servidor.pessoa_fisica.nome

    def get_gratificacao(self, obj):
        return obj.evento.titulo

    def get_lotacoes(self, obj):
        tag = Choice.objects.filter(
            name="WORKPLACE_TAG", description=obj.evento.numero
        ).first()
        if tag:
            return LotacaoGratificacaoSerializer(
                obj.grat_membro.designacoes.filter(
                    lotacao__workplace_config_tags__tag=tag.value,
                    from_substitution=False,
                ).distinct(),
                many=True,
            ).data
        return []
