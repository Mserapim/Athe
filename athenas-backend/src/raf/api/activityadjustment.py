# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import get_current_user
from raf.models import (
    WorkerLocation,
    Item,
    SubItem,
    Activity,
    ActivityAdjustment,
    TrustRelationship,
    Conversation,
)
from django.db.models import Q
from standard.models import Configuration
from rh.models import Lotacao as Location, Servidor
import raf.api.util as util
from django.http import QueryDict

log = getLogger(__name__)


class RAFActivityAdjustment(RestfulDRY):

    _model = ActivityAdjustment

    force_upper = False

    def model_to_dict(self, instance):
        _dict_ = super(RAFActivityAdjustment, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "status": instance.status,
                "conversation": (
                    instance.conversation.pk if instance.conversation else None
                ),
                "activity_created_at": (
                    instance.conversation.created_at_formatted
                    if instance.conversation
                    else instance.created_at_formatted
                ),
                "activity_amount_submitted": instance.activity.amount_submitted,
                "workerlocation_unicode": instance.activity.workerlocation.location.nome,
                # 'quiz': instance.activity.item.quiz.pk,
                "quiz_unicode": instance.activity.item.quiz.typequiz.title,
                "item_unicode": instance.activity.item.title,
                "subitem_unicode": instance.activity.subitem.title,
            }
        )
        return _dict_

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = util.request_params(self)
            adjustment = self.get_query().get(pk=int(params.get("adjustment", 0) or 0))
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=adjustment.rendered)
        self.renderer(rst)

    def undoAction(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            situation = params.get("situation", 0)
            list_adjustment = ActivityAdjustment.objects.filter(
                pk__in=params.get("adjustment_list").split(",")
            )
            for adjustment in list_adjustment:
                adjustment.undoAction(answer=params.get("answer", ""))
        except self.Model.DoesNotExist:
            rst.update(message="Solicitação de ajuste não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            txt = "Decisão foi desfeita com sucesso."
            rst.update(success=True, message=txt)
        self.renderer(rst)

    def sendAction(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            adjustment = ActivityAdjustment.objects.filter(
                pk=params.get("adjustment")
            ).first()
            adjustment.situation = 0
            adjustment.save()
            for da in adjustment.dataadjustment.all():
                da.situation = 0
                da.save()
        except self.Model.DoesNotExist:
            rst.update(message="Solicitação de ajuste não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            txt = "Envio realizado com sucesso."
            rst.update(success=True, message=txt)
        self.renderer(rst)

    def action(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            situation = params.get("situation", 0)
            list_adjustment = ActivityAdjustment.objects.filter(
                pk__in=params.get("adjustment_list").split(",")
            )
            for adjustment in list_adjustment:
                adjustment.action(
                    situation=int(situation), answer=params.get("answer", "")
                )
        except self.Model.DoesNotExist:
            rst.update(message="Pedido de ajuste não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            txt = ""
            if int(situation) == 2:
                txt = "Solicitação deferida com sucesso."
            if int(situation) == 3:
                txt = "Solicitação indeferida com sucesso."
            if int(situation) == 4:
                txt = "Solicitação cancelada com sucesso."
            rst.update(success=True, message=txt)
        self.renderer(rst)

    def save(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            activity = Activity.objects.filter(
                pk=int(params.get("activity", "0"))
            ).first()
            workerlocation = WorkerLocation.objects.filter(
                pk=int(params.get("workerlocation", "0"))
            ).first()
            item = Item.objects.filter(pk=int(params.get("item", "0"))).first()
            subitem = SubItem.objects.filter(pk=int(params.get("subitem", "0"))).first()
            if activity is None:
                activity = Activity.objects.filter(
                    workerlocation=workerlocation, item=item, subitem=subitem
                ).first()
                if activity is None:
                    activity = Activity()
                    activity.workerlocation = workerlocation
                    activity.item = item
                    activity.subitem = subitem
                    activity.amount_submitted = 0
                    activity.save()
            adjustment = ActivityAdjustment()
            adjustment.activity = activity
            adjustment.amount = activity.amount_submitted
            adjustment.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solicitação de ajuste criado com sucesso...",
                adjustment_id=adjustment.pk,
                activity_id=activity.pk,
            )
        self.renderer(rst)

    def newAmount(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            adjustment = ActivityAdjustment.objects.filter(
                pk=int(params.get("adjustment", "0"))
            ).first()
            retorno = adjustment.amount if adjustment else 0
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solicitação de ajuste criado com sucesso...",
                newAmount=retorno,
            )
        self.renderer(rst)

    def close(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            adjustment = ActivityAdjustment.objects.filter(
                pk=int(params.get("adjustment", "0"))
            ).first()
            if adjustment.dataadjustment.count() == 0:
                adjustment.delete()

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Fechamento concluído com sucesso...",
            )
        self.renderer(rst)


class RAFActivityAdjustmentEmployee(RAFActivityAdjustment):

    def model_to_dict(self, instance):
        _dict_ = super(RAFActivityAdjustmentEmployee, self).model_to_dict(instance)
        _dict_.update(
            {
                "location": instance.activity.workerlocation.location.pk,
                "conversation_in_box": self.conversation_in_box_employee(
                    instance=instance
                ),
            }
        )
        return _dict_

    def get_query(self):
        query = super(RAFActivityAdjustmentEmployee, self).get_query()
        if self.request.user.has_perm("raf.can_sign_adjustment"):
            return query.filter()
        return query.filter(
            activity__workerlocation__raf__employee__in=TrustRelationship.queryset_relationship_from_employee(
                pklist=True
            )
        )

    def conversation_in_box_employee(self, instance):
        try:
            flag = False
            query = self.employee_waiting_conversation_inbox()
            if instance.conversation:
                flag = (
                    instance.conversation.last_content.origin.pk
                    not in query.filter().values_list(
                        "activity__workerlocation__location__pk", flat=True
                    )
                )
        except Exception as e:
            log.info("Erro: %s" % e)
            return False
        else:
            return flag

    def inbox_waiting_conversation_employee(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }
        try:
            query = self.employee_waiting_conversation_inbox()
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
                inst = query.get(pk=args[0])
                rst.update(success=True, instance=self.model_to_dict(inst))
        except Exception as e:
            rst.update(message=str(e))
        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def employee_waiting_conversation_inbox(self):
        query = super(RAFActivityAdjustment, self).get_query()
        employee = employee_from_user(get_current_user())
        query_part = []
        query_trust = Q(~Q(activated=False) & Q(trust_employee=employee)) | Q(
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
                    dataadjustment__conversation__locations__pk__in=empl._raw_locations(
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
        return query.filter(result).distinct()

    def get_or_create_activity(self, args=[]):

        rst = {
            "success": False,
            "message": "nada foi feito ainda!",
        }
        try:
            params = util.request_params(self)
            msg = "ocorreu um erro ao gerar o formulário. %s não existe ou não foi infomado. Contate o administrador do sistema."
            if (
                not params.get("workerlocation")
                or not WorkerLocation.objects.filter(
                    pk=int(params.get("workerlocation", 0))
                ).exists()
            ):
                raise Exception(msg % "Local de Trabalho")
            if (
                not params.get("item")
                or not Item.objects.filter(pk=int(params.get("item", 0))).exists()
            ):
                raise Exception(msg % "Item")
            if (
                not params.get("subitem")
                or not SubItem.objects.filter(pk=int(params.get("subitem", 0))).exists()
            ):
                raise Exception(msg % "SubItem")
            workerlocation = WorkerLocation.objects.get(
                pk=params.get("workerlocation", 0)
            )
            item = Item.objects.get(pk=params.get("item", 0))
            subitem = SubItem.objects.get(pk=params.get("subitem", 0))
            activity = Activity.get_or_create(
                workerlocation=workerlocation, item=item, subitem=subitem
            )
            if activity:
                rst.update(activity=activity.pk)
            else:
                rst.update(activity=0)
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Atividade criada!")
        self.renderer(rst)


class RAFActivityAdjustmentInternalControl(RAFActivityAdjustment):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("raf.adjustment.AdjustmentInternalControlManage")'
        )

    def get_query(self):
        return (
            super(RAFActivityAdjustmentInternalControl, self)
            .get_query()
            .order_by("-created_at")
        )

    def model_to_dict(self, instance):
        _dict_ = super(RAFActivityAdjustmentInternalControl, self).model_to_dict(
            instance
        )
        cfg = Configuration.get_or_create("raf")
        location = Location.objects.get(pk=cfg.get("location"))
        _dict_.update(
            {
                "location": location.pk if location else None,
                "conversation_in_box": self.conversation_in_box_corregedor(
                    instance=instance
                ),
            }
        )
        return _dict_

    def conversation_in_box_corregedor(self, instance):
        try:
            flag = False
            cfg = Configuration.get_or_create("raf")
            location = Location.objects.get(pk=cfg.get("location"))
            if instance.conversation:
                flag = instance.conversation.last_content.origin.pk != location.pk
        except Exception as e:
            log.info("Erro: %s " % e)
            return False
        else:
            return flag

    def inbox_waiting(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }
        try:
            query = self.corregedor_inbox_waiting_conversation()
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
                inst = query.get(pk=args[0])
                rst.update(success=True, instance=self.model_to_dict(inst))
        except Exception as e:
            rst.update(message=str(e))
        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def corregedor_inbox_waiting_conversation(self):
        query = super(RAFActivityAdjustmentInternalControl, self).get_query()
        query_set = Q(Q(situation__in=[0, 1]))
        return query.filter(query_set)

    def get_adjustment(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        params = util.request_params(self)
        query = ActivityAdjustment.objects.filter(pk=int(params.get("adjustment", "0")))
        data = [
            {
                "adjustment_pk": adjustment.pk,
                "adjustment_situation": adjustment.situation,
                "raf_monthyear": str(adjustment.activity.workerlocation.raf.month)
                + "/"
                + str(adjustment.activity.workerlocation.raf.year),
                "employee_unicode": adjustment.activity.workerlocation.raf.employee.pessoa_fisica.nome,
                "workerlocation_unicode": adjustment.activity.workerlocation.location.nome,
                "quiz_unicode": adjustment.activity.item.quiz.typequiz.title,
                "item_unicode": adjustment.activity.item.title,
                "subitem_unicode": adjustment.activity.subitem.title,
                "activity_amount_submitted": adjustment.activity.amount_submitted,
            }
            for adjustment in query
        ]
        rst.update(
            success=True,
            message="Dados encontrados com sucesso.",
            count=query.count(),
            collection=data,
        )
        return self.renderer(rst)
