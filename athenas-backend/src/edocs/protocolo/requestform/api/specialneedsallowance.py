# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import SpecialNeedsAllowance
from edocs.protocolo.api.manage import EDOCManage
from rh.models import Servidor as Employee, Estado as State


log = getLogger(__name__)


class RequestFormSpecialNeedsAllowance(EDOCManage):

    _model = SpecialNeedsAllowance

    def prepare_params(self, querydict):
        params = super(RequestFormSpecialNeedsAllowance, self).prepare_params(querydict)

        if not params.get("dependent_name", ""):
            raise Exception("Por favor, preencha corretamente o campo Nome.")

        try:
            params.update(
                dependent_birth_date=DateUtils.str_to_date(
                    params.get("dependent_birth_date")
                )
            )
        except Exception:
            raise Exception(
                "Por favor, preencha corretamente o campo Data de nascimento."
            )

        try:
            params.update(disability_type=int(params.get("disability_type", "")))
        except Exception:
            raise Exception(
                "Por favor, preencha corretamente o campo Tipo de deficiência."
            )

        if not params.get("icd", ""):
            raise Exception("Por favor, preencha corretamente o campo CID-10.")

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

        if len(params.get("dependent_uf", "")) > 0:
            try:
                params.update(
                    dependent_uf=State.objects.get(pk=params.get("dependent_uf"))
                )
            except Exception:
                raise Exception("Por favor, preencha corretamente o campo UF.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormSpecialNeedsAllowance, self).model_to_dict(instance)

        form = instance.protocolo.specialneedsallowance

        birth_date = ""
        if form.dependent_birth_date is not None:
            birth_date = DateUtils.date_to_str(form.dependent_birth_date)

        data.update(
            {
                "contact_number": form.contact_number or "",
                "dependent_name": form.dependent_name or "",
                "dependent_birth_date": birth_date,
                "dependent_cpf": form.dependent_cpf or "",
                "dependent_rg": form.dependent_rg or "",
                "dependent_uf": (
                    form.dependent_uf.pk if form.dependent_uf is not None else ""
                ),
                "dependent_address": form.dependent_address or "",
                "disability_type": form.disability_type or "",
                "icd": form.icd or "",
                "spouse": form.spouse.pk if form.spouse is not None else "",
                "receiver": form.receiver.pk if form.receiver is not None else "",
            }
        )

        return data
