# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import Vote
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode, nil_datetime


log = getLogger(__name__)


class CouncilVote(Restful):

    _model = Vote

    force_upper = False

    def _filter_eval_value(self, value):
        log.debug("%s", value)
        if isinstance(value, str) and value.lower() == "true":
            return True
        elif isinstance(value, str) and value.lower() == "false":
            return False
        else:
            return value

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "from_distribution" in params:
            if params.get("from_distribution") != "":
                field = getattr(self.Model, "from_distribution")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        from_distribution=query.get(pk=params.get("from_distribution"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(from_distribution=None)

        if "vote_type" in params and not params.get("vote_type"):
            params.update(vote_type=None)

        if "invalide" in params:
            params.update(invalide=params.get("invalide", "off").lower() == "on")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        def nil_employee(councillor, default_value):
            return councillor.employee if councillor.employee else default_value

        def nil_employee_unicode(councillor, default_value):
            employee = nil_employee(councillor, None)
            return str(employee.pessoa_fisica) if employee else default_value

        def nil_employee_pk(councillor, default_value):
            employee = nil_employee(councillor, None)
            return employee.pk if employee else default_value

        rst.update(
            icons=instance.icons,
            from_distribution=nil_pk(instance.from_distribution, None),
            from_distribution_unicode=nil_unicode(instance.from_distribution, None),
            vote=instance.vote,
            rendered=instance.rendered,
            # rendered='unknow %d' % instance.pk,
            observation=instance.observation,
            vote_type=instance.vote_type,
            vote_type_display=nil_display(instance, "vote_type", None),
            invalide=instance.invalide,
            councillor=nil_pk(instance.councillor, None),
            councillor_unicode=nil_unicode(instance.councillor, None),
            signed_by=nil_pk(instance.signed_by, None),
            signed_by_unicode=nil_unicode(instance.signed_by, None),
            signed_at=nil_datetime(instance.signed_at, None),
            councillor_employee=nil_employee_pk(instance.councillor, None),
            councillor_employee_unicode=nil_employee_unicode(instance.councillor, None),
            councillor_type=(
                instance.councillor.councillor_type if instance.councillor else None
            ),
            councillor_type_display=nil_display(
                instance.councillor, "councillor_type", None
            ),
        )

        return rst
