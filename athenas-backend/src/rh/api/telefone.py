# -*- coding: utf-8 -*-

from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user
from rh.const import TYPE_PHONE_EMERGENCY
from rh.models import Telefone

from django.db.models import Q

from contrib.utils import getLogger

log = getLogger(__name__)


class RHTelefoneRestful(RestfulDRY):

    full_text_index = (
        "tipo_telefone__icontains",
        "numero__icontains",
    )

    exclude_fields = ["audittimestampmodel_ptr", "auditablemixins_ptr"]

    force_persist_boolean_fields = ["publico"]

    force_orm_single = True

    _model = Telefone

    def get_query(self):
        user = get_current_user()
        query = super(RHTelefoneRestful, self).get_query()

        if not (
            get_current_user().has_perm("rh.can_manage_person_employee")
            or get_current_user().has_perm("rh.view_servidor")
        ):
            query = query.filter(person__pessoafisica__servidor__isnull=True)
            employee = employee_from_user(user)
            query = query.filter(
                Q(person__pessoafisica__servidor__isnull=True)
                | Q(person__pk=employee.pessoa_fisica.pk)
            )

        return query.exclude(tipo_telefone=TYPE_PHONE_EMERGENCY)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.telefone.TelefoneManage")')


class RHPhoneByUser(RestfulDRY):
    """API de CRUD de telefones específica para o usuário corrente"""

    full_text_index = (
        "tipo_telefone__icontains",
        "numero__icontains",
    )

    exclude_fields = ["audittimestampmodel_ptr", "auditablemixins_ptr"]

    force_persist_boolean_fields = ["publico"]

    force_orm_single = True

    _model = Telefone

    def get_query(self):
        query = super().get_query()

        try:
            employee = employee_from_user(get_current_user())
            query = query.filter(person__pk=employee.pessoa_fisica.pk)
        except Exception as e:
            log.exception(str(e))
            query = query.none()

        return query

    def get_params(self, *args, **kargs):
        params = super().get_params(*args, **kargs)

        try:
            if not params.get("person", 0):
                employee = employee_from_user(get_current_user())
                params.update({"person": employee.pessoa_fisica})
        except Exception as e:
            log.exception(str(e))

        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.telefone.byUser.Manager")')


class RHTelefoneEmergenciaRestful(RestfulDRY):

    _model = Telefone

    def get_query(self):
        user = get_current_user()
        query = super(RHTelefoneEmergenciaRestful, self).get_query()

        if not (
            get_current_user().has_perm("rh.can_manage_person_employee")
            or get_current_user().has_perm("rh.view_servidor")
        ):
            query = query.filter(person__pessoafisica__servidor__isnull=True)
            employee = employee_from_user(user)
            query = query.filter(
                Q(person__pessoafisica__servidor__isnull=True)
                | Q(person__pk=employee.pessoa_fisica.pk)
            )

        return query.filter(tipo_telefone=TYPE_PHONE_EMERGENCY)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.telefone.TelefoneManage"),{emergency_type: "%s"})'
            % TYPE_PHONE_EMERGENCY
        )
