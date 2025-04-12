# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import set_current_user, get_current_user
from django.db.models import Q
from raf.models import DataAdjustment, AutoReference, TrustRelationship
from rh.models import Servidor
from judicial.models import LegalClass, LegalMatter, LegalMoviment as LegalMovement
from . import util
import datetime

log = getLogger(__name__)


class RAFDataAdjustment(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = DataAdjustment

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.adjustment.dataadjustment.Launcher")')

    def get_query(self):
        return super(RAFDataAdjustment, self).get_query().order_by("created_at")

    def model_to_dict(self, instance):
        _dict_ = super(RAFDataAdjustment, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "status": instance.status,
                "activityadjustment_id": instance.activityadjustment.pk,
                "classification": """Classe: <b>"""
                + (instance.legalclass.title if instance.legalclass else "")
                + """</b><br />Assunto: <b>"""
                + (instance.legalmatter.title if instance.legalmatter else "")
                + """</b><br />Movimento: <b>"""
                + (instance.movement.title if instance.movement else "")
                + """</b>""",
                "legalclass_title": (
                    instance.legalclass.title if instance.legalclass else ""
                ),
                "legalmatter_title": (
                    instance.legalmatter.title if instance.legalmatter else ""
                ),
                "movement_title": instance.movement.title if instance.movement else "",
                "process_number_formatted": instance.process_number_formatted,
                "location": instance.activityadjustment.activity.workerlocation.location.pk,
                "conversation": (
                    instance.conversation.pk if instance.conversation else None
                ),
                "conversation_in_box": self.conversation_in_box_employee(
                    instance=instance
                ),
                "conversation_last_content": (
                    instance.initial_message
                    if instance.conversation.last_content is None
                    else instance.conversation.last_content.message
                ),
            }
        )
        return _dict_

    def conversation_in_box_employee(self, instance):
        try:
            flag = False
            query = self.employee_waiting_conversation_inbox()
            if instance.conversation:
                if instance.conversation.last_content:
                    if instance.conversation.last_content.origin:
                        flag = instance.conversation.last_content.origin.pk not in query.filter().values_list(
                            "activityadjustment__activity__workerlocation__location__pk",
                            flat=True,
                        )
        except Exception as e:
            log.info("Erro: %s" % e)
            return False
        else:
            return flag

    def employee_waiting_conversation_inbox(self):
        query = super(RAFDataAdjustment, self).get_query()
        employee = employee_from_user(get_current_user())
        query_part = []
        query_trust = ~Q(activated=False) & Q(trust_employee=employee) | Q(
            employee=employee
        )
        query_employee = Q(
            Q(
                pk__in=TrustRelationship.objects.filter(query_trust).values_list(
                    "employee"
                )
            )
        )
        if get_current_user().has_perm("raf.can_management_raf"):
            query_employee = Q(pk__in=Servidor.objects.filter(tipo="M").values("pk"))
        for empl in Servidor.objects.filter(query_employee):
            query_part.append(
                Q(
                    conversation__locations__pk__in=empl._raw_locations(
                        option=2
                    ).values_list("lotacao__pk", flat=True)
                )
            )
        result = None
        if query_part:
            for part in query_part:
                result = part if not result else part | result
        else:
            result = Q(pk=0)
        return query.filter(result)

    def action(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            situation = params.get("situation", 0)
            answer = params.get("answer", 0)
            list_dataadjustment = []
            if params.get("dataadjustment_list") == "0":
                list_dataadjustment = DataAdjustment.objects.filter(
                    activityadjustment__pk=params.get("activityadjustment")
                )
            else:
                list_dataadjustment = DataAdjustment.objects.filter(
                    pk__in=params.get("dataadjustment_list").split(",")
                )
            for dataadjustment in list_dataadjustment:
                dataadjustment.action(situation=situation, answer=answer)
        except self.Model.DoesNotExist:
            rst.update(message="Item do ajuste não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            txt = ""
            if int(situation) == 2:
                txt = "Item deferido com sucesso."
            if int(situation) == 3:
                txt = "Item indeferido com sucesso."
            rst.update(success=True, message=txt)
        self.renderer(rst)

    def get_data_process(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            activity = params.get("activity", 0)
            source = params.get("source", 0)
            if int(source) == 1:
                process_number = int(
                    params.get("process_number", 0)
                    .replace(".", "")
                    .replace("-", "")
                    .replace("/", "")
                )
            else:
                process_number = params.get("process_number", 0)
            date = datetime.datetime.strptime(
                params.get("date", 0)[0:10], "%Y-%m-%d"
            ).date()
            autoreference = AutoReference.objects.filter(
                process_number=process_number,
                source_add=source,
                date__year=date.year,
                date__month=date.month,
                date__day=date.day,
            ).last()
            if autoreference:
                if (
                    autoreference.source_add == 1
                    and autoreference.is_adjustment is False
                ):
                    classe = (
                        LegalClass.objects.filter(
                            cnmp_code=autoreference.content_object.codclasse
                        )
                        .first()
                        .pk
                        if LegalClass.objects.filter(
                            cnmp_code=autoreference.content_object.codclasse
                        ).first()
                        else 0
                    )
                    matter = (
                        LegalMatter.objects.filter(
                            cnmp_code=autoreference.content_object.codassuntoprincipal
                        )
                        .first()
                        .pk
                        if LegalMatter.objects.filter(
                            cnmp_code=autoreference.content_object.codassuntoprincipal
                        ).first()
                        else 0
                    )
                    movement = (
                        LegalMovement.objects.filter(
                            cnmp_code=autoreference.content_object.codmovimento
                        )
                        .first()
                        .pk
                        if LegalMovement.objects.filter(
                            cnmp_code=autoreference.content_object.codmovimento
                        ).first()
                        else 0
                    )
                if (
                    autoreference.source_add == 1
                    and autoreference.is_adjustment is True
                ):
                    classe = autoreference.content_object.legalclass.pk
                    matter = autoreference.content_object.legalmatter.pk
                    movement = autoreference.content_object.movement.pk
                if autoreference.source_add == 3:
                    classe = 0
                    matter = 0
                    movement = 15128
                if autoreference.source_add == 4:
                    classe = (
                        LegalClass.objects.filter(
                            pk=autoreference.content_object.legalclass.pk
                        )
                        .first()
                        .pk
                        if LegalClass.objects.filter(
                            pk=autoreference.content_object.legalclass.pk
                        ).first()
                        else 0
                    )
                    matter = (
                        LegalMatter.objects.filter(
                            pk=autoreference.content_object.legalmatter.pk
                        )
                        .first()
                        .pk
                        if LegalMatter.objects.filter(
                            pk=autoreference.content_object.legalmatter.pk
                        ).first()
                        else 0
                    )
                    movement = (
                        LegalMovement.objects.filter(
                            pk=autoreference.content_object.movement.pk
                        )
                        .first()
                        .pk
                        if LegalMovement.objects.filter(
                            pk=autoreference.content_object.movement.pk
                        ).first()
                        else 0
                    )
        except self.Model.DoesNotExist:
            rst.update(message="Item do ajuste não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="sucesso",
                count=1 if autoreference else 0,
                classe=classe if autoreference else 0,
                matter=matter if autoreference else 0,
                movement=movement if autoreference else 0,
            )
        self.renderer(rst)

    def get_data_process_add(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            classe = 0
            matter = 0
            params = util.request_params(self)
            source = int(params.get("source", 0))
            process_number = int(
                params.get("process_number", 0)
                .replace(".", "")
                .replace("-", "")
                .replace("/", "")
            )
            autoreference = AutoReference.objects.filter(
                process_number=process_number
            ).first()

            if autoreference is None:
                autoreference = AutoReference.objects.filter(
                    process_number=params.get("process_number", 0)
                ).first()

            if autoreference:
                if (
                    autoreference.source_add == 1
                    and autoreference.is_adjustment is False
                ):
                    classe = (
                        LegalClass.objects.filter(
                            cnmp_code=autoreference.content_object.codclasse
                        )
                        .first()
                        .pk
                        if LegalClass.objects.filter(
                            cnmp_code=autoreference.content_object.codclasse
                        ).first()
                        else 0
                    )
                    matter = (
                        LegalMatter.objects.filter(
                            cnmp_code=autoreference.content_object.codassuntoprincipal
                        )
                        .first()
                        .pk
                        if LegalMatter.objects.filter(
                            cnmp_code=autoreference.content_object.codassuntoprincipal
                        ).first()
                        else 0
                    )
                if (
                    autoreference.source_add == 1
                    and autoreference.is_adjustment is True
                ):
                    classe = autoreference.content_object.legalclass.pk
                    matter = autoreference.content_object.legalmatter.pk
                if autoreference.source_add == 2:
                    classe = autoreference.content_object.legalclass.pk
                    matter = autoreference.content_object.legalmatter.pk
                if autoreference.source_add == 3:
                    classe = 0
                    matter = 0
                if autoreference.source_add == 4:
                    classe = (
                        LegalClass.objects.filter(
                            pk=autoreference.content_object.legalclass.pk
                        )
                        .first()
                        .pk
                        if LegalClass.objects.filter(
                            pk=autoreference.content_object.legalclass.pk
                        ).first()
                        else 0
                    )
                    matter = (
                        LegalMatter.objects.filter(
                            pk=autoreference.content_object.legalmatter.pk
                        )
                        .first()
                        .pk
                        if LegalMatter.objects.filter(
                            pk=autoreference.content_object.legalmatter.pk
                        ).first()
                        else 0
                    )
        except self.Model.DoesNotExist:
            rst.update(message="Item do ajuste não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="sucesso",
                count=1 if autoreference else 0,
                classe=classe if autoreference else 0,
                matter=matter if autoreference else 0,
            )
        self.renderer(rst)
