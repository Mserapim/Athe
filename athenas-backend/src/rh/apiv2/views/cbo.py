from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView

from rh.models import Cbo
from rh.apiv2.serializers.cbo import CboSerializer


from contrib.utils import getLogger

log = getLogger(__name__)


class CboListView(ListBaseView):

    queryset = Cbo.objects.filter()
    serializer_class = CboSerializer
    full_text_index = (
        "codigo__icontains",
        "descricao__icontains",
    )


class CboDetailView(ApiDetailView):

    model = Cbo
    serializer_class = CboSerializer


class CboApiCore(ApiCore):

    model = Cbo
    serializer_class = CboSerializer
