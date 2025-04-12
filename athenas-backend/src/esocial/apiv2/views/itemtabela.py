from apiv2.utils import response_api_view
from esocial.apiv2.serializers.itemtabela import ItemTabelaSerializer, OpcoesSerializer
from esocial.models import ItemTable
from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from django.db.models import Count
from standard.models import Choice
from drf_spectacular.utils import OpenApiParameter, extend_schema


class ItemTabelaView(ListBaseView):
    """
    View dos itens de tabelas do esocial
    """

    model = ItemTable
    serializer_class = ItemTabelaSerializer
    full_text_index = (
        "title__icontains",
        "code__iexact",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="tabela", description="Tabela esocial", type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View dos itens de tabelas do esocial
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.all()
        tabela = self.request.GET.get("tabela")
        if tabela:
            queryset = queryset.filter(esocial_table=tabela)
        return queryset


class TabelaEsocialView(ListBaseView):
    """
    View das tabelas do esocial
    """

    def get(self, request, *args, **kwargs):
        """
        View das tabelas do esocial
        """
        tabelas = ItemTable.objects.values("esocial_table").annotate(
            Count("esocial_table")
        )
        dados = [
            {"id": x["esocial_table"], "titulo": "Tabela " + x["esocial_table"]}
            for x in tabelas
        ]
        return response_api_view(dados)


class ItemTabelaDetailView(ApiDetailView):
    """
    Detalhes dos itens de tabela
    """

    model = ItemTable
    serializer_class = ItemTabelaSerializer


class ItemTabelaCoreView(ApiCore):
    """
    CRUD dos itens de tabela
    """

    model = ItemTable
    serializer_class = ItemTabelaSerializer


class OpcaoTableChoiceView(ListBaseView):
    """
    View das opçoes correspondente das tabelas do esocial
    """

    model = Choice
    serializer_class = OpcoesSerializer
    full_text_index = ("label__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="choice_filtro",
                description="name do choice da tabela do esocial",
                type=str,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View das opçoes correspondente das tabelas do esocial
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        choice_filtro = self.request.GET.get("choice_filtro", None)
        queryset = self.model.objects.filter(name=choice_filtro)
        return queryset
