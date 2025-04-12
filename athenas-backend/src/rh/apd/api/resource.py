# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_display, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.apd.models import Resource

log = getLogger(__name__)


class ApdResource(Restful):
    """Classe representativa do modelo Resource."""

    _model = Resource

    def json(self, args=[]):
        """JSON."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("apd.resource.Manage")')

    def get_params(self, *args, **kargs):
        """GET PARAMS."""
        params = Restful.get_params(self, *args, **kargs)

        if "evaluation" in params:
            if params.get("evaluation") != "":
                field = getattr(self.Model, "evaluation")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(evaluation=query.get(pk=params.get("evaluation")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(evaluation=None)

        return params

    def model_to_dict(self, instance):
        """MODEL TO DICT."""
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=str(instance.icons),
            deadline=str(instance.deadline),
            status=str(instance.status),
            days_to_judge=str(instance.days_to_judge),
            status_display=nil_display(instance, "status", None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            text=str(instance.text),
            evaluation=nil_pk(instance.evaluation, None),
            evaluation_unicode=str(instance.evaluation) or None,
            created_at=nil_datetime(instance.created_at, None),
            created_at_formated=DateUtils.date_to_str(instance.created_at),
            modified_at=nil_datetime(instance.modified_at, None),
            decision=str(instance.decision),
            decision_display=nil_display(instance, "decision", None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            date_science_decision=nil_datetime(instance.date_science_decision, None),
        )

        return rst
