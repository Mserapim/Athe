from auth.backend import MultiAuthentication
from rest_framework.permissions import IsAuthenticated
from apiv2.baseviews import ListBaseView
from rh.apiv2.serializers.gratificacoesmembros import GratificacaoSerializer
from rh.models import Gratificacao
from drf_spectacular.utils import OpenApiParameter, extend_schema
from standard.models import Item


class GratificacaoMembrosView(ListBaseView):
    """
    View da lista da gratificações de membros
    """

    permission_classes = [IsAuthenticated]
    queryset = Gratificacao.objects.all()
    authentication_classes = [MultiAuthentication]
    serializer_class = GratificacaoSerializer
    full_text_index = (
        "grat_membro__servidor__pessoa_fisica__nome__unaccent__icontains",
    )

    def get_queryset(self):
        ano = self.request.GET.get("ano", None)
        mes = self.request.GET.get("mes", None)
        eventos = Item.objects.get(
            key="gratificacoes_membros_transparencia"
        ).value.split(",")
        queryset = self.queryset.filter(evento__numero__in=eventos, status="DEFER")
        if ano:
            queryset = queryset.filter(grat_membro__periodo__ano=ano)
        if mes:
            queryset = queryset.filter(grat_membro__periodo__mes=mes)

        return queryset.order_by(
            "grat_membro__servidor__pessoa_fisica__nome"
        ).distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="ano", description="Ano", type=int),
            OpenApiParameter(name="mes", description="Mês", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View da lista da gratificações de membros
        """
        return self.list(request, *args, **kwargs)
