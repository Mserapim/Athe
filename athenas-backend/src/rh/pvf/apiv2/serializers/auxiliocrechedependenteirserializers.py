from contrib.utils import getLogger
from rest_framework import serializers
from rh.pvf.models import PVFSolicitacaoAuxilioCrecheDepenIR


log = getLogger(__name__)


class PVFSolicitacaoCreteAuxCrecheDepenIRSerializer(serializers.ModelSerializer):
    """
    classe serializer da solicitação de folha ponto
    """

    dependente_id = serializers.SerializerMethodField()
    dependente_name = serializers.SerializerMethodField()
    anexo_id = serializers.SerializerMethodField()
    tipo_parentesco_name = serializers.SerializerMethodField()
    dependente_tipo_name = serializers.SerializerMethodField()

    class Meta:
        model = PVFSolicitacaoAuxilioCrecheDepenIR
        fields = [
            "pk",
            "dependente_id",
            "dependente_name",
            "anexo_id",
            "dependente_aux_creche",
            "dependente_ir",
            "capacidade",
            "tipo_parentesco",
            "tipo_parentesco_name",
            "dependente_tipo",
            "dependente_tipo_name",
            "observacao",
        ]

    def get_dependente_id(sel, obj):
        return obj.pessoa_familia.pk

    def get_dependente_name(sel, obj):
        return obj.pessoa_familia.nome

    def get_anexo_id(sel, obj):
        return obj.anexo.pk

    def get_tipo_parentesco_name(sel, obj):
        return obj.get_tipo_parentesco_display()

    def get_dependente_tipo_name(sel, obj):
        return obj.get_dependente_tipo_display()

    def criar(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            instance = PVFSolicitacaoAuxilioCrecheDepenIR.create(data)
            rst.update(
                success=True,
                message="Registro criado com sucesso.",
                data={"pk": instance.pk},
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst

    def reenviar(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            PVFSolicitacaoAuxilioCrecheDepenIR.reenviar(data)
            rst = {"success": True, "message": "Envio realizado como sucesso."}
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst
