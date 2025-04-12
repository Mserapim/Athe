# -*- coding: utf-8 -*-
import json
from django.template.defaultfilters import slugify
from contrib.newrest import Restful
from contrib.utils import getLogger
from django.db import transaction
from judicial.models import Attached, PartLawsuit
from ged.models import Arquivo
from contrib.nil import nil_pk, nil_unicode, nil_datetime


log = getLogger(__name__)


class EJudAttached(Restful):

    _model = Attached

    force_upper = False

    force_orm_single = True

    def toggle_publish(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            attached = self.get_query().get(pk=args[0])
            attached.toggle_publish()

            rst.update(success=True, message="tudo certo")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "render_extract" in params:
            params.update(
                render_extract=params.get("render_extract", "off").lower() == "on"
            )

        if "attached_document" in params:
            if params.get("attached_document") != "":
                field = getattr(self.Model, "attached_document")

                query = field.get_queryset()

                try:
                    params.update(
                        attached_document=query.get(pk=params.get("attached_document"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(attached_document=None)

        if "attached_part_access" in params:
            if params.get("attached_part_access") != "":
                field = getattr(self.Model, "attached_part_access")

                query = field.get_queryset()

                try:
                    params.update(
                        attached_part_access=query.get(
                            pk=params.get("attached_part_access")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(attached_part_access=None)

        if "attached_manifestation" in params:
            if params.get("attached_manifestation") != "":
                field = getattr(self.Model, "attached_manifestation")

                query = field.get_queryset()

                try:
                    params.update(
                        attached_manifestation=query.get(
                            pk=params.get("attached_manifestation")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(attached_manifestation=None)

        if "attached_diligence" in params:
            if params.get("attached_diligence") != "":
                field = getattr(self.Model, "attached_diligence")

                query = field.get_queryset()

                try:
                    params.update(
                        attached_diligence=query.get(
                            pk=params.get("attached_diligence")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(attached_diligence=None)

        if "file_descriptor" in params:
            if params.get("file_descriptor") != "":
                field = getattr(self.Model, "file_descriptor")

                query = field.get_queryset()

                try:
                    params.update(
                        file_descriptor=query.get(pk=params.get("file_descriptor"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(file_descriptor=None)

        if "attached_response_officer" in params:
            if params.get("attached_response_officer") != "":
                field = getattr(self.Model, "attached_response_officer")

                query = field.get_queryset()

                try:
                    params.update(
                        attached_response_officer=query.get(
                            pk=params.get("attached_response_officer")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(attached_response_officer=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            attached_document=nil_pk(instance.attached_document, None),
            attached_document_unicode=nil_unicode(instance.attached_document, None),
            file_descriptor=nil_pk(instance.file_descriptor, None),
            file_descriptor_unicode=nil_unicode(instance.file_descriptor, None),
            title=instance.title,
            send_by=nil_unicode(instance.file_descriptor.user, None),
            send_at=nil_datetime(instance.file_descriptor.created, None),
            render_extract=instance.render_extract,
            number_pages=instance.number_pages,
        )

        return rst

    def save_batch(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                title = self.request.POST.get("title", None)
                file_descriptor = Arquivo.objects.get(
                    pk=self.request.POST.get("file_descriptor", None)
                )
                render_extract = (
                    self.request.POST.get("render_extract", "off").lower() == "on"
                )
                attached_documents = PartLawsuit.objects.filter(
                    pk__in=self.request.POST.getlist("attached_documents")
                )

                for part in attached_documents:
                    obj = Attached()

                    obj.title = title
                    obj.file_descriptor = file_descriptor
                    obj.render_extract = render_extract
                    obj.attached_document = part

                    obj.save()

        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(
                success=True, message="Documentos salvos nos procedimentos."
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))
