# -*- coding: utf-8 -*-
from contrib.middleware import get_current_user
from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, get_json_engine, getLogger, DateUtils
from rh.dayoff.models import Usufruct
from rh.afastamento.models import BaseLicencaAfastamento
from django.db import models
from rh.dayoff.const import *
from rh.dayoff.utils import competence_paid_unicode

json = get_json_engine()

log = getLogger(__name__)


class DAYOFFUsufructMPMT(RestfulDRY):

    _model = Usufruct

    def get_query(self):
        query = super(DAYOFFUsufructMPMT, self).get_query()
        return query.annotate(
            date_relevance=models.Case(
                models.When(
                    activity_modifieds__isnull=True, then=models.F("start_date")
                ),
                models.When(
                    activity_modifieds__isnull=False,
                    activity_modifieds__usufructs__isnull=True,
                    then=models.F("activity_modifieds__usufructs__start_date"),
                ),
                output_field=models.DateField(),
            ),
            status_mod=models.Case(
                models.When(status=USU_HOMOLOGATED, then=1),
                models.When(status=USU_NEW, then=1),
                models.When(status=USU_CHANGED, then=0),
                models.When(status=USU_SUSPENDED, then=0),
                models.When(status=USU_SOLD, then=-1),
                output_field=models.IntegerField(),
            ),
        ).order_by("date_relevance", "-status_mod", "-id")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.mpmt.usufruct.Manage")')

    @login_required(type="JSON")
    def get_conflicts(self, args=[]):
        obj = {
            "collection": [],
        }
        conflicts = Usufruct.objects.get(
            pk=self.request.GET.get("usufructPk")
        ).get_conflicts()
        for conflict in conflicts:
            for value in conflicts.get(conflict):
                info = value.get("info")
                label_origin = value.get("label_origin")
                print(f"{label_origin} - {info}")
                obj["collection"].append(value)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def model_to_dict(self, instance):
        _dict_ = super(DAYOFFUsufructMPMT, self).model_to_dict(instance)
        authorizers = []
        if instance.activity.immediate_authorization_by:
            authorizers.append(f"{instance.activity.immediate_authorization_by}")
        if instance.activity.immediate_authorization_by:
            authorizers.append(f"{instance.activity.immediate_authorization_by}")
        if instance.activity.mediate_authorization_by:
            authorizers.append(f"{instance.activity.mediate_authorization_by}")

        icons = instance.icons
        with_substitute = False
        afastamentos = BaseLicencaAfastamento.objects.filter(
            dayoff_usufructs__pk=instance.pk
        )
        for afastamento in afastamentos:
            log.info("for")
            if afastamento.substituicao.all().count() > 0:
                log.info("if true")
                with_substitute = True

        icons.append(self.icons_substitute(instance, with_substitute))

        _dict_.update({'icons': icons})
        _dict_.update({'employee_unicode': f'{instance.employee}'})
        _dict_.update({'authorized_by_unicode': ",".join(authorizers)})
        _dict_.update({'authorized_at': DateUtils.date_to_str(instance.activity.authorized_at) if instance.activity.authorized_at else ''})
        _dict_.update({'competence': f'{instance.payment_competence}'})
        _dict_.update({'employee_pk': f'{  str(instance.employee.pk) }'})
        _dict_.update({'employee_type': f'{  str(instance.employee.tipo) }'})
        _dict_.update({'employee_registry': f'{  str(instance.employee.matricula) }'})
        _dict_.update({'origin_of_request': instance.origin_of_request})
        _dict_.update({'is_suspension': instance.is_suspension})
        _dict_.update({'is_retification': instance.is_retification})
        _dict_.update({'parcelas_detalhadas': instance.parcelas_detalhadas})
        _dict_.update({'activity_label': instance.activity_label})
        _dict_.update({'competence_paid': competence_paid_unicode(instance)})
        _dict_.update({'allows_suspend': instance.allows_suspend})
        
        return _dict_

    def icons_substitute(self, instance, with_substitute):
        return {
            "icon": (
                "/athenas/static/rh/images/folha-pendencia.png"
                if with_substitute
                else ""
            ),
            "title": (
                "Para esta ocorrência existe substituto indicado, lembre-se de ajusta-los se for necessário."
                if with_substitute
                else ""
            ),
            "alt": (
                "Para esta ocorrência existe substituto indicado, lembre-se de ajusta-los se for necessário."
                if with_substitute
                else ""
            ),
        }


class DAYOFFEmployeeUsufructMPMT(DAYOFFUsufructMPMT):

    def get_query(self):
        query = super(DAYOFFEmployeeUsufructMPMT, self).get_query()

        return query.filter(
            activity__acquisition_period__employee=employee_from_user(
                get_current_user()
            ),
            activity__acquisition_period__blocked=False,
        )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.mpmt.usufruct.employee.EmployeeManage")'
        )
