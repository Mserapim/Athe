from contrib.middleware import set_current_user

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from standard.apiv2.serializers.classcodes import ClasscodesSerializer

from standard.models import ClassCode, TYPEOFEXECUTION

from apiv2.utils import response_api_view
from contrib.utils import getLogger

log = getLogger(__name__)


class ClasscodesView(ListBaseView):
    """
    View da lista de Classcodes
    """

    permission_classes = [IsAuthenticated]
    queryset = ClassCode.objects.filter()
    serializer_class = ClasscodesSerializer
    full_text_index = (
        "slug__icontains",
        "title__icontains",
        "description__icontains",
    )


class ClasscodesDetailView(ApiDetailView):
    """
    View de detalhes do Classcode
    """

    model = ClassCode
    serializer_class = ClasscodesSerializer


class ClasscodesApicoreView(ApiCore):
    """
    View da Criar, editar e apagar o Classcode
    """

    model = ClassCode
    serializer_class = ClasscodesSerializer
    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
    }


class TiposClasscodesView(ListBaseView):
    """
    View para retornar os Tipos classcodes
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        View da lista de tipos de classcodes
        """

        rst = []
        for item in TYPEOFEXECUTION.items():
            rst.append({"sigla": item[0], "texto": item[1]})

        return response_api_view(rst)
