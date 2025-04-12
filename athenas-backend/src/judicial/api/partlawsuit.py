# -*- coding: utf-8 -*-
import base64

from urllib.parse import urlencode
from contrib.newrest import Restful
from contrib.utils import getLogger
from functools import partial
from judicial.models import PartLawsuit
from contrib.utils import employee_from_user, DateUtils
from contrib.nil import nil_pk, nil_unicode, nil_datetime
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.conf import settings
from django.utils.text import slugify

log = getLogger(__name__)


class BasePartLawsuit(object):

    force_upper = False

    force_orm_single = True

    def do_filter(self, *args, **kwargs):
        return super(BasePartLawsuit, self).do_filter(*args, **kwargs).distinct()

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for attr in ("shared_with_lawsuit", "lawsuit", "acting_zone"):
            if attr in params:
                if params.get(attr) != "":
                    field = getattr(self.Model, attr)

                    query = field.get_queryset()

                    try:
                        params.update({attr: query.get(pk=params.get(attr))})
                    except Exception as e:
                        log.exception(e)
                        raise e
                else:
                    params.update({attr: None})

        return params

    def sign(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        pk = args[0]

        try:
            obj = self.Model.objects.get(pk=pk)
            log.debug("to sign %s", type(obj))
            obj.sign_part()
            obj.create_cache_document()
        except self.Model.DoesNotExist:
            rst.update(message="Não consegui encontrar o documento desejado.")
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Documento assinado com sucesso.",
                instance=self.model_to_dict(obj),
            )

        self.renderer(rst)

    def complement_model_to_dict(self, instance):
        return {}

    def read_render(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            doc = self.get_query().get(pk=self.request.GET.get("pk")).my_origin
            if doc.signed_by:
                doc.create_cache_document()
        except self.Model.DoesNotExist:
            rst.update(message="Não foi encontrado o documento desejado.")
        else:
            rst.update(
                unfolded=doc.unfolder.exists(),
                success=True,
                content=doc.rendered,
                extra_pages=doc.extra_pages,
            )

        self.renderer(rst)

    def read_pdf(self, args=[]):
        try:
            pk = int(args[0]) if args else 0
            doc = self.get_query().get(pk=pk).my_origin
            employee = employee_from_user(self.request.user)
            response = None

            if doc.can_read:
                with doc.cache_filestream() as fd:
                    response = self.response
                    response["ETag"] = fd.etag
                    response["Content-Type"] = "application/pdf"

                    if self.request.GET.get("force_download", "off") == "on":
                        response["Content-Disposition"] = (
                            "attachment;filename=%s.pdf" % slugify(doc.title)
                        )
                    else:
                        response["Content-Disposition"] = "inline"

                    for chunk in iter(partial(fd.stream.read, 8192), b""):
                        response.write(chunk)

            else:
                response = FileResponse(
                    open("%s" % (settings.JUDICIAL_PDF_ACCESS_DENIED), "rb"),
                    content_type="application/pdf",
                )
        except Exception as e:
            log.exception(e)
            self.response = FileResponse(
                open("%s" % (settings.JUDICIAL_PDF_ERROR), "rb"),
                content_type="application/pdf",
            )
        else:
            self.response = response

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        instance = instance.my_origin
        instance.refresh_from_db()

        rst.update(
            icons=instance.icons,
            can_read=instance.can_read,
            is_public=instance.is_public,
            unicode=instance.title,
            read_only=instance.read_only,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            signed_by=nil_pk(instance.signed_by, None),
            signed_by_unicode=nil_unicode(instance.signed_by, None),
            unfolded_by=nil_pk(instance.unfolded_by, None),
            unfolded_by_unicode=nil_unicode(instance.unfolded_by, None),
            cache_rendered=instance.cache_rendered,
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            signed_at=nil_datetime(instance.signed_at, None),
            unfolded_at=nil_datetime(instance.unfolded_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            path="%s.%s" % (instance._meta.app_label, instance._meta.model_name),
            acting_zone=nil_pk(instance.acting_zone, None),
            acting_zone_unicode=nil_unicode(instance.acting_zone, None),
            number_pages=instance.number_pages,
            event_control=[
                {"number_control": ec.number_control, "lawsuit": ec.lawsuit.pk}
                for ec in instance.has_event_controls.filter(discarded_by=None)
            ],
            url_cache=instance.url_cache,
            abs_url_cache=instance.abs_url_cache,
            size_cache=instance.cache_filestream_size,
            titles_reminders=[reminder.title for reminder in instance.my_reminders],
            unicode_with_signed_at=" ".join(
                [str(instance), nil_datetime(instance.signed_at, "")]
            ),
        )

        if instance.can_read:
            rst.update(self.complement_model_to_dict(instance))

        return rst


class EJudPartLawsuit(BasePartLawsuit, Restful):

    _model = PartLawsuit

    full_text_index = (
        "codename_part__icontains",
        "cache_rendered__icontains",
    )

    def publish(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            enable = self.request.POST.get("enable", "off").lower() == "on"
            with transaction.atomic():
                for part in self.get_query().filter(
                    pk__in=self.request.POST.getlist("pk")
                ):
                    part = part.my_origin
                    part.publish(enable)
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="publicidade alterada com sucesso.")

        self.renderer(rst)

    def sign_selected(self, args=[]):

        rst = {"success": False, "message": "Nada foi feito ainda"}

        try:
            log.debug(self.request.POST.getlist("pkset"))
            query = self.get_query().filter(pk__in=self.request.POST.getlist("pkset"))

            with transaction.atomic():
                for part in query:
                    part = part.my_origin
                    if self.need_sign:
                        part.my_origin.sign_part()
                    else:
                        raise Exception('O documento "%s" já esta assinado.' % part)
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Documentos assinados.")

        self.renderer(rst)

    def rebuild_cache_doc(self, args=[]):

        rst = {"success": False, "message": "Nada foi feito ainda"}

        try:
            self._read_special_verb()
            doc = self.get_query().get(pk=self.request.PUT.get("pk")).my_origin
            user = self.request.user
            if user.has_perm("judicial.outcourtlawsuitadmin"):
                doc.create_cache_document(force=True)
            else:
                rst.update(
                    message="Usuário não possui permisão para gerar este documento."
                )
        except Exception as e:
            rst.update(message=e.message)
        else:
            rst.update(success=True, message="Documento em fila para ser recriado.")

        self.renderer(rst)

    def to_printer(self, args=[]):
        dumper = """<!DOCTYPE html>
                    <html>
                        <head>
                            <link rel="stylesheet" type="text/css" href="/athenas/static/judicial/papper.css"/>
                            <link rel="stylesheet" type="text/css" href="/athenas/static/judicial/papper-pdf.css"/>
                        </head>
                        <body>
                            <div class="papper-model">%s</div>
                        </body>
                    </html>"""

        content = ""
        try:
            obj = self.Model.objects.get(pk=self.request.GET.get("part_id"))
            content = obj.my_origin.rendered
        except Exception as e:
            content = str(e)

        self.response.write(dumper % content)


class EJudPartLawsuitAPI(EJudPartLawsuit):

    def get_query(self):
        return super().get_query().order_by("-created_at")

    def model_to_dict(self, instance):
        instance = instance.my_origin

        signed_by = None
        if hasattr(instance.signed_by, "servidor"):
            signed_by = str(instance.signed_by.servidor.pessoa_fisica)

        _dict_ = {
            "id": instance.id,
            "lawsuit": instance.lawsuit.cache_number,
            "lawsuit_id": instance.lawsuit.id,
            "title": instance.title,
            "is_public": instance.is_public,
            "can_read": instance.can_read,
            "created_at": nil_datetime(instance.created_at, None),
            "signed": nil_datetime(instance.signed, None),
            "signed_by": signed_by,
            "has_document": True if instance.is_public else False,
            "event": (
                instance.event_control.number_control if instance.event_control else "-"
            ),
        }

        return _dict_

    def renderer_document(self, args=[]):
        response = {"success": False, "message": "", "collection": {}}

        part_id = self.request.GET.get("part_id")

        try:
            part = self._model.objects.filter(
                id=part_id, signed_by__isnull=False, signed_at__isnull=False
            ).last()
        except self._model.DoesNotExist as e:
            response.update(message="Movimentação não encontrada")
        else:
            specialized_part = part.my_origin
            extra_pages = specialized_part.extra_pages or []
            part_lawsuit_document = {
                "id": specialized_part.id,
                "is_public": specialized_part.is_public,
                "markup": base64.b64encode(specialized_part.rendered.encode()).decode(),
                "extra_pages": [
                    base64.b64encode(page.encode()).decode()
                    for page in extra_pages
                    if page
                ],
            }

        response.update(
            success=True,
            message="Processado com sucesso!",
            collection=part_lawsuit_document,
        )

        self.renderer(response)


class EJudPartLawsuitSearch(EJudPartLawsuit):

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        instance = instance.my_origin
        instance.refresh_from_db()

        rst.update(
            icons=instance.icons,
            can_read=instance.can_read,
            is_public=instance.is_public,
            unicode=instance.title,
            read_only=instance.read_only,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            signed_by=nil_pk(instance.signed_by, None),
            signed_by_unicode=nil_unicode(instance.signed_by, None),
            unfolded_by=nil_pk(instance.unfolded_by, None),
            unfolded_by_unicode=nil_unicode(instance.unfolded_by, None),
            cache_rendered=instance.cache_rendered,
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_location_unicode=nil_unicode(instance.lawsuit.location, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            signed_at=nil_datetime(instance.signed_at, None),
            unfolded_at=nil_datetime(instance.unfolded_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            path="%s.%s" % (instance._meta.app_label, instance._meta.model_name),
            acting_zone=nil_pk(instance.acting_zone, None),
            acting_zone_unicode=nil_unicode(instance.acting_zone, None),
            number_pages=instance.number_pages,
            url_cache=instance.url_cache,
            abs_url_cache=instance.abs_url_cache,
            size_cache=instance.cache_filestream_size,
            unicode_with_signed_at=" ".join(
                [str(instance), nil_datetime(instance.signed_at, "")]
            ),
        )

        return rst

    def get_query(self):
        return (
            super()
            .get_query()
            .filter(signed_by__isnull=False)
            .exclude(
                Q(access_controls__isnull=False)
                | Q(lawsuit__access_controls__isnull=False)
            )
            .order_by("-created_at")
        )

    def do_full_text_filter(self, query):
        query = query.filter(search_vector=self.request.GET.get("keyword"))
        return query

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.search.Manage")')
