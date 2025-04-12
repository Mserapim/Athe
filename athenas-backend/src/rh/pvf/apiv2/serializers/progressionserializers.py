from gettext import translation
from contrib.middleware import get_current_user
from ged.models import Arquivo
from rh.gfp.models import (
    HorizontalProgressionConfig,
    MovimentacaoProgressao,
    ProgressionDocument,
)
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
from contrib.utils import getLogger
from rh.pvf.const import MSG_SUCCESS_METHOD
from rh.pvf.models import (
    PRProgressionHDocument,
    PortalRequestProgression,
    PortalRequestProgressionH,
)
from django.db import transaction
import json

log = getLogger(__name__)


class PVFMovProgressionHSerializers(serializers.ModelSerializer):
    """
    classe serializer movimentação de progressão
    """

    reference = serializers.CharField(source="__str__")
    mov_posse = serializers.CharField(source="mov_posse_str")

    class Meta:
        model = MovimentacaoProgressao
        fields = ["pk", "mov_posse", "reference", "expected_date"]


class PVFConfigProgressionHSerializers(serializers.ModelSerializer):
    """
    classe serializer config da movimentação de progressão
    """

    class Meta:
        model = HorizontalProgressionConfig
        fields = [
            "pk",
            "name",
            "description",
            "target_level",
            "contribution_time",
            "qtd_documents",
            "schooling_str",
        ]


class PVFDocumentProgressionHSerializers(serializers.ModelSerializer):
    """
    classe serializer de documentos da solicitação de progressão horizontal
    """

    doc_origin_display = serializers.SerializerMethodField()

    class Meta:
        model = PRProgressionHDocument
        fields = [
            "pk",
            "pr_progression_h",
            "pr_progression_h_str",
            "description",
            "attachment",
            "doc_origin",
            "doc_origin_display",
        ]

    def get_doc_origin_display(self, obj):
        return obj.get_doc_origin_display(obj.doc_origin)

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            self.is_valid(raise_exception=True)
            self.save()
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

    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            self.is_valid(raise_exception=True)
            self.save()
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


class PVFDocumentProgressionVSerializers(serializers.ModelSerializer):
    """
    classe serializer de documentos da solicitação de progressão vertical
    """

    class Meta:
        model = ProgressionDocument
        fields = ["pk", "progression", "description", "attachment", "doc_origin"]

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            request = PortalRequestProgression.objects.filter(
                pk=self._kwargs["data"]["request_id"]
            ).first()
            self._kwargs["data"].update({"progression": request.progression})
            self._kwargs["data"].pop("request_id")
            self.is_valid(raise_exception=True)
            self.save()
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

    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            request = PortalRequestProgression.objects.filter(
                pk=self._kwargs["data"]["request_id"]
            ).first()
            self._kwargs["data"].update({"progression": request.progression})
            self._kwargs["data"].pop("request_id")
            self.is_valid(raise_exception=True)
            self.save()
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


class PVFSendProgressionHViewSetSerializer(serializers.ModelSerializer):
    """
    classe serializer de envio da solicitação de progressão horizontal
    """

    class Meta:
        model = PortalRequestProgressionH
        fields = "__all__"

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            with transaction.atomic():
                user = get_current_user()
                progression = data.get("progression")
                config = data.get("config")
                documents = json.loads(json.dumps(data.get("documents", "[]")))
                termo_aceite = data.get("termo_aceite")
                self.validar_solicitacao_em_andamento(user, progression, config)
                if progression:
                    progression = MovimentacaoProgressao.objects.get(pk=progression)
                if config:
                    config = HorizontalProgressionConfig.objects.get(pk=config)
                instance = self.Meta.model.create(progression, config, termo_aceite)
                docs = []
                for document in documents:
                    attach_id = document.get("attachment_id")
                    obj = PRProgressionHDocument(
                        pr_progression_h=instance,
                        description=document.get("name"),
                        attachment=(
                            Arquivo.objects.get(pk=attach_id) if attach_id else None
                        ),
                        created_by_id=user.id,
                        modified_by_id=user.id,
                    )
                    docs.append(obj)
                PRProgressionHDocument.objects.bulk_create(docs)
                rst.update(
                    success=True,
                    message="Registro criado com sucesso.",
                    data={"pk": instance.pk},
                )
        except ValidationError as e:
            rst.update({"message": e.detail})
            return rst
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst

    def update(self, pk, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            with transaction.atomic():
                user = get_current_user()
                documents = json.loads(json.dumps(data.get("documents", "[]")))
                instance = PortalRequestProgressionH.objects.filter(id=pk).first()
                docs = []
                for document in documents:
                    attach_id = document.get("attachment_id")
                    description = document.get("description") or document.get("name")
                    obj = PRProgressionHDocument(
                        pr_progression_h=instance,
                        description=description,
                        attachment=(
                            Arquivo.objects.get(pk=attach_id) if attach_id else None
                        ),
                        created_by_id=user.id,
                        modified_by_id=user.id,
                    )
                    docs.append(obj)
                PRProgressionHDocument.objects.bulk_create(docs)
                instance.resend_request()

                rst.update(
                    success=True,
                    message="Registro criado com sucesso.",
                    data={"pk": instance.pk},
                )
        except ValidationError as e:
            rst.update({"message": e.detail})
            return rst
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst

    def validar_solicitacao_em_andamento(self, user, progression, config):
        if (
            PortalRequestProgressionH.objects.exclude(
                status__in=[
                    4,
                    5,
                    6,
                    7,
                ]  # Efetivado, Cancelado DGP, Cancelado Solicitante e Indeferido
            )
            .filter(
                employee=user.servidor,
                progression=progression,
                config=config,
            )
            .exists()
        ):
            raise ValidationError(
                "Já existe uma solicitação em andamento para esta progressão."
            )

    def send(self, pk):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            instance = PortalRequestProgressionH.objects.get(pk=pk)
            instance.resend_request()
            rst = {"success": True, "message": "Envio realizado como sucesso."}
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst
