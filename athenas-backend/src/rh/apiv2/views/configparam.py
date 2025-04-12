from rh.apiv2.serializers.configparam import ConfigParamSerializer
from rest_framework.permissions import IsAuthenticated
from auth.backend import CustomTokenJWTAuthentication
from standard.models import Choice
from apiv2.baseviews import ListBaseView

from contrib.utils import getLogger

log = getLogger(__name__)


class ConfigTypeDepedentView(ListBaseView):
    """
    View Config tipo de dependente

    Esta classe é responsável por fornecer uma lista paginada das configurações de tipo de dependente.

    :queryset: conjunto de objetos do modelo Comarca
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Choice.objects.all()
    serializer_class = ConfigParamSerializer

    def get_queryset(self):
        return self.queryset.filter(name="DEPENDENT_TYPE")


class ConfigDegreekinshiptView(ListBaseView):
    """
    View Config grau de parentesco

    Esta classe é responsável por fornecer uma lista paginada das configurações de grau de parentesco.

    :queryset: conjunto de objetos do modelo Choice
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Choice.objects.all()
    serializer_class = ConfigParamSerializer

    def get_queryset(self):
        return self.queryset.filter(name="GRAU_PARENTESCO_CHOICES")


class ConfigSexualOrientationView(ListBaseView):
    """
    View Config de orientação sexual

    Esta classe é responsável por fornecer uma lista paginada das configurações orientação sexual.

    :queryset: conjunto de objetos do modelo Choice
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Choice.objects.all()
    serializer_class = ConfigParamSerializer

    def get_queryset(self):
        return self.queryset.filter(name="SEXUAL_ORIENTATION")


class ConfigImigrantResidenceTimeView(ListBaseView):
    """
    View Config de imigrante tempo de residência

    Esta classe é responsável por fornecer uma lista paginada das configuraçõesimigrante tempo de residência.

    :queryset: conjunto de objetos do modelo Choice
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Choice.objects.all()
    serializer_class = ConfigParamSerializer

    def get_queryset(self):
        return self.queryset.filter(name="IMMIGRANTE_RESIDENCE_TIME")


class ConfigImigranteEntryConditionView(ListBaseView):
    """
    View Config de condição de imigrante

    Esta classe é responsável por fornecer uma lista paginada das configurações condição de imigrante.

    :queryset: conjunto de objetos do modelo Choice
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Choice.objects.all()
    serializer_class = ConfigParamSerializer

    def get_queryset(self):
        return self.queryset.filter(name="IMMIGRANTE_ENTRY_CONDITION")
