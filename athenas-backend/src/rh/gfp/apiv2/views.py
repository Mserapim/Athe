from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rh.gfp.cedulac.import_cc import get_cedula_c
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rh.models import Servidor
from auth.backend import CustomTokenJWTAuthentication
from apiv2.utils import response_api_view


class CedulacView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="year", description="Ano", type=int),
        ]
    )
    def get(self, request):
        employee = Servidor.objects.get(user=self.request.user)
        year = request.data.get("year", None)
        data = get_cedula_c(employee.pessoa_fisica.cpf, year)
        return response_api_view(data)
