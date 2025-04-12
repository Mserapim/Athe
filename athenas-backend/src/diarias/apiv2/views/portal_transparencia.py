from drf_spectacular.utils import OpenApiParameter, extend_schema
from contrib.utils import getLogger
from diarias.apiv2.serializers.portal_transparencia import (
    BeneficiarioTransparenciaSerializer,
)
from diarias.models import Beneficiario
from apiv2.baseviews import ListBaseView


log = getLogger(__name__)


class BeneficiariosTransparenciaView(ListBaseView):

    serializer_class = BeneficiarioTransparenciaSerializer
    model = Beneficiario
    queryset = Beneficiario.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="page", description="Página", type=int),
            OpenApiParameter(
                name="matricula", description="Matricula beneficiario", type=int
            ),
            OpenApiParameter(name="mes", description="Mês", type=int),
            OpenApiParameter(name="ano", description="ano", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        matricula = self.request.GET.get("matricula")

        if matricula and matricula is not None:
            queryset = queryset.filter(servidor__matricula=matricula)

        mes = self.request.GET.get("mes")
        if mes and mes is not None:
            queryset = queryset.filter(viagem__data_inicio_viagem__month=mes)

        ano = self.request.GET.get("ano")
        if ano and ano is not None:
            queryset = queryset.filter(viagem__data_inicio_viagem__year=ano)

        if mes and ano is None:
            raise Exception("Obrigatório informar o ano, caso informe o mês")

        return queryset.distinct()
