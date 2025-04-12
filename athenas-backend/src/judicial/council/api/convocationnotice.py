# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import ConvocationNotice
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode, nil_date
from django.db import transaction


log = getLogger(__name__)


class CouncilConvocationNotice(Restful):

    _model = ConvocationNotice

    force_upper = False

    def request_publication(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda."}

        try:
            with transaction.atomic():
                for convocation in self.get_query().filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    convocation.request_publication()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Foram requistadas as publicações.")

        self.renderer(rst)

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

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            convocation_state=instance.convocation_state,
            convocation_state_display=nil_display(instance, "convocation_state", None),
            cached_number=instance.cached_number,
            distribution_rapporteur=nil_pk(instance.distribution_rapporteur, None),
            distribution_rapporteur_unicode=nil_unicode(
                instance.distribution_rapporteur, None
            ),
            publication=nil_pk(instance.publication, None),
            publication_unicode=nil_unicode(instance.publication, None),
            publication_date=(
                nil_date(instance.publication.data_publicacao, None)
                if instance.publication
                else None
            ),
            deadline_date=nil_date(instance.deadline_date, None),
            deadline_days=instance.deadline_days,
            year=int(instance.year or 0),
            convocation=instance.convocation,
            rendered=instance.rendered,
            icons=instance.icons,
            number=int(instance.number or 0),
        )

        return rst
