# -*- coding: utf-8 -*-

from django.db import transaction

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_display, nil_pk
from contrib.utils import getLogger
from rh.apd.models import Homologation, PeriodicEvaluationPerformance, Publicacao

log = getLogger(__name__)


class ApdHomologation(Restful):
    """Classe representativa do modelo Homologation."""

    _model = Homologation

    force_upper = False

    def json(self, args=[]):
        """JSON."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("apd.homologation.Manage")')

    def homologation_apd(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info(self.request.POST)
            pks = self.request.POST.get("pk")
            # log.info(self.request.POST)

            with transaction.atomic():
                employees = PeriodicEvaluationPerformance.objects.filter(
                    pk__in=pks.split(",")
                )
                for employee in employees:
                    Homologation(
                        periodic_evaluation=employee,
                        publication=Publicacao.objects.get(
                            pk=int(self.request.POST.get("publication"))
                        ),
                        status=2,
                        text=self.request.POST.get("text"),
                    ).save()
        except Publicacao.DoesNotExist:
            rst.update(message="Publicação não encontrada!")
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(
                success=True,
                message="Dados persistidos com sucesso!",
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        """GET PARAMS."""
        params = Restful.get_params(self, *args, **kargs)

        if "periodic_evaluation" in params:
            if params.get("periodic_evaluation") != "":
                field = getattr(self.Model, "periodic_evaluation")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        periodic_evaluation=query.get(
                            pk=params.get("periodic_evaluation")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(periodic_evaluation=None)

        if "publication" in params:
            if params.get("publication") != "":
                field = getattr(self.Model, "publication")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(publication=query.get(pk=params.get("publication")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(publication=None)

        return params

    def model_to_dict(self, instance):
        """MODEL TO DICT."""
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            status=instance.status,
            status_display=nil_display(instance, "status", None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=instance.modified_by or None,
            publication=nil_pk(instance.publication, None),
            publication_unicode=instance.publication or None,
            text=instance.text,
            periodic_evaluation=nil_pk(instance.periodic_evaluation, None),
            periodic_evaluation_unicode=instance.periodic_evaluation or None,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=instance.created_by or None,
        )

        return rst
