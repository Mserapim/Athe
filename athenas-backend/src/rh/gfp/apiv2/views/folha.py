from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView

from  rest_framework.exceptions import NotFound
from rh.gfp.models import Folha


from contrib.utils import getLogger
from rh.gfp.apiv2.serializers.folha import FolhaSerializer
log = getLogger(__name__)



class FolhaListView(ListBaseView):
    
    serializer_class = FolhaSerializer
    full_text_index = (
    )

    def get_queryset(self):

        return Folha.objects.filter()
        

class FolhaDetailView(ApiDetailView):
    
    model = Folha
    serializer_class = FolhaSerializer
    

class FolhaApiCore(ApiCore):
    
    model = Folha
    serializer_class = FolhaSerializer
