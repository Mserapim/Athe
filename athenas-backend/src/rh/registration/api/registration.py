# -*- coding: utf-8 -*-

import datetime
import json
import zipfile
from functools import partial
from io import BytesIO

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http.request import QueryDict

from contrib.controller import ContentType, DefaultController
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import DateUtils, employee_from_user, getLogger
from engine.notification.models import Notification
from ged.models import Arquivo
from rh import models as rh_models
from rh.api.employee import RHEmployeeSpecialized
from rh.const import (
    NOT_VALIDITY,
    PROCESSED,
    STABLE_BONDING,
    TYPE_PHONE_EMERGENCY,
    TYPE_PHONE_HOME,
)
from rh.registration.models import (
    STATE_DGPFP_RECEIVED,
    STATE_DGPFP_SENT,
    STATE_EMPLOYEE_EDITION,
    STATE_EMPLOYEE_VALIDATED,
    STATE_EMPLOYEE_VALIDATED_PROBLEM,
    DigitalDocument,
    DependentFormInformation,
    FormInformation,
    Validation,
)
from standard.models import Choice

log = getLogger(__name__)


class RegistrationFormInformationBase(RestfulDRY):

    _model = FormInformation

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
    )

    @login_required("JSON")
    def foto_resizelink(self, args=[]):
        rst = {
            "success": False,
            "message": "Não foi executado nada ainda.",
            "foto_link": "",
        }
        try:
            params = self.get_params(self.request.POST, check_case=True)
            pk = params.get("pk", None)
            if pk:
                rst.update(
                    {"foto_link": Arquivo.objects.get(pk=pk).resizelink((85, 113))}
                )
            rst["success"] = True
            rst["message"] = "Sucesso."
        except Exception as err:
            log.exception(err)
            rst["message"] = err

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def model_to_dict(self, instance):
        rst = super(RegistrationFormInformationBase, self).model_to_dict(instance)
        validation = Validation.objects.filter(form_information__pk=instance.pk)
        last_validation_text = ""
        if validation.exists():
            validation = validation.latest("created_at")
            last_validation_text = (
                "<p><b>Validado por:</b> %s</p> <p><b>Validado em:</b> %s</p><br>%s"
                % (
                    employee_from_user(validation.created_by),
                    DateUtils.datetime_to_str(validation.created_at),
                    validation.text,
                )
            )
        rst.update(description=instance.description)
        rst.update(
            foto_link=instance.foto.resizelink((85, 113)) if instance.foto else "",
            icons=[
                {
                    "iconCls": self.set_icons(instance.state),
                    "title": instance.get_state_display(),
                },
                {
                    "iconCls": (
                        "icon-registration icon-published"
                        if instance.active
                        else "icon-registration icon-no-published"
                    ),
                    "title": "Ativo" if instance.active else "Inativo",
                },
            ],
            current_user=get_current_user().pk,
            last_validation_text=last_validation_text,
        )
        pendency = ""
        key_value_err = []
        from_grid = self.request.GET.get("from_grid")
        if not from_grid:
            pendency, key_value_err = instance.pendency()

        rst.update(pendency=pendency)
        rst.update(pendency_errors=json.dumps(key_value_err))
        rst.update(pendency_errors_total=len(key_value_err))

        return rst

    def set_icons(self, state):
        parse = {
            STATE_EMPLOYEE_EDITION: "icon-core icon-core-edit",
            STATE_EMPLOYEE_VALIDATED_PROBLEM: "icon-core icon-core-error",
            STATE_EMPLOYEE_VALIDATED: "icon-core icon-core-success",
            STATE_DGPFP_SENT: "icon-core icon-core-waiting",
            STATE_DGPFP_RECEIVED: "icon-core icon-core-refresh",
        }
        return parse.get(state)

    def get_attachment(self, args=[]):
        obj = {"count": 0, "collectionc": [], "success": False}

        try:
            base = None

            if "form" in self.request.GET:
                base = FormInformation.objects.get(pk=self.request.GET.get("form"))
        except FormInformation.DoesNotExist as err:
            log.exception(err)
            obj.update(message="Formulário não encontrado.")
        else:
            digital_documents = base.digital_documents.filter().exclude(state=PROCESSED)
            obj.update(
                {
                    "count": digital_documents.count(),
                    "collection": [
                        {
                            "pk": anexo.pk,
                            "icone": anexo.icone,
                            "document_type": anexo.document_type,
                            "document_type_display": Choice.objects.get(
                                app_label="rh",
                                name="DIGITAL_DOCUMENT_TYPE",
                                value=anexo.document_type,
                            ).label,
                            "state": anexo.state,
                            "state_display": Choice.objects.get(
                                app_label="registration",
                                name="DIGITAL_DOCUMENT_STATE",
                                value=anexo.state,
                            ).label,
                            "file": anexo.file.pk,
                            "permalink": anexo.file.permalink(),
                            "created_by": str(employee_from_user(anexo.created_by)),
                        }
                        for anexo in digital_documents
                    ],
                    "success": True,
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    @ContentType("application/zip")
    def download_attachment(self, args=[]):
        try:
            documents = []

            if "pks" in self.request.GET:
                pks = self.request.GET.get("pks").split(",")
                documents = DigitalDocument.objects.filter(pk__in=pks)

            related = {
                "application/pdf": "pdf",
                "image/jpeg": "jpeg",
                "image/jpg": "jpg",
                "image/png": "png",
                "image/gif": "gif",
                "image/tiff": "tiff",
            }

            buff_file = BytesIO()
            buff_zipfile = zipfile.ZipFile(buff_file, "w")

            for doc in documents:
                document_type = Choice.objects.get(
                    app_label="rh",
                    name="DIGITAL_DOCUMENT_TYPE",
                    value=doc.document_type,
                ).label
                filename = "%s_%s.%s" % (
                    document_type,
                    str(doc.pk),
                    related.get(doc.file.mimetype),
                )
                buff_zipfile.write(doc.file.absolute_path, filename)
            buff_zipfile.close()

            self.response["Content-Type"] = "application/x-zip"
            self.response["content-disposition"] = 'attachment; filename="download.zip"'

            buff_file.seek(0)
            for chunk in iter(partial(buff_file.read, 8192), b""):
                self.response.write(chunk)

        except DigitalDocument.DoesNotExist as err:
            log.exception(err)

    def get_query(self):
        query = super(RegistrationFormInformationBase, self).get_query()
        return query.filter(employee__ativo=True)

    def change_active(self, args=[]):
        """Este método modifica active para True ou False."""
        obj = {"success": True}
        try:
            for form_information in FormInformation.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            ):
                form_information.change_active()
        except Exception as e:
            obj.update({"success": False, "message": "{}".format(e.args[0])})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))


class RegistrationFormInformation(RegistrationFormInformationBase):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.registration.forminformation.Manage")')

    def get_query(self):
        query = super(RegistrationFormInformation, self).get_query()
        user = employee_from_user(get_current_user())
        query = query.filter(employee=user)
        return query

    def send_validation(self, args=[]):
        obj = {
            "success": False,
            "message": "Não foram encontradas modificações no formulário.",
        }
        try:
            form_information = FormInformation.objects.get(
                pk=self.request.POST.get("form_information")
            )
            # form_information.save()
            form_information.send_validation()
            obj.update(
                {"message": "Formulário enviado para validação.", "success": True}
            )
        except Exception as err:
            obj.update({"message": "%s" % err})
            log.exception(err)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def undo_send_validation(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        try:
            form_information = FormInformation.objects.get(
                pk=self.request.POST.get("form")
            )
            form_information.undo_send_validation()
            obj.update({"message": "", "success": True})
        except Exception as err:
            obj.update({"message": "%s" % err})
            log.exception(err)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def remove_attachment(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        query = DigitalDocument.objects.filter(
            Q(pk__in=self.request.POST.getlist("pk"))
        )

        if query.count() > 0:
            query.filter().delete()
            obj.update(success=True)
        else:
            obj.update(
                {"success": False, "message": "Não foi possível remover o documento."}
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def update_attachment(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            anexo = DigitalDocument.objects.get(pk=self.request.POST.get("pk"))
            arquivo = Arquivo.objects.get(pk=self.request.POST.get("file"))
        except DigitalDocument.DoesNotExist as e:
            log.exception(e)
            obj.update(message="Anexo não encontrado, ou não pode mais ser modificado.")
        except Arquivo.DoesNotExist as e:
            log.exception(e)
            obj.update(message="Arquivo não encontrado.")
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e.args[0]))
        else:
            try:
                anexo.document_type = self.request.POST.get("document_type")
                anexo.file = arquivo
                anexo.save()
            except Exception as e:
                log.exception(e)
                obj.update(message="{}".format(e.args[0]))
            else:
                obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def create_attachment(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            base = None
            if "form" in self.request.POST:
                base = FormInformation.objects.get(
                    Q(pk=self.request.POST.get("form")),
                )
            arq = Arquivo.objects.get(pk=self.request.POST.get("file"))
        except FormInformation.DoesNotExist:
            obj.update(
                message="Formulário não encontrado, ou fora do momento de modificação."
            )
        except Arquivo.DoesNotExist:
            obj.update(message="Arquivo não encontrada.")
        except Exception as e:
            obj.update(message="{}".format(e.args[0]))
        else:
            try:
                base.digital_documents.add(
                    DigitalDocument(
                        document_type=self.request.POST.get("document_type"), file=arq
                    ),
                    bulk=False,
                )
            except Exception as e:
                obj.update(message="{}".format(e.args[0]))
                log.exception(e)
            else:
                obj.update(success=True)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))


class RegistrationFormInformationAdmin(RegistrationFormInformationBase):

    full_text_index = () + RegistrationFormInformationBase.full_text_index

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.registration.forminformation.admin.Manage", {current_user: "%s"})'
            % get_current_user().pk
        )

    def receive_information(self, args=[]):
        obj = {"success": True}
        try:
            for form_information in FormInformation.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            ):
                form_information.transition_state(STATE_DGPFP_RECEIVED)
        except Exception as e:
            obj.update({"success": False, "message": "{}".format(e.args[0])})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    @login_required(type="JSON")
    def perform_validation(self, args=[]):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        try:
            if can is False:
                rst.update(
                    message="Você não tem permissão para validar %s."
                    % self.Model._meta.object_name
                )
            else:
                self._perform_validation()
        except ValidationError as e:
            rst.update(
                errors=[
                    {"field": key, "values": value}
                    for key, value in list(e.message_dict.items())
                ],
                message="Alguns campos não foram preenchidos corretamente.",
            )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
            log.exception(e)
        else:
            rst.update(
                {
                    "success": True,
                    "message": "Dados persistidos com sucesso.",
                }
            )
        self.response["content-type"] = "text/json"
        self.response.write(json.dumps(rst))

    @login_required(type="JSON")
    def _perform_validation(self, args=[]):
        obj = {"errors": {}}
        message_err = "Não foi possível gravar as informações!"
        message_err += "<br>Verifique os erros e solicite correção."
        message_err += (
            "<br>Comunique o DMTI apenas em casos onde a mensagem não for clara."
        )
        done = False

        querydict_request = None
        querydict_request = (
            querydict_request
            if querydict_request is not None
            else getattr(self.request, "POST", QueryDict("", False))
        )
        data = json.loads(self.request.POST.get("data"))
        form_information = FormInformation.objects.get(pk=data.get("form"))
        natural_person = form_information.employee.pessoa_fisica

        querydict = form_information.extract_querydict_natural_person(
            data.get("valid_fields")
        )

        exclude_fields = []
        for key in list(form_information._map_info_from_natural_person().keys()):
            field_diff = "%s_diff" % key
            if (
                key not in data.get("valid_fields")
                and hasattr(form_information, field_diff)
                and getattr(form_information, field_diff)
            ):
                exclude_fields.append(key)

        obj_naturalperson = {"errors": {}}
        obj_document = {"errors": {}}

        try:
            with transaction.atomic():
                natural_person, obj_naturalperson = (
                    RHEmployeeSpecialized._save_natural_person_employee(
                        natural_person, querydict
                    )
                )
                natural_person.clean_fields()
                natural_person.clean()
                obj_document = RHEmployeeSpecialized._save_document(
                    natural_person, querydict
                )
                RegistrationFormInformationAdmin._save_digital_document(
                    form_information, data
                )
                RegistrationFormInformationAdmin._save_address(form_information, data)
                RegistrationFormInformationAdmin._save_phones(form_information, data)
                RegistrationFormInformationAdmin._set_date_stable_union(
                    form_information, data
                )

                RHEmployeeSpecialized._concat_obj(obj, obj_naturalperson)
                RHEmployeeSpecialized._concat_obj(obj, obj_document)

                RegistrationFormInformationAdmin.do_raise(obj)

                done = True
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"err_finish_persistence": message_err}
            )
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"err_finish_persistence": message_err}
            )
            RHEmployeeSpecialized._concat_validation_error(obj, {"err": err})

        DigitalDocument.objects.filter(form_information=form_information).exclude(
            state=PROCESSED
        ).update(state=NOT_VALIDITY)

        if (
            form_information.digital_documents.filter(state=NOT_VALIDITY)
            .exclude(pk__in=data.get("digital_documents"))
            .exists()
        ):
            exclude_fields.append("digital_documents")

        state = STATE_EMPLOYEE_VALIDATED
        if len(exclude_fields) > 0:
            state = STATE_EMPLOYEE_VALIDATED_PROBLEM

        obj = self._finish_validation(form_information, data, obj, done, state)

        if "err_finish_persistence" not in list(obj.get("errors").keys()):
            FormInformation.load_info_employee(
                employee=form_information.employee, exclude_fields=exclude_fields
            )
            form_information.transition_state(state)
            self._exclude_digital_documents(form_information, data)

        RegistrationFormInformationAdmin.do_raise(obj)

    @classmethod
    def do_raise(cls, obj={}):
        validation_error = {}
        errors = dict(obj.get("errors", {}))
        for key in errors:
            validation_error.update({key: errors.get(key)})
        if validation_error:
            raise ValidationError(validation_error)

    def _exclude_digital_documents(self, form_information, data):
        if data.get("digital_documents"):
            form_information.digital_documents.filter(
                pk__in=data.get("digital_documents")
            ).update(state=PROCESSED)

    @classmethod
    def _save_digital_document(cls, form_information, data):
        date_now = datetime.datetime.now()
        if data.get("digital_documents"):
            digital_documents = form_information.digital_documents.filter(
                pk__in=data.get("digital_documents")
            )
            for dd in digital_documents:
                document = form_information.employee.pessoa_fisica.documento.filter(
                    tipo_documento=dd.document_type
                )
                if document.exists():
                    document = document.last()
                    doc = rh_models.DigitalDocumentNaturalPerson()
                    doc.name = Choice.objects.get(
                        app_label="rh",
                        name="DIGITAL_DOCUMENT_TYPE",
                        value=dd.document_type,
                    ).label
                    doc.employee = form_information.employee
                    doc.file = dd.file
                    doc.document_type = dd.document_type
                    doc.document_natural_person = document
                    rh_models.DigitalDocumentNaturalPerson.objects.filter(
                        employee=form_information.employee,
                        document_type=doc.document_type,
                        modified_at__lt=date_now,
                        date_end=None,
                    ).update(date_end=date_now.date())
                else:
                    doc = rh_models.DigitalDocument()
                    doc.name = Choice.objects.get(
                        app_label="rh",
                        name="DIGITAL_DOCUMENT_TYPE",
                        value=dd.document_type,
                    ).label
                    doc.employee = form_information.employee
                    doc.file = dd.file
                    doc.document_type = dd.document_type
                    rh_models.DigitalDocument.objects.filter(
                        employee=form_information.employee,
                        document_type=doc.document_type,
                        modified_at__lt=date_now,
                        date_end=None,
                    ).update(date_end=date_now.date())
                doc.save()
            digital_documents.update(state=PROCESSED)

    @classmethod
    def _save_address(cls, form_information, data):
        data = data.get("valid_fields") if data.get("valid_fields") else []
        address_fields = [
            "address_type_street",
            "address_type_address",
            "address_city",
            "address_public_place",
            "address_district",
            "address_zip_code",
            "address_number",
            "address_complement",
            "address_outsider",
            "address_country",
            "address_outsider_citty",
        ]

        change = False
        for add in address_fields:
            if add in data:
                change = True
                break

        if change:
            address = None
            if not form_information.address_new:
                address = rh_models.Endereco.objects.filter(
                    person=form_information.employee.pessoa_fisica
                ).last()
            if not address:
                address = rh_models.Endereco(
                    person=form_information.employee.pessoa_fisica
                )

            if "address_type_street" in data or not address.pk:
                address.tipo_logradouro = form_information.address_type_street

            if "address_type_address" in data or not address.pk:
                address.tipo_endereco = form_information.address_type_address

            if "address_city" in data or not address.pk:
                address.municipio = form_information.address_city

            if "address_public_place" in data or not address.pk:
                address.logradouro = form_information.address_public_place

            if "address_district" in data or not address.pk:
                address.bairro = form_information.address_district

            if "address_zip_code" in data or not address.pk:
                address.cep = form_information.address_zip_code

            if "address_number" in data or not address.pk:
                address.numero = form_information.address_number

            if "address_complement" in data or not address.pk:
                address.complemento = form_information.address_complement

            if "address_outsider" in data or not address.pk:
                address.outsider = form_information.address_outsider

            if "address_country" in data or not address.pk:
                address.country = form_information.address_country

            if "address_outsider_citty" in data or not address.pk:
                address.outsider_citty = form_information.address_outsider_citty

            address.save()
            FormInformation.objects.filter(pk=form_information.pk).update(
                address_new=False
            )

    @classmethod
    def _set_date_stable_union(cls, form_information, data):
        data = data.get("valid_fields", [])
        if "uniao_estavel" in data:
            if not form_information.uniao_estavel:
                try:
                    rh_models.DigitalDocument.objects.filter(
                        employee=form_information.employee,
                        document_type=STABLE_BONDING,
                        date_end=None,
                    ).update(date_end=datetime.datetime.now())
                    rh_models.Documento.objects.filter(
                        naturalpersons=form_information.employee.pessoa_fisica,
                        tipo_documento=STABLE_BONDING,
                        data_validade=None,
                    ).update(data_validade=datetime.datetime.now())
                except Exception as err:
                    log.exception(err)

    @classmethod
    def _save_phones(cls, form_information, data):
        data = data.get("valid_fields", [])
        if "phone_main" in data:
            phone = rh_models.Telefone.objects.filter(
                person=form_information.employee.pessoa_fisica, main=True
            ).last()
            if not phone:
                phone = (
                    rh_models.Telefone.objects.filter(
                        person=form_information.employee.pessoa_fisica
                    )
                    .exclude(tipo_telefone=TYPE_PHONE_EMERGENCY)
                    .last()
                )
            if not phone:
                phone = rh_models.Telefone(
                    person=form_information.employee.pessoa_fisica,
                    tipo_telefone=TYPE_PHONE_HOME,
                )
            phone.main = True
            phone.numero = form_information.phone_main
            phone.save()

        if (
            "contact_emergency_name" in data
            or "contact_emergency_phone" in data
            or "contact_emergency_phone_kinship" in data
        ):
            emergency_phone = rh_models.Telefone.objects.filter(
                person=form_information.employee.pessoa_fisica,
                tipo_telefone=TYPE_PHONE_EMERGENCY,
            ).last()
            if not emergency_phone:
                emergency_phone = rh_models.Telefone(
                    person=form_information.employee.pessoa_fisica,
                    tipo_telefone=TYPE_PHONE_EMERGENCY,
                )
            if "contact_emergency_name" in data:
                emergency_phone.description = form_information.contact_emergency_name
            if "contact_emergency_phone" in data:
                emergency_phone.numero = form_information.contact_emergency_phone
            if "contact_emergency_phone_kinship" in data:
                emergency_phone.kinship = (
                    form_information.contact_emergency_phone_kinship
                )
            emergency_phone.save()

    def _finish_validation(self, form_information, data, obj, done_persistence, state):
        message = "Dados não foram gravados!"
        if done_persistence:
            message = "Dados gravados com sucesso!"
        if data.get("confirm_validation", False) or done_persistence:
            try:
                self._do_validation(form_information, data, state)
                message += "<br>Validação gravada com sucesso!"
                self._do_notification(form_information, data)
                message += "<br>Notificação enviada com sucesso!"
                obj.update({"errors": {}})
            except ValidationError as err:
                log.exception(err)
                message += "<br>%s<br> Contate o DMTI. Horário: %s." % (
                    err,
                    DateUtils.datetime_to_str(datetime.datetime.now()),
                )
                RHEmployeeSpecialized._concat_validation_error(
                    obj, {"err_finish_validation": message}
                )
                RHEmployeeSpecialized._concat_validation_error(obj, err)
            except Exception as err:
                log.exception(err)
                message += "<br>%s<br> Contate o DMTI. Horário: %s." % (
                    err,
                    DateUtils.datetime_to_str(datetime.datetime.now()),
                )
                RHEmployeeSpecialized._concat_validation_error(
                    obj, {"err_finish_validation": message}
                )
        return obj

    def _do_validation(self, form_information, data, state):
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

    def dependent_validation(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        data = json.loads(self.request.POST.get("data"))
        form = data.get("form")
        text = data.get("text")

        form_information = FormInformation.objects.get(pk=form)
        dependents_form = DependentFormInformation.objects.filter(
            employee=form_information.employee
        )
        if dependents_form.exists():
            text += """
                    <p style="color: #fd0101; font-size: 14px; font-weight: bold;">Dependentes não validados:</p>
                """
            for form in dependents_form:
                if form.nome_dependent_can_edit == True:
                    text += f"""
                        <p style="color: #ff3434; font-size: 14px;">- Campo Nome do Dependente {form.dependent}  </p>
                    """
                if form.cpf_dependent_can_edit == True:
                    text += f"""
                        <p style="color: #ff3434; font-size: 14px;">- Campo CPF do Dependente {form.dependent}  </p>
                    """
                if form.tipo_can_edit == True:
                    text += f"""
                        <p style="color: #ff3434; font-size: 14px;">- Campo Tipo do Dependente {form.dependent} </p>
                    """
        rst.update(
            {
                "success": True,
                "message": "Dados persistidos com sucesso.",
                "text": text,
            }
        )

        self.response["content-type"] = "text/json"
        self.response.write(json.dumps(rst))

    def _do_notification(self, form_information, data):
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


class RegistrationValidation(RestfulDRY):

    _model = Validation

    def model_to_dict(self, instance):
        rst = super(RegistrationValidation, self).model_to_dict(instance)
        rst.update(
            validate_employee="%s" % employee_from_user(instance.validated_by, False),
        )
        return rst


class RegistrationFormInformationReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.registration.forminformation.Report")')


class RegistrationFormInformationGeneral(RegistrationFormInformation):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.registration.forminformation.general.Manage")'
        )

    def get_query(self):
        query = super(RegistrationFormInformationBase, self).get_query()
        return query.order_by("employee")


class RegistrationDependenteRestful(RestfulDRY):
    _model = DependentFormInformation

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.registration.forminformation.dependente.DependenteManage")'
        )

    def get_query(self):
        query = super(RegistrationDependenteRestful, self).get_query()
        return query.filter(employee=employee_from_user(get_current_user()))


class RegistrationDependentFormInformationAdmin(RegistrationFormInformationAdmin):
    _model = DependentFormInformation

    def get_query(self):
        return super(RegistrationDependentFormInformationAdmin, self).get_query()

    def model_to_dict(self, instance):
        return super(RegistrationFormInformationBase, self).model_to_dict(instance)

    def perform_validation(self, args):

        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        try:
            if can is False:
                rst.update(
                    message="Você não tem permissão para validar %s."
                    % self.Model._meta.object_name
                )
            else:
                querydict_request = None
                querydict_request = (
                    querydict_request
                    if querydict_request is not None
                    else getattr(self.request, "POST", QueryDict("", False))
                )
                data = json.loads(self.request.POST.get("data"))
                form = DependentFormInformation.objects.get(
                    pk=data.get("dependent_form")
                )
                dependent = form.dependent
                dependency = form.dependency
                for field in data.get("valid_fields"):
                    if field in list(
                        form._map_info_from_natural_person_to_dependent().keys()
                    ):
                        if field == "nome_dependent":
                            dependent.pessoa_fisica.social_name = form.nome_dependent
                            form.nome_dependent_can_edit = False
                            rh_models.PessoaFisica.objects.filter(
                                pk=dependent.pessoa_fisica.pk
                            ).update(nome=form.nome_dependent)

                        if field == "cpf_dependent":
                            dependent.pessoa_fisica.cpf = form.cpf_dependent
                            form.cpf_dependent_can_edit = False
                            rh_models.PessoaFisica.objects.filter(
                                pk=dependent.pessoa_fisica.pk
                            ).update(cpf=form.cpf_dependent)

                        if field == "data_nascimento_dependent":
                            dependent.pessoa_fisica.data_nascimento = (
                                form.data_nascimento_dependent
                            )
                            form.data_nascimento_dependent_can_edit = False
                            rh_models.PessoaFisica.objects.filter(
                                pk=dependent.pessoa_fisica.pk
                            ).update(data_nascimento=form.data_nascimento_dependent)

                        if field == "sexo_dependent":
                            dependent.pessoa_fisica.sexo = form.sexo_dependent
                            form.sexo_dependent_can_edit = False
                            rh_models.PessoaFisica.objects.filter(
                                pk=dependent.pessoa_fisica.pk
                            ).update(sexo=form.sexo_dependent)

                        if field == "grau_parentesco":
                            dependent.grau_parentesco = form.grau_parentesco
                            form.grau_parentesco_can_edit = False

                        if field == "tipo":
                            dependent.tipo = form.tipo
                            form.tipo_can_edit = False
                    else:
                        if field == "data_inicio_dependent":
                            dependency.data_inicio = form.data_inicio_dependent
                            form.data_inicio_dependent_can_edit = False

            if True in [
                form.tipo_can_edit,
                form.nome_dependent_can_edit,
                form.cpf_dependent_can_edit,
            ]:
                state = STATE_EMPLOYEE_VALIDATED_PROBLEM
                form_information = FormInformation.objects.get(employee=form.employee)
                form_information.transition_state(state)
            try:
                form.save()
                dependent.save()

                if dependency:
                    dependency.save()

            except Exception as e:
                log.error(e)

            rst.update(
                {
                    "success": True,
                    "message": "Dados persistidos com sucesso.",
                }
            )

        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
            log.exception(e)

        self.response["content-type"] = "text/json"
        self.response.write(json.dumps(rst))
