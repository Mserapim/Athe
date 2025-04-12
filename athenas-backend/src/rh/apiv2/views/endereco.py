from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView

from  rest_framework.exceptions import NotFound
from rh.models import Endereco


from contrib.utils import getLogger
from rh.apiv2.serializers.endereco import EnderecoSerializer
log = getLogger(__name__)



class EnderecoListView(ListBaseView):
    
    serializer_class = EnderecoSerializer
    full_text_index = (
    )

    def get_queryset(self):

        pessoa_id = self.request.GET.get('pessoa_id', None)
        orgao_id = self.request.GET.get('orgao_id', None)


        if pessoa_id or orgao_id:
            if pessoa_id:
                return Endereco.objects.filter(person__id=pessoa_id)
            return Endereco.objects.filter(general_organ__id=orgao_id)
        
        raise NotFound("O parametro pessoa_id ou orgao_id deve ser fornecido")


class EnderecoDetailView(ApiDetailView):
    
    model = Endereco
    serializer_class = EnderecoSerializer
    

class EnderecoApiCore(ApiCore):
    
    model = Endereco
    serializer_class = EnderecoSerializer
