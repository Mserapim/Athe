from apiv2.baseviews import ListAPIView, ApiCore, ApiDetailView, ListBaseView
from drf_spectacular.utils import OpenApiParameter, extend_schema

from rh.apiv2.serializers.orgao_geral import OrgaoGeralSerializer

from rh.models import OrgaoGeral, UnidadeAdministrativa


class OrgaoGeralListView(ListBaseView):
    """
    View de Orgão Geral
    """

    model = OrgaoGeral
    serializer_class = OrgaoGeralSerializer
    queryset = OrgaoGeral.objects.filter()

    full_text_index = (
        "nome__unaccent__icontains",
        "sigla__icontains",
        "abreviacao__unaccent__icontains",
        "cache_identifier__icontains",
    )


class OrgaoGeralDetailView(ApiDetailView):
    """
    Detalhes de Orgão Geral
    """

    model = OrgaoGeral
    serializer_class = OrgaoGeralSerializer


class OrgaoGeralCoreView(ApiCore):
    """
    CRUD de Orgão Geral
    """

    model = OrgaoGeral
    serializer_class = OrgaoGeralSerializer


class UnidadeAdmnistrativaListView(ListBaseView):
    """
    View da unidade administrativa
    """

    model = UnidadeAdministrativa
    serializer_class = OrgaoGeralSerializer
    queryset = UnidadeAdministrativa.objects.all()

    full_text_index = (
        "nome__unaccent__icontains",
        "sigla__icontains",
        "abreviacao__unaccent__icontains",
        "cache_identifier__icontains",
    )
