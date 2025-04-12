# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.tac.models import Document
from contrib.utils import DateUtils
from ged.models import Arquivo
from contrib.nil import nil_pk, nil_unicode, nil_display
from contrib.nil import nil_datetime


log = getLogger(__name__)


class TacDocument(Restful):

    _model = Document

    force_upper = False

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "activity_document" in params:
            if params.get("activity_document") != "":
                field = getattr(self.Model, "activity_document")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        activity_document=query.get(pk=params.get("activity_document"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(activity_document=None)

        if params.get("file_document", "") != "":
            params.update(
                {"file_document": Arquivo.objects.get(pk=params.get("file_document"))}
            )
        elif "file_document" in params:
            del params["file_document"]

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            title=instance.title,
            description=instance.description,
            activity_document=nil_pk(instance.activity_document, None),
            activity_document_unicode=nil_unicode(instance.activity_document, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            accepted=instance.accepted,
            accepted_display=nil_display(instance, "accepted", None),
            file_document=(
                instance.file_document.pk
                if not instance.file_document is None
                else None
            ),
            filename=(
                instance.file_document.filename
                if not instance.file_document is None
                else None
            ),
            permalink=(
                instance.file_document.permalink()
                if not instance.file_document is None
                else None
            ),
        )

        return rst

    def action_accept(self, args=[]):
        rst = {"success": False, "values": {}}
        try:
            doc = self._model.objects.get(pk=self.request.POST["pk"])
            doc.accepted = int(self.request.POST["acao"])
            doc.save()
        except Exception as e:
            log.info(e)
        else:
            rst.update(success=True)
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
