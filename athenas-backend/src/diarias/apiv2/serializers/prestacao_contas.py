from apiv2.baseserializers import BaseSerializer
import django.db.models
from rest_framework import serializers
from diarias.models import Beneficiario, PrestacaoContas, PrestacaoContasAnexo
from rest_framework import status
from django.db import transaction
from contrib.utils import getLogger
import rest_framework.serializers
from ged.apiv2.serializers import ArquivoSerializer
from ged.models import Arquivo
from apiv2.const import MSG_SUCCESS_METHOD
from rh.gfp.models import BankingConvenant


log = getLogger(__name__)


class PrestacaoContasSerializer(BaseSerializer):

    anexos = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    assinado_por_nome = serializers.SerializerMethodField()
    beneficiario_nome = serializers.SerializerMethodField()
    beneficiario_matricula = serializers.SerializerMethodField()
    beneficiario_situcacao = serializers.SerializerMethodField()
    beneficiario_categoria_funcional = serializers.SerializerMethodField()
    status_servidor = serializers.SerializerMethodField()
    avaliador_nome = serializers.SerializerMethodField()
    doc_encerramento_obj = ArquivoSerializer(source="doc_encerramento", read_only=True)
    viagem = serializers.IntegerField(source="beneficiario.viagem.id", read_only=True)

    class Meta:
        model = PrestacaoContas
        fields = "__all__"

    def get_assinado_por_nome(self, obj):
        return obj.assinado_por_nome

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_anexos(self, obj):
        anexos = [a.arquivo for a in obj.anexos.all()]
        return ArquivoSerializer(anexos, many=True).data

    def get_beneficiario_nome(self, obj):
        return obj.beneficiario.servidor.pessoa_fisica.social_name

    def get_beneficiario_matricula(self, obj):
        return obj.beneficiario.servidor.matricula

    def get_beneficiario_situcacao(self, obj):
        return obj.beneficiario.fluxo.get_situacao_display()

    def get_beneficiario_categoria_funcional(self, obj):
        return obj.beneficiario.servidor.type_by_possession

    def get_status_servidor(self, obj):
        return obj.beneficiario.servidor.ativo

    def get_avaliador_nome(self, obj):
        if obj.avaliador:
            return obj.avaliador.pessoa_fisica.social_name or ""
        return ""

    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            with transaction.atomic():
                self.is_valid(raise_exception=True)
                self.save()

                request = self.context.get("request")
                anexos = request.data.get("anexos", None)

                if anexos:
                    for anexo_id in anexos:
                        arquivo = Arquivo.objects.get(pk=anexo_id)

                        anexo, _ = PrestacaoContasAnexo.objects.get_or_create(
                            prestacao=self.instance, arquivo=arquivo
                        )

                rst.update(
                    {
                        "success": True,
                        "message": MSG_SUCCESS_METHOD["put"],
                        "data": self.data,
                    }
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


class ContaMpmtSerializer(BaseSerializer):
    banco = serializers.SerializerMethodField()
    agencia = serializers.SerializerMethodField()
    conta = serializers.SerializerMethodField()
    chave_pix = serializers.SerializerMethodField()

    class Meta:
        model = BankingConvenant
        fields = ["banco", "agencia", "conta", "chave_pix"]

    def get_banco(self, obj):
        return str(obj.bank)

    def get_agencia(self, obj):
        return f"{obj.agency_cod}-{obj.agency_cod_dv}"

    def get_conta(self, obj):
        return f"{obj.account_cod}-{obj.account_cod_dv}"

    def get_chave_pix(self, obj):
        return obj.chave_pix
