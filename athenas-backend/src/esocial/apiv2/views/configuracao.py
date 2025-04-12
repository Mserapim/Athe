from django.conf import settings
from contrib.middleware import set_current_user
from esocial.apiv2.serializers.configuracao import (
    CertificaoEsocialSerializer,
    ConfiguracaoSerializer,
    EventosChoiceSerializer,
)
from esocial.models import Configuration
from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from esocial.security import extract_certificate
from ged.models import Arquivo
from standard.models import Choice
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response

from contrib.utils import getLogger


log = getLogger(__name__)


class ConfiguracaoView(ListBaseView):
    """
    View das configurações do esocial
    """

    model = Configuration
    serializer_class = ConfiguracaoSerializer
    full_text_index = ()

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset


class EventosChoiceView(ListBaseView):
    """
    View das opçoes correspondente das tabelas do esocial
    """

    model = Choice
    serializer_class = EventosChoiceSerializer
    full_text_index = ("label__unaccent__icontains",)

    def get_queryset(self):
        queryset = self.model.objects.filter(name="ACRONYM")
        return queryset


class ConfiguracaoCoreView(ApiCore):
    """
    CRUD das configurações do esocial
    """

    model = Configuration
    serializer_class = ConfiguracaoSerializer


class AtualizarCertificadoCoreView(ApiCore):
    """
    Atualizar certificado digital do esocial
    """

    model = Configuration

    path_function_map = {
        "atualizar-certificado": "atualizar_certificado",
    }

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "certificado_id": {"type": "integer"},
                    "certificado_senha": {"type": "str"},
                    "certificado_ca_id": {"type": "integer"},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Descrição da operação POST

        executa uma função conforme o path da requisição
        """
        return super(AtualizarCertificadoCoreView, self).post(request, args, kwargs)

    def atualizar_certificado(self, request, *args, **kwargs):
        set_current_user(request.user)
        resposta = {"code": 200, "resposta": "Nada feito"}

        certificado_id = request.data.get("certificado_id")
        certificado = Arquivo.objects.get(pk=certificado_id) if certificado_id else None

        certificado_ca_id = request.data.get("certificado_ca_id")
        certificado_ca = (
            Arquivo.objects.get(pk=certificado_ca_id) if certificado_ca_id else None
        )

        certificado_senha = request.data.get("certificado_senha")

        if certificado and certificado_ca and certificado_senha:
            try:
                extract_certificate(
                    certificate_path=certificado,
                    certificate_ca_path=certificado_ca,
                    passwd=certificado_senha,
                )
                config = Configuration.objects.first()
                config.certificado_a1 = certificado
                config.certificado_cas = certificado_ca
                config.save()
            except Exception as e:
                log.exception(e)
                resposta.update(code=500, resposta="{}".format(e))
            else:
                resposta.update(resposta="Certificado atualizado com sucesso!")
        else:
            resposta.update(
                code=400, resposta="Informe os dados do certificado antes de continuar."
            )

        return Response(resposta, status=resposta["code"])


class CertificadoEsocialView(ApiDetailView):
    """
    View do certificado digital
    """

    model = Configuration
    serializer_class = CertificaoEsocialSerializer

    def get(self, request, *args, **kwargs):
        """
        Descrição da operação GET
        """
        config = Configuration.objects.first()
        serializer = self.serializer_class(config)
        return Response(serializer.data)
