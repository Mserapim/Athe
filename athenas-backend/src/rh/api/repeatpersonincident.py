# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import RepeatPersonIncident


log = getLogger(__name__)


class RHRepeatPersonIncident(RestfulDRY):

    _model = RepeatPersonIncident

    def mark_false(self, args=[]):
        [pk] = args
        rst = {"success": False, "message": "not implemented"}

        try:
            incident = self.get_query().get(pk=pk)
            incident.mark_as(3)
            rst.update(
                success=True, message="Item marcado como falso positivo com sucesso."
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o item que desejava marcar com falso."
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def merge(self, args=[]):
        [pk] = args
        rst = {"success": False, "message": "not implemented"}

        try:
            incident = self.get_query().get(pk=pk)
            incident.mark_as(2)
            rst.update(
                success=True, message="Item marcado como falso positivo com sucesso."
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o item que desejava marcar com falso."
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        rst.update(
            target_person_rate_fill=float(instance.target_person.rate_fill),
            main_person_rate_fill=float(instance.main_person.rate_fill),
            target_person_kind=instance.target_person.kind,
            main_person_kind=instance.main_person.kind,
        )

        return rst

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.person.repeatPersonIncident.Manage")')
