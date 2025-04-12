# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Ordinace
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode, nil_unicode, nil_pk
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudOrdinace(BasePartLawsuit, Restful):

    _model = Ordinace

    def get_params(self, *args, **kargs):
        params = super(EJudOrdinace, self).get_params(*args, **kargs)

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

    def create_supplement(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda."}

        try:
            ordinace = self.get_query().get(pk=self.request.POST.get("ordinace"))
            supplement = ordinace.create_supplement()
        except self.Model.DoesNotExist:
            rst.update(message="Não consegui encontrar a Portaria de Instauração.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Suplementar criada com sucesso.",
                pk=supplement.pk,
            )

        self.renderer(rst)
