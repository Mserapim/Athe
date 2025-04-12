# -*- coding: utf-8 -*-

import unittest

from django.contrib.auth.models import User

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from engine.notification.models import Notification
from rh.registration.models import (
    STATE_DGPFP_RECEIVED,
    STATE_DGPFP_SENT,
    STATE_EMPLOYEE_VALIDATED,
    STATE_EMPLOYEE_VALIDATED_PROBLEM,
    STATE_TRANSITION,
    Choice,
    FormInformation,
    Validation,
)

log = getLogger(__name__)

set_current_user(User.objects.get(username="patriciacabral"))


def setUpModule():
    pass

    # Documento.migration_cpf_rg()

    # employeers = Servidor.objects.filter(ativo=True)
    # for employee in employeers:
    #     for address in employee.pessoa_fisica.address.filter():
    #         if address.complemento:
    #             p = re.compile(r'<.*?>')
    #             complemento = p.sub('', address.complemento)
    #             Endereco.objects.filter(pk=address.pk).update(complemento=complemento)

    #         if address.cep:
    #             cep = ''.join(i for i in address.cep if i.isdigit())
    #             Endereco.objects.filter(pk=address.pk).update(cep=cep)

    #     for number in employee.pessoa_fisica.phone.exclude(tipo_telefone=6).filter():
    #         if number.numero:
    #             numero = ''.join(i for i in number.numero if i.isdigit())
    #             Telefone.objects.filter(pk=number.pk).update(numero=numero)

    # FormInformation.command_load_info_employee()
    # if not FormInformation.objects.exists():
    #     do_diff_fields = FormInformation.do_diff_fields
    #     FormInformation.do_diff_fields = lambda x, y: True
    #     FormInformation.validate_mandatory_field_doc_digital = lambda x: True
    #     FormInformation.validate_mandatory_doc_digital_field = lambda x: True
    #     FormInformation.command_load_info_employee(Servidor.objects.get(matricula=94109))
    #     FormInformation.do_diff_fields = do_diff_fields

    # # modificando dados e enviando para validação
    # form_information = FormInformation.objects.filter(state__in=[2, 3])
    # if not form_information.exists():
    #     validate_mandatory_field_doc_digital = FormInformation.validate_mandatory_field_doc_digital
    #     validate_mandatory_doc_digital_field = FormInformation.validate_mandatory_doc_digital_field

    #     form_information = FormInformation.objects.get(employee__matricula=94109)
    #     form_information.nome = '%s - novo' % form_information.nome
    #     form_information.contact_emergency_name = 'novo a'
    #     form_information.contact_emergency_phone = '6332167565'
    #     form_information.state = 3
    #     digital_document = DigitalDocument(document_type=14, file=Arquivo.objects.filter().last())
    #     digital_document.save()
    #     form_information.digital_documents.add(digital_document)
    #     form_information.save()
    #     FormInformation.validate_mandatory_field_doc_digital = validate_mandatory_field_doc_digital
    #     FormInformation.validate_mandatory_doc_digital_field = validate_mandatory_doc_digital_field


def tearDownModule():
    pass


def _do_validation(form_information, data, state):
    try:
        if not Choice.objects.filter(
            app_label="registration", name="VALIDATION_STATE", value=state
        ).exists():
            state = STATE_EMPLOYEE_VALIDATED
        validation = Validation()
        validation.form_information = form_information
        validation.text = data.get("text")
        validation.state = state
        validation.save(form_information_data=data)
    except Exception as err:
        log.exception(err)
        raise Exception(
            "Validação não gravada! <br>Notificação não enviada! <br>ERRO: %s" % err
        )


def _do_notification(form_information, data):
    try:
        Notification.notify(
            "REGISTRATION_NOTIFICATION",
            form_information.employee,
            form_information,
            message=data.get("text"),
            types=["ONTOP"],
        )
    except Exception as err:
        log.exception(err)
        raise Exception("Notificação não enviada! <br>ERRO: %s" % err)


def dont_do():
    data = {
        "text": """

        <p style=\"color: #ff3434; font-size: 14px;\"> É necessário preencher o campo ESTADO CIVIL. <p>

        <br>O sistema E-social obedece estritamente o Código Civil Brasileiro no qual a união estável não é considerada estado civil. Diante disso o sistema de recadastramento foi readequado, motivo pelo qual solicitamos o preenchimento do campo "Estado Civil".
<br><br>As informações de união estável já enviadas permanecem indicadas no sistema no campo "Possui União Estável?", bem como os documentos comprobatórios já anexados."""
    }

    # for form_information in FormInformation.objects.filter(
    #     pk__in=[344, 57, 24, 190, 786, 592, 232, 164, 189, 284, 92, 34, 296, 160, 112, 625, 827, 398, 102, 788, 330, 359, 422, 848, 529, 578, 86, 659, 19, 18, 837, 39, 458, 537, 556, 567, 583, 799, 506, 871, 236, 54, 335, 290, 753, 826],
    for form_information in FormInformation.objects.filter(
        pk__in=[
            344,
            57,
            24,
            190,
            786,
            592,
            232,
            164,
            189,
            284,
            92,
            34,
            296,
            160,
            112,
            625,
            827,
            398,
            102,
            788,
            330,
            359,
            422,
            848,
            529,
            578,
            86,
            659,
            19,
            18,
            837,
            39,
            458,
            537,
            556,
            567,
            583,
            799,
            506,
            871,
            236,
            54,
            335,
            290,
            753,
            826,
        ],
    ).order_by("employee__pessoa_fisica__nome"):
        if form_information.state in [
            STATE_EMPLOYEE_VALIDATED,
            STATE_DGPFP_SENT,
            STATE_DGPFP_RECEIVED,
        ]:
            state_before = form_information.get_state_display()
            state = STATE_EMPLOYEE_VALIDATED_PROBLEM
            _do_validation(form_information, data, state)
            _do_notification(form_information, data)
            FormInformation.objects.filter(pk=form_information.pk).update(state=state)
            FormInformation.objects.filter(pk=form_information.pk).update(
                estado_civil=None
            )
            FormInformation.objects.filter(pk=form_information.pk).update(
                estado_civil_diff=True
            )
            state_after = FormInformation.objects.get(
                pk=form_information.pk
            ).get_state_display()
            print(
                form_information.pk,
                "|",
                form_information,
                "|",
                state_before,
                "|",
                state_after,
            )
            print("-------------------------")
        FormInformation.objects.filter(pk=form_information.pk).update(
            uniao_estavel=True
        )


class RegistrationTestCase(unittest.TestCase):

    def test(self):
        fi = FormInformation.objects.get(employee__matricula=120023)
        print(fi)
        fi.clean_all_validate()

    # def test(self):
    #     data = {
    #         'text': '''

    #         <p style=\"color: #ff3434; font-size: 14px;\"> É necessário preencher o campo ESTADO CIVIL. <p>

    #         <br>O sistema E-social obedece estritamente o Código Civil Brasileiro no qual a união estável não é considerada estado civil. Diante disso o sistema de recadastramento foi readequado, motivo pelo qual solicitamos o preenchimento do campo "Estado Civil".
    # <br><br>As informações de união estável já enviadas permanecem indicadas no sistema no campo "Possui União Estável?", bem como os documentos comprobatórios já anexados.'''
    #     }

    #     # for form_information in FormInformation.objects.filter(
    #     #     pk__in=[344, 57, 24, 190, 786, 592, 232, 164, 189, 284, 92, 34, 296, 160, 112, 625, 827, 398, 102, 788, 330, 359, 422, 848, 529, 578, 86, 659, 19, 18, 837, 39, 458, 537, 556, 567, 583, 799, 506, 871, 236, 54, 335, 290, 753, 826],
    #     for form_information in FormInformation.objects.filter(
    #         pk__in=[344, 57, 24, 190, 786, 592, 232, 164, 189, 284, 92, 34, 296, 160, 112, 625, 827, 398, 102, 788, 330, 359, 422, 848, 529, 578, 86, 659, 19, 18, 837, 39, 458, 537, 556, 567, 583, 799, 506, 871, 236, 54, 335, 290, 753, 826],
    #     ).order_by('employee__pessoa_fisica__nome'):
    #         if form_information.state in [
    #             STATE_EMPLOYEE_VALIDATED,
    #             STATE_DGPFP_SENT,
    #             STATE_DGPFP_RECEIVED
    #         ]:
    #             print form_information.pk, form_information, '======', form_information.get_state_display()
    #             state = STATE_EMPLOYEE_VALIDATED_PROBLEM
    #             _do_validation(form_information, data, state)
    #             _do_notification(form_information, data)
    #             FormInformation.objects.filter(pk=form_information.pk).update(state=state)
    #             FormInformation.objects.filter(pk=form_information.pk).update(estado_civil=None)
    #             print('-------------------------')
    #         FormInformation.objects.filter(pk=form_information.pk).update(uniao_estavel=True)

    # from rh.models import DigitalDocument, DocumentSpecialized
    # for dg in DigitalDocument.objects.filter(document_type=54):
    #     print dg.employee, dg
    #     try:
    #         document = DocumentSpecialized(
    #             tipo_documento=STABLE_BONDING,
    #             numero='1',
    #             data_expedicao=datetime.datetime.now(),
    #             data_validade=None,
    #             estado_expedicao=None
    #         )
    #         document.clean()
    #         document.save()
    #         employee.pessoa_fisica.documento.add(document)
    #     except Exception as err:
    #         print(err)


def validate_transition_state(fi, state):
    if state not in STATE_TRANSITION.get(fi.state) and state != fi.state:
        raise Exception(
            "Não é possível modificar o estado para %s. Modifique alguma informação antes de enviar."
            % Choice.objects.filter(
                app_label="registration", name="FORMINFORMATION_STATE", value=state
            ).last()
        )


def transition_state(fi, state):
    validate_transition_state(fi, state)
    if state == STATE_DGPFP_SENT:
        fi.validate_send_rh()
        fi._set_sent()
    elif state in [STATE_EMPLOYEE_VALIDATED, STATE_EMPLOYEE_VALIDATED_PROBLEM]:
        fi._set_validated()
    elif state in [STATE_DGPFP_RECEIVED]:
        fi._set_received()
    fi._set_modified()
    # FormInformation.objects.filter(pk=fi.pk).update(state=state)
    return True


def test():

    validations = Validation.objects.filter(
        form_information__employee__matricula=106710
        # text__icontains='#ff3434',
        # text__icontains='não validados:</p>',
        # state=STATE_EMPLOYEE_VALIDATED
        # text__icontains='validados:</p>',
        # state=STATE_EMPLOYEE_VALIDATED_PROBLEM
    )
    print(validations.count())
    for validation in validations.order_by(
        "form_information__employee__pessoa_fisica__nome"
    ):
        validation_state = "NUNCA VALIDADO"
        validated_at = ""
        validation_state = "%s = %s" % (validation.pk, validation.get_state_display())
        validated_at = DateUtils.datetime_to_str(validation.validated_at)
        fi = validation.form_information
        print(fi.employee).replace(
            ":", "|"
        ), "|", fi.employee.get_tipo_display(), "|", fi.get_state_display(), "|", validation_state, "|", validated_at
        # if validation:
        #     print(validation.text)

    # STATE_TRANSITION = {
    #     STATE_EMPLOYEE_EDITION: [STATE_DGPFP_SENT],
    #     STATE_EMPLOYEE_VALIDATED_PROBLEM: [STATE_DGPFP_SENT],
    #     STATE_EMPLOYEE_VALIDATED: [STATE_EMPLOYEE_EDITION],
    #     STATE_DGPFP_SENT: [STATE_DGPFP_RECEIVED, STATE_EMPLOYEE_EDITION],
    #     STATE_DGPFP_RECEIVED: [STATE_EMPLOYEE_VALIDATED_PROBLEM, STATE_EMPLOYEE_VALIDATED],
    # }

    # for fi in FormInformation.objects.filter().order_by('employee__pessoa_fisica__nome'):
    #     try:
    #         state = STATE_EMPLOYEE_VALIDATED
    #         transition_state(fi, state)
    #         state = STATE_EMPLOYEE_VALIDATED_PROBLEM
    #         transition_state(fi, state)
    #     except Exception as err:
    #         print(unicode(err))
