from apiv2.baseserializers import BaseSerializer
from diarias.models import Destino, EventoBeneficiario, VeiculoPassageiro, VeiculoViagem
from rest_framework import status
from apiv2.const import MSG_SUCCESS_METHOD

from rest_framework import serializers


from contrib.utils import getLogger

log = getLogger(__name__)


class DestinoSerializer(BaseSerializer):

    uf_origem = serializers.SerializerMethodField()
    uf_origem_display = serializers.SerializerMethodField()
    uf_destino = serializers.SerializerMethodField()
    uf_destino_display = serializers.SerializerMethodField()
    municipio_origem_display = serializers.SerializerMethodField()
    municipio_destino_display = serializers.SerializerMethodField()
    uf_origem_sigla = serializers.SerializerMethodField()
    uf_destino_sigla = serializers.SerializerMethodField()
    forma_deslocamento_display = serializers.SerializerMethodField()
    pref_turno_ida_display = serializers.SerializerMethodField()
    evento = serializers.SerializerMethodField()
    evento_display = serializers.SerializerMethodField()
    analise_daa = serializers.SerializerMethodField()
    beneficiario_unicode = serializers.SerializerMethodField()

    class Meta:
        model = Destino
        fields = "__all__"

    def get_uf_origem(self, obj):
        return obj.municipio_origem.estado.pk

    def get_uf_origem_display(self, obj):
        return obj.municipio_origem.estado.nome

    def get_uf_destino(self, obj):
        return obj.municipio_destino.estado.pk

    def get_uf_destino_display(self, obj):
        return obj.municipio_destino.estado.nome

    def get_municipio_origem_display(self, obj):
        return obj.municipio_origem.nome

    def get_municipio_destino_display(self, obj):
        return obj.municipio_destino.nome

    def get_uf_origem_sigla(self, obj):
        return obj.municipio_origem.estado.sigla

    def get_uf_destino_sigla(self, obj):
        return obj.municipio_destino.estado.sigla

    def get_forma_deslocamento_display(self, obj):
        return obj.get_forma_deslocamento_display()

    def get_pref_turno_ida_display(self, obj):
        return obj.get_pref_turno_ida_display()

    def get_evento(self, obj):
        return obj.eventos.first().id if obj.eventos.exists() else None

    def get_evento_display(self, obj):
        if obj.eventos.exists():
            evento = obj.eventos.first()
            dt_inicio = evento.data_inicio.strftime("%d/%m/%Y")
            dt_fim = (
                f" até {evento.data_fim.strftime('%d/%m/%Y')}"
                if evento.data_fim
                else ""
            )
            txt_data = f"de {dt_inicio}{dt_fim}" if dt_fim else f"data: {dt_inicio}"
            return f"{evento.titulo} - {txt_data}"
        return ""

    def get_analise_daa(self, obj):
        return obj.analise_daa

    def get_beneficiario_unicode(self, obj):
        return f"{obj.beneficiario.servidor.matricula} - {obj.beneficiario.servidor.pessoa_fisica.social_name}"

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            request = self.context.get("request")
            evento_id = request.data.get("evento")
            evento = EventoBeneficiario.objects.get(id=evento_id)

            self.is_valid(raise_exception=True)
            self.save()

            evento.destinos.add(self.instance)

            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["post"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst
