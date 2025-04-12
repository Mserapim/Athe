from contrib.middleware import set_current_user
from contrib.utils import getLogger

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from diarias.config.apiv2.serializers import (
    CargoDiariasSerializer,
    LimiteDiariasSerializer,
    ValorDiariasSerializer,
)

from diarias.models import CargoDiarias, LimiteDiarias, ValorDiarias
from rh.apiv2.serializers.servidor import ServidorListagemSerializer
from rh.models import Servidor
from standard.models import Item

log = getLogger(__name__)


class CargoDiariasView(ListBaseView):
    """
    View da lista de Cargos
    """

    permission_classes = [IsAuthenticated]
    queryset = CargoDiarias.objects.filter()
    serializer_class = CargoDiariasSerializer
    full_text_index = ("nome__unaccent__icontains",)


class CargoDiariasDetailView(ApiDetailView):
    """
    View de detalhes de Cargo
    """

    model = CargoDiarias
    serializer_class = CargoDiariasSerializer


class CargoDiariasApicoreView(ApiCore):
    """
    View da Criar, editar e apagar de Cargo
    """

    model = CargoDiarias
    serializer_class = CargoDiariasSerializer
    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
    }


class ValorDiariasView(ListBaseView):
    """
    View da lista de Valores
    """

    permission_classes = [IsAuthenticated]
    queryset = ValorDiarias.objects.filter()
    serializer_class = ValorDiariasSerializer
    full_text_index = (
        "valor_estado__icontains",
        "valor_fora_estado__icontains",
        "valor_exterior__icontains",
    )


class ValorDiariasDetailView(ApiDetailView):
    """
    View de detalhes de Valor
    """

    model = ValorDiarias
    serializer_class = ValorDiariasSerializer


class ValorDiariasApicoreView(ApiCore):
    """
    View da Criar, editar e apagar de Valor
    """

    model = ValorDiarias
    serializer_class = ValorDiariasSerializer
    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
    }


class LimiteDiariasView(ListBaseView):
    """
    View da lista de Limites de Diarias
    """

    permission_classes = [IsAuthenticated]
    queryset = LimiteDiarias.objects.filter().order_by("-tipo")
    serializer_class = LimiteDiariasSerializer
    full_text_index = (
        "tipo__unaccent__icontains",
        "referencia__unaccent__icontains",
    )


class LimiteDiariasApicoreView(ApiCore):
    """
    View de criar, editar e apagar de Limite de Diárias
    """

    model = LimiteDiarias
    serializer_class = LimiteDiariasSerializer

    def exclude(self, request, *args, **kwargs):
        try:
            set_current_user(request.user)
            instance = self.get_object()
            instance.delete()
            return Response(
                {"detail": "Item excluído com sucesso"}, status=status.HTTP_200_OK
            )

        except self.model.DoesNotExist:
            return Response(
                {"detail": "O objeto não existe ou já foi excluído"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

        except Exception as e:
            return Response(
                {"detail": f"Erro ao tentar excluir o item - {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LimiteDiariasDetailView(ApiDetailView):
    """
    View de detalhes de Limite de diária
    """

    model = LimiteDiarias
    serializer_class = LimiteDiariasSerializer


class MotoristasDiariasAPIList(ListBaseView):
    """
    View para listar servidores cujas matrículas estão na lista 'motoristas_diarias_matriculas' do Item.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ServidorListagemSerializer
    queryset = Servidor.objects.all()

    def filter_extra_queryset(self, queryset):
        """
        Filtro extra para buscar apenas os servidores cujas matrículas estão no item 'motoristas_diarias_matriculas'.
        """
        try:
            item = Item.objects.get(key="motoristas_diarias_matriculas")
            matriculas = item.value.split(",")

            queryset = queryset.filter(matricula__in=matriculas)

        except Item.DoesNotExist:
            queryset = Servidor.objects.none()

        return queryset
