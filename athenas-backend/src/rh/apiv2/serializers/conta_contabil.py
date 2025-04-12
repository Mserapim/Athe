from contrib.utils import getLogger
from rest_framework import serializers
from rh.gfp.models import Evento, FolhaEvento
from rh.models import MovimentacaoPosse
from standard.models import Choice
from django.db.models import Sum


log = getLogger(__name__)


class ContaContabilSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Lotaçâo
    """

    id = serializers.SerializerMethodField()
    conta_contabil = serializers.SerializerMethodField()
    qtd_pagamentos = serializers.SerializerMethodField()
    total_pagamentos = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["id", "conta_contabil", "qtd_pagamentos", "total_pagamentos"]

    def __init__(self, *args, **kwargs):
        # Acesse o contexto da solicitação e passe para a classe pai
        context = kwargs.pop("context", None)

        if context:
            self.request = context.get("request")
            self.mes = self.request.query_params.get("mes")
            self.ano = self.request.query_params.get("ano")

        super(ContaContabilSerializer, self).__init__(*args, **kwargs)

    def get_id(self, obj):
        return obj.value

    def get_conta_contabil(self, obj):
        return obj.label

    def get_qtd_pagamentos(self, obj):

        eventos = FolhaEvento.objects.filter(
            evento__conta_contabil=obj.value,
            folha__dt_pagamento__month=self.mes,
            folha__dt_pagamento__year=self.ano,
        ).distinct()

        return eventos.count()

    def get_total_pagamentos(self, obj):

        eventos = (
            FolhaEvento.objects.filter(
                evento__conta_contabil=obj.value,
                folha__dt_pagamento__month=self.mes,
                folha__dt_pagamento__year=self.ano,
            )
            .distinct()
            .aggregate(soma=Sum("valor"))
        )

        return eventos["soma"]


class PagamentoSerializer(serializers.ModelSerializer):

    valor = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    lotacao = serializers.SerializerMethodField()
    tipo_posse = serializers.SerializerMethodField()
    matricula = serializers.SerializerMethodField()
    descricao_posse = serializers.SerializerMethodField()

    class Meta:
        model = FolhaEvento
        fields = [
            "valor",
            "data",
            "lotacao",
            "tipo_posse",
            "matricula",
            "descricao_posse",
        ]

    def get_valor(self, obj):
        return obj.valor

    def get_lotacao(self, obj):
        return obj.servidor.lotacoes.last().id if obj.servidor.lotacoes.last() else ""

    def get_tipo_posse(self, obj):
        return obj.servidor.type_by_possession

    def get_data(self, obj):
        return obj.folha.dt_pagamento.strftime("%d/%m/%Y")

    def get_matricula(self, obj):
        return obj.servidor.matricula

    def get_descricao_posse(self, obj):
        mov_posse = (
            MovimentacaoPosse.objects.filter(servidor=obj.servidor)
            .order_by("data_posse")
            .last()
        )
        return (
            mov_posse.my_origin.quadro.cargo.pk
            if mov_posse and mov_posse.my_origin.quadro
            else ""
        )
