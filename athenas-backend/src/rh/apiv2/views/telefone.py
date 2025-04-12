from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView

from  rest_framework.exceptions import NotFound
from rh.models import Telefone


from contrib.utils import getLogger
from rh.apiv2.serializers.telefone import TelefoneSerializer
log = getLogger(__name__)



class TelefoneListView(ListBaseView):
    
    serializer_class = TelefoneSerializer
    full_text_index = (
    )

    def get_queryset(self):

        pessoa_id = self.request.GET.get('pessoa_id', None)
        if pessoa_id:
            return Telefone.objects.filter(person__id=pessoa_id)
        
        raise NotFound("O parametro pessoa_id não foi fornecido")


class TelefoneDetailView(ApiDetailView):
    
    model = Telefone
    serializer_class = TelefoneSerializer
    

class TelefoneApiCore(ApiCore):
    
    model = Telefone
    serializer_class = TelefoneSerializer