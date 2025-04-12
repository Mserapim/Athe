# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import SwitchExecutionOrgan
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class CouncilSwitchExecutionOrgan(BasePartLawsuit, Restful):

    _model = SwitchExecutionOrgan

    def get_params(self, *args, **kargs):
        params = super(CouncilSwitchExecutionOrgan, self).get_params(*args, **kargs)

        if "legal_matter" in params:
            if params.get("legal_matter") != "":
                field = getattr(self.Model, "legal_matter")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(legal_matter=query.get(pk=params.get("legal_matter")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(legal_matter=None)

        if "create_location" in params:
            if params.get("create_location") != "":
                field = getattr(self.Model, "create_location")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        create_location=query.get(pk=params.get("create_location"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(create_location=None)

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

        return params

    def model_to_dict(self, instance):
        rst = super(CouncilSwitchExecutionOrgan, self).model_to_dict(instance)

        rst.update(
            execution_organ=nil_pk(instance.execution_organ, None),
            execution_organ_unicode=nil_unicode(instance.execution_organ, None),
            legal_matter=nil_pk(instance.legal_matter, None),
            legal_matter_unicode=nil_unicode(instance.legal_matter, None),
            from_colegial_decision=nil_pk(instance.from_colegial_decision, None),
            from_colegial_decision_unicode=nil_unicode(
                instance.from_colegial_decision, None
            ),
            observation=instance.observation,
        )

        return rst
