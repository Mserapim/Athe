# -*- coding: utf-8 -*-
import json
from datetime import date

from adm.patrimonio.models import Notification
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.nil import nil_datetime, nil_pk, nil_unicode
from contrib.utils import employee_from_user, getLogger
from rh.models import Lotacao


log = getLogger(__name__)


class PATNotification(RestfulDRY):

    _model = Notification

    force_orm_single = True

    force_upper = False

    exclude_fields = [""]

    def model_to_dict(self, instance):
        _dict_ = super(PATNotification, self).model_to_dict(instance)

        _dict_.update(
            {
                "icons": instance.icons,
                "protocol_unicode": (
                    instance.protocol.codigo if instance.protocol else ""
                ),
                "received_by": nil_pk(instance.received_by, None),
                "received_by_unicode": nil_unicode(instance.received_by, None),
                "received_at": nil_datetime(instance.received_at, None),
                "was_sent": instance.was_sent,
            }
        )

        return _dict_

    def get_origin(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            employee = work_locations = None
            employee = employee_from_user(get_current_user())
            work_locations = Lotacao.objects.filter(
                pk__in=employee.get_work_assignment(date=date.today()).values_list(
                    "lotacao", flat=True
                )
            )
        except Exception as e:
            self.log.exception(e)
            obj.update(message=str(e))
        else:
            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=work_locations.count(),
                collection=[
                    {"pk": l.pk, "description": str(l.nome)} for l in work_locations
                ],
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def send(self, *args):
        result = {"success": False, "message": "Nothing done yet."}

        try:
            pkset = self.request.POST.getlist("pkset")
            if not len(pkset):
                raise ValueError(
                    "Forneça um array de notificações para o parâmetro 'pkset'."
                )

            notifications = self.Model.objects.filter(pk__in=pkset)
            for notification in notifications:
                if not notification.was_sent:
                    notification.send()
        except Exception as e:
            log.exception(e)
            result.update(message=str(e))
        else:
            result.update(
                success=True, message="Notificação(ões) enviada(s) com sucesso."
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(result))

    def bulk_send(self, *args):
        """Envia notificações em lote

        Etapas:
            - Para cada Movimento:
                - Gera uma notificação
            - Para cada notificação gerada:
                - Gera um Termo de Responsabilidade
                - Gera um protocolo
                - Anexa o Termo de Responsabilidade ao protocolo
                - Despacha o protocolo

        """
        from adm.patrimonio.tasks import bulk_send

        result = {"success": False, "message": "Nothing done yet."}

        try:
            # Espera-se uma lista de ids de Movimento
            pkset = self.request.REQUEST.getlist("pkset")
            if not len(pkset):
                raise ValueError(
                    "Forneça um array de movimentações para o parâmetro 'pkset'."
                )

            bulk_send.delay(movements_pk=pkset, username=get_current_user().username)
        except Exception as e:
            log.exception(e)
            result.update(message=str(e))
        else:
            result.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(result))
