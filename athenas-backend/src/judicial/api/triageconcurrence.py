# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import TriageConcurrence
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class EJudTriageConcurrence(Restful):

    _model = TriageConcurrence

    force_orm_single = True

    force_upper = False

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "execution_organ" in params:
            if params.get("execution_organ") != "":
                field = getattr(self.Model, "execution_organ")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        execution_organ=query.get(pk=params.get("execution_organ"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(execution_organ=None)

        if "triage_part" in params:
            if params.get("triage_part") != "":
                field = getattr(self.Model, "triage_part")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(triage_part=query.get(pk=params.get("triage_part")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(triage_part=None)

        if "incident_type" not in params:
            params.update(incident_type=1)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            execution_organ=nil_pk(instance.execution_organ, None),
            execution_organ_unicode=nil_unicode(instance.execution_organ, None),
            incident=instance.incident,
            incident_display=nil_display(instance, "incident", None) or "Nenhum",
            incident_type=instance.incident_type,
            incident_display_type=nil_display(instance, "incident_type", None),
            direct=instance.direct,
            argumentation=instance.argumentation,
            triage_part=nil_pk(instance.triage_part, None),
            triage_part_unicode=nil_unicode(instance.triage_part, None),
        )

        return rst
