from ged.models import Arquivo
from rest_framework.serializers import ModelSerializer
from rh.pvf.models import (
    PortalRequest,
    PRProgressionHDocument,
    PortalRequestProgressionH,
)
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from rh.pvf.const import REQUEST_STEP_GER_DEV
from rest_framework import serializers
import json

from rh.gratifications_manager.cumulative_exercices_utils import (
    validar_periodo_vigente_exerc_cumul_subs,
)


log = getLogger(__name__)


class PVFApprovalActionsSerializer(serializers.Serializer):
    """
    classe serializer das ações permitidas para aprovação da solicitação
    """

    label = serializers.CharField()
    action = serializers.CharField()
    disabled = serializers.BooleanField()


class PVFRequestAuthorizeSerializer(ModelSerializer):
    """
    classe serializer para realiza as operações do fluxo de aprovação
    (deferir, indeferir, efetivar, cancelar, ciência e anotar)
    """

    class Meta:
        model = PortalRequest
        fields = []

    def authorize(self, data, request):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        user = get_current_user()
        documents = json.loads(json.dumps(data.get("documents", [])))
        action = data.get("action")
        klass = request.get_classe()
        try:
            docs = []
            for document in documents:
                attach_id = (
                    document.get("attachment_id")
                    if document.get("attachment_id")
                    else document.get("fileId")
                )
                arquivo = Arquivo.objects.filter(pk=attach_id) if attach_id else None
                if arquivo:
                    obj = PRProgressionHDocument(
                        pr_progression_h=PortalRequestProgressionH.objects.get(
                            id=data.get("requestId")
                        ),
                        doc_origin=REQUEST_STEP_GER_DEV,
                        description=document.get("name"),
                        attachment=(
                            Arquivo.objects.get(pk=attach_id) if attach_id else None
                        ),
                        created_by_id=user.id,
                        modified_by_id=user.id,
                    )
                    docs.append(obj)
            PRProgressionHDocument.objects.bulk_create(docs)

            success = True
            message = "Procedimento realizado com sucesso."
            if action == "consolidated":
                validacao_periodo = validar_periodo_vigente_exerc_cumul_subs()
                if validacao_periodo["success"] == False:
                    success = False
                    message = validacao_periodo["msg"]

            if success == True:
                klass.homologar_indeferir(request, data)

            rst.update(success=success, message=message)

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst
