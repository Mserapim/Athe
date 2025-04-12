# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import DadoBancario as BankingData
from rh.models import DadoBancarioPessoa as BankingDataPerson

log = getLogger(__name__)


class RHBankingDataRestful(RestfulDRY):

    _model = BankingData

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pessoa.BankingDataManage")')


class RHBankingDataPerson(RestfulDRY):

    _model = BankingDataPerson

    full_text_index = (
        "pessoa__nome__icontains",
        "conta_corrente_completa__icontains",
        "banco__nome__icontains",
    )

    exclude_fields = [
        "dadobancario_ptr",
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pessoa.BankingDataPersonManage")')

    def model_to_dict(self, instance):
        params = super().model_to_dict(instance)
        params.update(
            {
                "pessoa_display": (
                    f"{instance.pessoa.specialized_instance.nome} - CPF: {instance.pessoa.specialized_instance.cpf}"
                    if instance.pessoa.specialized_instance.cpf
                    else instance.pessoa
                )
            }
        )
        return params
