# -*- coding: utf-8 -*-

import datetime

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_pk
from contrib.utils import getLogger
from rh.apd.models import ScoreEvaluation

log = getLogger(__name__)


class ApdScoreEvaluation(Restful):
    """Classe representativa do modelo ScoreEvaluation."""

    _model = ScoreEvaluation

    def get_params(self, *args, **kargs):
        """GET PARAMS."""
        params = Restful.get_params(self, *args, **kargs)

        # if 'date_modified' in params:
        #     params.update(date_modified=None)
        #     if params.get('date_modified') != '':
        #         params.update(date_modified=DateUtils.str_to_date(params.get('date_modified')))
        #     else:
        #         params.update(date_modified=None)

        if "element" in params:
            if params.get("element") != "":
                field = getattr(self.Model, "element")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(element=query.get(pk=params.get("element")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(element=None)

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

        # if 'user_modified' in params:
        #     if params.get('user_modified') != '':
        #         field = getattr(self.Model, 'user_modified')

        #         # mater compatibilidade com django-1.4.x
        #         get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
        #         query = get_queryset()

        #         try:
        #             params.update(
        #                 user_modified=query.get(pk=params.get('user_modified'))
        #             )
        #         except Exception as e:
        #             log.exception(e)
        #             raise e
        #     else:
        #         params.update(user_modified=None)
        # log.info(datetime.datetime.now())
        # log.info(self.request.user.servidor)
        params.update(user_modified=self.request.user.servidor)
        params.update(date_modified=datetime.datetime.now())
        log.info(params)

        return params

    def model_to_dict(self, instance):
        """MODEL TO DICT."""
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            date_modified=nil_date(instance.date_modified, None),
            final_score=float(instance.final_score or 0),
            created_at=nil_datetime(instance.created_at, None),
            top_score=float(instance.top_score or 0),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            element=nil_pk(instance.element, None),
            element_unicode=instance.element.elemento.label or None,
            score_obtained=float(instance.score_obtained or 0),
            evaluation=nil_pk(instance.evaluation, None),
            evaluation_unicode=str(instance.evaluation) or None,
            user_modified=nil_pk(instance.user_modified, None),
            user_modified_unicode=str(instance.user_modified) or None,
        )

        return rst
