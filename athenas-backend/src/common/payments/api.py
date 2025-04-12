# -*- coding:utf-8 -*-

import json
import re

from datetime import datetime, timedelta

from django.db import transaction

from contrib.controller import JsonResponseController, DefaultController
from contrib.middleware import get_current_user
from contrib.utils import getLogger, employee_from_user
from contrib.newrest import RestfulDRY

from rh.models import PessoaFisica, Endereco

from .models import TicketPay, BankPartnership


log = getLogger(__name__)


def translate(key):
    bb_params = [
        "id",
        "nome",
        "cpfCnpj",
        "cidade",
        "uf",
        "cep",
        "motivo",
        "processo",
        "msgLoja",
        "endereco",
        "valor",
        "control",
        "refTran",
        "dtVenc",
        "indicadorPessoa",
        "tpPagamento",
        "boletoParte",
        "tpDuplicata",
    ]

    our_params = [
        "id",
        "name",
        "cpf_cnpj",
        "city",
        "state",
        "zip_code",
        "types_recipes",
        "process_number",
        "message_store",
        "address",
        "value",
        "control",
        "ticket_number",
        "expiration_date",
        "person_type",
        "payment_type",
        "partnership",
        "document_type",
    ]

    translations = dict(list(zip(our_params, bb_params)))

    return translations.get(key)


class TicketPayController(JsonResponseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.no_render = getattr(self.__class__, "no_render", False)

    def ticket_save(self, args=[]):

        params = extract_from_post(self.request)
        log.info(params)
        message = generate_ticket(**params)

        return message if self.no_render else self.render(message)

    def ticket_recovery(self, args=[]):
        message = ticket_recovery(self.request.POST.get("ticket_number"))
        return message if self.no_render else self.render(message)


class InternalTicketPayController(RestfulDRY, TicketPayController):

    _model = TicketPay
    no_render = True

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.payments.TicketPayManage")')

    def ticket_save(self, args=[]):
        message = super(InternalTicketPayController, self).ticket_save(*args)
        return self.render(message)

    def ticket_recovery(self, args=[]):

        message = super(InternalTicketPayController, self).ticket_recovery(*args)
        return self.render(message)


def model2dict(instance):
    obj = {}
    for f in instance._meta.fields:
        obj.update({translate(f.name): getattr(instance, f.name, None)})
        if f.name == "value":
            valor = str(int(round(float(obj.get("valor", "0.0")), 2) * round(100, 2)))
            obj.update(valor=valor)

    return obj


def extract_from_post(request):

    return dict(
        name=request.POST.get("nome"),
        cpf_cnpj=request.POST.get("cpfCnpj").replace(".", "").replace("-", ""),
        city=request.POST.get("cidade"),
        state=request.POST.get("uf"),
        zip_code=request.POST.get("cep").replace("-", ""),
        types_recipes=request.POST.get("motivo"),
        process_number=request.POST.get("process_number"),
        message_store=request.POST.get("msgLoja"),
        address=re.sub(
            r"\s-\s", "-", re.sub(r"'\s", "'", request.POST.get("endereco"))
        ),
        value=request.POST.get("valor").replace(",", "."),
        person_type=request.POST.get("person_type"),
        identifier=request.POST.get("identifier"),
    )


def generate_ticket(**kwargs):

    message = {"success": False}

    try:
        partnership = BankPartnership.objects.get(identifier=kwargs.get("identifier"))

    except Exception as e:
        log.exception(e)
        message["error"] = "".join(
            [
                "Parece que não há uma conta cadastrada para a geração de um Boleto. \
            Procure o administrador do sistema. Descrição do Erro: ",
                str(e),
            ]
        )
    else:
        tp = TicketPay(
            name=kwargs.get("name"),
            cpf_cnpj=kwargs.get("cpf_cnpj"),
            city=kwargs.get("city"),
            state=kwargs.get("state"),
            zip_code=kwargs.get("zip_code"),
            types_recipes=kwargs.get("types_recipes"),
            process_number=kwargs.get("process_number"),
            message_store=kwargs.get("message_store"),
            address=kwargs.get("address")[:60],
            value=round(float(kwargs.get("value", "0.0")), 2) * round(0.01, 2),
            person_type=kwargs.get("person_type"),
            # Vencimento de X dias a partir da data de emissão
            expiration_date=datetime.now()
            + timedelta(days=int(partnership.days_remaining)),
            payment_type=2,  # 2 - Boleto primeira via, 21 - Segunda Via
            document_type="DS",
            partnership=partnership,
        )

        try:
            log.info(tp)

            with transaction.atomic():
                tp.save()
                """
                    Gerador do Número do Boleto refTran(17 dígitos) 'Codigo de Cobrança' + PK
                """
                num_control = tp.formatControl()
                ticket_number = "%s%s" % (partnership.charge_code, num_control)
                tp.control = num_control
                tp.ticket_number = ticket_number
                tp.save()

        except Exception as e:
            log.exception(e)
            message["error"] = str(e)
        else:
            obj = model2dict(tp)
            obj["idConv"] = (
                partnership.partnertship_code
            )  # Número do Comercio Eletronico
            obj["urlRetorno"] = partnership.callback_url
            obj["partinership"] = ""

            message.update(success=True, obj=obj)  # model2dict(tp)
    return message


def ticket_recovery(ticket_number):

    message = {"success": False}
    ticket_pay = None

    try:
        ticket_pay = TicketPay.objects.get(ticket_number=ticket_number)
        obj = model2dict(ticket_pay)

        obj["idConv"] = (
            ticket_pay.partnership.partnertship_code
        )  # Número do Comercio Eletronico
        obj["urlRetorno"] = ticket_pay.partnership.callback_url  #
        obj["tpPagamento"] = 21

    except TicketPay.DoesNotExist:
        log.info("O Boleto não existe")
        message["error"] = "O Boleto não existe"
    except Exception as e:
        log.info(str(e))
        message["error"] = str(e)
    else:
        message.update(success=True, obj=obj)
    return message


class IssueTicketController(DefaultController):  # Emissão de Boleto, formulário inicial

    def get_employee_data(self):
        servidor = employee_from_user(get_current_user())
        person_id = servidor.pessoa_fisica_id
        person = PessoaFisica.objects.get(id=person_id)
        address = Endereco.objects.filter(
            person__pessoafisica__servidor__ativo=True, person=person, tipo_endereco=1
        ).last()

        obj = {}
        for f in person._meta.fields:
            obj.update({f.name: getattr(person, f.name, None)})

        city = getattr(address, "municipio", None)
        if not city:
            raise Exception(
                "Cadastro de endereço incompleto, falta informar o município, procure o RH."
            )

        employee_name = obj.get("nome")
        employee_cpf = obj.get("cpf")
        employee_cep = address.cep
        employee_city = city.nome
        employee_state = city.estado.sigla
        employee_address = ", ".join([address.logradouro, address.bairro])
        employee_person_type = 1

        params_to_check = [
            employee_name,
            employee_cpf,
            employee_cep,
            employee_city,
            employee_state,
            address.logradouro,
            address.bairro,
        ]

        emp_obj = {}

        if all(params_to_check):
            emp_obj = {
                "employee_name": employee_name,
                "employee_cpf": employee_cpf.replace(".", "").replace("-", ""),
                "employee_cep": employee_cep.replace("-", ""),
                "employee_city": employee_city,
                "employee_state": employee_state,
                "employee_address": employee_address,
                "employee_person_type": employee_person_type,
            }
        return emp_obj

    def json(self, args=[]):

        try:
            emp_obj = {"success": True, "data": self.get_employee_data()}
        except Exception as e:
            emp_obj = {"success": False, "message": str(e)}
        finally:
            self.response["content-type"] = "text/javascript"
            self.response.write(
                "Ext._create('common.payments.IssueTicketManage', {0})".format(
                    json.dumps(emp_obj)
                )
            )


class CBankPartnership(RestfulDRY):

    _model = BankPartnership

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.payments.BankPartnershipManage")')


class IssueSecondWayTicketController(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.payments.SecondTicketWayForm")')
