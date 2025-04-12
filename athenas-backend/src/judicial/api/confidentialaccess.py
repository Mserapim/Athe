# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import (
    GrantConfidentialAccess,
    PartLawsuit,
    RevokeConfidentialAccess,
)
from contrib.nil import nil_pk, nil_unicode
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudConfidentialAccess(BasePartLawsuit, Restful):

    def request_params(self):
        params = {}
        for key in list(self.request.POST.keys()):
            value = self.request.POST.getlist(key)
            if len(value) > 1:
                params.update({key: value})
            else:
                params.update({key: value[0]})

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudConfidentialAccess, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                apply_in=instance.apply_in,
            )

        return rst

    def valueOfList(sefl, values=[]):
        return values if isinstance(values, (tuple, list, set)) is True else [values]

    def markerPartLawsuit(self, *args, **kargs):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        try:
            params = self.request_params()

            confidentialaccess = self.get_query().get(
                pk=int(params.get("confidentialaccess", 0))
            )

            parts = self.valueOfList(values=params.get("part", 0))
            log.info(parts)
            if confidentialaccess.signed:
                raise Exception(
                    "O documento encontra-se assinado. Por isso não pode ser modificado."
                )

            for p in PartLawsuit.objects.filter(pk__in=parts):
                confidentialaccess.add_part(part=p)

        except self.Model.DoesNotExist:
            rst.update(message="Não foi encontrado o documento desejado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Adicionado",
            )

        self.renderer(rst)

    def unmarkerPartLawsuit(self, *args, **kargs):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        try:
            params = self.request_params()

            confidentialaccess = self.get_query().get(
                pk=int(params.get("confidentialaccess", 0))
            )
            parts = self.valueOfList(values=params.get("part", 0))

            if confidentialaccess.signed:
                raise Exception(
                    "O documento encontra-se assinado. Por isso não pode ser modificado."
                )

            for p in PartLawsuit.objects.filter(pk__in=parts):
                confidentialaccess.remove_part(part=p)

        except self.Model.DoesNotExist:
            rst.update(message="Não foi encontrado o documento desejado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Removido",
            )

        self.renderer(rst)


class EJudRevokeConfidentialAccess(EJudConfidentialAccess):
    _model = RevokeConfidentialAccess

    def get_params(self, *args, **kargs):
        params = super(EJudRevokeConfidentialAccess, self).get_params(*args, **kargs)

        return params


class EJudGrantConfidentialAccess(EJudConfidentialAccess):

    _model = GrantConfidentialAccess

    def get_params(self, *args, **kargs):
        params = super(EJudGrantConfidentialAccess, self).get_params(*args, **kargs)

        return params
