from auth.permissions.vdf.permissions import IsPermissionVDF
from contrib.utils import getLogger
from rest_framework.permissions import IsAuthenticated
from rh.pvf.apiv2.serializers.historyretificationserializers import (
    PVFObservationRetificationSerializer,
)
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rh.pvf.models import PortalRequestHistory
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


log = getLogger(__name__)


class PVFObservationRetificationViewSet(BaseRequestViewSet):
    """
    View para o retificar o campo 'observation' no histórico
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalRequestHistory.objects.filter()
    serializer_class = PVFObservationRetificationSerializer

    @action(detail=True, methods=["post"])
    def retificate_observation(self, request, pk=None):
        if pk is None:
            return Response(
                {"message": "ID da observação não fornecido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            history_instance = self.get_object()
            serializer = self.get_serializer(history_instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"success": True, "message": "Histórico atualizado com sucesso!"},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PortalRequestHistory.DoesNotExist:
            return Response(
                {"success": False, "message": "Histórico não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            log.error(f"Erro ao retificar anotação do histórico de requisições: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Erro ao atualizar histórico da requisição.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
