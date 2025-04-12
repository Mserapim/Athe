# -*- coding: utf-8 -*-

from contrib.middleware import get_current_user
from contrib.utils import employee_from_user
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger

from django.db.models import Q

from rh.models import Endereco

log = getLogger(__name__)


class RHEnderecoRestful(RestfulDRY):

    full_text_index = (
        "tipo_endereco__icontains",
        "tipo_logradouro__icontains",
        "municipio__nome__icontains",
        "cep__icontains",
        "logradouro__icontains",
        "logradouro__icontains",
        "numero__icontains",
        "bairro__icontains",
        "complemento__icontains",
    )

    exclude_fields = [
        "audittimestampmodel_ptr",
        "auditablemixins_ptr",
        "data_alteracao",
    ]

    force_orm_single = True

    force_upper = False

    _model = Endereco

    def get_query(self):
        user = get_current_user()
        query = super(RHEnderecoRestful, self).get_query()

        if not (
            get_current_user().has_perm("rh.can_manage_person_employee")
            or get_current_user().has_perm("rh.view_servidor")
        ):
            employee = employee_from_user(user)
            query = query.filter(
                Q(person__pessoafisica__servidor__isnull=True)
                | Q(person__pk=employee.pessoa_fisica.pk)
            )

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.endereco.EnderecoManage")')
