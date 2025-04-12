# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger, employee_from_user
from judicial.models import (
    JudicialDiligence,
    OfficerDiligence,
    County,
    RequestCollaboration,
    Lotacao,
    Secretary,
)
from ged.models import Arquivo
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from contrib.middleware import get_current_user
from django.db import transaction
from django.db.models import Q
from django.template import loader

import json

log = getLogger(__name__)


class EJudJudicialDiligence(Restful):

    _model = JudicialDiligence

    _sort_map = {
        "out_court_lawsuit_location_unicode": "part__lawsuit__location__nome",
        "out_court_lawsuit_number": "part__lawsuit__cache_number",
    }

    full_text_index = (
        "responsible_delivering__officer_diligence__pessoa_fisica__nome__icontains",
        "formated_number__icontains",
    )

    force_upper = False

    def printer(self, args=[]):
        self.response["Content-Type"] = "text/html; charset=utf-8"
        tpl = loader.get_template("judicial/printer.html")
        documents = []

        try:
            diligence = self.get_query().get(pk=args[0])
            documents.append({"at": diligence.signed_at, "page": diligence.rendered})
        except self.Model.DoesNotExist as ex:
            log.exception(ex)
            documents.append("<h1>Diligência não encontrada</h1>")
        except Exception as e:
            log.exception(e)
            documents.append(str(e))
        finally:
            self.response.write(tpl.render({"documents": documents}))

    def assume_delivery(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                for diligence in self.get_query().filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    diligence.assume_delivery()

            rst.update(
                message="Diligencias assumida para serem entregues pelo órgão de execução.",
                success=True,
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def send_to_officer_diligence(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}

        try:
            officer = OfficerDiligence.objects.get(pk=self.request.POST.get("officer"))
            with transaction.atomic():
                for diligence in self.Model.objects.filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    diligence.send_to_officer_diligence(officer)
        except OfficerDiligence.DoesNotExist:
            rst.update(message="Não consegui encontrar o oficial de diligencia.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Procedimento realizado com sucesso.")

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    def send_to_random_officer_diligence(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}

        try:
            with transaction.atomic():
                for diligence in self.Model.objects.filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    diligence.send_to_random_officer_diligence()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Procedimento realizado com sucesso.")

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    def remove_from_officer_diligence(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}

        try:
            with transaction.atomic():
                for diligence in self.Model.objects.filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    diligence.remove_from_officer_diligence()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Procedimento realizado com sucesso.")

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('judicial.diligences.Manage')")

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "prevent_delivery_in_executionorgan" in params:
            params.update(
                prevent_delivery_in_executionorgan=params.get(
                    "prevent_delivery_in_executionorgan", "off"
                ).lower()
                == "on"
            )

        if "date_delivery" in params:
            if params.get("date_delivery") != "":
                params.update(
                    date_delivery=DateUtils.str_to_datetime(params.get("date_delivery"))
                )
            else:
                params.update(date_delivery=None)

        for attr in ("part", "county", "who", "responsible_delivering"):
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

        if params.get("diligence_file", "") != "":
            params.update(
                {"diligence_file": Arquivo.objects.get(pk=params.get("diligence_file"))}
            )
        elif "diligence_file" in params:
            del params["diligence_file"]

        return params

    def get_subclass(self, obj):
        if hasattr(obj, "citation"):
            return str(obj.citation)
        if hasattr(obj, "intimation"):
            return str(obj.intimation)
        if hasattr(obj, "notificationdiligence"):
            return str(obj.notificationdiligence)
        if hasattr(obj, "scientization"):
            return str(obj.scientization)
        if hasattr(obj, "diligencerequest"):
            return str(obj.diligencerequest)
        else:
            return ""

    def get_query(self, *args, **kwargs):
        query = super(EJudJudicialDiligence, self).get_query(*args, **kwargs)

        user = get_current_user()
        employee = employee_from_user(user)

        if user.has_perm("judicial.admin_dilig"):
            log.debug("(1)")
            pass
        elif user.has_perm("judicial.manager_dilig"):
            counties = None

            counties = County.objects.filter(
                locations__in=employee.work_locations.values("localidade_id")
            )

            # query = self.Model.diligences_in_county(county)
            query = self.Model.objects.filter(county__in=counties)
        else:
            query = query.none()

        return query

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)
        rst.update(
            title=instance.title,
            formated_number=instance.formated_number,
            text=instance.text,
            created_at=nil_datetime(instance.created_at, None),
            signed_at=nil_datetime(instance.signed_at, None),
            date_delivery=nil_datetime(instance.date_delivery, None),
            date_receipt_diligence=nil_datetime(
                (
                    instance.date_receipt_diligence
                    if not instance.assumed_delivery_at
                    else instance.assumed_delivery_at
                ),
                None,
            ),
            observation=instance.observation,
            responsible_delivering=nil_pk(instance.responsible_delivering, None),
            responsible_delivering_unicode=nil_unicode(
                instance.responsible_delivering, "Aguardando distribuição"
            ),
            who=nil_pk(instance.who, None),
            who_unicode=nil_unicode(instance.who, None),
            delivery_status=instance.delivery_status,
            delivery_status_display=nil_display(instance, "delivery_status", None),
            who_type=instance.who_type,
            who_type_display=nil_display(instance, "who_type", None),
            icon_status=instance.icons,
            deadline=instance.deadline,
            type_diligence=self.get_subclass(instance),
            diligence_file=(
                instance.diligence_file.pk if instance.diligence_file else None
            ),
            filename=(
                instance.diligence_file.filename if instance.diligence_file else None
            ),
            permalinks=instance.permalinks,
            prevent_delivery_in_executionorgan=instance.prevent_delivery_in_executionorgan,
            assumed_delivery_by=nil_pk(instance.assumed_delivery_by, None),
            assumed_delivery_by_unicode=nil_unicode(instance.assumed_delivery_by, None),
            county=nil_pk(instance.county, None),
            county_unicode=nil_unicode(instance.county, None),
            assumed_delivery_at=nil_datetime(instance.assumed_delivery_at, None),
            assumed_delivery=(True if instance.assumed_delivery_by else False),
            out_court_lawsuit_number=instance.part.lawsuit.cache_number,
            out_court_lawsuit_pk=instance.part.lawsuit.pk,
            out_court_lawsuit_location_unicode=nil_unicode(
                instance.part.lawsuit.location, None
            ),
            deadline_date_for_delivery=nil_datetime(
                instance.deadline_date_for_delivery, None
            ),
            count_type=instance.count_type,
            has_response_officer=instance.has_response_officer,
            response_is_signed_by_officer=instance.response_is_signed_by_officer,
            number_event=instance.number_event_control,
        )

        return rst

    def do_copy(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                jd = JudicialDiligence.objects.get(pk=self.request.POST.get("pk"))
                jd.do_copy()
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(success=True, message="Cópia realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))

    def finish_diligence(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                for jd in JudicialDiligence.objects.filter(
                    pk__in=self.request.POST.getlist("pk")
                ):
                    log.info(self.request.POST.getlist("pk"))
                    jd.finish_diligence()
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(success=True, message="Finalização realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))

    def render(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        oid = args[0] if args else 0

        try:
            obj = self.Model.objects.get(pk=oid)
            rst.update(
                success=True,
                message="Dados processados com sucesso",
                rendered=obj.rendered,
                extra_pages=obj.extra_pages,
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)


class EJudJudicialDiligenceOfficer(EJudJudicialDiligence):

    def get_query(self, *args, **kwargs):
        query = Restful.get_query(self, *args, **kwargs)

        user = get_current_user()
        employee = employee_from_user(user)

        if user.has_perm("judicial.oficial_dilig"):
            query = query.filter(responsible_delivering__officer_diligence=employee)
        else:
            query = query.none()

        return query


class EJudJudicialDiligenceExecutionOrgan(EJudJudicialDiligence):

    def get_query(self, *args, **kwargs):
        query = Restful.get_query(self, *args, **kwargs)

        user = get_current_user()
        employee = employee_from_user(user)

        if not user.has_perm("judicial.admin_dilig") and user.has_perm(
            "judicial.promotor_dilig"
        ):
            collab_location_ids = (
                RequestCollaboration.objects.filter(canceled_by=None)
                .filter(
                    Q(requestcollaborationperson__person=employee.pessoa_fisica)
                    | Q(
                        requestcollaborationgeneralorgan__general_organ__in=employee.work_locations
                    )
                )
                .values("lawsuit__location_id")
            )

            employee_locations = employee.work_assignment_effective_exercise.values(
                "lotacao"
            )
            secretaries = Secretary.objects.filter(location__in=employee_locations)
            execution_organs = secretaries.values("execution_organs")

            acting_locations = Lotacao.objects.filter(
                Q(pk__in=employee.work_locations)
                | Q(pk__in=collab_location_ids)
                | Q(pk__in=execution_organs)
            )

            query = query.filter(part__lawsuit__location__in=acting_locations)
        elif not user.has_perm("judicial.admin_dilig") and not user.has_perm(
            "judicial.promotor_dilig"
        ):
            query = query.empty()

        return query
