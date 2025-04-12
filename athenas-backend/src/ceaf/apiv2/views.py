from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView


from ceaf.models import Capacitation, Participant
from ceaf.apiv2.serializers import CapacitacaoSerializer, ParticipanteSerializer


class CapacitacaoListView(ListBaseView):
    model = Capacitation
    serializer_class = CapacitacaoSerializer
    full_text_index = (
        "name__icontains",
        "description__icontains",
        "local__icontains",
        "period__icontains",
    )
    queryset = Capacitation.objects.filter()


class CapacitacaoDetailView(ApiDetailView):
    model = Capacitation
    serializer_class = CapacitacaoSerializer


class CapacitacaoApiCore(ApiCore):
    model = Capacitation
    serializer_class = CapacitacaoSerializer


class ParticipanteListView(ListBaseView):
    model = Participant
    serializer_class = ParticipanteSerializer
    full_text_index = ("name__icontains", "employee__matricula__icontains")
    queryset = Participant.objects.filter()


class ParticipanteDetailView(ApiDetailView):
    model = Participant
    serializer_class = ParticipanteSerializer


class ParticipanteApiCore(ApiCore):
    model = Participant
    serializer_class = ParticipanteSerializer
