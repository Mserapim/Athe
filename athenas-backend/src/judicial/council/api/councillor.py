# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import Councillor
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class CouncilCouncillor(Restful):

    _model = Councillor

    force_upper = False

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "distribution_rapporteur" in params:
            if params.get("distribution_rapporteur") != "":
                field = getattr(self.Model, "distribution_rapporteur")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        distribution_rapporteur=query.get(
                            pk=params.get("distribution_rapporteur")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(distribution_rapporteur=None)

        if "possession" in params:
            if params.get("possession") != "":
                field = getattr(self.Model, "possession")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(possession=query.get(pk=params.get("possession")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(possession=None)

        if "incident_type" in params:
            if params.get("incident_type") == "":
                params.update(incident_type=None)
            else:
                params.update(incident_type=int(params.get("incident_type") or 0))

        if "substitute" in params:
            if params.get("substitute") != "":
                field = getattr(self.Model, "substitute")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(substitute=query.get(pk=params.get("substitute")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(substitute=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            comment=instance.comment,
            formated_comment=instance.formated_comment,
            possession=nil_pk(instance.possession, None),
            possession_unicode=nil_unicode(instance.possession, None),
            employee=nil_pk(instance.employee, None),
            employee_unicode=nil_unicode(instance.employee, None),
            employee_name=(
                nil_unicode(instance.employee.pessoa_fisica, None)
                if instance.employee
                else None
            ),
            owner=nil_pk(instance.owner, None),
            owner_unicode=nil_unicode(instance.owner, None),
            owner_name=(
                nil_unicode(instance.owner.pessoa_fisica, None)
                if instance.owner
                else None
            ),
            substitute=nil_pk(instance.substitute, None),
            substitute_unicode=nil_unicode(instance.substitute, None),
            substitute_name=(
                nil_unicode(instance.substitute.pessoa_fisica, None)
                if instance.substitute
                else None
            ),
            distribution_rapporteur=nil_pk(instance.distribution_rapporteur, None),
            distribution_rapporteur_unicode=nil_unicode(
                instance.distribution_rapporteur, None
            ),
            incident_type=instance.incident_type,
            incident_type_display=nil_display(instance, "incident_type", None),
            councillor_type=instance.councillor_type,
            councillor_type_display=nil_display(instance, "councillor_type", None),
        )

        return rst
