# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime
from functools import partial

from django.conf import settings
from django.db import transaction
from django.db.models import Model, Q
from django.http import FileResponse
from django.template import loader

from contrib.decorator import is_public
from contrib.middleware import get_current_user
from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_display, nil_pk, nil_unicode
from contrib.utils import employee_from_user, getLogger
from default.views import Application
from edocs.protocolo.models import Movimentacao, Protocolo
from judicial.api.mixins import FilterEvalValueMixin
from judicial.models import AuditDispatchSecretary, OutCourtLawsuit, Secretary, Tag
from rh.models import Lotacao
from standard.models import Choice

log = getLogger(__name__)


class Sumary:

    class Item:
        def __init__(self, number, title):
            self._number = number
            self._title = title

        def __str__(self):
            return self._title

    def reg(self, item):
        db = getattr(self, "_db", [])
        db.append(item)
        self._db = db

    def __str__(self):
        html = ["<h1>Sumário</h3>"]

        html = ['<div class="papper-container-a4">', '<div class="papper-model">']

        html.append("<h1>Sumário</h1>")
        html.append("<ul>")
        for item in getattr(self, "_db", []):
            html.append('<li style="line-height: 1.5em">')
            html.append(
                '<a href="#I%(number)s">(E-%(number_formated)s) - %(title)s</a>'
                % {
                    "number": item._number,
                    "number_formated": ("%04d" % item._number),
                    "title": item._title,
                }
            )
            html.append("</li>")
        html.append("<ul>")

        html.append("</div>")
        html.append("</div>")

        return "".join(html)


class EJudOutCourtLawsuit(FilterEvalValueMixin, Restful):

    _model = OutCourtLawsuit

    full_text_index = (
        "title__icontains",
        "origin__interessado__nome__icontains",
        "origin__codigo__icontains",
        "origin__chancela__icontains",
        "origin__assunto__icontains",
        "cache_number__icontains",
        "has_connected__cache_number__icontains",
    )

    _sort_map = {"date_last_document_signed": "last_part_lawsuit__signed_at"}

    def qrcode(self, args=[]):
        info = args[0]

        if not re.match(r"^\d{4}\.\d{7}$", info):
            info = "inválido"

    def all_authorized_lawsuits(self):
        query = self.Model.objects.none()
        user = self.request.user

        if user.has_perm("judicial.outcourtlawsuitadmin"):
            query = self.Model.objects.all()
        else:
            query = self.Model.objects.filter(
                Q(pk__in=self.get_query().values("pk"))
                | Q(pk__in=self.get_archived_query().values("pk"))
                | Q(pk__in=self.historic_query().values("pk"))
                | Q(pk__in=self.get_query_by_officer().values("pk"))
            )

        return query

    def printer(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        pklist = self.request.GET.getlist("part")
        query = self.all_authorized_lawsuits()
        pure = False

        try:
            lawsuit = query.get(pk=self.request.GET.get("lawsuit"))
        except Exception as e:
            rst.update(message=str(e))
        else:
            pages = []
            extra_pages = []
            query = None
            pure = self.request.GET.get("pure", "off").lower() == "on"

            sumary = Sumary()

            pages = [{"at": None, "page": lawsuit.cover}, {"at": None, "page": sumary}]

            number = 1

            if not pklist and lawsuit.all_signed_documents.exists():
                first_doc = lawsuit.all_signed_documents.first().my_origin

                pages.append(
                    {
                        "at": datetime(1900, 1, 1, 0, 0, 0),
                        "page": '<a name="I%(number)d"></a>%(page)s'
                        % {"number": number, "page": first_doc.my_origin.rendered},
                    }
                )

                sumary.reg(Sumary.Item(number=number, title=str(first_doc)))
                number += 1

                extra_pages += first_doc.extra_pages_complete
                query = lawsuit.all_signed_documents.exclude(pk=first_doc.pk)
            elif len(pklist) == 1:
                doc = lawsuit.all_documents.get(pk=pklist[0]).my_origin

                pages = [{"at": doc.signed_at, "page": doc.rendered}]

                pages += doc.extra_pages_complete
                query = []
            else:
                query = lawsuit.all_signed_documents.filter(pk__in=pklist)

            for doc in query:
                doc = doc.my_origin
                extra_pages.append(
                    {
                        "at": doc.signed_at,
                        "page": '<a name="I%(number)d"></a>%(page)s'
                        % {"number": number, "page": doc.rendered},
                    }
                )

                sumary.reg(Sumary.Item(number=number, title=str(doc)))
                number += 1

                extra_pages += doc.extra_pages_complete

            pages += sorted(
                extra_pages,
                key=lambda d: d.get("at") if d.get("at") else datetime.now(),
            )

            rst.update(
                documents=pages, success=True, message="Arquivo gerado com sucesso.!"
            )

        if not pure:
            self.response.write(
                loader.get_template("judicial/printer.html").render(rst)
            )
        else:
            self.response["Content-Type"] = "text/plain"
            self.response.write(
                "".join(
                    [
                        doc.get("page")
                        for doc in pages
                        if isinstance(doc.get("page"), str)
                    ]
                )
                .encode("ascii", "xmlcharrefreplace")
                .encode("base64")
            )

    def read_pdf(self, args=[]):
        try:
            pk = int(args[0]) if args else 0
            query = self.all_authorized_lawsuits()
            lawsuit = query.get(pk=pk)
            employee = employee_from_user(self.request.user)

            if lawsuit:
                with lawsuit.cache_filestream() as fd:
                    response = self.response
                    response["ETag"] = fd.etag
                    response["Content-Type"] = "application/pdf"

                    if self.request.GET.get("force_download", "off") == "on":
                        response["Content-Disposition"] = (
                            "attachment;filename=%s.pdf" % slugify(lawsuit.title)
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

    def create_cache_lawsuit(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        query = self.all_authorized_lawsuits()

        try:
            lawsuit = query.get(pk=self.request.POST.get("pk"))
            lawsuit.create_cache_lawsuit()
        except Exception as e:
            rst.update(message="Erro ao gerar documentos.")
        else:
            rst.update(
                success=True,
                message="Procedimento está sendo consolidado e assim que terminar será oferecido para download.",
            )

        self.renderer(rst)

    def import_from_protocol(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                inst = self.Model.import_from_protocol(
                    protocol=self.request.POST.get("protocol"),
                    location=self.request.POST.get("location"),
                    type_lawsuit=self.request.POST.get("type_lawsuit"),
                )

            rst.update(success=True, instance=self.model_to_dict(inst))
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def parts(self, args=[]):
        rst = {"message": "Nada foi feito ainda", "success": False}

        try:
            lawsuit = self.Model.objects.get(pk=self.request.GET.get("pk"))
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados carregados.",
                count=lawsuit.parts.filter().count(),
                collection=[
                    {
                        "pk": part.pk,
                        "title": part.my_origin.title,
                        "rendered": part.my_origin.rendered,
                        "needSign": False,
                        "signed": False,
                        "iconCls": getattr(
                            part.my_origin, "default_icon", lambda: None
                        )(),
                        "part_type": ".".join(
                            [
                                part.my_origin._meta.app_label,
                                part.my_origin._meta.model_name,
                            ]
                        ),
                    }
                    for part in lawsuit.parts.filter()
                ],
            )

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def my_tracks_executionorgan(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            lawsuit = self.get_query().get(pk=self.request.GET.get("pk"))
            rst.update(
                success=True,
                count=lawsuit.my_tracks_executionorgan.count(),
                message="dados carregados com sucesso",
                collection=[
                    {"pk": eo.pk, "description": str(eo)}
                    for eo in lawsuit.my_tracks_executionorgan
                ],
            )
        except self.Model.DoesNotExist:
            rst.update(message="Não consegui encontra o procedimento.")
        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def historic(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.historic_query()

            if len(args) == 0:
                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                count = query.count()
                query = self.do_page(query)

                rst.update(
                    success=True,
                    count=count,
                    message="dados carregados com sucesso",
                    collection=[self.model_to_dict(lw) for lw in query],
                )
            else:
                inst = self.historic_query().filter(pk=args[0]).first()

                log.debug("lawsuit: %s", inst)
                log.debug("lawsuits: %s", self.historic_query())
                log.debug(args[0])

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def archived(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.get_archived_query()

            if len(args) == 0:

                if "filter" in self.request.GET:
                    query = self.do_filter(query).distinct()
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                count = query.count()
                query = self.do_page(query)

                rst.update(
                    success=True,
                    count=count,
                    message="dados carregados com sucesso",
                    collection=[self.model_to_dict(lw) for lw in query],
                )
            else:
                inst = query.filter(pk=args[0]).first()

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def cover(self, args=[]):
        try:
            user = self.request.user
            employee = employee_from_user(user)
            lawsuit = self.Model.objects.get(pk=self.request.GET.get("pk"))

            if user.has_perm("judicial.outcourtlawsuitadmin"):
                self.response.write(lawsuit.cover)
            elif lawsuit.all_signed_documents.filter(
                diligences__responsible_delivering__officer_diligence=employee_from_user(
                    user
                )
            ):
                self.response.write(lawsuit.cover)
            else:
                lawsuit = self.Model.objects.filter(
                    Q(pk__in=self.get_query().values_list("pk"))
                    | Q(pk__in=self.get_archived_query().values_list("pk"))
                    | Q(pk__in=self.historic_query().values_list("pk"))
                ).filter(pk=self.request.GET.get("pk"))
                if not lawsuit:
                    lawsuit = self.Model.objects.filter(
                        origin__movimentacoes__lotacao_origem__in=employee.work_locations,
                        pk=self.request.GET.get("pk"),
                    )

                self.response.write(lawsuit[0].cover)

        except Exception as e:
            log.exception(e)
            self.response.write("Error buscando o procedimento. Acesso negado.")

    def get_query(self):

        data_mode = self.request.GET.get("data_mode", None)
        employer = employee_from_user(self.request.user)
        query = super(EJudOutCourtLawsuit, self).get_query()

        employee_locations = employer.work_assignment_effective_exercise.values(
            "lotacao"
        )

        secretaries = Secretary.objects.filter(location__in=employee_locations)
        execution_organs = secretaries.values("execution_organs")

        if data_mode == "historic":
            return self.historic_query()
        else:
            if data_mode != "archived":
                query = query.filter(closed_by=None)

        if data_mode == "historic":
            return self.historic_query()
        else:
            if data_mode != "archived":
                query = query.filter(closed_by=None)

            query = (
                query.filter(removed_by=None)
                .filter(
                    Q(location__in=employer.work_locations if employer else [])
                    | Q(
                        Q(requestcollaboration__canceled_by=None)
                        & Q(
                            Q(
                                requestcollaboration__requestcollaborationperson__person=employer.pessoa_fisica
                            )
                            | Q(
                                requestcollaboration__requestcollaborationgeneralorgan__general_organ__in=employer.work_locations
                            )
                        )
                    )
                    | Q(location__in=execution_organs if execution_organs else [])
                )
                .values_list("pk")
            )

            return self.Model.objects.filter(pk__in=query)

    def historic_query(self):
        employer = employee_from_user(self.request.user)

        query = Protocolo.objects.filter(
            pk__in=Movimentacao.outbox_queryset()
            .filter(
                Q(
                    lotacao_origem__in=employer.work_locations.filter(
                        pk=self.request.GET.get("execution_organ")
                    )
                )
                & Q(passo__gt=0)
            )
            .values("protocolo")
        )

        return self.Model.objects.filter(origin__in=query)

    def get_archived_query(self):
        employer = employee_from_user(self.request.user)

        return self.Model.objects.exclude(closed_by=None).filter(
            location__in=employer.work_locations,
            origin__movimentacoes__in=Movimentacao.closedbox_queryset(),
        )

    def get_query_by_officer(self):
        employee = employee_from_user(self.request.user)

        pkset = self.Model.objects.filter(
            parts__diligences__responsible_delivering__officer_diligence=employee
        ).values_list("pk")

        return self.Model.objects.filter(pk__in=pkset)

    def viewer(self, args=[]):
        tpl = loader.get_template("judicial/outcourtlawsuit-viewproccess.html")

        self.response.write(
            tpl.render(
                {
                    "jslist": Application.get_session_javascripts(),
                    "csslist": Application.get_session_stylesheet(),
                    "path": {
                        "minified": getattr(settings, "MINIFY_JS_OUT", False),
                        "context": "/".join(["", getattr(settings, "CONTEXT")]),
                        "static": "/".join(
                            ["", getattr(settings, "CONTEXT"), "static"]
                        ),
                    },
                }
            )
        )

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "origin" in params:
            if params.get("origin") != "":
                field = getattr(self.Model, "origin")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(origin=query.get(pk=params.get("origin")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(origin=None)

        if "location" in params:
            if params.get("location") != "":
                field = getattr(self.Model, "location")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(location=query.get(pk=params.get("location")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(location=None)

        return params

    def export(self, args=[]):
        rst = []

        route = {
            "historic": self.historic_query,
            "archived": self.get_archived_query,
            "default": self.get_query,
        }

        query = route.get(self.request.GET.get("defaultRoute", "default"), "default")()

        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = [self.model_to_dict(record) for record in query]

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        def location_pk(obj):
            if not isinstance(obj, Model):
                return [i.pk for i in obj]
            else:
                return [obj.pk]

        def location_unicode(obj):
            if not isinstance(obj, Model):
                return [str(i) for i in obj]
            else:
                return [str(obj)]

        def extract_interested(instance):
            if instance.can_read:
                return (
                    nil_unicode(instance.origin.interessado, None)
                    if instance.origin
                    else None
                )
            else:
                return "COM CONTROLE DE ACESSO"

        last_part = instance.last_part_lawsuit_signed
        lawsuit_title = (
            instance.title if instance.can_read else "COM CONTROLE DE ACESSO"
        )

        rst.update(
            origin=nil_pk(instance.origin, None),
            origin_unicode=nil_unicode(instance.origin, None),
            origin_codigo=getattr(instance.origin, "codigo", None),
            origin_assunto=getattr(instance.origin, "assunto", "Desconhecido"),
            origin_interessado_unicode=extract_interested(instance),
            type_lawsuit=instance.type_lawsuit,
            type_lawsuit_display=nil_display(instance, "type_lawsuit", None),
            location_unicode=nil_unicode(instance.location, None),
            location=nil_pk(instance.location, None),
            # FIXME para manter a compatibilidade
            current_location_unicode=", ".join(
                location_unicode(instance.current_location)
            ),
            current_location=location_pk(instance.current_location),
            external_location_unicode=", ".join(
                location_unicode(
                    [organ for organ in instance.external_locations.filter()]
                )
            ),
            external_location=location_pk(
                [organ for organ in instance.external_locations.filter()]
            ),
            cache_number=instance.cache_number,
            year=int(instance.year or 0),
            title=lawsuit_title,
            deadline=instance.deadline,
            closed=(
                (True if instance.origin.data_finalizado else False)
                if instance.origin
                else False
            ),
            number_lawsuit=int(instance.number_lawsuit or 0),
            icons=instance.icons,
            last_document_signed=nil_unicode(last_part, None),
            date_last_document_signed=nil_datetime(
                last_part.signed_at if last_part else None, None
            ),
            acting_zone_unicode=nil_unicode(instance.acting_zone, None),
            acting_zone=nil_pk(instance.acting_zone, None),
            urgent=instance.tags.filter(tag_type=1, slug="urgente").exists(),
            is_received=instance.is_received,
            lawsuit_unicode=("%s - %s" % (instance.cache_number, lawsuit_title)),
            titles_reminders=[reminder.title for reminder in instance.my_reminders],
            in_secretary=instance.in_secretary,
            in_give_back_box=instance.in_give_back_box,
        )

        return rst

    def mark_with_tag(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        try:
            self._read_special_verb()
            oid = self.request.PUT.get("outCourtLawsuit", 0)
            oid_tag = self.request.PUT.get("tag", False)
            checked = self.request.PUT.get("checked").lower() in (
                "true",
                "1",
                "t",
                "yes",
            )
            outcourtlawsuit = self.Model.objects.get(pk=oid)
            tag = (
                Tag.objects.get(pk=oid_tag)
                if oid_tag
                else Tag.objects.get(slug="urgente", tag_type=1)
            )
            msg = "Nada foi realizado."

            if checked and not outcourtlawsuit.tags.filter(id=tag.id).exists():
                outcourtlawsuit.tags.add(tag)
                msg = "Localizador associado ao procedimento com sucesso."
            elif not checked and outcourtlawsuit.tags.filter(id=tag.id).exists():
                outcourtlawsuit.tags.remove(tag)
                msg = "Localizador removido de procedimento com sucesso."

            rst.update(success=True, message=msg)
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def mark_execution_secretary(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        try:
            self._read_special_verb()
            with transaction.atomic():
                lawsuits = self.Model.objects.filter(
                    pk__in=self.request.PUT.getlist("pkset")
                )
                tag = Tag.objects.get(slug="caixa-da-secretaria", tag_type=1)

                for lawsuit in lawsuits:
                    secretary = None
                    secretaries = Secretary.objects.filter(
                        execution_organs=lawsuit.location
                    )
                    if not secretaries.exists():
                        raise Exception(
                            "A promotoria deste procedimento ainda não está em uma secretaria."
                        )
                    else:
                        secretary = secretaries.first()

                    if not lawsuit.tags.filter(
                        slug="caixa-da-secretaria", tag_type=1
                    ).exists():
                        lawsuit.tags.add(tag)

                        AuditDispatchSecretary.objects.create(
                            lawsuit=lawsuit,
                            location=lawsuit.location,
                            secretary=secretary,
                            type_dispatch=1,
                        )
                    else:
                        raise Exception(
                            "Este procedimento já se encontra na secretaria."
                        )

            rst.update(
                success=True,
                message="Procedimento(s) enviado(s) para secretaria com sucesso",
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def remove_lawsuit_tag(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        try:
            self._read_special_verb()
            with transaction.atomic():
                lawsuits = self.Model.objects.filter(
                    pk__in=self.request.PUT.getlist("pkset")
                )
                tag = Tag.objects.get(slug=self.request.PUT.get("slug_tag"), tag_type=1)

                for lawsuit in lawsuits:
                    lawsuit.tags.remove(tag)

            rst.update(success=True, message="Procedimento recebido da secretaria")
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def mark_give_back_execution_organ(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        try:
            self._read_special_verb()
            with transaction.atomic():
                lawsuits = self.Model.objects.filter(
                    pk__in=self.request.PUT.getlist("pkset")
                )
                tag = Tag.objects.get(slug="caixa-da-secretaria", tag_type=1)
                tag_back = Tag.objects.get(slug="proc-devolvidos", tag_type=1)

                for lawsuit in lawsuits:
                    secretary = None
                    secretaries = Secretary.objects.filter(
                        execution_organs=lawsuit.location
                    )
                    if not secretaries.exists():
                        raise Exception(
                            "A promotoria deste procedimento ainda não está em uma secretaria."
                        )
                    else:
                        secretary = secretaries.first()

                    if lawsuit.tags.filter(
                        slug="caixa-da-secretaria", tag_type=1
                    ).exists():
                        lawsuit.tags.remove(tag)

                        AuditDispatchSecretary.objects.create(
                            lawsuit=lawsuit,
                            location=lawsuit.location,
                            secretary=secretary,
                            type_dispatch=2,
                        )

                    lawsuit.tags.add(tag_back)

            rst.update(
                success=True,
                message="Procedimento(s) retirado(s) da secretaria com sucesso.",
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def receive_movement(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            self._read_special_verb()
            rest_resource = self.request.PUT.get("rest_resource")

            if rest_resource == "EJudOutCourtLawsuit":
                with transaction.atomic():
                    for ocl in OutCourtLawsuit.objects.filter(
                        pk__in=self.request.PUT.getlist("pk")
                    ):
                        ocl.receive_movement()

                response.update(message="Procedimento recebido com sucesso.")
            else:
                response.update(
                    message="Procedimento carregado (por admin), porém não recebido"
                )

            response.update(success=True)
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))


class EJudOutCourtLawsuitOfficer(EJudOutCourtLawsuit):

    def get_query(self):
        query = self.Model.objects.none()
        user = self.request.user

        if user.has_perm("judicial.oficial_dilig"):
            pkset = self.Model.objects.filter(
                parts__diligences__responsible_delivering__officer_diligence=employee_from_user(
                    user
                )
            ).values_list("pk")
            query = self.Model.objects.filter(pk__in=pkset)

        return query


class EJudOutCourtLawsuitAPI(EJudOutCourtLawsuit):

    full_text_index = (
        "has_interested__person__nome__icontains",
        "blokes__person__bloke__nome__icontains",
        "blokes__commonperson__bloke__nome__icontains",
        "blokes__governmentpublic__bloke__nome__icontains",
        "blokes__company__bloke__nome__icontains",
        "blokes__governmentpublic__bloke__nome__icontains",
    )

    def get_query(self):
        query = super(EJudOutCourtLawsuit, self).get_query()
        query = (
            query.filter(removed_at__isnull=True, parts__signed_by__isnull=False)
            .distinct()
            .order_by("-year", "-number_lawsuit")
        )

        return query

    def model_to_dict(self, instance):
        _dict_ = {}

        _dict_ = {
            "id": instance.id,
            "subjects": [str(matter) for matter in instance.matters.all()]
            or ["Não informado"],
            "kind": instance.type_lawsuit,
            "kind_text": instance.get_type_lawsuit_display(),
            "code": instance.origin.codigo,
            "number": instance.number_lawsuit,
            "year": instance.year,
            "can_read": instance.can_read,
            "full_number": instance.cache_number,
            "location": (
                str(instance.location)
                if hasattr(instance, "location")
                else "Não informado"
            ),
            "cities": [str(city) for city in instance.notice_locations.all()]
            or ["Não informado"],
            "interested": list(instance.interested.values_list("nome", flat=True))
            or ["Não informado"],
            "investigated": [str(bloke) for bloke in instance.blokes.all()]
            or ["Não informado"],
        }

        return _dict_

    @is_public()
    def fetch_kind_choices(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda.", "collection": None}

        kind_choices = [
            choice for choice in Choice.get_choices_for("judicial", "TYPE_LAWSUIT")
        ]
        rst.update(
            success=True,
            message="Processado com sucesso!",
            collection=[("", "Todos")] + sorted(kind_choices, key=lambda c: c[1]),
        )

        self.renderer(rst)

    @is_public()
    def fetch_years(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda.", "collection": None}

        years = (
            OutCourtLawsuit.objects.filter(year__isnull=False)
            .values_list("year", flat=True)
            .order_by("-year")
            .distinct()
        )

        rst.update(
            success=True,
            message="Processado com sucesso!",
            collection=[("", "Todos")] + [(year, year) for year in years],
        )

        self.renderer(rst)

    @is_public()
    def fetch_cities(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda.", "collection": None}

        cities = (
            Lotacao.objects.filter(nome__icontains="promotoria")
            .values_list("localidade", "localidade__nome")
            .order_by("localidade__nome")
            .distinct()
        )

        rst.update(
            success=True,
            message="Processado com sucesso!",
            collection=[("", "Todas")] + list(cities),
        )

        self.renderer(rst)


class EJudOutCourtLawsuitSecretary(EJudOutCourtLawsuit):

    def get_query(self):
        query = self.Model.objects.none()

        user = get_current_user()
        employee = employee_from_user(user)

        if (
            user.has_perm("judicial.can_view_outcourtlawsuit_secretary")
            or user.is_superuser
        ):
            employee_locations = employee.work_assignment_effective_exercise.values(
                "lotacao"
            )

            secretaries = Secretary.objects.filter(location__in=employee_locations)
            execution_organs = secretaries.values("execution_organs")

            query = (
                self.Model.objects.filter(
                    tags__slug="caixa-da-secretaria", location__in=execution_organs
                )
                .prefetch_related("dispatches")
                .order_by("-dispatches__created_at")
            )

        return query

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        date_send_secretary = None
        query = instance.dispatches.filter(type_dispatch=1, location=instance.location)

        if query.exists():
            audit = query.first()
            date_send_secretary = audit.created_at

        rst.update(date_send_secretary=nil_datetime(date_send_secretary, None))

        return rst


class EJudOutCourtLawsuitSearch(EJudOutCourtLawsuit):

    def get_query(self):
        query = self.Model.objects.none()

        user = get_current_user()
        employee = employee_from_user(user)

        query = (
            self.Model.objects.filter()
            .prefetch_related("has_interested")
            .prefetch_related("blokes")
        )

        return query

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        def extract_interesteds(instance):
            if instance.can_read:
                return ", ".join(
                    [item.person.nome for item in instance.has_interested.all()]
                )
            else:
                return "COM CONTROLE DE ACESSO"

        def extract_blokes(instance):
            if instance.can_read:
                return ", ".join(
                    [item.my_origin.bloke.nome for item in instance.blokes.all()]
                )
            else:
                return "COM CONTROLE DE ACESSO"

        def location_unicode(obj):
            if not isinstance(obj, Model):
                return [str(i) for i in obj]
            else:
                return [str(obj)]

        lawsuit_title = (
            instance.title if instance.can_read else "COM CONTROLE DE ACESSO"
        )

        rst.update(
            origin_codigo=getattr(instance.origin, "codigo", None),
            cache_number=instance.cache_number,
            title=lawsuit_title,
            type_lawsuit_display=nil_display(instance, "type_lawsuit", None),
            current_location_unicode=", ".join(
                location_unicode(instance.current_location)
            ),
            location_unicode=nil_unicode(instance.location, None),
            interesteds=extract_interesteds(instance),
            blokes=extract_blokes(instance),
            status="Finalizado" if instance.closed_by else "Em andamento",
        )

        return rst

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.search.person.Manage")')
