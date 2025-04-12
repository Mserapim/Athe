from apiv2.baseviews import ApiCore, ListBaseView, ApiDetailView

from diarias.apiv2.serializers.evento import EventoSerializer
from diarias.models import EventoBeneficiario, Destino, Beneficiario
from rest_framework.response import Response
from rest_framework import status
from contrib.middleware import set_current_user
from rest_framework.views import APIView

from contrib.utils import getLogger
from diarias.utils.utils import clonar_evento


log = getLogger(__name__)


class EventosApiList(ListBaseView):

    serializer_class = EventoSerializer
    model = EventoBeneficiario

    def get_queryset(self):
        beneficiario = self.request.GET.get("beneficiario")
        return EventoBeneficiario.objects.filter(beneficiario__pk=beneficiario)


class EventoApiCore(ApiCore):

    serializer_class = EventoSerializer
    model = EventoBeneficiario

    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
        "clonar": "clonar",
    }

    def clonar(self, request, *args, **kwargs):
        resposta = {"code": 200, "datail": "Nada Feito"}

        try:
            set_current_user(request.user)
            instance = self.get_object()

            beneficiarios_id = request.data.get("beneficiarios")
            if beneficiarios_id:
                for beneficiario in Beneficiario.objects.filter(
                    pk__in=beneficiarios_id
                ):
                    clonar_evento(instance, beneficiario)
                resposta["datail"] = "Evento Clonado com sucesso"
            else:
                resposta["datail"] = "Lista de beneficiarios não informada"

        except self.model.DoesNotExist:
            resposta["datail"] = "Evento Não encontrado"
            resposta["code"] = 400
        except Exception as e:
            resposta["datail"] = f"Erro ao tentar clonar o evento - {e}"
            resposta["code"] = 400

        return Response(resposta, status=resposta["code"])


class EventoDetailView(ApiDetailView):

    serializer_class = EventoSerializer
    model = EventoBeneficiario


class EventoCloneLoteView(APIView):

    def post(self, request, format=None):
        beneficiario_base = request.data.get("beneficiario_base")
        beneficiarios = request.data.get("beneficiarios")

        try:
            set_current_user(request.user)

            eventos = EventoBeneficiario.objects.filter(
                beneficiario__pk=beneficiario_base
            )
            beneficiarios = Beneficiario.objects.filter(pk__in=beneficiarios)

            for evento in eventos:
                for beneficiario in beneficiarios:
                    clonar_evento(evento, beneficiario)

            return Response(
                {"message": "Eventos Clonados"}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
