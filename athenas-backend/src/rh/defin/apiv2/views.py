from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView

from rh.models import PessoaFisica
from rh.defin.apiv2.serializers import (
    ColaboradorPfSerializer,
    PagamentoColaboradorSerializer,
)

from rh.defin.models import PFProviderEntry

from django.http import Http404

from contrib.utils import getLogger

log = getLogger(__name__)


class ColaboradorPfListView(ListBaseView):

    queryset = PessoaFisica.objects.filter(servidor__type_by_possession="COE")
    serializer_class = ColaboradorPfSerializer
    full_text_index = (
        "nome__unaccent__icontains",
        "social_name__unaccent__icontains",
        "cpf__icontains",
    )


class ColaboradorPfDetailView(ApiDetailView):

    model = PessoaFisica
    serializer_class = ColaboradorPfSerializer


class ColaboradorPfApiCore(ApiCore):

    model = PessoaFisica
    serializer_class = ColaboradorPfSerializer


class PagamentoColaboradorListView(ListBaseView):

    serializer_class = PagamentoColaboradorSerializer
    model = PFProviderEntry
    full_text_index = ()

    def get_queryset(self):
        """
        Ajustando para pegar os pagmentos referentes ao Colaborador Eventual
        """
        pk_colaborador = self.request.GET.get("colaborador_id", None)
        if pk_colaborador:
            return self.model.objects.filter(natural_person=pk_colaborador)

        raise Http404("O parametro colaborador_id não foi fornecido")


class PagamentoColaboradorDetailView(ApiDetailView):

    model = PFProviderEntry
    serializer_class = PagamentoColaboradorSerializer


class PagamentoColaboradorApiCore(ApiCore):

    model = PFProviderEntry
    serializer_class = PagamentoColaboradorSerializer
