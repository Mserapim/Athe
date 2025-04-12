# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.apd.models import Configuration

log = getLogger(__name__)


class ApdConfiguration(Restful):
    """Classe representativa do modelo Configuration."""

    _model = Configuration

    force_upper = False

    def json(self, args=[]):
        """JSON."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("apd.configuration.Manage")')

    def get_params(self, *args, **kargs):
        """GET PARAMS."""
        params = Restful.get_params(self, *args, **kargs)

        if "publication" in params:
            if params.get("publication") != "":
                field = getattr(self.Model, "publication")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(publication=query.get(pk=params.get("publication")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(publication=None)

        if "end_date" in params:
            if params.get("end_date") != "":
                params.update(end_date=DateUtils.str_to_date(params.get("end_date")))
            else:
                params.update(end_date=None)

        if "questionnaire_subordinate" in params:
            if params.get("questionnaire_subordinate") != "":
                field = getattr(self.Model, "questionnaire_subordinate")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        questionnaire_subordinate=query.get(
                            pk=params.get("questionnaire_subordinate")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(questionnaire_subordinate=None)

        if "previus_configuration" in params:
            if params.get("previus_configuration") != "":
                field = getattr(self.Model, "previus_configuration")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        previus_configuration=query.get(
                            pk=params.get("previus_configuration")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(previus_configuration=None)

        if "questionnaire_boss" in params:
            if params.get("questionnaire_boss") != "":
                field = getattr(self.Model, "questionnaire_boss")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        questionnaire_boss=query.get(
                            pk=params.get("questionnaire_boss")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(questionnaire_boss=None)

        if "start_date" in params:
            if params.get("start_date") != "":
                params.update(
                    start_date=DateUtils.str_to_date(params.get("start_date"))
                )
            else:
                params.update(start_date=None)

        return params

    def model_to_dict(self, instance):
        """MODEL TO DICT."""
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            publication=nil_pk(instance.publication, None),
            publication_unicode=str(instance.publication) or None,
            end_date=nil_date(instance.end_date, None),
            interval_periodic_evaluation=int(
                instance.interval_periodic_evaluation or 0
            ),
            deadline_rectify_evaluation=int(instance.deadline_rectify_evaluation or 0),
            deadline_appeal=int(instance.deadline_appeal or 0),
            deadline_blocking=instance.deadline_blocking,
            deadline_begin=instance.deadline_begin,
            deadline_rectification_commission=int(
                instance.deadline_rectification_commission or 0
            ),
            deadline_judge_resource=int(instance.deadline_judge_resource or 0),
            deadline_reconsideration=int(instance.deadline_reconsideration or 0),
            deadline_science_resul_evaluation=int(
                instance.deadline_science_resul_evaluation or 0
            ),
            porcentage_approval=float(instance.porcentage_approval or 0),
            questionnaire_subordinate=nil_pk(instance.questionnaire_subordinate, None),
            questionnaire_subordinate_unicode=str(instance.questionnaire_subordinate)
            or None,
            previus_configuration=nil_pk(instance.previus_configuration, None),
            previus_configuration_unicode=str(instance.previus_configuration or ""),
            questionnaire_boss=nil_pk(instance.questionnaire_boss, None),
            questionnaire_boss_unicode=str(instance.questionnaire_boss) or None,
            start_date=nil_date(instance.start_date, None),
            created_at=nil_datetime(instance.created_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            modified_by=nil_pk(instance.modified_by, None),
            modified_at=nil_datetime(instance.modified_at, None),
            modified_by_unicode=str(instance.modified_by) or None,
            instructions=instance.instructions,
        )

        return rst
