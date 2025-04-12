# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import get_current_user
from standard.models import Configuration
from django.db.models import Q
from django.template.defaultfilters import slugify
from datetime import datetime
from decimal import Decimal, ROUND_UP
from corregedoria.inspection.models import (
    Recommendations,
    DeadlineRecommendation,
    Inspection,
)
from corregedoria.models import ConfigScoreTable, BandScoreTable
from rh.models import Lotacao
from judicial.models import ExecutionOrgan

log = getLogger(__name__)


class INSPECTIONFollowRecommendation(RestfulDRY):
    _model = Recommendations
    force_upper = False

    full_text_index = (
        "inspection__responsible__pessoa_fisica__nome__icontains",
        "inspection__execution_organ__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.follow_recommendation.Manage")'
        )

    def get_query(self):
        query = super(INSPECTIONFollowRecommendation, self).get_query()
        return query.order_by("pk")

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONFollowRecommendation, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "deadline_grid": (
                    instance.deadline.strftime("%d/%m/%Y")
                    if instance.waiting_response and instance.deadline
                    else "--"
                ),
                "delayoftime": (
                    (
                        False
                        if instance.atual_deadline >= datetime.now().date()
                        else True
                    )
                    if instance.atual_deadline
                    else False
                ),
                "delayoftime_pending": DeadlineRecommendation.objects.filter(
                    recommendation=instance,
                    sent=True,
                    extension=True,
                    signdecision_by__isnull=True,
                ).exists(),
                "reportcompliance_pending": DeadlineRecommendation.objects.filter(
                    recommendation=instance, sent=True, signdecision_by__isnull=True
                )
                .filter(~Q(extension=True))
                .exists(),
                "delayoftime_editing": DeadlineRecommendation.objects.filter(
                    recommendation=instance,
                    extension=True,
                    signdecision_by__isnull=True,
                )
                .filter(~Q(sent=True))
                .exists(),
                "reportcompliance_editing": DeadlineRecommendation.objects.filter(
                    recommendation=instance, signdecision_by__isnull=True
                )
                .filter(~Q(extension=True))
                .filter(~Q(sent=True))
                .exists(),
            }
        )
        return _dict_

    def employee_initial(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda.",
        }
        try:
            employee = employee_from_user(get_current_user())
            workplaces = []
            for w in employee.responsible():
                workplaces.append(w.lotacao.pk)

            for insp in Inspection.objects.exclude(
                execution_organ__in=workplaces
            ).filter(employee=employee):
                workplaces.append(insp.execution_organ.pk)

        except self.Model.DoesNotExist:
            rst.update(message="Pessoa não encontrada.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="dados carregados com sucesso",
                employee_pk=employee.pk,
                workplaces=workplaces,
            )
        self.renderer(rst)

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = self.request.POST
            recommendation = Recommendations.objects.filter(
                pk=int(params.get("recommendation", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=recommendation.rendered)
        self.renderer(rst)

    def get_recommendation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            typeResponse = params.get("type_response")
            recommendation = (
                int(params.get("recommendation"))
                if params.get("recommendation") != ""
                else 0
            )
            data = []
            delayOfTime = None
            recommendation = Recommendations.objects.filter(pk=recommendation).first()
            if recommendation:
                if typeResponse == "delayOfTime":
                    delayOfTime = (
                        DeadlineRecommendation.objects.filter(
                            recommendation=recommendation, extension=True
                        )
                        .filter(~Q(sent=True))
                        .last()
                    )
                    if delayOfTime is None:
                        delayOfTime = DeadlineRecommendation()
                        delayOfTime.recommendation = recommendation
                        delayOfTime.extension = True
                        delayOfTime.save()
                else:
                    reportCompliance = (
                        DeadlineRecommendation.objects.filter(
                            recommendation=recommendation
                        )
                        .filter(~Q(extension=True))
                        .filter(~Q(sent=True))
                        .last()
                    )
                    if reportCompliance is None:
                        reportCompliance = DeadlineRecommendation()
                        reportCompliance.recommendation = recommendation
                        reportCompliance.save()
            data.append(
                {
                    "recommendation": (
                        recommendation.recommendation
                        if recommendation.recommendation
                        else ""
                    ),
                    "deadline_grid": (
                        recommendation.deadline.strftime("%d/%m/%Y")
                        if recommendation.recommendation and recommendation.deadline
                        else "--"
                    ),
                    "execution_organ_unicode": recommendation.inspection.execution_organ.nome,
                    "inspection_date_initial_formatted": recommendation.inspection.inspection_date_initial_formatted,
                    "inspection_date_final_formatted": recommendation.inspection.inspection_date_final_formatted,
                    "deadlinerecommendation_id": (
                        delayOfTime.pk if delayOfTime else reportCompliance.pk
                    ),
                    "deadlinerecommendation_response": (
                        delayOfTime.response
                        if delayOfTime
                        else reportCompliance.response
                    ),
                }
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True, message="Dados encontrados com sucesso.", collection=data
            )
        return self.renderer(rst)

    def saveDelayOfTime(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            delayOfTime = DeadlineRecommendation.objects.filter(
                pk=(
                    int(params.get("deadlinerecommendation_id"))
                    if params.get("deadlinerecommendation_id") != ""
                    else 0
                )
            ).first()
            if delayOfTime is None:
                recommendation = Recommendations.objects.filter(
                    pk=(
                        int(params.get("recommendation"))
                        if params.get("recommendation") != ""
                        else 0
                    )
                ).first()
                delayOfTime = DeadlineRecommendation()
                delayOfTime.recommendation = recommendation
                delayOfTime.extension = True
            delayOfTime.response = params.get("response")
            delayOfTime.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solcitação enviada com sucesso.",
            )
        return self.renderer(rst)

    def sendDelayOfTime(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            delayOfTime = DeadlineRecommendation.objects.filter(
                pk=(
                    int(params.get("deadlinerecommendation_id"))
                    if params.get("deadlinerecommendation_id") != ""
                    else 0
                )
            ).first()
            if delayOfTime is None:
                recommendation = (
                    Recommendations.objects.filter(
                        pk=(
                            int(params.get("recommendation"))
                            if params.get("recommendation") != ""
                            else 0
                        )
                    )
                    .filter(~Q(sent=True))
                    .first()
                )
                delayOfTime = DeadlineRecommendation()
                delayOfTime.recommendation = recommendation
                delayOfTime.extension = True
            delayOfTime.response = params.get("response")
            delayOfTime.sent = True
            delayOfTime.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solcitação enviada com sucesso.",
            )
        return self.renderer(rst)

    def cleanDelayOfTime(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            delayOfTime = (
                DeadlineRecommendation.objects.filter(
                    pk=(
                        int(params.get("deadlinerecommendation_id"))
                        if params.get("deadlinerecommendation_id") != ""
                        else 0
                    ),
                    response__isNull=True,
                )
                .filter(~Q(sent=True))
                .first()
            )
            if delayOfTime:
                delayOfTime.delete()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solcitação cancelada com sucesso.",
            )
        return self.renderer(rst)

    def cancelDelayOfTime(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            delayOfTime = (
                DeadlineRecommendation.objects.filter(
                    pk=(
                        int(params.get("deadlinerecommendation_id"))
                        if params.get("deadlinerecommendation_id") != ""
                        else 0
                    )
                )
                .filter(~Q(sent=True))
                .first()
            )
            if delayOfTime:
                delayOfTime.delete()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solcitação cancelada com sucesso.",
            )
        return self.renderer(rst)

    def saveReportCompliance(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            reportCompliance = DeadlineRecommendation.objects.filter(
                pk=(
                    int(params.get("deadlinerecommendation_id"))
                    if params.get("deadlinerecommendation_id") != ""
                    else 0
                )
            ).first()
            if reportCompliance is None:
                recommendation = (
                    Recommendations.objects.filter(
                        pk=(
                            int(params.get("recommendation"))
                            if params.get("recommendation") != ""
                            else 0
                        )
                    )
                    .filter(~Q(sent=True))
                    .first()
                )
                reportCompliance = DeadlineRecommendation()
                reportCompliance.recommendation = recommendation
                # reportCompliance.extension = True
            reportCompliance.response = params.get("response")
            reportCompliance.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solcitação enviada com sucesso.",
            )
        return self.renderer(rst)

    def sendReportCompliance(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            reportCompliance = DeadlineRecommendation.objects.filter(
                pk=(
                    int(params.get("deadlinerecommendation_id"))
                    if params.get("deadlinerecommendation_id") != ""
                    else 0
                )
            ).first()
            if reportCompliance is None:
                recommendation = (
                    Recommendations.objects.filter(
                        pk=(
                            int(params.get("recommendation"))
                            if params.get("recommendation") != ""
                            else 0
                        )
                    )
                    .filter(~Q(sent=True))
                    .first()
                )
                reportCompliance = DeadlineRecommendation()
                reportCompliance.recommendation = recommendation
                # reportCompliance.extension = True
            reportCompliance.response = params.get("response")
            reportCompliance.sent = True
            reportCompliance.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solcitação enviada com sucesso.",
            )
        return self.renderer(rst)

    def cleanReportCompliance(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            reportCompliance = (
                DeadlineRecommendation.objects.filter(
                    pk=(
                        int(params.get("deadlinerecommendation_id"))
                        if params.get("deadlinerecommendation_id") != ""
                        else 0
                    ),
                    response__isNull=True,
                )
                .filter(~Q(sent=True))
                .first()
            )
            if reportCompliance:
                reportCompliance.delete()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solcitação cancelada com sucesso.",
            )
        return self.renderer(rst)

    def cancelReportCompliance(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            reportCompliance = (
                DeadlineRecommendation.objects.filter(
                    pk=(
                        int(params.get("deadlinerecommendation_id"))
                        if params.get("deadlinerecommendation_id") != ""
                        else 0
                    )
                )
                .filter(~Q(sent=True))
                .first()
            )
            if reportCompliance:
                reportCompliance.delete()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Solcitação cancelada com sucesso.",
            )
        return self.renderer(rst)


class INSPECTIONFollowRecommendationCorregedoria(INSPECTIONFollowRecommendation):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.analyze_recommendation.Manage")'
        )

    def get_query(self):
        query = super(INSPECTIONFollowRecommendation, self).get_query()
        return query.order_by("pk")
        # return query.filter(Q(pk__in=DeadlineRecommendation.objects.filter(sent=True).values('recommendation'))).order_by('pk')

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONFollowRecommendation, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "deadline_grid": (
                    instance.deadline.strftime("%d/%m/%Y")
                    if instance.waiting_response and instance.deadline
                    else "--"
                ),
                "delayoftime_pending": DeadlineRecommendation.objects.filter(
                    recommendation=instance,
                    sent=True,
                    extension=True,
                    signdecision_at__isnull=True,
                ).exists(),
                "reportcompliance_pending": DeadlineRecommendation.objects.filter(
                    recommendation=instance, sent=True, signdecision_at__isnull=True
                )
                .filter(~Q(extension=True))
                .exists(),
                "delayoftime_editing": DeadlineRecommendation.objects.filter(
                    recommendation=instance,
                    extension=True,
                    signdecision_at__isnull=True,
                )
                .filter(~Q(sent=True))
                .exists(),
                "reportcompliance_editing": DeadlineRecommendation.objects.filter(
                    recommendation=instance, signdecision_at__isnull=True
                )
                .filter(~Q(extension=True))
                .filter(~Q(sent=True))
                .exists(),
            }
        )
        return _dict_

    def get_recommendation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            recommendation = (
                int(params.get("recommendation"))
                if params.get("recommendation") != ""
                else 0
            )
            data = []
            recommendation = Recommendations.objects.filter(pk=recommendation).first()
            deadlineRecomendation = DeadlineRecommendation.objects.filter(
                recommendation=recommendation, sent=True
            ).last()
            data.append(
                {
                    "recommendation": (
                        recommendation.recommendation
                        if recommendation.recommendation
                        else ""
                    ),
                    "deadline": (
                        deadlineRecomendation.deadline.strftime("%d/%m/%Y")
                        if deadlineRecomendation and deadlineRecomendation.deadline
                        else "--"
                    ),
                    "deadline_grid": (
                        recommendation.deadline.strftime("%d/%m/%Y")
                        if recommendation.recommendation and recommendation.deadline
                        else "--"
                    ),
                    "execution_organ_unicode": recommendation.inspection.execution_organ.nome,
                    "inspection_date_initial_formatted": recommendation.inspection.inspection_date_initial_formatted,
                    "inspection_date_final_formatted": recommendation.inspection.inspection_date_final_formatted,
                    "deadlinerecommendation_id": deadlineRecomendation.pk,
                    "deadlinerecommendation_response": deadlineRecomendation.response,
                    "deadlinerecommendation_decision": deadlineRecomendation.decision,
                }
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True, message="Dados encontrados com sucesso.", collection=data
            )
        return self.renderer(rst)

    def saveDecision(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            decision = DeadlineRecommendation.objects.filter(
                pk=(
                    int(params.get("deadlinerecommendation_id"))
                    if params.get("deadlinerecommendation_id") != ""
                    else 0
                )
            ).first()
            recommendation = Recommendations.objects.filter(
                pk=(
                    int(params.get("recommendation"))
                    if params.get("recommendation") != ""
                    else 0
                )
            ).first()
            if decision is None:
                decision = DeadlineRecommendation()
                decision.recommendation = recommendation
            decision.decision = params.get("decision")
            decision.deadline = (
                (
                    datetime.strptime(params.get("deadline"), "%d/%m/%Y").date()
                    if params.get("deadline") != ""
                    else None
                )
                if params.get("deadline") is not None
                else None
            )
            decision.decision_at = datetime.now()
            decision.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Decisão foi salva com sucesso.",
            )
        return self.renderer(rst)

    def sendDecision(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            decision = DeadlineRecommendation.objects.filter(
                pk=(
                    int(params.get("deadlinerecommendation_id"))
                    if params.get("deadlinerecommendation_id") != ""
                    else 0
                )
            ).first()
            recommendation = Recommendations.objects.filter(
                pk=(
                    int(params.get("recommendation"))
                    if params.get("recommendation") != ""
                    else 0
                )
            ).first()
            if decision is None:
                decision = DeadlineRecommendation()
                decision.recommendation = recommendation
            decision.decision = params.get("decision")
            decision.deadline = (
                (
                    datetime.strptime(params.get("deadline"), "%d/%m/%Y").date()
                    if params.get("deadline") != ""
                    else None
                )
                if params.get("deadline") is not None
                else None
            )
            decision.decision_at = datetime.now()
            # adicionar aqui a paradas para novo prazo
            decision.signdecision_by = get_current_user()
            decision.signdecision_at = datetime.now()
            decision.save()
            if decision.deadline or int(params.get("finalized")) == 2:
                if decision.deadline:
                    recommendation.deadline = decision.deadline
                if int(params.get("finalized")) == 2:
                    recommendation.finalized = True
                    recommendation.finalized_at = datetime.now()
                recommendation.finalize()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Decisão foi salva com sucesso.",
            )
        return self.renderer(rst)

    def notify_delay(self, args=[]):

        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST

            query = Inspection.objects.filter(
                recommendations__deadline__lt=datetime.now().date(),
                recommendations__finalized=False,
            ).distinct()

            if params.get("inspection") != "0":
                pk_o = int(params.get("inspection", 0))
                query = query.filter(pk=pk_o)
                if not query:
                    raise Exception(
                        "As recomendações da inspeção selecionada encontram-se dentro do prazo."
                    )

            for inspection in query:
                if params.get("message"):
                    inspection.notify_delay(
                        new_message=params.get("message"),
                        deadline=datetime.strptime(
                            params.get("deadline"), "%d/%m/%Y"
                        ).date(),
                    )
                else:
                    inspection.notify_delay()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Envio realizado com sucesso.",
            )
        return self.renderer(rst)
