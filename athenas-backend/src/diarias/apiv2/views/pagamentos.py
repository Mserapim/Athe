from contrib.utils import getLogger
from diarias.utils.utils import assinar_pgto, gerar_cnab_pgto
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apiv2.baseviews import ListBaseView
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from drf_spectacular.utils import OpenApiParameter, extend_schema
from diarias.apiv2.serializers.pagamentos import PagamentoSerializer
from diarias.models import Pagamento

log = getLogger(__name__)


class PagamentoView(ListBaseView):
    """
    View da lista de Pagamento
    """

    permission_classes = [IsAuthenticated]
    queryset = Pagamento.objects.filter()
    serializer_class = PagamentoSerializer
    full_text_index = (
        "beneficiario__servidor__matricula__icontains",
        "beneficiario__servidor__pessoa_fisica__social_name__unaccent__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="status[]", description="Lista de status dos pagamentos", type=str
            ),
            OpenApiParameter(
                name="data_pgto_inicio",
                description="Data de início do pagamento",
                type=str,
            ),
            OpenApiParameter(
                name="data_pgto_fim", description="Data de fim do pagamento", type=str
            ),
            OpenApiParameter(
                name="palavra_chave", description="Campo de Pesquisa", type=str
            ),
        ]
    )
    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        # Filtro por status do pagamento
        status = self.request.GET.getlist("status[]")
        servidores = self.request.GET.getlist("servidores[]")
        if status:
            queryset = queryset.filter(status__in=status)

        # Filtro por intervalo de datas de pagamento
        data_pgto_inicio = self.request.GET.get("data_pgto_inicio")
        data_pgto_fim = self.request.GET.get("data_pgto_fim")

        if data_pgto_inicio and data_pgto_fim:
            queryset = queryset.filter(
                data_pgto__range=[data_pgto_inicio, data_pgto_fim]
            )
        elif data_pgto_inicio:
            queryset = queryset.filter(data_pgto__gte=data_pgto_inicio)
        elif data_pgto_fim:
            queryset = queryset.filter(data_pgto__lte=data_pgto_fim)

        if servidores and len(servidores) > 0:
            queryset = queryset.filter(beneficiario__servidor__in=servidores)

        return queryset


class GerarCnabView(APIView):
    """
    View para gerar CNAB de pagamentos.
    """

    def post(self, request):
        set_current_user(request.user)

        pgto_ids = request.data.get("pgto_ids")
        data_pgto = request.data.get("data_pgto")
        assinado_por = request.data.get("assinado_por")

        if not pgto_ids or not data_pgto or not assinado_por:
            return Response(
                {
                    "detail": "pgto_ids, data_pgto, and assinado_por são campos obrigatórios."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            usuario = User.objects.get(username=assinado_por)

            if usuario != request.user:
                return Response(
                    {
                        "detail": "Usuário autenticado não corresponde ao usuário de assinatura."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            data_pgto = timezone.datetime.strptime(data_pgto, "%Y-%m-%d").date()

            with transaction.atomic():
                cnab = gerar_cnab_pgto(pgto_ids, data_pgto)
                assinar_pgto(pgto_ids, usuario)

            return Response(
                {
                    "message": "CNAB gerado com sucesso",
                    "cnab_id": cnab.id,
                    "file_id": cnab.cnab.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
