# -*- coding: utf-8 -*-

from django.db import transaction

from contrib.newrest import Restful
from contrib.nil import nil_pk
from contrib.utils import getLogger
from rh.profile.models import JobProfile

log = getLogger(__name__)

if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


class PFJobProfile(Restful):

    _model = JobProfile

    def sync_grants(self, args=[]):
        rst = {"message": "Não foi realizado nenhum processamento.", "success": False}

        query = self.Model.objects.filter(pk__in=self.request.POST.getlist("pk__in"))
        try:
            with transaction.atomic():
                for profile in query:
                    log.info("Processando sincronismo do perfil %s", profile.codename)
                    profile.sync_grants()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Sincronismo realizado com sucesso!!!")

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("rh.profile.JobProfileManage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "for_work_assignment" in params:
            params.update(
                for_work_assignment=params.get("for_work_assignment", "off").lower()
                == "on"
            )
        if "for_workplace" in params:
            params.update(
                for_workplace=params.get("for_workplace", "off").lower() == "on"
            )
        if "for_leadership" in params:
            params.update(
                for_leadership=params.get("for_leadership", "off").lower() == "on"
            )
        if "for_activity_statement" in params:
            params.update(
                for_activity_statement=params.get(
                    "for_activity_statement", "off"
                ).lower()
                == "on"
            )

        if "workplace" in params:
            if params.get("workplace") != "":
                field = getattr(self.Model, "workplace")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(workplace=query.get(pk=params.get("workplace")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(workplace=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            for_work_assignment=instance.for_work_assignment,
            for_workplace=instance.for_workplace,
            codename=instance.codename,
            workplace=nil_pk(instance.workplace, None),
            workplace_unicode=str(instance.workplace) or None,
            for_leadership=instance.for_leadership,
            for_activity_statement=instance.for_activity_statement,
        )

        return rst
