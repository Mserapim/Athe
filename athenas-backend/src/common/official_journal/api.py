# -*- coding: utf-8 -*-

from django.db import transaction
from contrib.newrest import RestfulDRY
from common.official_journal.models import JournalBase, Journal, Suplement
from contrib.utils import getLogger

log = getLogger()


class JournalBaseRestful(RestfulDRY):
    _model = JournalBase
    force_upper = False
    force_orm_single = True
    full_text_index = ["name__icontains"]
    exclude_fields = ["created_by", "modified_by", "modified_at"]

    def __init__(self, *args, **kwargs):
        super(JournalBaseRestful, self).__init__(*args, **kwargs)
        self.set_restful("json")

    def model_to_dict(self, instance):
        m2d = super(JournalBaseRestful, self).model_to_dict(instance)
        if instance.ged:
            m2d["ged_uri"] = instance.ged.permalink()
        return m2d

    def publish(self, args=[]):
        r = {"success": False, "message": "Não foi possivel realizar publicação."}

        instance = self.__class__._model.objects.filter(
            pk=self.request.REQUEST.get("pk")
        ).first()

        if instance:
            try:
                with transaction.atomic():
                    instance.publish()
                    instance.save()
            except Exception as e:
                log.exception(e)
                r["message"] = str(e)
            else:
                r = {"success": True, "message": "Item publicado."}

        self.response["content-type"] = "text/javascript"
        self.render(r)


class JournalRestful(JournalBaseRestful):

    _model = Journal

    exclude_fields = JournalBaseRestful.exclude_fields + ["journalbase_ptr"]

    full_text_index = JournalBaseRestful.full_text_index + ["code__icontains"]

    def model_to_dict(self, instance):
        m2d = super(JournalRestful, self).model_to_dict(instance)
        m2d["year"] = instance.year
        return m2d

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.official_journal.Manage")')

    def fetch_years(self, args=[]):
        response = {"success": False, "message": "", "collection": None}

        try:
            years = self._model.objects.filter(
                published_date__isnull=False
            ).values_list("published_date__year", flat=True)
        except self._model.DoesNotExist:
            response.update(message="Não foram encontrados os anos")
        else:
            response.update(
                success=True,
                message="Processado com sucesso!",
                collection=[(year, year) for year in list(set(years))[::-1]],
            )

        self.renderer(response)


class JournalSuplementRestful(JournalBaseRestful):
    _model = Suplement
    exclude_fields = JournalBaseRestful.exclude_fields + ["journalbase_ptr"]
