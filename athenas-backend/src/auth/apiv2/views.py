
# coding: utf-8
from auth.backend import ExternalJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from drf_spectacular.utils import OpenApiParameter, extend_schema

from contrib.mastiff import get_permission
from contrib.utils import getLogger
from apiv2.utils import response_api_view

log = getLogger(__name__)


class MastiffPermissionView(APIView):
    """
    View que retorna as permissões (mastiff) do usuário logado
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="app", description="Aplicativo", type=str),
        ]
    )
    def get(self, request):
        permission_data = get_permission(request, request.GET.get("app", ""))
        return response_api_view(permission_data)


class TokenObtainView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        auth = ExternalJWTAuthentication
        user, autheticate = auth.authenticate_login(request, "basic")
        if autheticate:
            data = {
                "user": user.id,
            }
            return Response({"access_token": auth.create_access_token(data, 30)})

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_full(request):
    """
    Endpoint que retorna todos os dados do usuário logado em uma única chamada:
    - dados do usuário
    - permissões (mastiff)
    - menus
    - favoritos
    - sessão
    """
    user = request.user

    # Dados do usuário
    usuario = {
        "id": user.id,
        "nome": user.get_full_name(),
        "email": user.email,
        "matricula": getattr(user, "matricula", None),
        "lotacao": getattr(user, "lotacao", None),
    }

    # Permissões usando mastiff
    permissoes = get_permission(request, request.GET.get("app", ""))

    # Aqui você coloca a lógica real para montar menus e favoritos, por enquanto vazio
    menus = []
    favoritos = []

    ip = request.META.get("REMOTE_ADDR")

    return Response({
        "usuario": usuario,
        "permissoes": permissoes,
        "menus": menus,
        "favoritos": favoritos,
        "sessao": {
            "ultimo_login": user.last_login,
            "ip": ip
        }
    })




# from auth.backend import ExternalJWTAuthentication
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from contrib.mastiff import get_permission
# from rest_framework.response import Response
# from drf_spectacular.utils import OpenApiParameter, extend_schema
# from apiv2.utils import response_api_view
# from rest_framework import status

# from contrib.utils import getLogger

# log = getLogger(__name__)


# class MastiffPermissionView(APIView):
#     """
#     View que retorna as permissões(mastiff) do usuário logado
#     """

#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         parameters=[
#             OpenApiParameter(name="app", description="Aplicativo", type=str),
#         ]
#     )
#     def get(self, request):
#         permission_data = get_permission(request, request.GET.get("app", ""))
#         return response_api_view(permission_data)


# class TokenObtainView(APIView):

#     permission_classes = []
#     authentication_classes = []

#     def get(self, request, *args, **kwargs):
#         auth = ExternalJWTAuthentication
#         user, autheticate = auth.authenticate_login(request, "basic")
#         if autheticate:
#             data = {
#                 "user": user.id,
#             }
#             return Response({"access_token": auth.create_access_token(data, 30)})

#         return Response(
#             {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
#         )
