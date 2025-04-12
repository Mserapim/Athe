# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from judicial.models import DeliveryAttempt
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class EJudDeliveryAttempt(RestfulDRY):

    _model = DeliveryAttempt

    force_upper = False

    force_orm_single = True

    def sign(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        pk = args[0] if args else 0

        try:
            obj = self.Model.objects.get(pk=pk)
            obj.sign()
        except self.Model.DoesNotExist:
            rst.update(message="Não consegui encontrar o documento desejado.")
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Documento assinado com sucesso.",
                instance=self.model_to_dict(obj),
            )

        self.renderer(rst)

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            icons_sign=instance.icons_sign,
            delivered=instance.delivered,
            delivered_display=nil_display(instance, "delivered", None),
            cancel_delivery=instance.cancel_delivery,
            cancel_delivery_type=instance.cancel_delivery_type,
            cancel_delivery_type_display=nil_display(
                instance, "cancel_delivery_type", None
            ),
            type_vehicle=instance.type_vehicle,
            type_vehicle_display=nil_display(instance, "type_vehicle", None),
            exit_date=nil_datetime(instance.exit_date, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            observation=instance.observation,
            diligence=nil_pk(instance.diligence, None),
            diligence_unicode=nil_unicode(instance.diligence, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            delivery_date=nil_datetime(instance.delivery_date, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            attempt=instance.attempt,
            return_date=nil_datetime(instance.return_date, None),
            file_delivery=instance.file_delivery.pk if instance.file_delivery else None,
            file_delivery_permalink=(
                instance.file_delivery.complete_permalink()
                if instance.file_delivery
                else None
            ),
            file_delivery_hash=(
                instance.file_delivery.file if instance.file_delivery else None
            ),
        )

        return rst

    def render_delivery_attempt(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        oid = args[0] if args else 0

        try:
            rst.update(
                success=True,
                message="Dados processados com sucesso",
                rendered=self.Model.objects.get(pk=oid).rendered,
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
