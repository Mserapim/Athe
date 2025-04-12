# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import ChildcareAllowance
from edocs.protocolo.api.manage import EDOCManage
from rh.models import Servidor as Employee


log = getLogger(__name__)


class RequestFormChildcareAllowance(EDOCManage):

    _model = ChildcareAllowance

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("bank", ""):
            raise Exception("Por favor, preencha corretamente o campo Banco.")

        if not params.get("agency", ""):
            raise Exception("Por favor, preencha corretamente o campo Agência.")

        if not params.get("account", ""):
            raise Exception("Por favor, preencha corretamente o campo Conta.")

        if not params.get("child_name", ""):
            raise Exception("Por favor, preencha corretamente o campo Nome da criança.")

        try:
            params.update(child_type=int(params.get("child_type", "")))
        except ValueError:
            raise Exception("Por favor, preencha corretamente o campo Tipo vínculo.")

        try:
            params.update(
                child_birth_date=DateUtils.str_to_date(params.get("child_birth_date"))
            )
        except Exception:
            raise Exception(
                "Por favor, preencha corretamente o campo Data de nascimento."
            )

        if not params.get("child_cpf", ""):
            raise Exception("Por favor, preencha corretamente o campo CPF.")

        if len(params.get("spouse", "")) > 0:
            try:
                params.update(spouse=Employee.objects.get(pk=params.get("spouse")))
            except Exception:
                raise Exception("Por favor, preencha corretamente o campo Cônjuge.")

        if len(params.get("receiver", "")) > 0:
            try:
                params.update(receiver=Employee.objects.get(pk=params.get("receiver")))
            except Exception:
                raise Exception(
                    "Por favor, preencha corretamente o campo Responsável pelo recebimento."
                )

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        form = instance.protocolo.childcareallowance

        birth_date = ""
        if form.child_birth_date:
            birth_date = DateUtils.date_to_str(form.child_birth_date)

        data.update(
            {
                "contact_number": form.contact_number or "",
                "bank": form.bank or "",
                "agency": form.agency or "",
                "account": form.account or "",
                "child_type": form.child_type if form.child_type is not None else "",
                "child_name": form.child_name or "",
                "child_birth_date": birth_date,
                "child_cpf": form.child_cpf or "",
                "spouse": form.spouse.pk if form.spouse else 0,
                "receiver": form.receiver.pk if form.receiver else 0,
            }
        )

        return data
