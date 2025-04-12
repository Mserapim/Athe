from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView
from painel_controle.configuracoes.apiv2.serializers import (
    ConfiguracaoDePontoSerializer,
)
from standard.models import ConfigPoint
from django.db.models import Q


class ConfiguracaoDePontoView(ListBaseView):
    queryset = ConfigPoint.objects.all()
    serializer_class = ConfiguracaoDePontoSerializer
    full_text_index = (
        "place__icontains",
        "prosecution__icontains",
        "network__icontains",
    )


class ConfiguracaoDePontoCoreView(ApiCore):
    model = ConfigPoint
    serializer_class = ConfiguracaoDePontoSerializer


class ConfiguracaoDePontoDetailView(ApiDetailView):
    model = ConfigPoint
    serializer_class = ConfiguracaoDePontoSerializer
