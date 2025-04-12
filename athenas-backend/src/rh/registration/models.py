# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from contrib.middleware import get_current_user
from contrib.utils import DateUtils, employee_from_user, getLogger
from rh.const import (
    ADDRESS_CERTIFICATE,
    BIRTH_CERTIFICATE,
    CASADO,
    CNH,
    CNH_CATEGORY_TYPE,
    CPF,
    CTPS,
    DIGITAL_DOCUMENT_TYPE,
    DIVORCIADO,
    NIS,
    NOT_IMMIGRANT,
    NOT_PROCESSED,
    NOT_VALIDITY,
    PASSPORT,
    PIS_PASEP,
    PROCESSED,
    PROFESSIONAL_COUNCIL,
    RESERVISTA,
    RG,
    RIC,
    RNE,
    SEPARADO_JUDICIALMENTE,
    SEXO_CHOICES,
    SOLTEIRO,
    STABLE_BONDING,
    TITULO_ELEITOR,
    TYPE_PHONE_EMERGENCY,
    VIUVO,
    WEDDING_CERTIFICATE,
)
from rh.models import AnotacaoGeral, Dependencia, Dependente
from rh.models import DigitalDocument as DigitalDocumentRh
from rh.models import Documento, Servidor
from rh.utils import _concat_dict
from standard.models import AuditTimestampModel, Choice

log = getLogger(__name__)


STATE_EMPLOYEE_EDITION = 1
STATE_EMPLOYEE_VALIDATED_PROBLEM = 4
STATE_EMPLOYEE_VALIDATED = 5
STATE_DGPFP_SENT = 2
STATE_DGPFP_RECEIVED = 3


STATE_TRANSITION = {
    STATE_EMPLOYEE_EDITION: [STATE_DGPFP_SENT],
    STATE_EMPLOYEE_VALIDATED_PROBLEM: [STATE_DGPFP_SENT],
    STATE_EMPLOYEE_VALIDATED: [STATE_EMPLOYEE_EDITION],
    STATE_DGPFP_SENT: [STATE_DGPFP_RECEIVED, STATE_EMPLOYEE_EDITION],
    STATE_DGPFP_RECEIVED: [STATE_EMPLOYEE_VALIDATED_PROBLEM, STATE_EMPLOYEE_VALIDATED],
}


def is_admin():
    """Este método verifica se o usuário corrente é admin. Utiliza get_current_user e has_perm.

    Returns:
        bool
    """
    return get_current_user().has_perm("registration.registration_admin")


def is_current_user_system():
    """Este método verifica se o usuário corrente é o athenas. Utiliza get_current_user.

    Returns:
        bool
    """
    return get_current_user() == User.objects.get(username="athenas")


def _raw_estado_civil_validate(estado_civil, found):
    message = ""
    if estado_civil == SOLTEIRO and not found:
        message += "<br>É necessário anexar o documento digital %s." % (
            DIGITAL_DOCUMENT_TYPE.get(BIRTH_CERTIFICATE)
        )
    elif (
        estado_civil in [CASADO, VIUVO, DIVORCIADO, SEPARADO_JUDICIALMENTE]
        and not found
    ):
        """CASADO
        VIUVO
        DIVORCIADO
        SEPARADO_JUDICIALMENTE [WEDDING_CERTIFICATE]"""
        message += "<br>É necessário anexar o documento digital %s." % (
            DIGITAL_DOCUMENT_TYPE.get(WEDDING_CERTIFICATE)
        )
    return message


def validate_mandatory_companion(form_information, field, fields_to_check):
    message = ""

    digital_documents = form_information.digital_documents.filter().exclude(
        state=PROCESSED
    )
    wedding_certificate_choice = Choice.objects.get(
        app_label="rh", name="DIGITAL_DOCUMENT_TYPE", value=WEDDING_CERTIFICATE
    )
    stable_bonding_choice = Choice.objects.get(
        app_label="rh", name="DIGITAL_DOCUMENT_TYPE", value=STABLE_BONDING
    )
    check_diff = getattr(form_information, field)
    if field in fields_to_check and check_diff:
        if form_information.estado_civil in [
            CASADO,
            VIUVO,
            DIVORCIADO,
            SEPARADO_JUDICIALMENTE,
        ]:
            if (
                not form_information.uniao_estavel
                and not digital_documents.filter(
                    document_type__in=[WEDDING_CERTIFICATE]
                ).exists()
            ):
                message += (
                    "<br>%s - Necessário anexar o documento de comprovação: %s<br>"
                    % ("Nome Conjuge", wedding_certificate_choice)
                )
            elif (
                form_information.uniao_estavel
                and not digital_documents.filter(
                    document_type__in=[WEDDING_CERTIFICATE, STABLE_BONDING]
                ).exists()
            ):
                message += (
                    "<br>%s - Necessário anexar o documento de comprovação: %s/%s<br>"
                    % (
                        "Nome Conjuge",
                        wedding_certificate_choice,
                        stable_bonding_choice,
                    )
                )
        elif (
            form_information.estado_civil == SOLTEIRO
            and form_information.nome_conjuge
            and not form_information.uniao_estavel
        ):
            message += "Nessário marcar União Estável ou mudar estado Civil para alterar nome do Conjuge"

    return message


def marital_status_map(digital_documents):
    return {
        SOLTEIRO: lambda digital_documents: digital_documents.filter(
            document_type=BIRTH_CERTIFICATE
        ).exists(),
        CASADO: lambda digital_documents: digital_documents.filter(
            document_type=WEDDING_CERTIFICATE
        ).exists(),
        VIUVO: lambda digital_documents: digital_documents.filter(
            document_type=WEDDING_CERTIFICATE
        ).exists(),
        DIVORCIADO: lambda digital_documents: digital_documents.filter(
            document_type=WEDDING_CERTIFICATE
        ).exists(),
        SEPARADO_JUDICIALMENTE: lambda digital_documents: digital_documents.filter(
            document_type=WEDDING_CERTIFICATE
        ).exists(),
    }


def estado_civil_validate(form_information, field, fields_to_check):
    digital_document_mandatory = [BIRTH_CERTIFICATE, WEDDING_CERTIFICATE]
    if form_information.estado_civil == SOLTEIRO:
        digital_document_mandatory = [BIRTH_CERTIFICATE]
    elif form_information.estado_civil in [
        CASADO,
        VIUVO,
        DIVORCIADO,
        SEPARADO_JUDICIALMENTE,
    ]:
        digital_document_mandatory = [WEDDING_CERTIFICATE]

    message = ""

    """ DIGITAL DOCUMENT FORM INFORMATION """
    employee = form_information.employee
    digital_documents = form_information.digital_documents.filter().exclude(
        state=PROCESSED
    )

    check_diff = getattr(form_information, field)
    if (
        field in fields_to_check
        and check_diff
        and not digital_documents.filter(
            document_type__in=digital_document_mandatory
        ).exists()
    ):
        if form_information.estado_civil:
            message += _raw_estado_civil_validate(
                form_information.estado_civil,
                marital_status_map(digital_documents).get(
                    form_information.estado_civil
                )(digital_documents),
            )
        else:
            message = "Preencha o campo ESTADO CIVIL."

    if (
        not message
        and not digital_documents.filter(
            document_type__in=digital_document_mandatory
        ).exists()
    ):
        if form_information.estado_civil:
            digital_documents = DigitalDocumentRh.objects.filter(
                employee=employee, active=True
            )
            message += _raw_estado_civil_validate(
                employee.pessoa_fisica.estado_civil,
                marital_status_map(digital_documents).get(
                    employee.pessoa_fisica.estado_civil
                )(digital_documents),
            )
        else:
            message = "Preencha o campo ESTADO CIVIL."

    return message


def validate_mandatory_stable_union(form_information, field, fields_to_check):
    digital_document_mandatory = [STABLE_BONDING]
    message = ""

    digital_documents = form_information.digital_documents.filter().exclude(
        state=PROCESSED
    )

    check_diff = getattr(form_information, field)
    if (
        field in fields_to_check
        and check_diff
        and not digital_documents.filter(
            document_type__in=digital_document_mandatory
        ).exists()
    ):
        if form_information.uniao_estavel:
            message = (
                "<br><br>É necessário anexar pelo menos 1(um) dos documentos como %s:<br>"
                % Choice.objects.get(
                    app_label="rh", name="DIGITAL_DOCUMENT_TYPE", value=STABLE_BONDING
                )
            )
            message += "- Certidão de Nascimento de filho em comum;<br>"
            message += "- Certidão de Casamento Religioso;<br>"
            message += "- Declaração de IRPF do ano anterior em que conste o companheiro(a) como dependente;<br>"
            message += "- Comprovante de conta bancária conjunta;<br>"
            message += "- Comprovante de mesmo domicílio em nome do companheiro(a);<br>"
            message += "- Apólice de seguro em que conste o companheiro(a) como dependente;<br>"
            message += "- Documento de propriedade de bem móvel ou imóvel em nome dos companheiros;<br>"
            message += "- Declaração de união estável feita em cartório;<br>"
            message += "- Sentença judicial declaratória."

    return message


def validate_address_citty_diff(form_information, field, fields_to_check):
    message = ""
    digital_document_mandatory = [ADDRESS_CERTIFICATE]

    digital_documents = form_information.digital_documents.filter().exclude(
        state=PROCESSED
    )

    check_diff = getattr(form_information, field)
    if (
        field in fields_to_check
        and check_diff
        and not digital_documents.filter(
            document_type__in=digital_document_mandatory
        ).exists()
    ):
        if (
            not form_information.address_outsider and not form_information.address_city
        ) or (
            form_information.address_outsider
            and not form_information.address_outsider_citty
        ):
            message = (
                "<br><br>Endereço - %s para comprovar a alteração cadastre o documento: COMPROVANTE DE ENDEREÇO.<br>"
                % getattr(form_information, field.replace("_diff", "")).verbose_name
            )

    return message


class FormInformationBase(AuditTimestampModel):
    employee = models.ForeignKey(Servidor, on_delete=models.PROTECT)
    sent_by = models.ForeignKey(
        User, blank=True, on_delete=models.PROTECT, related_name="+", null=True
    )
    sent_at = models.DateTimeField(default=None, null=True, blank=True)
    validated_by = models.ForeignKey(
        User, blank=True, on_delete=models.PROTECT, related_name="+", null=True
    )
    validated_at = models.DateTimeField(default=None, null=True, blank=True)
    received_by = models.ForeignKey(
        User, blank=True, on_delete=models.PROTECT, related_name="+", null=True
    )
    received_at = models.DateTimeField(default=None, null=True, blank=True)
    state = models.IntegerField(
        verbose_name="Estado",
        default=STATE_EMPLOYEE_EDITION,
        blank=True,
        choices=Choice.get_choices_for("registration", "FORMINFORMATION_STATE"),
    )

    """
        Campo para relacionar os campos modificados com os documentos digitais obrigatórios.
    """
    field_mandatory_digital_document = {
        "social_name_diff": [RG],
        "nome_diff": [
            CNH,
            RG,
            PASSPORT,
            PROFESSIONAL_COUNCIL,
            WEDDING_CERTIFICATE,
            BIRTH_CERTIFICATE,
            TITULO_ELEITOR,
        ],
        "nome_pai_diff": [
            CNH,
            RG,
            PROFESSIONAL_COUNCIL,
            WEDDING_CERTIFICATE,
            BIRTH_CERTIFICATE,
        ],
        "nome_mae_diff": [
            CNH,
            RG,
            PROFESSIONAL_COUNCIL,
            WEDDING_CERTIFICATE,
            BIRTH_CERTIFICATE,
        ],
        "nome_conjuge_diff": validate_mandatory_companion,
        "estado_civil_diff": estado_civil_validate,
        "municipio_naturalidade_diff": [RG, BIRTH_CERTIFICATE, WEDDING_CERTIFICATE],
        "nationality_diff": [RG, BIRTH_CERTIFICATE, WEDDING_CERTIFICATE],
        "nationality_birth_diff": [RG, BIRTH_CERTIFICATE, WEDDING_CERTIFICATE],
        "immigrant_residence_time_diff": [RG, BIRTH_CERTIFICATE, WEDDING_CERTIFICATE],
        "immigrant_entry_condition_diff": [RG, BIRTH_CERTIFICATE, WEDDING_CERTIFICATE],
        "data_nascimento_diff": [
            CNH,
            RG,
            PASSPORT,
            PROFESSIONAL_COUNCIL,
            WEDDING_CERTIFICATE,
            BIRTH_CERTIFICATE,
            TITULO_ELEITOR,
        ],
        "rg_diff": [RG],
        "rg_data_expedicao_diff": [RG],
        "rg_orgao_diff": [RG],
        "rg_uf_diff": [RG],
        "cnh_diff": [CNH],
        "cnh_categoria_diff": [CNH],
        "cnh_state_diff": [CNH],
        "cnh_validity_date_diff": [CNH],
        "address_type_street_diff": [ADDRESS_CERTIFICATE],
        "address_type_address_diff": [ADDRESS_CERTIFICATE],
        "address_city_diff": validate_address_citty_diff,
        "address_outsider_citty_diff": validate_address_citty_diff,
        "address_outsider_country_diff": [ADDRESS_CERTIFICATE],
        "address_public_place_diff": [ADDRESS_CERTIFICATE],
        "address_district_diff": [ADDRESS_CERTIFICATE],
        "address_zip_code_diff": [ADDRESS_CERTIFICATE],
        "address_number_diff": [ADDRESS_CERTIFICATE],
        "professional_council_diff": [PROFESSIONAL_COUNCIL],
        "professional_council_state_diff": [PROFESSIONAL_COUNCIL],
        "professional_council_expedition_date_diff": [PROFESSIONAL_COUNCIL],
        "professional_council_issuer_diff": [PROFESSIONAL_COUNCIL],
        "pis_pasep_diff": [PIS_PASEP],
        "nis": [NIS],
        "ctps_diff": [CTPS],
        "ctps_state_diff": [CTPS],
        "serie_ctps_diff": [CTPS],
        "reservista_diff": [RESERVISTA],
        "titulo_eleitor_diff": [TITULO_ELEITOR],
        "municipio_titulo_diff": [TITULO_ELEITOR],
        "secao_titulo_diff": [TITULO_ELEITOR],
        "zona_titulo_diff": [TITULO_ELEITOR],
        "uniao_estavel_diff": validate_mandatory_stable_union,
    }

    """
        Campo para relacionar o documento digital com o campo que deve ser preenchido.
        Utiliza a constante field_group_mandatory para informar quais os campos relacionados ao campo principal.
    """
    digital_document_mandatory_field = {
        CNH: ["cnh"],
        TITULO_ELEITOR: ["titulo_eleitor"],
        CTPS: ["ctps"],
        PIS_PASEP: ["pis_pasep"],
        NIS: ["nis"],
        RESERVISTA: ["reservista"],
        PROFESSIONAL_COUNCIL: ["professional_council"],
        RIC: ["ric"],
        RNE: ["rne"],
        CPF: ["cpf"],
        RG: ["rg"],
        PASSPORT: ["passaport"],
        ADDRESS_CERTIFICATE: ["address_public_place"],
        STABLE_BONDING: ["uniao_estavel"],
    }

    exception_digital_document_mandatory_field = {
        "address_city": ["address_outsider_citty", "address_outsider"],
        "address_outsider_citty": ["address_city", "address_outsider"],
        "address_outsider": ["address_city", "address_outsider_citty"],
    }

    field_group_mandatory = {
        "cnh": [
            "cnh_categoria",
            "cnh_expedition_date",
            "cnh_first_date",
            "cnh_state",
            "cnh_validity_date",
        ],
        "professional_council": [
            "professional_council_state",
            "professional_council_expedition_date",
            "professional_council_issuer",
        ],
        "ctps": ["ctps_state", "serie_ctps"],
        "rg": ["rg_data_expedicao", "rg_orgao", "rg_uf"],
        "ric": ["ric_expedition_date", "ric_issuer", "ric_state"],
        "rne": ["rne_expedition_date", "rne_issuer", "rne_state"],
        "titulo_eleitor": ["municipio_titulo", "secao_titulo", "zona_titulo"],
        "address_public_place": [
            "address_type_street",
            "address_type_address",
            "address_city",
            "address_public_place",
            "address_district",
            "address_zip_code",
            "address_number",
            "address_outsider",
            "address_outsider_citty",
        ],
    }

    field_group = {
        "cnh": [
            "cnh_categoria",
            "cnh_expedition_date",
            "cnh_first_date",
            "cnh_state",
            "cnh_validity_date",
        ],
        "professional_council": [
            "professional_council_state",
            "professional_council_expedition_date",
            "professional_council_issuer",
        ],
        "ctps": ["ctps_state", "serie_ctps"],
        "reservista": [],
    }

    field_group_canot_edit = {
        "cpf": "cpf",
    }

    class Meta:
        abstract = True

    @classmethod
    def possible_docs(cls, field, fields_to_check):
        possible_docs = ""
        for choice in Choice.objects.filter(
            app_label="rh",
            name="DIGITAL_DOCUMENT_TYPE",
            value__in=fields_to_check.get(field),
        ):
            if not possible_docs:
                possible_docs = "%s" % choice
            else:
                possible_docs += ", %s" % choice
        return possible_docs

    def check_fields_is_null(self, field_request):
        for field_name in self.field_group:
            if field_name == field_request:
                if getattr(self, field_name) == "":
                    return True
            else:
                fields_in = self.field_group.get(field_name, [])
                for field in fields_in:
                    if field == field_request:
                        if (
                            getattr(self, field) == "" or getattr(self, field) is None
                        ) and (
                            getattr(self, field_name) == ""
                            or getattr(self, field_name) is None
                        ):
                            return True
                        elif (
                            getattr(self, field) != ""
                            or getattr(self, field) is not None
                        ) and (
                            getattr(self, field_name) == ""
                            or getattr(self, field_name) is None
                        ):
                            return False

        return False

    def _diff_fields_form(self):
        return [
            field.name
            for field in self._meta.get_fields()
            if field.name.find("_diff") >= 0
        ]

    def validate_canot_edit(self):
        """
        :py:function:: validate_canot_edit(self)

        This method validates fields that canot be edited.

        :return: True
        :rtype: boolean
        :raises Exception: if there are at least one
        """
        fields_to_check = self.field_group_canot_edit
        message = ""
        for fld in fields_to_check:
            if hasattr(self, "%s_diff" % fld) and getattr(self, "%s_diff" % fld, False):
                message += (
                    "Não é possível alterar o campo: %s.<br>"
                    % self._meta.get_field(fld).verbose_name
                )
        if message:
            raise Exception(message)
        return True

    def validate_mandatory_field_digital_document(self):
        """
        :py:function:: validate_mandatory_field_digital_document(self)

        This method validates fields that require a digital documents filed.

        CAMPOS QUE EXIGEM DOCUMENTO DIGITAL.

        :return: True
        :rtype: boolean
        :raises Exception: if there are at least one
        """
        fields = self._diff_fields_form()
        sorted(fields)
        fields_to_check = self.field_mandatory_digital_document
        message = ""
        try:
            for fld in fields:
                result = fields_to_check.get(fld)
                if (
                    not callable(result)
                    and fld in fields_to_check
                    and getattr(self, fld)
                    and not self.check_fields_is_null(fld.replace("_diff", ""))
                    and not self.digital_documents.filter(document_type__in=result)
                    .exclude(state=PROCESSED)
                    .exists()
                ):
                    possible_docs = FormInformationBase.possible_docs(
                        fld, fields_to_check
                    )
                    message += (
                        "<br><b>%s</b> - para comprovar a alteração cadastre algum documento (do membro/servidor): %s."
                        % (
                            self._meta.get_field(fld.replace("_diff", "")).verbose_name,
                            possible_docs,
                        )
                    )
                elif callable(result):
                    message += result(self, fld, fields_to_check)
        except Exception as err:
            log.exception(err)
        if message:
            raise Exception(message)

    def check_not_exception(self, field, fields_mandatory):
        check = False
        for fld in self.exception_digital_document_mandatory_field.get(field, []):
            if getattr(self, fld):
                check = True
                break
        return check

    def validate_mandatory_digital_document_field(self):
        """
        :py:function:: validate_mandatory_digital_document_field(self)

        This method validates digital documents that require a field filed.

        DOCUMENTO DIGITAL QUE EXIGE CAMPO PREENCHIDO.

        :return: True
        :rtype: boolean
        :raises Exception: if there are at least one
        """
        message = ""
        digital_documents = self.digital_documents.filter().exclude(state=PROCESSED)
        dict_err = {}
        for digital_document in digital_documents:
            fields_mandatory = []
            message_err = ""
            fields = self.digital_document_mandatory_field.get(
                digital_document.document_type, []
            )
            for field in fields:
                fields_mandatory.append(field)
                fields_mandatory += self.field_group_mandatory.get(field, [])

            for field in fields_mandatory:
                if not getattr(self, field) and not self.check_not_exception(
                    field, fields_mandatory
                ):
                    field_verbose_name = self._meta.get_field(field).verbose_name
                    message_err += "%s%s" % (
                        ", " if message_err else "",
                        field_verbose_name,
                    )
                    dict_err.update(
                        {
                            field: "Para anexo %s é necessário preencher %s."
                            % (
                                digital_document.get_document_type_display(),
                                field_verbose_name,
                            )
                        }
                    )
            message += message_err
        if dict_err:
            raise ValidationError(dict_err)

    def validate_mandatory_digitaldocument_documentnaturalperson(self):
        """
        :py:function:: validate_mandatory_digitaldocument_documentnaturalperson(self)

        This method validates natural person's document that require a digital document.

        DOCUMENTO DA PESSOA FISICA QUE EXIGE DOCUMENTO DIGITAL.

        :return: True
        :rtype: boolean
        :raises Exception: if there are at least one
        """
        message = ""
        digital_document_mandatory = Documento.digital_document_mandatory
        digital_document_mandatory += DigitalDocumentRh.digital_document_mandatory
        exists_document = self.digital_documents.filter(
            document_type__in=digital_document_mandatory
        ).exclude(state=PROCESSED)
        exclude_digital_document = [
            dg.get("document_type") for dg in exists_document.values("document_type")
        ]
        try:
            Documento.validate_mandatory_digital_document(
                self.employee, exclude=exclude_digital_document
            )
        except Exception as err:
            message = str(err)
        try:
            digital_document_mandatory = [CPF, RG, CNH]

            rh_digital_documents = DigitalDocumentRh.objects.filter(
                employee=self.employee, active=True
            )
            fi_digital_documents = self.digital_documents.filter().exclude(
                state=PROCESSED
            )

            if (
                not fi_digital_documents.filter(
                    document_type__in=digital_document_mandatory
                ).exists()
                and not rh_digital_documents.filter(
                    document_type__in=digital_document_mandatory
                ).exists()
            ):
                message += "<br>É necessário anexar o documento digital CPF, RG ou CNH com documento de CPF legível."
        except Exception as err:
            message += str(err)
        try:
            DigitalDocumentRh.validate_mandatory_digital_document(
                self.employee, exclude=exclude_digital_document
            )
        except Exception as err:
            message += str(err)
        if message:
            raise Exception(message)
        return True

    def validate_digital_document_not_processed(self):
        message = ""
        for digital_document in self.digital_documents.filter(state=NOT_VALIDITY):
            message += (
                "<br>Documento digital não validado: %s. Remova-o e cadastre o correto."
                % (digital_document.get_document_type_display())
            )
        if message:
            raise Exception(message)
        return True

    def validate_transition_state(self, state):
        if (
            state not in STATE_TRANSITION.get(self.state)
            and state != self.state
            and not (is_admin() or is_current_user_system())
        ):
            raise Exception(
                "Não é possível modificar o estado para %s. Modifique alguma informação antes de enviar."
                % Choice.objects.filter(
                    app_label="registration", name="FORMINFORMATION_STATE", value=state
                ).last()
            )

    def validate_send_rh(self):
        changes_digital_documents = self.digital_documents.exclude(
            state=PROCESSED
        ).exists()
        fields = self._diff_fields_form()
        changes_fields = False
        for fld in fields:
            if getattr(self, fld):
                changes_fields = True
                break
        if not changes_fields and not changes_digital_documents:
            raise Exception("Nenhum campo foi alterado.")
        return True

    def transition_state(self, state):
        self.validate_transition_state(state)
        if state == STATE_DGPFP_SENT:
            self.validate_send_rh()
            self._set_sent()
        elif state in [STATE_EMPLOYEE_VALIDATED, STATE_EMPLOYEE_VALIDATED_PROBLEM]:
            self._set_validated()
        elif state in [STATE_DGPFP_RECEIVED]:
            self._set_received()
        self._set_modified()
        FormInformation.objects.filter(pk=self.pk).update(state=state)

    def send_validation(self):
        if not is_current_user_system():
            self.clean_all_validate()
        self.transition_state(STATE_DGPFP_SENT)

    def undo_send_validation(self):
        self.transition_state(STATE_EMPLOYEE_EDITION)

    def _set_received(self):
        FormInformation.objects.filter(pk=self.pk).update(
            received_by=get_current_user(), received_at=datetime.datetime.now()
        )

    def _set_validated(self):
        FormInformation.objects.filter(pk=self.pk).update(
            validated_by=get_current_user(), validated_at=datetime.datetime.now()
        )

    def _set_sent(self):
        FormInformation.objects.filter(pk=self.pk).update(
            sent_by=get_current_user(), sent_at=datetime.datetime.now()
        )

    def _set_modified(self):
        FormInformation.objects.filter(pk=self.pk).update(
            modified_by=get_current_user(), modified_at=datetime.datetime.now()
        )


class FormInformation(FormInformationBase):

    AUDITABLE = {
        "fields": [
            "cnh",
            "cnh_categoria",
            "cnh_expedition_date",
            "cnh_first_date",
            "cnh_state_id",
            "cnh_validity_date",
            "professional_council",
            "professional_council_state_id",
            "professional_council_expedition_date",
            "professional_council_validity_date",
            "professional_council_issuer",
            "cpf",
            "ctps",
            "ctps_state_id",
            "serie_ctps",
            "data_nascimento",
            "doador",
            "email_institucional",
            "estado_civil",
            "immigrant_residence_time",
            "fator_rh",
            "foto_id",
            "grau_instrucao",
            "municipio_naturalidade_id",
            "municipio_naturalidade",
            "nationality_id",
            "nationality",
            "nationality_birth_id",
            "nationality_birth",
            "nis",
            "nome",
            "nome_conjuge",
            "immigrant_entry_condition",
            "nome_mae",
            "nome_pai",
            "pis_pasep",
            "raca_cor",
            "reservista",
            "classe_reservista",
            "rg",
            "rg_data_expedicao",
            "rg_orgao",
            "rg_uf_id",
            "ric",
            "ric_expedition_date",
            "ric_issuer",
            "ric_state_id",
            "rne",
            "rne_expedition_date",
            "rne_issuer",
            "rne_state_id",
            "sangue",
            "sexo",
            "sexual_orientation",
            "social_name",
            "titulo_eleitor",
            "municipio_titulo_id",
            "secao_titulo",
            "zona_titulo",
            "address_type_street",
            "address_type_address",
            "address_city_id",
            "address_public_place",
            "address_district",
            "address_zip_code",
            "address_number",
            "address_complement",
            "address_outsider",
            "address_country_id",
            "address_outsider_citty",
            "phone_main",
            "phone_outsider",
            "contact_emergency_name",
            "contact_emergency_phone",
            "contact_emergency_phone_kinship",
            "uniao_estavel",
            "genero",
            "address_new",
            "grau_instrucao",
        ]
    }

    active = models.BooleanField(default=True, blank=True)

    address_can_edit = models.BooleanField(default=True, blank=True)
    address_type_street = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_STREET"),
        verbose_name="Endereço - Tipo do Logradouro",
        null=True,
        blank=True,
    )
    address_type_street_diff = models.BooleanField(default=False, blank=True)
    address_type_address = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_ADDRESS"),
        verbose_name="Endereço - Tipo do Endereço",
        null=True,
        blank=True,
    )
    address_type_address_diff = models.BooleanField(default=False, blank=True)
    address_city = models.ForeignKey(
        "rh.Localidade",
        null=True,
        blank=True,
        verbose_name="Endereço - Cidade",
        related_name="+",
        on_delete=models.CASCADE,
    )
    address_city_diff = models.BooleanField(default=False, blank=True)
    address_public_place = models.CharField(
        max_length=80, null=True, blank=True, verbose_name="Endereço - Logradouro"
    )
    address_public_place_diff = models.BooleanField(default=False, blank=True)
    address_district = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Endereço - Bairro"
    )
    address_district_diff = models.BooleanField(default=False, blank=True)
    address_zip_code = models.CharField(
        max_length=10, verbose_name="CEP", null=True, blank=True
    )
    address_zip_code_diff = models.BooleanField(default=False, blank=True)
    address_number = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Endereço - Número"
    )
    address_number_diff = models.BooleanField(default=False, blank=True)
    address_complement = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Endereço - Complemento"
    )
    address_complement_diff = models.BooleanField(default=False, blank=True)
    address_outsider = models.BooleanField(
        verbose_name="Endereço no exterior", default=False, blank=True
    )
    address_outsider_diff = models.BooleanField(default=False, blank=True)
    address_country = models.ForeignKey(
        "rh.Pais",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forminformation_address_country",
        verbose_name="País(Residentes no Exterior)",
    )
    address_country_diff = models.BooleanField(default=False, blank=True)
    address_outsider_citty = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Cidade no Exterior"
    )
    address_outsider_citty_diff = models.BooleanField(default=False, blank=True)
    address_new = models.BooleanField(
        verbose_name="Endereço novo", default=False, blank=True
    )
    address_new_diff = models.BooleanField(default=False, blank=True)

    phone_main = models.CharField(
        max_length=15,
        verbose_name="Telefone Principal",
        default="",
        blank=True,
        null=True,
    )
    phone_main_diff = models.BooleanField(default=False, blank=True)
    phone_main_can_edit = models.BooleanField(default=True, blank=True)
    phone_outsider = models.BooleanField(
        verbose_name="Telefone no exterior", default=False, blank=True
    )
    phone_outsider_diff = models.BooleanField(default=False, blank=True)
    contact_emergency_name = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name="Nome do Contato de Emergência",
    )
    contact_emergency_name_diff = models.BooleanField(default=False, blank=True)
    contact_emergency_name_can_edit = models.BooleanField(default=True, blank=True)
    contact_emergency_phone = models.CharField(
        max_length=15,
        verbose_name="Telefone de Emergência",
        default="",
        blank=True,
        null=True,
    )
    contact_emergency_phone_can_edit = models.BooleanField(default=True, blank=True)
    contact_emergency_phone_diff = models.BooleanField(default=False, blank=True)
    contact_emergency_phone_kinship = models.CharField(
        max_length=13,
        verbose_name="Grau de Parentesco/Contato de Emergência",
        default="",
        blank=True,
        null=True,
    )
    contact_emergency_phone_kinship_can_edit = models.BooleanField(
        default=True, blank=True
    )
    contact_emergency_phone_kinship_diff = models.BooleanField(
        default=False, blank=True
    )

    cnh_can_edit = models.BooleanField(default=True, blank=True)
    cnh = models.CharField(
        max_length=11, verbose_name="CNH", default="", blank=True, null=True
    )
    cnh_diff = models.BooleanField(default=False, blank=True)
    cnh_categoria = models.CharField(
        max_length=30, verbose_name="CNH - Categoria", default="", blank=True, null=True
    )
    cnh_categoria_diff = models.BooleanField(default=False, blank=True)
    cnh_expedition_date = models.DateField(
        verbose_name="CNH - Data da Expedição", null=True, blank=True
    )
    cnh_expedition_date_diff = models.BooleanField(default=False, blank=True)
    cnh_first_date = models.DateField(
        verbose_name="CNH - Data da primeira habilitação", null=True, blank=True
    )
    cnh_first_date_diff = models.BooleanField(default=False, blank=True)
    cnh_state = models.ForeignKey(
        "rh.Estado",
        null=True,
        blank=True,
        verbose_name="CNH - Estado",
        related_name="+",
        on_delete=models.CASCADE,
    )
    cnh_state_diff = models.BooleanField(default=False, blank=True)
    cnh_validity_date = models.DateField(
        verbose_name="CNH - Data de Validade", null=True, blank=True
    )
    cnh_validity_date_diff = models.BooleanField(default=False, blank=True)

    professional_council_can_edit = models.BooleanField(default=True, blank=True)
    professional_council = models.CharField(
        max_length=30,
        verbose_name="Conselho Profissional",
        default="",
        blank=True,
        null=True,
    )
    professional_council_diff = models.BooleanField(default=False, blank=True)
    professional_council_state = models.ForeignKey(
        "rh.Estado",
        null=True,
        blank=True,
        verbose_name="Conselho Profissional - Estado",
        related_name="+",
        on_delete=models.CASCADE,
    )
    professional_council_state_diff = models.BooleanField(default=False, blank=True)
    professional_council_expedition_date = models.DateField(
        verbose_name="Conselho Profissional - Data da Expedição", null=True, blank=True
    )
    professional_council_expedition_date_diff = models.BooleanField(
        default=False, blank=True
    )
    professional_council_validity_date = models.DateField(
        verbose_name="Conselho Profissional - Data de Validade", null=True, blank=True
    )
    professional_council_validity_date_diff = models.BooleanField(default=False)
    professional_council_issuer = models.CharField(
        max_length=256,
        default="",
        blank=True,
        null=True,
        verbose_name="Conselho Profissional - Orgão de Expedição",
    )
    professional_council_issuer_diff = models.BooleanField(default=False, blank=True)

    cpf_can_edit = models.BooleanField(default=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True, verbose_name="CPF")
    cpf_doc_digital_required = models.BooleanField(default=True, blank=True)
    cpf_diff = models.BooleanField(default=False, blank=True)

    ctps_can_edit = models.BooleanField(default=True, blank=True)
    ctps = models.CharField(
        max_length=30, verbose_name="CTPS", default="", blank=True, null=True
    )
    ctps_diff = models.BooleanField(default=False, blank=True)
    ctps_state = models.ForeignKey(
        "rh.Estado",
        null=True,
        blank=True,
        verbose_name="CTPS - Estado",
        related_name="+",
        on_delete=models.CASCADE,
    )
    ctps_state_diff = models.BooleanField(default=False, blank=True)
    serie_ctps = models.CharField(
        max_length=30, default="", blank=True, null=True, verbose_name="CTPS - Série"
    )
    serie_ctps_diff = models.BooleanField(default=False, blank=True)

    data_nascimento_can_edit = models.BooleanField(default=True, blank=True)
    data_nascimento = models.DateField(
        null=True, blank=True, verbose_name="Data de Nascimento"
    )
    data_nascimento_diff = models.BooleanField(default=False, blank=True)

    doador = models.BooleanField(
        default=True, blank=True, verbose_name="Doador de órgãos"
    )
    doador_can_edit = models.BooleanField(default=True, blank=True)
    doador_diff = models.BooleanField(default=False, blank=True)

    uniao_estavel = models.BooleanField(
        default=False, blank=True, verbose_name="União Estável"
    )
    uniao_estavel_can_edit = models.BooleanField(default=True, blank=True)
    uniao_estavel_diff = models.BooleanField(default=False, blank=True)

    email_institucional_can_edit = models.BooleanField(default=True, blank=True)
    email_institucional = models.CharField(
        max_length=40,
        default="",
        blank=True,
        null=True,
        verbose_name="E-mail Institucional",
    )
    email_institucional_diff = models.BooleanField(default=False, blank=True)

    email_pessoal_can_edit = models.BooleanField(default=True, blank=True)
    email_pessoal = models.CharField(
        max_length=40, default="", blank=True, null=True, verbose_name="E-mail Pessoal"
    )
    email_pessoal_diff = models.BooleanField(default=False, blank=True)

    estado_civil_can_edit = models.BooleanField(default=True, blank=True)
    estado_civil = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "MARITAL_STATUS"),
        null=True,
        verbose_name="Estado civíl",
    )
    estado_civil_diff = models.BooleanField(default=False, blank=True)

    fator_rh_can_edit = models.BooleanField(default=True, blank=True)
    fator_rh = models.IntegerField(
        default=2,
        choices=Choice.get_choices_for("rh", "FACTOR_RH"),
        null=True,
        blank=True,
        verbose_name="Fator RH",
    )
    fator_rh_diff = models.BooleanField(default=False, blank=True)

    foto_can_edit = models.BooleanField(default=True, blank=True)
    foto = models.ForeignKey(
        "ged.Arquivo",
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Foto",
        on_delete=models.CASCADE,
    )
    foto_diff = models.BooleanField(default=False, blank=True)

    grau_instrucao_can_edit = models.BooleanField(default=True, blank=True)
    grau_instrucao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEGREE_EDUCATION"),
        verbose_name="Grau de Instrução",
        default=8,
        blank=True,
        null=True,
    )
    grau_instrucao_diff = models.BooleanField(default=False, blank=True)
    municipio_naturalidade = models.ForeignKey(
        "rh.Localidade",
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Naturalidade",
        on_delete=models.CASCADE,
    )
    municipio_naturalidade_can_edit = models.BooleanField(default=True, blank=True)
    municipio_naturalidade_diff = models.BooleanField(default=False, blank=True)

    nationality = models.ForeignKey(
        "rh.Pais", verbose_name="Nacionalidade", on_delete=models.PROTECT, default=1
    )
    nationality_can_edit = models.BooleanField(default=True, blank=True)
    nationality_diff = models.BooleanField(default=False, blank=True)

    nationality_birth = models.ForeignKey(
        "rh.Pais",
        verbose_name="País de nascimento",
        on_delete=models.PROTECT,
        default=1,
        related_name="forminformation_nationality_birth",
    )
    nationality_birth_can_edit = models.BooleanField(default=True, blank=True)
    nationality_birth_diff = models.BooleanField(default=False, blank=True)

    immigrant_residence_time = models.IntegerField(
        choices=Choice.get_choices_for("rh", "IMMIGRANTE_RESIDENCE_TIME"),
        verbose_name="Tempo de residência do imigrante",
        default=NOT_IMMIGRANT,
    )
    immigrant_residence_time_can_edit = models.BooleanField(default=True, blank=True)
    immigrant_residence_time_diff = models.BooleanField(default=False, blank=True)

    immigrant_entry_condition = models.IntegerField(
        choices=Choice.get_choices_for("rh", "IMMIGRANTE_ENTRY_CONDITION"),
        verbose_name="Condição de ingresso do imigrante",
        default=NOT_IMMIGRANT,
    )
    immigrant_entry_condition_can_edit = models.BooleanField(default=True, blank=True)
    immigrant_entry_condition_diff = models.BooleanField(default=False, blank=True)

    nis_can_edit = models.BooleanField(default=True, blank=True)
    nis = models.CharField(
        max_length=30, verbose_name="NIS", default="", blank=True, null=True
    )
    nis_diff = models.BooleanField(default=False, blank=True)

    nome_can_edit = models.BooleanField(default=True, blank=True)
    nome = models.CharField(max_length=100, verbose_name="Nome", default="", blank=True)
    nome_diff = models.BooleanField(default=False, blank=True)
    nome_doc_digital_required = models.BooleanField(default=True, blank=True)

    nome_conjuge = models.CharField(
        max_length=80, null=True, blank=True, verbose_name="Nome Cônjuge"
    )
    nome_conjuge_diff = models.BooleanField(default=False, blank=True)
    nome_conjuge_can_edit = models.BooleanField(default=True, blank=True)

    nome_mae = models.CharField(
        max_length=80, null=True, blank=True, verbose_name="Nome Mãe"
    )
    nome_mae_diff = models.BooleanField(default=False, blank=True)
    nome_mae_can_edit = models.BooleanField(default=True, blank=True)

    nome_pai = models.CharField(
        max_length=80, null=True, blank=True, verbose_name="Nome Pai"
    )
    nome_pai_can_edit = models.BooleanField(default=True, blank=True)
    nome_pai_diff = models.BooleanField(default=False, blank=True)

    genero = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Gênero"
    )
    genero_diff = models.BooleanField(default=False, blank=True)
    genero_can_edit = models.BooleanField(default=True, blank=True)

    pis_pasep_can_edit = models.BooleanField(default=True, blank=True)
    pis_pasep = models.CharField(
        max_length=30, verbose_name="PIS/PASEP", default="", blank=True, null=True
    )
    pis_pasep_diff = models.BooleanField(default=False, blank=True)

    raca_cor_can_edit = models.BooleanField(default=True, blank=True)
    raca_cor = raca_cor = models.IntegerField(
        default=5,
        choices=Choice.get_choices_for("rh", "TYPE_RACE"),
        verbose_name="Raça/Cor",
        null=True,
    )
    raca_cor_diff = models.BooleanField(default=False, blank=True)

    reservista_can_edit = models.BooleanField(default=True, blank=True)
    reservista = models.CharField(
        max_length=30, verbose_name="Reservista", default="", blank=True, null=True
    )
    reservista_diff = models.BooleanField(default=False, blank=True)

    classe_reservista = models.CharField(
        max_length=30,
        default="",
        blank=True,
        null=True,
        verbose_name="Reservista - Classe",
    )
    classe_reservista_diff = models.BooleanField(default=False, blank=True)

    rg_can_edit = models.BooleanField(default=True, blank=True)
    rg = models.CharField(
        max_length=30, verbose_name="RG", default="", blank=True, null=True
    )
    rg_diff = models.BooleanField(default=False, blank=True)
    rg_data_expedicao = models.DateField(
        verbose_name="RG - Data da Expedição", null=True, blank=True
    )
    rg_data_expedicao_diff = models.BooleanField(default=False, blank=True)
    rg_orgao = models.CharField(
        max_length=30, default="", blank=True, null=True, verbose_name="RG - Orgão"
    )
    rg_orgao_diff = models.BooleanField(default=False, blank=True)
    rg_uf = models.ForeignKey(
        "rh.Estado",
        null=True,
        blank=True,
        verbose_name="RG - UF",
        on_delete=models.CASCADE,
    )
    rg_uf_diff = models.BooleanField(default=False, blank=True)

    ric_can_edit = models.BooleanField(default=True, blank=True)
    ric = models.CharField(
        max_length=30, verbose_name="RIC", default="", blank=True, null=True
    )
    ric_diff = models.BooleanField(default=False, blank=True)
    ric_expedition_date = models.DateField(
        verbose_name="RIC - Data da Expedição", null=True, blank=True
    )
    ric_expedition_date_diff = models.BooleanField(default=False, blank=True)
    ric_issuer = models.CharField(
        max_length=256,
        default="",
        blank=True,
        null=True,
        verbose_name="RIC - Orgão Emissor",
    )
    ric_issuer_diff = models.BooleanField(default=False, blank=True)
    ric_state = models.ForeignKey(
        "rh.Estado",
        null=True,
        blank=True,
        verbose_name="RIC - Estado",
        related_name="+",
        on_delete=models.CASCADE,
    )
    ric_state_diff = models.BooleanField(default=False, blank=True)

    rne_can_edit = models.BooleanField(default=True, blank=True)
    rne = models.CharField(
        max_length=30, verbose_name="RNE", default="", blank=True, null=True
    )
    rne_diff = models.BooleanField(default=False, blank=True)
    rne_expedition_date = models.DateField(
        verbose_name="RNE - Data da Expedição", null=True, blank=True
    )
    rne_expedition_date_diff = models.BooleanField(default=False, blank=True)
    rne_issuer = models.CharField(
        max_length=256,
        default="",
        blank=True,
        null=True,
        verbose_name="RNE - Orgão Emissor",
    )
    rne_issuer_diff = models.BooleanField(default=False, blank=True)
    rne_state = models.ForeignKey(
        "rh.Estado",
        null=True,
        blank=True,
        verbose_name="RNE - Estado",
        related_name="+",
        on_delete=models.CASCADE,
    )
    rne_state_diff = models.BooleanField(default=False, blank=True)

    sangue_can_edit = models.BooleanField(default=True, blank=True)
    sangue = models.IntegerField(
        choices=Choice.get_choices_for("rh", "BLOOD"),
        blank=True,
        default=4,
        verbose_name="Tipo Sanguíneo",
    )
    sangue_diff = models.BooleanField(default=False, blank=True)

    sexo_can_edit = models.BooleanField(default=True, blank=True)
    sexo = models.CharField(
        max_length=1, choices=SEXO_CHOICES, null=True, blank=True, verbose_name="Sexo"
    )
    sexo_diff = models.BooleanField(default=False, blank=True)

    sexual_orientation_can_edit = models.BooleanField(default=True, blank=True)
    sexual_orientation = models.PositiveSmallIntegerField(
        verbose_name="Orientação Sexual",
        blank=True,
        null=True,
        choices=Choice.get_choices_for("rh", "SEXUAL_ORIENTATION"),
        default=5,
    )
    sexual_orientation_diff = models.BooleanField(default=False, blank=True)

    social_name_can_edit = models.BooleanField(default=True, blank=True)
    social_name = models.CharField(
        max_length=100, verbose_name="Nome Social", blank=True, null=True
    )
    social_name_diff = models.BooleanField(default=False, blank=True)

    titulo_eleitor_can_edit = models.BooleanField(default=True, blank=True)
    titulo_eleitor = models.CharField(
        max_length=30, verbose_name="Título Eleitor", default="", blank=True, null=True
    )
    titulo_eleitor_diff = models.BooleanField(default=False, blank=True)
    municipio_titulo = models.ForeignKey(
        "rh.Localidade",
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Título de Eleitor - Municipio",
        on_delete=models.CASCADE,
    )
    municipio_titulo_diff = models.BooleanField(default=False, blank=True)
    secao_titulo = models.CharField(
        max_length=30,
        default="",
        blank=True,
        null=True,
        verbose_name="Título de Eleitor - Seção",
    )
    secao_titulo_diff = models.BooleanField(default=False, blank=True)
    zona_titulo = models.CharField(
        max_length=30,
        default="",
        blank=True,
        null=True,
        verbose_name="Título de Eleitor - Zona",
    )
    zona_titulo_diff = models.BooleanField(default=False, blank=True)

    grau_instrucao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEGREE_EDUCATION"),
        verbose_name="Grau de Instrução",
        default=8,
    )
    grau_instrucao_diff = models.BooleanField(default=False, blank=True)
    grau_instrucao_can_edit = models.BooleanField(default=True, blank=True)

    class Meta:
        verbose_name = "Formulário de Informações - Recadastramento"
        ordering = ("sent_at",)
        permissions = (("registration_admin", "Admin"),)

    def __str__(self):
        return "Recadastramento de %s" % self.employee

    @property
    def description(self):
        return "%s : %s" % (self.employee.matricula, self.nome)

    def _diff_fields(self):
        for key in list(self.old_fields.keys()):
            key = key.replace("_id", "")
            if hasattr(self, "%s_diff" % key):
                setattr(self, "%s_diff" % key, True)

        phone = self.employee.pessoa_fisica.phone.filter()
        if (
            not phone.filter(main=True).exists()
            and phone.filter(numero=self.phone_main).exists()
            and not getattr(self, "phone_main_diff", False)
        ):
            setattr(self, "phone_main_diff", True)

    def _diff_natural_person_field(self, key):
        diff = False
        if hasattr(self.employee.pessoa_fisica, key):
            natural_person_value = getattr(self.employee.pessoa_fisica, key)
            form_information_value = getattr(self, key)
            if natural_person_value != form_information_value:
                diff = True
        return diff

    def do_diff_fields(self, kargs):
        if kargs.get("do_diff_fields", True):
            self._diff_fields()

    def _remove_keyword(self, kargs):
        if "do_diff_fields" in kargs:
            kargs.pop("do_diff_fields")
        if "do_validate" in kargs:
            kargs.pop("do_validate")
        return kargs

    def save(self, *args, **kargs):
        employee_try_change = employee_from_user(get_current_user())
        if self.employee == employee_try_change:
            self.state = STATE_EMPLOYEE_EDITION

        self.validate_transition_state(self.state)
        self.do_diff_fields(kargs)
        self.address_zip_code = (
            self.address_zip_code.lstrip()
            .replace(".", "")
            .replace("-", "")
            .replace(" ", "")
            if self.address_zip_code
            else ""
        )
        self.address_public_place = (
            " ".join(self.address_public_place.split())
            if self.address_public_place
            else ""
        )
        self.address_number = (
            self.address_number.lstrip() if self.address_number else ""
        )
        self.address_district = (
            " ".join(self.address_district.split()) if self.address_district else ""
        )
        self.address_complement = (
            " ".join(self.address_complement.split()) if self.address_complement else ""
        )
        self.address_outsider_citty = (
            " ".join(self.address_outsider_citty.split())
            if self.address_outsider_citty
            else ""
        )

        kargs = self._remove_keyword(kargs)
        try:
            super(FormInformation, self).save(*args, **kargs)
        except Exception as err:
            log.exception(err)

    def clean_all_validate(self):
        errors = {}
        try:
            self.validate_mandatory_rg_number()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_rg_issuer()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_rg_state()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_rg_date_expedition()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_sex()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_race()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_degree_education()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_date_born()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_municipality_naturalness()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_nationality()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_ctps_series()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_ctps_state()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_cpf()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_professional_council()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_cnh_len()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_cnh_category()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_cnh_date_validity()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_cnh_state()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_cnh_job_position()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_voter()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_zone()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_section()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_city()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_state()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_address_street()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_address_type()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_address_number()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_address_district()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_address_city()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_address_public_place()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_address_zip_code()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_address_country()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_outsider_citty()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_phone()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_contact_emergency_name()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_contact_emergency_phone()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_digitaldocument_documentnaturalperson()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_field_digital_document()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_mandatory_digital_document_field()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        try:
            self.validate_canot_edit()
        except (Exception, ValidationError) as err:
            log.exception(err)
            errors = _concat_dict(errors, err)
        form_informations = DependentFormInformation.objects.filter(
            employee=self.employee
        )
        for form_information in form_informations:
            try:
                try:
                    self.validate_exists_cpf_dependent(form_information)
                except (Exception, ValidationError) as err:
                    log.exception(err)
                    errors = _concat_dict(errors, err)
                    pass
                try:
                    self.validate_cpf_dependent(form_information)
                except (Exception, ValidationError) as err:
                    log.exception(err)
                    errors = _concat_dict(errors, err)
                    pass
                try:
                    self.validate_tipo_dependent(form_information)
                except (Exception, ValidationError) as err:
                    log.exception(err)
                    errors = _concat_dict(errors, err)
                    pass
            except:
                pass

        if errors:
            log.debug(type(errors))
            raise ValidationError(errors)

    def validate(self, kargs):
        if kargs.get("do_validate", True):
            self.validate_mandatory_rg()
            self.validate_mandatory_sex()
            self.validate_mandatory_race()
            self.validate_mandatory_degree_education()
            self.validate_mandatory_date_born()
            self.validate_mandatory_municipality_naturalness()
            self.validate_mandatory_nationality()
            self.validate_mandatory_ctps()
            self.validate_mandatory_cpf()
            self.validate_mandatory_professional_council()
            self.validate_mandatory_cnh()
            self.validate_mandatory_voter()
            self.validate_mandatory_address_street()
            self.validate_mandatory_address_type()
            self.validate_mandatory_address_number()
            self.validate_mandatory_address_district()
            self.validate_mandatory_address_city()
            self.validate_mandatory_address_public_place()
            self.validate_mandatory_address_zip_code()
            self.validate_mandatory_address_country()
            self.validate_mandatory_outsider_citty()
            self.validate_mandatory_phone()
            self.validate_mandatory_contact_emergency_name()
            self.validate_mandatory_contact_emergency_phone()
            self.validate_mandatory_field_digital_document()
            self.validate_mandatory_digital_document_field()
            self.validate_mandatory_digitaldocument_documentnaturalperson()
            self.validate_canot_edit()
            self.validate_dependents()
        return True

    def validate_mandatory_sex(self):
        if not self.sexo:
            raise ValidationError({"sexo": "Preencha o campo Sexo."})
        return True

    def validate_mandatory_address_street(self):
        if not self.address_type_street:
            raise ValidationError(
                {"address_type_street": "Preencha o campo Tipo do Logradouro."}
            )
        return True

    def validate_mandatory_address_type(self):
        if not self.address_type_address:
            raise ValidationError(
                {"address_type_address": "Preencha o campo Tipo de Endereço."}
            )
        return True

    def validate_mandatory_address_number(self):
        if not self.address_number:
            raise ValidationError({"address_number": "Preencha o campo Numero."})
        return True

    def validate_mandatory_address_district(self):
        if not self.address_district:
            raise ValidationError({"address_district": "Preencha o campo Bairro."})
        return True

    def validate_mandatory_address_city(self):
        if not self.address_outsider and not self.address_city:
            raise ValidationError({"address_city": "Preencha o campo Cidade."})
        return True

    def validate_mandatory_address_public_place(self):
        if not self.address_public_place:
            raise ValidationError(
                {"address_public_place": "Preencha o campo Logradouro."}
            )
        return True

    def validate_mandatory_address_zip_code(self):
        if not self.address_zip_code:
            raise ValidationError({"address_zip_code": "Preencha o campo CEP."})
        elif len(self.address_zip_code) < 8:
            raise ValidationError(
                {"address_zip_code": "Preencha o campo CEP com 8 dígitos."}
            )
        elif not self.address_zip_code.isdigit():
            raise Exception("Preencha o campo CEP apenas com dígitos.")
        return True

    def validate_mandatory_address_country(self):
        if self.address_outsider and not self.address_country:
            raise ValidationError({"address_country": "Preencha o campo País."})
        return True

    def validate_mandatory_outsider_citty(self):
        if self.address_outsider and not self.address_outsider_citty:
            raise ValidationError(
                {"address_outsider_citty": "Preencha o campo Cidade no Exterior."}
            )
        return True

    def validate_mandatory_phone(self):
        if not self.phone_main:
            raise ValidationError(
                {"phone_main": "Preencha o campo Telefone Principal."}
            )
        elif self.phone_main and len(self.phone_main) < 8:
            raise ValidationError(
                {
                    "phone_main": "Preencha o campo Telefone Principal no mínimo 8 e no máximo 15 dígitos."
                }
            )
        return True

    def validate_mandatory_contact_emergency_name(self):
        if not self.contact_emergency_name:
            raise ValidationError(
                {
                    "contact_emergency_name": "Preencha o campo Nome do Contato de Emergência."
                }
            )
        return True

    def validate_mandatory_contact_emergency_phone(self):
        if not self.contact_emergency_phone:
            raise ValidationError(
                {
                    "contact_emergency_phone": "Preencha o campo Telefone do Contato de Emergência."
                }
            )
        elif self.contact_emergency_phone and len(self.contact_emergency_phone) < 8:
            raise ValidationError(
                {
                    "contact_emergency_phone": "Preencha o campo Telefone do Contato de Emergência no mínimo 8 e no máximo 15 dígitos."
                }
            )
        return True

    def validate_mandatory_race(self):
        if not self.raca_cor:
            raise ValidationError({"raca_cor": "Preencha o campo Raça."})
        return True

    def validate_mandatory_degree_education(self):
        if not self.grau_instrucao:
            raise ValidationError(
                {"grau_instrucao": "Preencha o campo Grau de Instrução."}
            )
        return True

    def validate_mandatory_civil_state(self):
        if not self.estado_civil:
            raise ValidationError({"estado_civil": "Preencha o campo Estado Civil."})
        return True

    def validate_mandatory_date_born(self):
        if not self.data_nascimento:
            raise ValidationError(
                {"data_nascimento": "Preencha o campo Data de Nascimento."}
            )
        return True

    def validate_mandatory_municipality_naturalness(self):
        if not self.municipio_naturalidade:
            raise ValidationError(
                {
                    "municipio_naturalidade": "Preencha o campo Município de Naturalidade."
                }
            )
        return True

    def validate_mandatory_nationality(self):
        if not self.nationality:
            raise ValidationError({"nationality": "Preencha o campo Nacionalidade."})
        return True

    def validate_mandatory_nis(self):
        if not self.nis and not self.pis_pasep:
            raise ValidationError(
                {"nis": "Preencha NIS ou PIS/PASEP. Um deles deve ser preenchido."}
            )
        return True

    def validate_mandatory_ctps(self):
        self.validate_mandatory_ctps_series()
        self.validate_mandatory_ctps_state()
        return True

    def validate_mandatory_ctps_number(self):
        if not self.ctps:
            raise ValidationError({"ctps": "Preencha o campo CTPS - Número."})
        return True

    def validate_mandatory_ctps_series(self):
        if self.ctps and not self.serie_ctps:
            raise ValidationError({"serie_ctps": "Preencha o campo CTPS - Série."})
        return True

    def validate_mandatory_ctps_state(self):
        if self.ctps and not self.ctps_state:
            raise ValidationError({"ctps_state": "Preencha o campo CTPS - UF"})
        return True

    def validate_mandatory_rg(self):
        self.validate_mandatory_rg_number()
        self.validate_mandatory_rg_issuer()
        self.validate_mandatory_rg_state()
        self.validate_mandatory_rg_date_expedition()
        return True

    def validate_mandatory_rg_number(self):
        if not self.rg:
            raise ValidationError({"rg": "Preencha o campo RG."})
        return True

    def validate_mandatory_rg_issuer(self):
        if not self.rg_orgao:
            raise ValidationError({"rg_orgao": "Preencha o campo RG - Emissor."})
        return True

    def validate_mandatory_rg_state(self):
        if not self.rg_uf:
            raise ValidationError({"rg_uf": "Preencha o campo RG - UF"})
        return True

    def validate_mandatory_rg_date_expedition(self):
        if not self.rg_data_expedicao:
            raise ValidationError(
                {"rg_data_expedicao": "Preencha o campo RG - Data Expedição"}
            )
        return True

    def validate_mandatory_ric(self):
        self.validate_mandatory_ric_issuer()
        return True

    def validate_mandatory_ric_issuer(self):
        if self.ric and not self.ric_issuer:
            raise ValidationError({"ric_issuer": "Preencha o campo RIC - Emissor."})
        return True

    def validate_mandatory_rne(self):
        self.validate_mandatory_rne_issuer()
        return True

    def validate_mandatory_rne_issuer(self):
        if self.rne and not self.rne_issuer:
            raise ValidationError({"rne_issuer": "Preencha o campo RNE - Emissor."})
        return True

    def validate_mandatory_cpf(self):
        if not self.cpf:
            raise ValidationError({"cpf": "Preencha o campo CPF - Número."})
        return True

    def validate_mandatory_professional_council(self):
        self.validate_mandatory_professional_council_issuer()
        self.validate_mandatory_professional_council_required()
        return True

    def validate_mandatory_professional_council_issuer(self):
        if self.professional_council and not self.professional_council_issuer:
            raise ValidationError(
                {
                    "professional_council_issuer": "Preencha o campo Conselho profissional - Emissor."
                }
            )
        return True

    def validate_mandatory_professional_council_required(self):
        if (
            not self.professional_council
            and self.employee.posses_ativas.filter(
                quadro__requires_profissional_council=True
            ).exists()
        ):
            raise ValidationError(
                {
                    "professional_council_issuer": "Conselho profissional obrigatório para seu cargo!"
                }
            )
        return True

    def validate_mandatory_cnh(self):
        self.validate_cnh_len()
        self.validate_mandatory_cnh_category()
        self.validate_mandatory_cnh_date_validity()
        self.validate_mandatory_cnh_state()
        self.validate_mandatory_cnh_job_position()
        return True

    def validate_cnh_len(self):
        if self.cnh and len(self.cnh) != Documento.cnh_max_len:
            raise ValidationError(
                {"cnh": "Para CNH o tamanho deve ser %s.' % Documento.cnh_max_le"}
            )
        return True

    def validate_mandatory_cnh_category(self):
        if self.cnh and not self.cnh_categoria:
            raise ValidationError(
                {"cnh_categoria": "Preencha o campo CNH - Categoria."}
            )
        elif self.cnh_categoria and self.cnh_categoria not in list(
            CNH_CATEGORY_TYPE.values()
        ):
            raise ValidationError(
                {"cnh_categoria": "Preencha o campo CNH - Categoria com valor válido."}
            )
        return True

    def validate_mandatory_cnh_date_validity(self):
        if self.cnh and not self.cnh_validity_date:
            raise ValidationError(
                {"cnh_validity_date": "Preencha o campo CNH - Data de validade."}
            )
        return True

    def validate_mandatory_cnh_state(self):
        if self.cnh and not self.cnh_state:
            raise ValidationError({"cnh_state": "Preencha o campo CNH - UF"})
        return True

    def validate_mandatory_cnh_job_position(self):
        if (
            not self.cnh
            and self.employee.posses_ativas.filter(
                quadro__cargo__codigo__in=["OFD", "MOT", "XXXMOT", "25c", "MOP"]
            ).exists()
        ):
            raise Exception("CNH obrigatória para o seu cargo.")
        return True

    def validate_pis_pasep(self):
        if not self.pis_pasep:
            raise ValidationError({"pis_pasep": "Preencha PIS/PASEP."})
        return True

    def validate_mandatory_voter(self):
        if not self.titulo_eleitor:
            raise ValidationError(
                {"titulo_eleitor": "Preencha o campo Títulor de Eleitor - Uf."}
            )
        self.validate_mandatory_voter_zone()
        self.validate_mandatory_voter_section()
        self.validate_mandatory_voter_city()
        self.validate_mandatory_voter_state()
        return True

    def validate_mandatory_voter_zone(self):
        if not self.zona_titulo:
            raise ValidationError(
                {"zona_titulo": "Preencha o campo Títulor de Eleitor - Zona."}
            )
        return True

    def validate_mandatory_voter_section(self):
        if not self.secao_titulo:
            raise ValidationError(
                {"secao_titulo": "Preencha o campo Títulor de Eleitor - Seção."}
            )
        return True

    def validate_mandatory_voter_city(self):
        if not self.municipio_titulo:
            raise ValidationError(
                {"municipio_titulo": "Preencha o campo Títulor de Eleitor - Município."}
            )
        return True

    def validate_mandatory_voter_state(self):
        if not self.municipio_titulo.estado:
            raise ValidationError(
                {"municipio_titulo": "Preencha o campo Títulor de Eleitor - Uf."}
            )
        return True

    def validate_exists_cpf_dependent(self, form):
        if not form.cpf_dependent:
            raise ValidationError(
                {
                    f"CPF do Dependente": f"Preencha o campo CPF do Dependente {form.dependent}."
                }
            )
        return True

    def validate_cpf_dependent(self, form):
        if not form.validate_dependent_cpf():
            raise ValidationError(
                {
                    "CPF do Dependente": f"Preencha o CPF do dependente {form.dependent} com um número válido."
                }
            )

    def validate_tipo_dependent(self, form):
        if not form.tipo:
            raise ValidationError(
                {
                    f"Tipo do Dependente": f"Preencha o campo tipo do Dependente {form.dependent}."
                }
            )

    def validate_dependents(self):
        if self.employee:
            form_informations = DependentFormInformation.objects.filter(
                employee=self.employee
            )
            for form_information in form_informations:
                if not form_information.cpf_dependent:

                    raise ValidationError(
                        {
                            f"CPF do Dependente": f"Preencha o campo CPF do Dependente {form_information.dependent}."
                        }
                    )
                else:
                    if not form_information.validate_dependent_cpf():
                        raise ValidationError(
                            {
                                "CPF do Dependente": f"Preencha o CPF do dependente {form_information.dependent} com um número válido."
                            }
                        )
                if not form_information.tipo:
                    raise ValidationError(
                        {
                            f"Tipo do Dependente": f"Preencha o campo tipo do Dependente {form_information.dependent}."
                        }
                    )
            return True

        else:
            raise Exception("Informe um servidor para verificação de seus dependentes.")

    @classmethod
    def _map_info_from_natural_person(cls):
        return {
            "nome": lambda employee: employee.pessoa_fisica.nome,
            "nome_conjuge": lambda employee: employee.pessoa_fisica.nome_conjuge,
            "nome_mae": lambda employee: employee.pessoa_fisica.nome_mae,
            "nome_pai": lambda employee: employee.pessoa_fisica.nome_pai,
            "genero": lambda employee: employee.pessoa_fisica.genero,
            "social_name": lambda employee: (
                employee.pessoa_fisica.social_name
                if employee.pessoa_fisica.social_name
                else ""
            ),
            "sexo": lambda employee: employee.pessoa_fisica.sexo,
            "sexual_orientation": lambda employee: employee.pessoa_fisica.sexual_orientation,
            "raca_cor": lambda employee: employee.pessoa_fisica.raca_cor,
            "estado_civil": lambda employee: employee.pessoa_fisica.estado_civil,
            "immigrant_residence_time": lambda employee: employee.pessoa_fisica.immigrant_residence_time,
            "immigrant_entry_condition": lambda employee: employee.pessoa_fisica.immigrant_entry_condition,
            "sangue": lambda employee: employee.pessoa_fisica.sangue,
            "fator_rh": lambda employee: employee.pessoa_fisica.fator_rh,
            "doador": lambda employee: employee.pessoa_fisica.doador,
            "municipio_naturalidade": lambda employee: employee.pessoa_fisica.municipio_naturalidade,
            "nationality": lambda employee: employee.pessoa_fisica.nationality,
            "nationality_birth": lambda employee: employee.pessoa_fisica.nationality_birth,
            "email_institucional": lambda employee: (
                employee.pessoa_fisica.email_institucional.upper()
                if employee.pessoa_fisica.email_institucional
                else ""
            ),
            "data_nascimento": lambda employee: employee.pessoa_fisica.data_nascimento,
            "cpf": lambda employee: employee.pessoa_fisica.cpf,
            "rg": lambda employee: employee.pessoa_fisica.rg,
            "foto": lambda employee: employee.pessoa_fisica.foto,
            "grau_instrucao": lambda employee: employee.pessoa_fisica.grau_instrucao,
            "rg_orgao": lambda employee: (
                employee.pessoa_fisica.rg_orgao
                if employee.pessoa_fisica.rg_orgao
                else ""
            ),
            "rg_data_expedicao": lambda employee: (
                employee.pessoa_fisica.rg_data_expedicao
                if employee.pessoa_fisica.rg_data_expedicao
                else None
            ),
            "rg_uf": lambda employee: (
                employee.pessoa_fisica.rg_uf if employee.pessoa_fisica.rg_uf else None
            ),
            "cnh": lambda employee: (
                employee.pessoa_fisica.cnh.numero if employee.pessoa_fisica.cnh else ""
            ),
            "cnh_categoria": lambda employee: (
                employee.pessoa_fisica.cnh.cnh_category.valor
                if employee.pessoa_fisica.cnh
                and employee.pessoa_fisica.cnh.cnh_category
                else ""
            ),
            "cnh_expedition_date": lambda employee: (
                employee.pessoa_fisica.cnh.data_expedicao
                if employee.pessoa_fisica.cnh
                else None
            ),
            "cnh_validity_date": lambda employee: (
                employee.pessoa_fisica.cnh.data_validade
                if employee.pessoa_fisica.cnh
                else None
            ),
            "cnh_first_date": lambda employee: (
                DateUtils.str_to_date(employee.pessoa_fisica.cnh.cnh_first_date.valor)
                if employee.pessoa_fisica.cnh
                and employee.pessoa_fisica.cnh.cnh_first_date
                else None
            ),
            "cnh_state": lambda employee: (
                employee.pessoa_fisica.cnh.estado_expedicao
                if employee.pessoa_fisica.cnh
                else None
            ),
            "ctps": lambda employee: (
                employee.pessoa_fisica.ctps.numero
                if employee.pessoa_fisica.ctps
                else ""
            ),
            "serie_ctps": lambda employee: (
                employee.pessoa_fisica.ctps.ctps_series.valor
                if employee.pessoa_fisica.ctps
                and employee.pessoa_fisica.ctps.ctps_series
                else ""
            ),
            "ctps_state": lambda employee: (
                employee.pessoa_fisica.ctps.estado_expedicao
                if employee.pessoa_fisica.ctps
                else None
            ),
            "pis_pasep": lambda employee: (
                employee.pessoa_fisica.pis_pasep.numero
                if employee.pessoa_fisica.pis_pasep
                else ""
            ),
            "reservista": lambda employee: (
                employee.pessoa_fisica.reservist.numero
                if employee.pessoa_fisica.reservist
                else ""
            ),
            "classe_reservista": lambda employee: (
                employee.pessoa_fisica.reservist.reservist_class.valor
                if employee.pessoa_fisica.reservist
                and employee.pessoa_fisica.reservist.reservist_class
                else ""
            ),
            "professional_council": lambda employee: (
                employee.pessoa_fisica.professional_council.numero
                if employee.pessoa_fisica.professional_council
                else ""
            ),
            "professional_council_state": lambda employee: (
                employee.pessoa_fisica.professional_council.estado_expedicao
                if employee.pessoa_fisica.professional_council
                else None
            ),
            "professional_council_expedition_date": lambda employee: (
                employee.pessoa_fisica.professional_council.data_expedicao
                if employee.pessoa_fisica.professional_council
                else None
            ),
            "professional_council_validity_date": lambda employee: (
                employee.pessoa_fisica.professional_council.data_validade
                if employee.pessoa_fisica.professional_council
                else None
            ),
            "professional_council_issuer": lambda employee: (
                employee.pessoa_fisica.professional_council.professional_council_issuer.valor
                if employee.pessoa_fisica.professional_council
                and employee.pessoa_fisica.professional_council.professional_council_issuer
                else ""
            ),
            "titulo_eleitor": lambda employee: (
                employee.pessoa_fisica.voter.numero
                if employee.pessoa_fisica.voter
                else ""
            ),
            "zona_titulo": lambda employee: (
                employee.pessoa_fisica.voter.voter_zone.valor
                if employee.pessoa_fisica.voter
                and employee.pessoa_fisica.voter.voter_zone
                else ""
            ),
            "secao_titulo": lambda employee: (
                employee.pessoa_fisica.voter.voter_section.valor
                if employee.pessoa_fisica.voter
                and employee.pessoa_fisica.voter.voter_section
                else ""
            ),
            "municipio_titulo": lambda employee: (
                employee.pessoa_fisica.voter.voter_city_local
                if employee.pessoa_fisica.voter
                and employee.pessoa_fisica.voter.voter_city_local
                else None
            ),
            "ric": lambda employee: (
                employee.pessoa_fisica.ric.numero if employee.pessoa_fisica.ric else ""
            ),
            "ric_issuer": lambda employee: (
                employee.pessoa_fisica.ric.ric_issuer.valor
                if employee.pessoa_fisica.ric and employee.pessoa_fisica.ric.ric_issuer
                else ""
            ),
            "ric_expedition_date": lambda employee: (
                employee.pessoa_fisica.ric.data_expedicao
                if employee.pessoa_fisica.ric
                else None
            ),
            "ric_state": lambda employee: (
                employee.pessoa_fisica.ric.estado_expedicao
                if employee.pessoa_fisica.ric
                and employee.pessoa_fisica.ric.estado_expedicao
                else None
            ),
            "rne": lambda employee: (
                employee.pessoa_fisica.rne.numero if employee.pessoa_fisica.rne else ""
            ),
            "rne_issuer": lambda employee: (
                employee.pessoa_fisica.rne.rne_issuer.valor
                if employee.pessoa_fisica.rne and employee.pessoa_fisica.rne.rne_issuer
                else ""
            ),
            "rne_expedition_date": lambda employee: (
                employee.pessoa_fisica.rne.data_expedicao
                if employee.pessoa_fisica.rne
                else None
            ),
            "rne_state": lambda employee: (
                employee.pessoa_fisica.rne.estado_expedicao
                if employee.pessoa_fisica.rne
                and employee.pessoa_fisica.rne.estado_expedicao
                else None
            ),
            "nis": lambda employee: (
                employee.pessoa_fisica.nis.numero if employee.pessoa_fisica.nis else ""
            ),
            "address_type_street": lambda employee: (
                employee.pessoa_fisica.address.last().tipo_logradouro
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().tipo_logradouro
                else None
            ),
            "address_type_address": lambda employee: (
                employee.pessoa_fisica.address.last().tipo_endereco
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().tipo_endereco
                else None
            ),
            "address_city": lambda employee: (
                employee.pessoa_fisica.address.last().municipio
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().municipio
                else None
            ),
            "address_public_place": lambda employee: (
                employee.pessoa_fisica.address.last().logradouro[:80]
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().logradouro
                else None
            ),
            "address_district": lambda employee: (
                employee.pessoa_fisica.address.last().bairro
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().bairro
                else None
            ),
            "address_zip_code": lambda employee: (
                employee.pessoa_fisica.address.last().cep[:10]
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().cep
                else None
            ),
            "address_number": lambda employee: (
                employee.pessoa_fisica.address.last().numero[:10].upper()
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().numero
                else None
            ),
            "address_complement": lambda employee: (
                employee.pessoa_fisica.address.last().complemento[:30]
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().complemento
                else ""
            ),
            "address_outsider": lambda employee: (
                employee.pessoa_fisica.address.last().outsider
                if employee.pessoa_fisica.address.last()
                else False
            ),
            "address_outsider_citty": lambda employee: (
                employee.pessoa_fisica.address.last().outsider_citty[:50]
                if employee.pessoa_fisica.address.last()
                and employee.pessoa_fisica.address.last().outsider_citty
                else ""
            ),
            "address_country": lambda employee: (
                employee.pessoa_fisica.address.last().country
                if employee.pessoa_fisica.address.last()
                else None
            ),
            "phone_main": lambda employee: (
                employee.pessoa_fisica.phone.filter(main=True)
                .exclude(tipo_telefone=TYPE_PHONE_EMERGENCY)
                .last()
                .numero[:13]
                if employee.pessoa_fisica.phone.filter(main=True)
                .exclude(tipo_telefone=TYPE_PHONE_EMERGENCY)
                .last()
                else (
                    employee.pessoa_fisica.phone.exclude(
                        tipo_telefone=TYPE_PHONE_EMERGENCY
                    )
                    .last()
                    .numero[:13]
                    if employee.pessoa_fisica.phone.exclude(
                        tipo_telefone=TYPE_PHONE_EMERGENCY
                    ).last()
                    else None
                )
            ),
            "contact_emergency_name": lambda employee: (
                employee.pessoa_fisica.phone.filter(tipo_telefone=TYPE_PHONE_EMERGENCY)
                .last()
                .description
                if employee.pessoa_fisica.phone.filter(
                    tipo_telefone=TYPE_PHONE_EMERGENCY
                ).last()
                else None
            ),
            "contact_emergency_phone": lambda employee: (
                employee.pessoa_fisica.phone.filter(tipo_telefone=TYPE_PHONE_EMERGENCY)
                .last()
                .numero[:13]
                if employee.pessoa_fisica.phone.filter(
                    tipo_telefone=TYPE_PHONE_EMERGENCY
                ).last()
                else None
            ),
            "contact_emergency_phone_kinship": lambda employee: (
                employee.pessoa_fisica.phone.filter(tipo_telefone=TYPE_PHONE_EMERGENCY)
                .last()
                .kinship
                if employee.pessoa_fisica.phone.filter(
                    tipo_telefone=TYPE_PHONE_EMERGENCY
                ).last()
                else None
            ),
            "grau_instrucao": lambda employee: (
                employee.pessoa_fisica.grau_instrucao
                if employee.pessoa_fisica.grau_instrucao
                else None
            ),
        }

    @classmethod
    def load_info_employee(cls, employee=None, exclude_fields=[]):
        FormInformation.command_load_info_employee(
            employee=employee, exclude_fields=exclude_fields
        )

    @classmethod
    def command_load_info_employee(
        cls, employee=None, exclude_fields=[], all_employee=False
    ):
        map_info = FormInformation._map_info_from_natural_person()
        user = get_current_user()
        if all_employee:
            employees = Servidor.objects.filter(ativo=True)
        if employee:
            employees = Servidor.objects.filter(pk=employee.pk)
        if not employee and all_employee is False:
            raise Exception("Informe um servidor ou envie True em all_employee.")
        for emp in employees:
            form_information = FormInformation.objects.filter(employee=emp)
            if form_information.exists():
                form_information = form_information.last()
            if not form_information:
                form_information = FormInformation()
                form_information.employee = emp

            form_information.sent_by = (
                user if not form_information.sent_by else form_information.sent_by
            )
            form_information.state = (
                STATE_EMPLOYEE_EDITION
                if not form_information.pk
                else form_information.state
            )

            for field_name in list(map_info.keys()):
                if field_name not in exclude_fields:
                    field_diff = "%s_diff" % field_name
                    field_value = map_info.get(field_name)(emp)
                    setattr(form_information, field_name, field_value)
                    setattr(form_information, field_diff, False)
            form_information.save(do_diff_fields=False, do_validate=False)

    def extract_field_value(self, key, employee):
        try:
            return FormInformation._map_info_from_natural_person().get(key)(employee)
        except Exception as err:
            log.info(key)
            log.info(employee)
            log.exception(err)
        return None

    def extract_querydict_natural_person(self, valid_fields):
        querydict = {}
        try:
            for field in self._meta.get_fields():
                if (
                    hasattr(self, field.name)
                    and field.name.find("_diff") < 0
                    and field.name.find("_edit") < 0
                    and field.name.find("_required") < 0
                ):
                    value = self.extract_field_value(field.name, self.employee)

                    if field.name in valid_fields:
                        value = getattr(self, field.name)

                    try:
                        _type = field.get_internal_type()
                    except Exception:
                        _type = field.__class__.__name__
                    if _type in ["ForeignKey", "OneToOneField"]:
                        if not value:
                            value = None
                        else:
                            value = value.pk
                    elif _type == "DateTimeField":
                        value = DateUtils.datetime_to_str(value) if value else None
                    elif _type == "DateField":
                        value = DateUtils.date_to_str(value) if value else None
                    elif _type == "ManyToManyField":
                        value = querydict.getlist(value)
                    elif _type in [
                        "IntegerField",
                        "PositiveIntegerField",
                        "PositiveSmallIntegerField",
                        "SmallIntegerField",
                    ]:
                        value = int(value) if value not in ("", None) else None
                    elif _type == "DecimalField":
                        value = float(value) if value not in ("", None) else None
                    elif _type == "BooleanField":
                        if value in ("", "off", "OFF", None, 0, False, "FALSE"):
                            value = False
                        elif not isinstance(value, bool) and value.lower() in (
                            "on",
                            "true",
                        ):
                            value = True
                    querydict.update({field.name: value})
        except Exception as err:
            log.exception(err)
        return querydict

    def pendency(self):
        key_value_err = []
        pendency = ""
        try:
            self.clean_all_validate()
        except ValidationError as err:
            items = dict(list(err.message_dict.items()))
            keys = list(items.keys())
            sorted(keys)
            for key in keys:
                value = items.get(key)
                pendency_err = ""
                if not isinstance(value, (dict, list)):
                    value = [value]
                key_value_err.append({"field": key, "values": value})
                for v in value:
                    pendency_err += "<br>%s" % v
                if pendency_err:
                    pendency += "<br>%s" % pendency_err
        return pendency, key_value_err

    def change_active(self):
        """Este método modifica active para True ou False."""
        self.active = not self.active
        self.save()


class DependentFormInformation(FormInformationBase):

    dependent = models.ForeignKey(
        Dependente, verbose_name="Dependente", on_delete=models.CASCADE
    )

    cpf_dependent_can_edit = models.BooleanField(default=True, blank=True)
    cpf_dependent = models.CharField(
        max_length=14, null=True, blank=True, verbose_name="CPF"
    )
    cpf_dependent_doc_digital_required = models.BooleanField(default=True, blank=True)
    cpf_dependent_diff = models.BooleanField(default=False, blank=True)

    data_inicio_dependent_can_edit = models.BooleanField(default=True, blank=True)
    data_inicio_dependent = models.DateField(
        null=True, blank=True, verbose_name="Data de Início"
    )
    data_inicio_dependent_diff = models.BooleanField(default=False, blank=True)

    data_nascimento_dependent_can_edit = models.BooleanField(default=True, blank=True)
    data_nascimento_dependent = models.DateField(
        null=True, blank=True, verbose_name="Data de Nascimento"
    )
    data_nascimento_dependent_diff = models.BooleanField(default=False, blank=True)

    grau_parentesco_can_edit = models.BooleanField(default=True, blank=True)
    grau_parentesco = models.IntegerField(
        choices=Choice.get_choices_for("rh", "GRAU_PARENTESCO_CHOICES"),
        verbose_name="Grau de Parentesco",
        null=True,
        blank=True,
    )
    grau_parentesco_diff = models.BooleanField(default=False, blank=True)

    nome_dependent_can_edit = models.BooleanField(default=True, blank=True)
    nome_dependent = models.CharField(
        max_length=100, verbose_name="Nome", default="", null=True, blank=True
    )
    nome_dependent_diff = models.BooleanField(default=False, blank=True)
    nome_dependent_doc_digital_required = models.BooleanField(default=True, blank=True)

    sexo_dependent_can_edit = models.BooleanField(default=True, blank=True)
    sexo_dependent = models.CharField(
        max_length=1, choices=SEXO_CHOICES, null=True, blank=True, verbose_name="Sexo"
    )
    sexo_dependent_diff = models.BooleanField(default=False, blank=True)

    tipo_can_edit = models.BooleanField(default=True, blank=True)
    tipo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEPENDENT_TYPE"),
        null=True,
        blank=True,
        verbose_name="Tipo de Dependete",
    )
    tipo_diff = models.BooleanField(default=False, blank=True)

    incapacity_can_edit = models.BooleanField(default=True, blank=True)
    incapacity = models.BooleanField(
        default=False, blank=True, verbose_name="Incapacidade física/mental"
    )
    incapacity_diff = models.BooleanField(default=False, blank=True)
    incapacity_doc_digital_required = models.BooleanField(default=True, blank=True)

    @property
    def dependency(self):
        return (
            Dependencia.objects.filter(dependente=self.dependent)
            .irrf_actives(self.employee, datetime.datetime.now())
            .last()
        )

    def __str__(self):
        return "Recadastramento de %s" % self.dependent

    @classmethod
    def _map_info_from_natural_person_to_dependent(cls):
        """
        Função que mapeia as informações de um model rh/Dependente clonando para a classe super, dicionarizando somente as informações necessárias ao envio do Esocial S-2200

        :return: Dicionário contendo como key os campos da classe e como value o valor correspondente da dependent clonado
        :rtype: dict
        """
        return {
            "nome_dependent": lambda dependent: dependent.pessoa_fisica.social_name,
            "cpf_dependent": lambda dependent: dependent.pessoa_fisica.cpf,
            "data_nascimento_dependent": lambda dependent: dependent.pessoa_fisica.data_nascimento,
            "sexo_dependent": lambda dependent: dependent.pessoa_fisica.sexo,
            "grau_parentesco": lambda dependent: dependent.grau_parentesco,
            "incapacity": lambda dependent: dependent.incapacity,
            "tipo": lambda dependent: dependent.tipo,
        }

    @classmethod
    def load_info_dependent(cls, employee=None, exclude_fields=[]):
        FormInformation.command_load_info_employee(
            employee=employee, exclude_fields=exclude_fields
        )

    @classmethod
    def command_load_info_dependent(cls, employee, exclude_fields=[]):
        try:
            map_info = (
                DependentFormInformation._map_info_from_natural_person_to_dependent()
            )
            user = get_current_user()
            if employee:
                dependencies = Dependencia.objects.filter(
                    tipo=1, suspenso=False
                ).irrf_actives(employee, datetime.datetime.now())
            if not employee:
                raise Exception(
                    "Informe um servidor para verificação de seus dependentes."
                )
            for dependency in dependencies:
                try:
                    form_information = DependentFormInformation.objects.filter(
                        dependent=dependency.dependente
                    )
                    if form_information.exists():
                        form_information = form_information.last()

                    if not form_information:
                        form_information = DependentFormInformation()
                        form_information.dependent = dependency.dependente
                        form_information.employee = employee

                    form_information.sent_by = (
                        user
                        if not form_information.sent_by
                        else form_information.sent_by
                    )
                    form_information.state = (
                        STATE_EMPLOYEE_EDITION
                        if not form_information.pk
                        else form_information.state
                    )

                    for field_name in list(map_info.keys()):
                        if field_name not in exclude_fields:
                            field_diff = "%s_diff" % field_name
                            field_value = map_info.get(field_name)(
                                dependency.dependente
                            )
                            setattr(form_information, field_name, field_value)
                            setattr(form_information, field_diff, False)
                    form_information.save()
                except Exception as e:
                    log.error(
                        f"Ao importar o Formulário do dependente {dependency.dependente}"
                    )
                    log.error(e)
        except Exception as e:
            log.error(
                "Ao importar Fomulário de Atualização de Dependentes ocorreu o seguinte erro"
            )
            log.error(e)

    def validate_dependent_cpf(self):
        """Validação para o campo de cpf do dependente.

        :return: Retorna True se o cpf é válido ou False caso não.
        :rtype: bool
        """
        if len(self.cpf_dependent) < 11:
            return False

        if self.cpf_dependent in [s * 11 for s in [str(n) for n in range(10)]]:
            return False

        calc = lambda i: int(i[1]) * (i[0] + 2)
        d1 = (sum(map(calc, enumerate(reversed(self.cpf_dependent[:-2])))) * 10) % 11
        d2 = (sum(map(calc, enumerate(reversed(self.cpf_dependent[:-1])))) * 10) % 11
        if d1 == 10:
            d1 = 0
        if d2 == 10:
            d2 = 0
        return (d1 == int(self.cpf_dependent[9]) or d1 == 10) and d2 == int(
            self.cpf_dependent[10]
        )

    def save(self, *args, **kargs):
        employee_try_change = employee_from_user(get_current_user())
        if self.employee == employee_try_change:
            self.state = STATE_EMPLOYEE_EDITION

        self.validate_transition_state(self.state)

        self.created_by = get_current_user()
        if self.dependency:
            if not self.data_inicio_dependent:
                self.data_inicio_dependent = self.dependency.data_inicio
        if self.pk:
            if not self.validate_dependent_cpf():
                raise Exception("Preencha o campo CPF com um número válido.")

        try:
            super(DependentFormInformation, self).save(*args, **kargs)
            return self
        except Exception as err:
            log.exception(err)


class Validation(AuditTimestampModel):
    form_information = models.ForeignKey(
        FormInformation, on_delete=models.PROTECT, related_name="validations"
    )
    text = models.TextField(null=True, blank=True)
    state = models.IntegerField(
        verbose_name="Estado",
        default=STATE_EMPLOYEE_VALIDATED,
        blank=True,
        choices=Choice.get_choices_for("registration", "VALIDATION_STATE"),
    )
    annotation = models.ForeignKey(
        AnotacaoGeral, on_delete=models.PROTECT, null=True, blank=True
    )

    validated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    validated_at = models.DateTimeField(default=None, null=True, blank=True)
    fi_sent_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    fi_sent_at = models.DateTimeField(default=None, null=True, blank=True)
    fi_received_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    fi_received_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = "Validação de Recadastramento Funcional"
        ordering = ("-created_at",)

    def __str__(self):
        return "Validação de %s" % self.form_information.employee

    def _set_validate_form_information(self):
        FormInformation.objects.filter(pk=self.form_information.pk).update(
            validated_by=self.validated_by, validated_at=self.validated_at
        )

    def validate(self):
        return True

    def save(self, *args, **kargs):
        self.validate()
        form_information_data = kargs.pop("form_information_data", {})
        self.annotate(form_information_data)
        if not self.pk:
            self.validated_by = get_current_user()
            self.validated_at = datetime.datetime.now()
            self.fi_sent_by = self.form_information.sent_by
            self.fi_sent_at = self.form_information.sent_at
            self.fi_received_by = self.form_information.received_by
            self.fi_received_at = self.form_information.received_at
        super(Validation, self).save(*args, **kargs)
        self._set_validate_form_information()

    def annotate(self, form_information_data):
        anotacao_geral = AnotacaoGeral()
        anotacao_geral.servidor = self.form_information.employee
        anotacao_geral.data_portaria_inicio = self.created_at
        anotacao_geral.resumo = "RECADASTRAMENTO FUNCIONAL"
        anotacao_geral.texto = self.text
        anotacao_geral.save()


class DigitalDocument(AuditTimestampModel):
    form_information = models.ForeignKey(
        FormInformation,
        related_name="digital_documents",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    document_type = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DIGITAL_DOCUMENT_TYPE"),
        verbose_name="Tipo de Documento",
    )
    file = models.ForeignKey(
        "ged.Arquivo",
        null=True,
        blank=True,
        verbose_name="Arquivo",
        on_delete=models.CASCADE,
    )
    state = models.IntegerField(
        choices=Choice.get_choices_for("registration", "DIGITAL_DOCUMENT_STATE"),
        verbose_name="Estado de processamento",
        default=NOT_PROCESSED,
    )

    def __str__(self):
        return "%s - %s" % (
            self.form_information.employee,
            self.get_document_type_display(),
        )

    @property
    def icone(self):
        related = {
            "application/pdf": "archive-pdf",
            "image/jpeg": "archive-image",
            "image/jpg": "archive-image",
            "image/png": "archive-image",
            "image/gif": "archive-image",
            "image/tiff": "archive-image",
            "text/plain": "archive-document",
            "application/vnd.oasis.opendocument.text": "archive-document",
            "application/msword": "archive-document",
            "application/vnd.oasis.opendocument.spreadsheet": "archive-planilha",
            "application/msexcel": "archive-planilha",
            "application/msexcel": "archive-planilha",
            "application/vnd.oasis.opendocument.presentation": "archive-impress",
        }

        return [
            {
                "iconCls": "icon-diarias icon-%s"
                % related.get(self.file.mimetype, "archive"),
            }
        ]


def report_script():
    for fi in FormInformation.objects.filter(employee__ativo=True).order_by(
        "employee__pessoa_fisica__nome"
    ):
        validation_state = "NUNCA VALIDADO"
        validated_at = ""
        if fi.validation_set.exists():
            validation = fi.validation_set.latest("validated_at")
            validation_state = validation.get_state_display()
            validated_at = DateUtils.datetime_to_str(validation.validated_at)
        print(str(fi.employee)).replace(
            ":", "|"
        ), "|", fi.employee.get_tipo_display(), "|", fi.get_state_display(), "|", validation_state, "|", validated_at
