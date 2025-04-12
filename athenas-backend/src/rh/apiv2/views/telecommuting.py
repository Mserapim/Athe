from rest_framework.permissions import IsAuthenticated

from auth.backend import CustomTokenJWTAuthentication
from rh.apiv2.serializers.telecommuting import TelecommutingSerializer
from rh.lotacionogram import get_data_resume
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from apiv2.pagination import CustomPagination
from rh.models import MembersTelecommuting


class TelecommutingView(ListAPIView):
    """
    View de Membros em Trabalho Remoto

    Esta classe é responsável por fornecer uma lista paginada de Membros em Trabalho Remoto.
    """

    queryset = MembersTelecommuting.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    pagination_class = CustomPagination
    serializer_class = TelecommutingSerializer
    full_text_index = ("nome__unaccent__icontains",)

    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada de Comarcas.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
