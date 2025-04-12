from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rh.apiv2.serializers.empoloyeecurrent import EmployeeCurrentSerializer
from rh.models import Servidor
from contrib.utils import getLogger

log = getLogger(__name__)


class EmployeeCurrentView(APIView):
    """
    View das Informações básicas do servidor
    """

    permission_classes = [IsAuthenticated]
    queryset = Servidor.objects.all()
    serializer_class = EmployeeCurrentSerializer

    def get(self, request, *args, **kwargs):
        """
        Informações do servidor
        """
        instance = self.queryset.get(user=request.user)
        serializer = self.serializer_class(instance)
        return Response(serializer.data)
