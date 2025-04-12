# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Triage
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from django.db import transaction

if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


log = getLogger(__name__)


class EJudTriage(BasePartLawsuit, Restful):

    _model = Triage

    force_orm_single = True

    def delivery(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        """
        Carrega a váriavel PUT
        """
        self._read_special_verb()

        try:
            triage = Triage.objects.get(pk=self.request.PUT.get("pk"))
            with transaction.atomic():
                triage.delivery()
        except self.Model.DoesNotExist:
            rst.update(
                message="Não foi possivel encontrar o documento de triagem especificado."
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = super(EJudTriage, self).get_params(*args, **kargs)

        if "matter" in params:
            if params.get("matter") != "":
                field = getattr(self.Model, "matter")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(matter=query.get(pk=params.get("matter")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(matter=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudTriage, self).complement_model_to_dict(instance)

        rst.update(
            triage_number=int(instance.triage_number or 0),
            triage_year=int(instance.triage_year or 0),
            formated_number=instance.formated_number,
        )

        return rst
