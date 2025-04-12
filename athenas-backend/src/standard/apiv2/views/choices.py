from contrib.middleware import set_current_user

from rest_framework.permissions import IsAuthenticated

from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from standard.apiv2.serializers.choices import ChoicesFormularioSerializer

from standard.models import Choice
from  rest_framework.exceptions import NotFound

from contrib.utils import getLogger

log = getLogger(__name__)


class ChoicesListFormulariosView(ListBaseView):
    """
    View da lista de Choices para formularios
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ChoicesFormularioSerializer
    full_text_index = (
        'description__icontains',
        'label__icontains',
    )

    def get_queryset(self):
        app = self.request.GET.get('app', None)
        name = self.request.GET.get('name', None)
        if app and name:
            return Choice.objects.filter(app_label=app, name=name)
        
        raise NotFound("Os parametros app e name são obrigatorios.")
        
