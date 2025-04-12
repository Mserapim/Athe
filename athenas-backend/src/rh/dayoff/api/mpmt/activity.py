# -*- coding: utf-8 -*-
import json

from django.db.models import Q

from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from rh.dayoff.const import (
    ACT_ST_AUTHORIZED,
    ACT_ST_AUTHORIZED_M,
    ACT_ST_CREATED,
    ACTIVITY_TO_METHOD_NAME,
)
from rh.dayoff.models import (
    Activity,
    ActivitySell,
    Attachment,
    Configuration,
    AcquisitionPeriod,
)
from rh.dayoff.contrib import (
    has_perm_homologate_admin,
    has_perm_homologate,
    has_perm_mediate_chief,
)
from rh.models import Lotacao, Servidor, ServidorLotacao

log = getLogger(__name__)


class DAYOFFActivityMPMT(RestfulDRY):

    _model = Activity

    context = None

    full_text_index = (
        "acquisition_period__employee__pessoa_fisica__nome__icontains",
        "acquisition_period__employee__matricula__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = super(DAYOFFActivityMPMT, self).model_to_dict(instance)
        status_next_display = ""
        if (
            instance.configuration.mediate_authorization is True
            and instance.status == ACT_ST_AUTHORIZED
        ):
            status_next_display = "AGUARDANDO AUTORIZAÇÃO DE CHEFE MEDIATO"
        elif instance.status == ACT_ST_CREATED:
            status_next_display = "AGUARDANDO AUTORIZAÇÃO DE CHEFE IMEDIATO"
        elif instance.status in (ACT_ST_AUTHORIZED, ACT_ST_AUTHORIZED_M):
            status_next_display = "AGUARDANDO HOMOLOGAÇÃO"
        workplace = instance.employee.workplace_by_date()
        workplace = f"{workplace}" if workplace else "Não possui lotação ativa"
        _dict_.update(
            employee_unicode="%s" % instance.employee,
            acquisition_period_title=instance.acquisition_period.configuration.title,
            booked_days_cache=instance.acquisition_period.booked_days_cache,
            days_to_enjoy_cache=instance.acquisition_period.days_to_enjoy_cache,
            days_not_booked_cache=instance.acquisition_period.days_not_booked_cache,
            type_of_usufruct=instance.configuration.type_of_usufruct,
            type_of_usufruct_display=instance.configuration.get_type_of_usufruct_display(),
            booked_usufructs_display=instance.booked_usufructs_display,
            modifieds_usufructs_display=instance.modifieds_usufructs_display,
            employee_admin_authorization_by="%s"
            % employee_from_user(instance.admin_authorization_by),
            status_next_display=status_next_display,
            action_custom=ACTIVITY_TO_METHOD_NAME.get(instance.type_of_activity),
            chief_immediate_unicode=f"{instance.employee.chefe_imediato}",
            employee_workplace_unicode=workplace,
            group_period="%s" % instance.acquisition_period.group_period,
            sub_type_of_usufruct=instance.configuration.sub_type_of_usufruct,
        )
        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.mpmt.activity.Manage")')

    @login_required("JSON")
    def notificate(self, args=[]):
        # FIXME: ORGANIZAR
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            params = json.loads(self.request.body)
            activity = params.get("activity", False)
            if activity:
                activity = self.Model.objects.get(pk=activity).my_origin
                # escrever acao
                rst.update(
                    {
                        "success": True,
                        "message": "%s notificada com sucesso."
                        % activity.get_type_of_activity_display(),
                    }
                )
            else:
                raise Exception("Atividade não informada.")
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def cancel(self, args=[]):
        # FIXME: ORGANIZAR
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            activity = self.request.POST.get("activity")

            if activity:
                activity = self.Model.objects.get(pk=activity).my_origin
                activity = activity.cancel()
                message = "não foi cancelada."
                if activity.canceled:
                    message = "cancelada com sucesso."
                message = "%s %s" % (activity.get_type_of_activity_display(), message)
                rst.update(
                    {
                        "success": True,
                        "message": message,
                    }
                )
            else:
                raise Exception("Atividade não informada.")
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def delete(self, args=[]):
        # FIXME: ORGANIZAR
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            activity = self.request.POST.get("activity")

            if activity:
                activity = self.Model.objects.get(pk=activity).my_origin
                activity = activity.exclude()
                message = "não foi cancelada."
                if not activity:
                    message = "Excluído com sucesso."
                message = "%s %s" % (activity.get_type_of_activity_display(), message)
                rst.update(
                    {
                        "success": True,
                        "message": message,
                    }
                )
            else:
                raise Exception("Atividade não informada.")
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    # TODO: FAZER UM AUTHORIZE_BATCH

    @login_required("JSON")
    def authorize(self, args=[]):
        # FIXME: ORGANIZAR
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        _activity = self.request.POST.getlist("activity", [])
        _authorize = self.request.POST.get("authorize", False)

        _mediate_authorization = None
        _immediate_authorization = None
        _attachment = None

        if self.context == "admin":
            mediate_employee_pk = self.request.POST.get("mediate_employee_pk") or None
            try:
                _mediate_authorization = Servidor.objects.get(pk=mediate_employee_pk)
            except Servidor.DoesNotExist:
                pass

            immediate_employee_pk = (
                self.request.POST.get("immediate_employee_pk") or None
            )
            try:
                _immediate_authorization = Servidor.objects.get(
                    pk=immediate_employee_pk
                )
            except Servidor.DoesNotExist:
                pass

            _attachment = self.request.POST.get("attachment") or None
            try:
                _attachment = Attachment.objects.get(pk=_attachment)
            except Attachment.DoesNotExist:
                pass

        try:
            activity = self.Model.objects.filter(pk__in=_activity)
            if activity.count() < 5:
                for act in activity:
                    act = act.my_origin
                    act = act.authorize_and_homologate(
                        authorize=True if _authorize.lower() == "true" else False,
                        mediate_authorization=_mediate_authorization,
                        immediate_authorization=_immediate_authorization,
                        attachment=_attachment,
                        context=self.context,
                    )
                rst.update(
                    {
                        "success": True,
                        "message": "%s realizada com sucesso."
                        % act.get_type_of_activity_display(),
                    }
                )
            else:
                AcquisitionPeriod.authorize_batch(
                    authorize=True if _authorize.lower() == "true" else False,
                    attachment=_attachment,
                    activity=_activity,
                    mediate_authorization=_mediate_authorization,
                    immediate_authorization=_immediate_authorization,
                    context=self.context,
                )
                rst.update(
                    {
                        "success": True,
                        "message": "Autorização iniciada com sucesso, acompanhe pelo gestor de processos.",
                    }
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def homologate(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            activity = self.request.POST.getlist("activity", [])

            if not activity:
                raise Exception("Atividade não informada.")
            activities = self.Model.objects.filter(pk__in=activity)
            if activities.count() < 3:
                for activity in activities:
                    activity = activity.my_origin
                    activity.homologate(homologate=True, context=self.context)
                rst.update(
                    {
                        "success": True,
                        "message": "%s realizada com sucesso."
                        % activity.get_type_of_activity_display(),
                    }
                )
            else:
                AcquisitionPeriod.homologate_batch(
                    activity=activity, context=self.context
                )
                rst.update(
                    {
                        "success": True,
                        "message": "Homologação iniciada com sucesso, acompanhe pelo gestor de processos.",
                    }
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def update_activity(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            activity = self.request.POST.get("activity", 0)

            if not activity:
                raise Exception("Atividade não informada.")

            attachment = self.request.POST.get("attachment") or None
            try:
                attachment = Attachment.objects.get(pk=attachment)
            except Attachment.DoesNotExist:
                pass

            activity = Activity.objects.get(pk=activity)
            activity.update_activity(attachment)
            rst.update(
                {
                    "success": True,
                    "message": "%s atualizada com sucesso." % activity,
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class DAYOFFAuthorizationMPMT(DAYOFFActivityMPMT):

    context = "immediate"

    def get_query(self, *args, **kwargs):
        query = super(DAYOFFAuthorizationMPMT, self).get_query()

        employee = employee_from_user(get_current_user())

        query = query.filter(
            acquisition_period__employee__pk__in=employee.subordinados_ids,
            status__in=[ACT_ST_CREATED, ACT_ST_AUTHORIZED],
        )

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.mpmt.activity.authorization.AuthorizeManage")'
        )


class DAYOFFMediateAuthorizationMPMT(DAYOFFActivityMPMT):

    context = "mediate"

    def get_query(self):
        query = self._model.objects.none()
        if has_perm_mediate_chief():
            query = (
                super(DAYOFFMediateAuthorizationMPMT, self)
                .get_query()
                .filter(
                    Q(
                        acquisition_period__group_period__configuration__mediate_authorization=True
                    )
                )
            )
        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.mpmt.activity.authorization.MediateAuthorizeManage")'
        )


class DAYOFFMediateAuthorizationChartMPMT(DAYOFFMediateAuthorizationMPMT):

    def get_query(self):
        query = super(DAYOFFMediateAuthorizationChartMPMT, self).get_query()

        employee = employee_from_user(get_current_user())

        def get_workplaces(workplaces_pk, workplaces=[]):
            for workplace in Lotacao.objects.filter(pk__in=workplaces_pk, ativo=True):
                workplaces.append(workplace.pk)
                get_workplaces(workplace.lotacoes_subordinadas.values("pk"), workplaces)

            return workplaces

        workplaces_pk_list = get_workplaces(
            employee.responsavel_por.filter(ativo=True).values("pk")
        )

        employees_pks = ServidorLotacao.objects.filter(
            lotacao__pk__in=workplaces_pk_list, ativo=True, designacao=True
        ).values_list("servidor__pk", flat=True)

        indirect_subordinates_pks = [
            item
            for item in set(employees_pks)
            if item not in set(employee.subordinados_ids)
        ]

        query = query.filter(
            Q(acquisition_period__employee__pk__in=indirect_subordinates_pks)
            & Q(
                acquisition_period__group_period__configuration__mediate_authorization=True
            )
            & Q(immediate_authorization_by__isnull=False)
        )

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.mpmt.activity.authorization.MediateAuthorizeChartManage")'
        )


class DAYOFFAdminAuthorizationMPMT(DAYOFFActivityMPMT):
    context = "admin"

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.mpmt.activity.authorization.AdminAuthorizeManage")'
        )


class DAYOFFSellActivityMPMT(DAYOFFActivityMPMT):

    _model = ActivitySell

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.mpmt.activity.sell.Manage")')


class DAYOFFHomologateMPMT(DAYOFFActivityMPMT):

    context = "admin"

    def get_query(self, *args, **kwargs):
        query = self._model.objects.none()
        if has_perm_homologate_admin() or has_perm_homologate():
            query = super(DAYOFFHomologateMPMT, self).get_query()
        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.mpmt.activity.authorization.HomologateManage")'
        )
