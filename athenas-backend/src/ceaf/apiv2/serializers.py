from apiv2.baseserializers import BaseSerializer

from ceaf.models import Capacitation, Participant

from contrib.utils import getLogger

log = getLogger(__name__)


class CapacitacaoSerializer(BaseSerializer):
    """
    Serializer do model Capacitation (cursos)
    """

    class Meta:
        model = Capacitation
        fields = "__all__"


class ParticipanteSerializer(BaseSerializer):
    """
    Serializer do model Participant
    """

    class Meta:
        model = Participant
        fields = "__all__"
