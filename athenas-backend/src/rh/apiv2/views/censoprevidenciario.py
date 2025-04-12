from datetime import datetime
from rh.apiv2.serializers.censoprevidenciario import CensoPrevidenciarioSerializer
from rest_framework.permissions import IsAuthenticated
from auth.backend import CustomTokenJWTAuthentication
from apiv2.baseviews import ListBaseView
from django.db.models import Q

from rh.const import TIPO_POSSE

from rh.models import Dependencia, Dependente, Servidor

from contrib.utils import getLogger

log = getLogger(__name__)


class CensoprevidenciarioView(ListBaseView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    serializer_class = CensoPrevidenciarioSerializer

    # queryset = Servidor.objects.filter(ativo=True)
    queryset = Servidor.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        # verificar se setando essa variável a lógica está correta
        lista = [6564]

        return queryset.filter(matricula__in=lista)
