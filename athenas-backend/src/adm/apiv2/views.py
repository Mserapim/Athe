import base64
from django.shortcuts import get_object_or_404
import requests
from apiv2.utils import response_api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.views import APIView
from rest_framework import status

from contrib.utils import getLogger

log = getLogger(__name__)

from apiv2.baseviews import ApiDetailView
from auth.backend import MultiAuthentication

from rh.models import Servidor

from adm.apiv2.serializers import UsuarioAdmSerializer

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate


class UsuarioApiAdmView(ApiDetailView):
    """
    View para eibir informações de um usuário
    """

    model = Servidor
    serializer_class = UsuarioAdmSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiAuthentication]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="username", description="Nome de usuário", type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        username = self.request.query_params.get("username", None)

        queryset = self.get_queryset()
        item = get_object_or_404(queryset, user__username=username)
        serializer = self.serializer_class(item)

        return Response(serializer.data)


class AssinadorAthenas(APIView):
    def post(self, request, format=None):
        response = {"message": "", "code": status.HTTP_200_OK}
        try:
            usuario = request.data.get("usuario")
            senha = request.data.get("senha")

            user = authenticate(username=usuario, password=senha)

            if user is not None:
                if user == request.user:
                    response["message"] = "Usuário Autenticado"
                    response["code"] = status.HTTP_200_OK
                else:
                    response["message"] = (
                        "O usuário informado não corresponde ao usuário logado"
                    )
                    response["code"] = status.HTTP_401_UNAUTHORIZED
            else:
                response["message"] = "O usuário ou a senha informados estão incorretos"
                response["code"] = status.HTTP_401_UNAUTHORIZED
        except Exception as e:
            response["message"] = (
                f"Ocorreu um erro ao tentar autenticar o usuário: {str(e)}"
            )
            response["code"] = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=response["code"])


class NotificacaoHermesView(APIView):
    """
    Notificaçoes do hermes
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        resposta = self.buscar_notificacoes_hermes(request)
        if resposta.status_code == 200:
            return response_api_view(resposta.json())
        mensagem = {
            "mensagem": "Erro ao buscar as notificações.",
            "código": resposta.status_code,
        }
        return Response(mensagem, status=resposta.status_code)

    def buscar_notificacoes_hermes(self, request):
        per_page = request.GET.get("per_page", None)
        url = settings.HERMES_URL_NOTIFICACAO
        if per_page:
            url = f"{url}?size={per_page}"
        crowd_token = f"{settings.CROWD_SESSION_NAME}:{request.COOKIES.get(settings.CROWD_SESSION_NAME,None)}"
        encoded_data = base64.b64encode(crowd_token.encode("utf-8"))
        header = {
            "content-type": "application/json",
            "accept": "application/json",
            "Authorization": encoded_data,
        }
        response = requests.get(url, headers=header)
        return response
