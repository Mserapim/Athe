# -*- coding:utf-8 -*-

import re
import socket
from threading import Thread
from unicodedata import normalize

from django.db import transaction, IntegrityError
from django import forms as django_forms
from django.template.defaultfilters import slugify, addslashes

from rh.models import Servidor
from contrib.extjs import ExtWidget, ExtReportBuild

from contrib.decorator import login_required, validate
from contrib.helpers import capitalize_words
from contrib.utils import getLogger, person_from_user

from common.mailing import models, forms


log = getLogger()


# Fallback do modulo transaction entre o django 1.8 e versões anteriores
if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


class MailingCommon(ExtWidget):
    Model = models.Common
    Form = forms.CommonForm

    @login_required(type="JSON")
    def all(self, args=[]):
        R = self.request.REQUEST
        qs = self.Model.objects.values().order_by("name")
        total = qs.count()
        if R.get("limit"):
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start
            qs = qs[start:end]
        self.render(dict(total=total or "0", result=list(qs)))

    @login_required(type="JSON")
    def delete(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        user = self.request.user.mailing_user
        if user.permission in ["reviser", "admin"]:
            ID = self.request.REQUEST.get("id")
            try:
                if not ID:
                    raise Exception("É necesserário o código identificador.")

                with transaction.atomic():
                    self.Model.objects.get(id=ID).delete()

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(success=True, msg="Realizado com sucesso.")

        self.render(response)

    @login_required(type="JSON")
    @validate(Form)
    def add_or_edit(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        user = self.request.user
        mailing_user = getattr(user, "mailing_user", None)

        if (
            mailing_user and mailing_user.permission in ["reviser", "admin"]
        ) or user.is_superuser:
            try:
                data = self.request.data
                model = (
                    self.Model()
                    if not data.get("id")
                    else self.Model.objects.get(id=data.get("id"))
                )
                model.name = addslashes(data.get("name"))
                model.slug = slugify(model.name)

                with transaction.atomic():
                    model.save()

            except IntegrityError as e:
                response["msg"] += (
                    '<br/> Já existe um item cadastrado com o nome "%s", por favor escolha outro.'
                    % model.name
                )
                self.log.error(e)

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(
                    success=True, msg="Realizado com sucesso.", data=model.id
                )

        self.render(response)


class MailingProfile(MailingCommon):
    Model = models.Profile
    Form = forms.ProfileForm

    @login_required(type="JSON")
    def json(self, args=[]):
        self.render("new toolkit.common.mailing.Profiles()")

    @login_required(type="JSON")
    @validate(Form)
    def add_or_edit(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        user = self.request.user
        mailing_user = getattr(user, "mailing_user", None)

        if (
            mailing_user and mailing_user.permission in ["reviser", "admin"]
        ) or user.is_superuser:
            try:
                data = self.request.data
                model = (
                    self.Model()
                    if not data.get("id")
                    else self.Model.objects.get(id=data.get("id"))
                )
                model.name = addslashes(data.get("name"))
                model.slug = slugify(model.name)
                model.printer_name = addslashes(data.get("printer_name"))

                with transaction.atomic():
                    model.save()

            except IntegrityError as e:
                response["msg"] += (
                    '<br/> Já existe um item cadastrado com o nome "%s", por favor escolha outro.'
                    % model.name
                )
                self.log.error(e)

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(
                    success=True, msg="Realizado com sucesso.", data=model.id
                )

        self.render(response)


class MailingProfileUsers(MailingCommon):
    Model = models.MailingUser
    Form = forms.ProfileUserForm
    DeleteForm = forms.DeleteProfileUserForm

    @login_required(type="JSON")
    def get(self, args):
        R = self.request.REQUEST
        start = int(R.get("start", 0))
        end = int(R.get("limit", 20)) + start
        qs = self.Model.objects.filter(profiles=R.get("profile"))

        users = []
        for mailing_user in qs[start:end]:
            log.info(
                "%s, %s " % (mailing_user.user, person_from_user(mailing_user.user))
            )
            person = person_from_user(mailing_user.user)
            if person:
                users.append(
                    dict(
                        id=mailing_user.user.id,
                        fullname=capitalize_words(person.nome),
                        permission=mailing_user.permission,
                        permission_name=dict(models.PERMISSION_CHOICES)[
                            mailing_user.permission
                        ],
                    )
                )

        self.render(dict(total=qs.count() or "0", result=users))

    @login_required(type="JSON")
    def users(self, args):
        R = self.request.REQUEST
        rjson = dict(total=0, result=[])
        if "query" in R and R["query"]:
            qs = Servidor.objects.filter(
                pessoa_fisica__nome__icontains=R["query"], ativo=True
            )
            rjson = {
                "total": len(qs),
                "result": [
                    {"id": i.user.id, "fullname": i.pessoa_fisica.nome}
                    for i in qs
                    if i.user
                ],
            }
        self.render(rjson)

    @login_required(type="JSON")
    @validate(Form)
    def add_user(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        if self.request.user.is_superuser:
            try:
                data = self.request.data
                mailing_user = (
                    self.Model.objects.filter(user=data.get("user")).last()
                    or self.Model()
                )
                self.log.info(data)

                mailing_user.user = data.get("user")
                mailing_user.permission = data.get("permission")

                with transaction.atomic():
                    mailing_user.save()
                    if (
                        not data.get("profile")
                        .users.filter(id=mailing_user.id)
                        .exists()
                    ):
                        mailing_user.profiles.clear()
                        data.get("profile").users.add(mailing_user)

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(success=True, msg="Realizado com sucesso.")

        self.render(response)

    @login_required(type="JSON")
    @validate(DeleteForm)
    def remove_user(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        if self.request.user.is_superuser:
            try:
                data = self.request.data

                with transaction.atomic():
                    data.get("profile").users.remove(data.get("user").mailing_user)

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(success=True, msg="Realizado com sucesso.")

        self.render(response)


class MailingTreatment(MailingCommon):
    Model = models.Treatment
    Form = forms.TreatmentForm


class MailingCompany(MailingCommon):
    Model = models.Company
    Form = forms.CompanyForm


class MailingPosition(MailingCommon):
    Model = models.Position
    Form = forms.PositionForm


class MailingGroup(MailingCommon):
    Model = models.Group
    Form = forms.GroupForm

    @login_required(type="JSON")
    def all(self, args):
        R = self.request.REQUEST
        qs = (
            self.Model.objects.filter(profile=R.get("profile"))
            .values()
            .order_by("name")
        )
        total = qs.count()
        if R.get("limit"):
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start
            qs = qs[start:end]
        groups = list(qs)
        if int(R.get("fakeItem", 0)) == 1:
            groups.insert(0, dict(id=-1, name="Todos os selecionados"))
        self.render(dict(total=total or "0", result=groups))

    @login_required(type="JSON")
    @validate(Form)
    def add_or_edit(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        user = self.request.user.mailing_user
        if user.permission in ["reviser", "admin"]:
            try:
                data = self.request.data
                self.log.info(data)
                model = (
                    self.Model()
                    if not data.get("id")
                    else self.Model.objects.get(id=data.get("id"))
                )
                model.name = addslashes(data.get("name"))
                model.slug = slugify(model.name)
                model.profile = data.get("profile")

                with transaction.atomic():
                    model.save()

            except IntegrityError as e:
                response["msg"] += (
                    '<br/> Já existe um item cadastrado com o nome "%s", por favor escolha outro.'
                    % model.name
                )
                self.log.error(e)

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(
                    success=True, msg="Realizado com sucesso.", data=model.id
                )

        self.render(response)


class MailingState(MailingCommon):
    Model = models.State
    Form = forms.StateForm

    @login_required(type="JSON")
    @validate(Form)
    def add_or_edit(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        user = self.request.user.mailing_user
        if user.permission in ["reviser", "admin"]:
            try:
                data = self.request.data
                model = (
                    self.Model()
                    if not data.get("id")
                    else self.Model.objects.get(id=data.get("id"))
                )
                model.name = addslashes(data.get("name"))
                model.slug = slugify(model.name)
                model.uf = data.get("UF")

                with transaction.atomic():
                    model.save()

            except IntegrityError as e:
                response["msg"] += (
                    '<br/> Já existe um item cadastrado com o nome "%s", por favor escolha outro.'
                    % model.name
                )
                self.log.error(e)

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(
                    success=True, msg="Realizado com sucesso.", data=model.id
                )

        self.render(response)


class MailingCity(MailingCommon):
    Model = models.City
    Form = forms.CityForm

    @login_required(type="JSON")
    def all(self, args=[]):
        R = self.request.REQUEST
        qs = self.Model.objects.all().order_by("name")
        total = qs.count()
        if R.get("limit"):
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start
            qs = qs[start:end]
        self.render(
            dict(
                total=total or "0",
                result=[
                    dict(
                        id=city.id,
                        name=city.name,
                        fullname=str(city),
                        state_id=city.state.id,
                        state=city.state.name,
                    )
                    for city in qs
                ],
            )
        )

    @login_required(type="JSON")
    @validate(Form)
    def add_or_edit(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        user = self.request.user.mailing_user
        if user.permission in ["reviser", "admin"]:
            try:
                data = self.request.data
                model = (
                    self.Model()
                    if not data.get("id")
                    else self.Model.objects.get(id=data.get("id"))
                )
                model.name = addslashes(data.get("name"))
                model.slug = slugify(model.name)
                model.state = data.get("state")

                with transaction.atomic():
                    model.save()

            except IntegrityError as e:
                response["msg"] += (
                    '<br/> Já existe um item cadastrado com o nome "%s", por favor escolha outro.'
                    % model.name
                )
                self.log.error(e)

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(
                    success=True, msg="Realizado com sucesso.", data=model.id
                )

        self.render(response)


class MailingContact(MailingCommon):
    Model = models.Contact
    Form = forms.ContactForm

    @login_required(type="JSON")
    def json(self, args=[]):
        profile = "null"
        perm = "false"
        try:
            qs = self.request.user.mailing_user.profiles.all()
            perm = self.request.user.mailing_user.permission
            profile = qs[0].id if qs.exists() else "null"
        except Exception:
            pass
        self.render('new toolkit.common.mailing.Contacts(%s, "%s")' % (profile, perm))

    @login_required(type="JSON")
    @validate(forms.PrintForm)
    def print_tags(self, args=[]):
        data = self.request.data
        group = data.get("group")
        profile = data.get("profile")
        selected = data.get("selected", "").split(",")
        positions = data.get("positions", "").split(",")
        type_paper = data.get("type_paper")

        qs = self.Model.objects.filter(profile=profile)
        if group:
            qs = qs.filter(groups=group)
        elif selected:
            qs = qs.filter(id__in=selected)
        else:
            qs = qs.none()

        response_data = dict(
            success=False,
            msg="É necessário escolher algum contato ou grupo de contatos para realizar uma impressão",
        )
        if qs.exists():
            response_data.update(success=True)
            if type_paper < 3:
                tags = ["%s" % t for t in qs.values_list("id", flat=True)]
                for i in range(len(positions)):
                    if int(positions[i]) == 0:
                        tags.insert(i, "0")
                tags = ",".join(tags)
                response_data.update(
                    msg="Aguarde a geração das etiquetas para impressão", data=tags
                )
            else:
                MailingPrintTagsRoll(qs).start()
                response_data.update(msg="Aguarde a impressão das etiquetas.")

        self.render(response_data)

    @login_required(type="JSON")
    def get(self, args=[]):
        R = self.request.REQUEST
        start = int(R.get("start", 0))
        end = int(R.get("limit", 20)) + start

        params = {"profile": R.get("profile")}
        if R.get("search"):
            params["name__icontains"] = R.get("search")

        qs = self.Model.objects.filter(**params).order_by("name")
        contacts = []
        for contact in qs[start:end]:
            group, group_id, groups = "", "", contact.groups.all()
            if groups.exists():
                group, group_id = groups[0].name, groups[0].id

            contacts.append(
                dict(
                    id=contact.id,
                    name=contact.name,
                    slug=contact.slug,
                    profile_id=contact.profile.id,
                    groups=list(contact.groups.values()),
                    company=str(contact.company),
                    company_id=contact.company.id,
                    position=str(contact.position),
                    position_id=contact.position.id,
                    treatment=str(contact.treatment),
                    treatment_id=contact.treatment.id,
                    locality=contact.address.locality,
                    neighborhood=contact.address.neighborhood,
                    code=contact.address.code,
                    city=str(contact.address.city),
                    city_id=contact.address.city.id,
                    normal=contact.phone.normal,
                    fax=contact.phone.fax,
                    mobile=contact.phone.mobile,
                    group_id=group_id,
                    group=group,
                )
            )
        self.render(dict(total=qs.count() or "0", result=contacts))

    @login_required(type="JSON")
    @validate(Form)
    def add_or_edit(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação.")
        user = self.request.user.mailing_user
        if user.permission in ["reviser", "admin"]:
            try:
                data = self.request.data
                self.log.info(data)

                model = (
                    self.Model()
                    if not data.get("id")
                    else self.Model.objects.get(id=data.get("id"))
                )
                model.name = addslashes(data.get("name"))
                model.slug = slugify(model.name)

                address = models.Address() if not model.address_id else model.address
                address.locality = addslashes(data.get("locality"))
                address.neighborhood = addslashes(data.get("neighborhood"))
                address.code = re.sub(r"[\W]+", "", data.get("code"))
                address.city = data.get("city")

                phone = models.Phone() if not model.phone_id else model.phone
                phone.normal = re.sub(r"[\W]+", "", data.get("normal"))
                phone.mobile = re.sub(r"[\W]+", "", data.get("mobile"))
                phone.fax = re.sub(r"[\W]+", "", data.get("fax"))

                model.profile = data.get("profile")
                model.treatment = data.get("treatment")
                model.company = data.get("company")
                model.position = data.get("position")

                with transaction.atomic():
                    address.save()
                    phone.save()
                    model.address = address
                    model.phone = phone
                    model.save()

                    model.groups.clear()
                    if data.get("group"):
                        model.groups.add(data.get("group"))

            except IntegrityError as e:
                response["msg"] += (
                    '<br/>Já existe um item cadastrado com o nome "%s", por favor escolha outro.'
                    % model.name
                )
                self.log.error(e)

            except Exception as e:
                response["msg"] += "<br/>%s" % e
                self.log.error(e)

            else:
                response = dict(
                    success=True, msg="Realizado com sucesso.", data=model.id
                )

        self.render(response)


class MailingPrintTags(ExtReportBuild):

    class Form(django_forms.Form):
        id = django_forms.CharField()
        profile = django_forms.CharField()

    report_src = "/to/mpe/maladireta/carta/catorze/main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/maladireta/carta/catorze/",
        }
    ]

    def get_generated_filename(self):
        # self.log.info(self.request.REQUEST)
        return "etiquetas.pdf"


class MailingPrintTagsA4(ExtReportBuild):

    class Form(django_forms.Form):
        id = django_forms.CharField()
        profile = django_forms.CharField()

    report_src = "/to/mpe/maladireta/a4/catorze/main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/maladireta/a4/catorze/",
        }
    ]

    def get_generated_filename(self):
        # self.log.info(self.request.REQUEST)
        return "etiquetas.pdf"


class MailingPrintTagsRoll(Thread):

    def __init__(self, tags):
        self.__tags = tags
        self.__tpl = "\n".join(
            [
                "SIZE 50 mm, 90mm",
                "GAP 3 mm, 0mm",
                "CLS",
                'TEXT 360,30,"0",90,10,10,"%s"',
                'TEXT 300,30,"0",90,10,10,"%s"',
                'TEXT 240,30,"0",90,10,10,"%s"',
                'TEXT 180,30,"0",90,10,10,"%s"',
                'TEXT 120,30,"0",90,10,10,"%s"',
                'TEXT 60,30,"0",90,10,10,"%s"',
                "PRINT 1",
                "",
            ]
        )
        super(MailingPrintTagsRoll, self).__init__()

    def run(self):
        try:
            from edocs.protocolo.models import Impressora

            printer_name = (
                self.__tags.first().profile.printer_name
                if self.__tags and self.__tags.first()
                else "----#####----"
            )
            printer = Impressora.objects.filter(nome__iexact=printer_name).first()
            if not self.__tags:
                raise Exception(
                    "Selecione etiquetas ou grupos de etiquetas para imprimir"
                )

            if not printer:
                raise Exception("Impressora não encontrada.")
            log.info("%s:%s" % (printer.host, str(printer.port)))

            fd = socket.create_connection((printer.host, str(printer.port)))
            log.info(self.__tags)
            for tag in self.__tags:
                addr = tag.address
                tag_data = self.__tpl % (
                    str(tag.treatment),
                    str(tag.name),
                    str(tag.position),
                    str(tag.company),
                    "%s %s" % (addr.locality, addr.neighborhood),
                    "%s - CEP: %s" % (str(addr.city), addr.code),
                )
                tag_data = normalize("NFKD", tag_data).encode("ascii", "ignore")
                fd.send(tag_data.upper())
            fd.close()
        except Exception as e:
            print(e)
            log.error(e)
