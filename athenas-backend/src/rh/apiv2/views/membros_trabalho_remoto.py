from apiv2.baseviews import ListAPIView, ApiCore, ApiDetailView
from drf_spectacular.utils import OpenApiParameter, extend_schema

from rh.apiv2.serializers.membros_trabalho_remeto import MembrosTrabalhoRemotoSerializer

from rh.models import MembersTelecommuting


class MembrosTrabalhoRemotoListView(ListAPIView):
    """
    View de Membros Trabalho Remoto
    """

    model = MembersTelecommuting
    serializer_class = MembrosTrabalhoRemotoSerializer
    queryset = MembersTelecommuting.objects.filter()

    full_text_index = (
        "employee__pessoa_fisica__nome__unaccent__icontains",
        "employee__matricula__icontains",
    )

    def get_queryset(self):
        queryset = self.model.objects.all()

        params = self.request.query_params
        status = params.get("status", None)
        if status:
            queryset = queryset.filter(status=status)
        return self.filter_queryset(queryset)


class MembrosTrabalhoRemotoDetailView(ApiDetailView):
    """
    Detalhes de Membros Trabalho Remoto
    """

    model = MembersTelecommuting
    serializer_class = MembrosTrabalhoRemotoSerializer


class MembrosTrabalhoRemotoCoreView(ApiCore):
    """
    CRUD de Membros Trabalho Remoto
    """

    model = MembersTelecommuting
    serializer_class = MembrosTrabalhoRemotoSerializer
