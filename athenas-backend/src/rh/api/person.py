# -*- coding: utf-8 -*-

import json
import re

import requests
from datetime import datetime
from django.conf import settings

from contrib.newrest import RestfulDRY
from contrib.nil import nil_date, nil_pk
from contrib.utils import DateUtils, getLogger, person_from_user
from contrib.middleware import get_current_user
from rh.models import AnonymousPerson, Lawyer
from rh.models import Pessoa as Person
from rh.models import PessoaFisica as NaturalPerson
from rh.models import PessoaJuridica as LegalPerson
from rh.models import NaturalPersonHistory

log = getLogger(__name__)


class RHPersonRestful(RestfulDRY):

    _model = Person

    full_text_index = (
        "nome__icontains",
        "name_cache__icontains",
        "address__logradouro__icontains",
        "phone__numero__icontains",
        "pessoafisica__cpf__icontains",
        "pessoafisica__rg__icontains",
        "pessoajuridica__cnpj__icontains",
        "pessoajuridica__razao_social__icontains",
        "pessoafisica__lawyer__oab__icontains",
        "pessoafisica__social_name__icontains",
    )

    exclude_fields = ["pessoa_ptr"]

    force_upper = True

    force_orm_single = True

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.person.Manage")')

    def get_query(self):
        return super(RHPersonRestful, self).get_query()

    def remove_projection(self, query):
        """Este método deve ser sobrescrito para remover valores repetidos no self._model.

        Args:
            query (queryset):

        Returns:
            queryset: default é query
        """
        if self.full_text_index and self.request.GET.get("keyword"):
            gen_pk = (pk for pk in query.values_list("pk", flat=True))
            query = self._model.objects.filter(pk__in=gen_pk)
        return query

    def person_type(self, person):
        if hasattr(person, "pessoafisica"):
            return "pf"
        elif hasattr(person, "pessoajuridica"):
            return "pj"
        else:
            return "p"

    def get_icons(self, instance):
        icon_kind_person_map = {
            "pessoa": {"iconCls": "icon-rh icon-core-person", "title": "Pessoa"},
            "pessoafisica": {
                "iconCls": "icon-rh icon-core-natural-person",
                "title": "Pessoa Física",
            },
            "naturalperson_employee": {
                "iconCls": "icon-rh icon-core-natural-person-employee",
                "title": "Servidor - Pessoa Física",
            },
            "pessoajuridica": {
                "iconCls": "icon-rh icon-core-legal-person",
                "title": "Pessoa Jurídica",
            },
            "anonymousperson": {
                "iconCls": "icon-rh icon-core-anonymous-person",
                "title": "Pessoa Anônima",
            },
            "lawyer": {"iconCls": "icon-rh icon-core-lawyer", "title": "Advogado"},
        }

        kind = instance.kind

        if (
            instance.kind == "pessoafisica"
            and hasattr(instance, "servidor_set")
            and instance.servidor_set.filter(ativo=True).exists()
        ):
            kind = "naturalperson_employee"

        kind_person = icon_kind_person_map.get(kind)

        return kind_person

    def model_to_dict(self, instance):
        instance = getattr(instance, instance.kind, instance)
        _dict_ = super(RHPersonRestful, self).model_to_dict(instance)
        can_manage_person_employee = False
        if instance.kind == "pessoafisica":
            document = instance.specialized_instance.cpf
            nome_social = instance.specialized_instance.social_name
        try:
            can_manage_person_employee = (
                instance.specialized_instance.validate_perm_person()
            )
        except Exception as err:
            log.exception(err)
        _dict_.update(
            {
                "icons": self.get_icons(instance),
                "verbose_kind": instance.verbose_kind,
                "can_manage_person_employee": can_manage_person_employee,
                "can_view_person_employee": get_current_user().has_perm(
                    "rh.view_servidor"
                ),
                "can_merge": instance.can_merge,
                "document": document,
                "nome_social": nome_social,
            }
        )

        return _dict_

    def _filter_eval_value(self, value):
        if isinstance(value, str) and value.lower() in ("on", "true"):
            value = True
        elif isinstance(value, str) and value.lower() in ("off", "false"):
            value = False
        return value


class RHNaturalPersonRestful(RestfulDRY):

    _model = NaturalPerson

    full_text_index = ("nome__icontains", "cpf__icontains", "rg__icontains")

    exclude_fields = RHPersonRestful.exclude_fields + []

    force_persist_boolean_fields = [
        "doador",
        "necessidade_especial",
        "enable_protocol",
        "has_serious_diseases",
    ]

    force_upper = True

    force_orm_single = True

    def update_personal_mail_and_password(self, args=[]):
        person = person_from_user(self.request.user)
        rst = {"success": False, "message": "nada foi feito ainda"}

        test_institucional = re.compile(r"^.*@(mpto\.mp|mp\.to\.gov)\.br$")
        test_mail = re.compile(r"^(\d|.|[0-9]|_)+\@.*")

        if not test_mail.match(self.request.POST.get("email_institucional")):
            rst.update(message="Email informado não é inválido.")
        elif self.request.POST.get("email_institucional") != self.request.POST.get(
            "confirm_email_institucional"
        ):
            rst.update(message="Os emails informados não são iguais.")
        elif test_institucional.match(self.request.POST.get("email_institucional")):
            rst.update(message="Seu email institucional não pode ser o pessoal.")
        else:
            if person:
                req = requests.post(
                    getattr(
                        settings, "ACCOUNT_INTEGRATION_CHANGE_PASSWORD", "undefined"
                    ),
                    json={
                        "username": self.request.user.username,
                        "passwd": self.request.POST.get("password"),
                        "new_pwd": self.request.POST.get("new_password"),
                        "new_pwd2": self.request.POST.get("confirm_new_password"),
                    },
                )

                if req.status_code == 200 and req.json().get("success"):
                    self.Model.objects.filter(pk=person.pk).update(
                        email_institucional=self.request.POST.get("email_institucional")
                    )

                    rst.update(success=True, message="Dados atualizados com sucesso.")
                elif req.status_code == 200 and not req.json().get("success"):
                    rst.update(message=req.json().get("message"))
                else:
                    rst.update(
                        message="Não foi possivel processar sua requisição, problema de integridade nos dados."
                    )
            else:
                rst.update(
                    message="Não foi possivel processar sua requisição, problema de integridade nos dados."
                )

        self.renderer(rst)

    def check_personal_mail(self, args=[]):
        rst = {}

        person = person_from_user(self.request.user)

        if person and person.servidor_set.filter(ativo=True).exists():
            rst.update(result=(person.email_institucional is not None))
        else:
            rst.update(result=True)

        self.response["Content-Type"] = "application/json"
        self.response.write(json.dumps(rst))

    def model_to_dict(self, instance):
        params = super(RHNaturalPersonRestful, self).model_to_dict(instance)
        params.update(
            {
                "rg_unicode": (
                    "%s  %s/%s %s"
                    % (
                        instance.rg if instance.rg else "",
                        instance.rg_orgao if instance.rg_orgao else "",
                        instance.rg_uf.sigla if instance.rg_uf else "",
                        (
                            DateUtils.date_to_str(instance.rg_data_expedicao)
                            if instance.rg_data_expedicao
                            else ""
                        ),
                    )
                ),
                "identification": f"{instance.nome} - {instance.cpf}",
            }
        )

        log.info(params)
        return params

    def person_diff(self, args=[]):
        rst = {"success": True, "message": "", "result": []}
        result = []
        message = ""
        try:
            result = self._diff(self.request.GET.getlist("pkset"))
        except Exception as err:
            log.exception(err)
            message = err
        rst.update(result=result, message=message)

        self.response["Content-Type"] = "application/json"
        self.response.write(json.dumps(rst))

    def _diff(self, person=[]):
        query = NaturalPerson.objects.filter(pk__in=person)
        naturalperson = query[0]
        duplicated = query[1]

        naturalperson_dict = self.model_to_dict(naturalperson)
        duplicated_dict = self.model_to_dict(duplicated)

        all_field = self._fields_of(naturalperson)

        diff = []
        for fld in all_field:
            fld_from_raw = naturalperson_dict.get(fld.name)
            fld_to_raw = duplicated_dict.get(fld.name)
            fld_from = fld_from_raw
            fld_to = fld_to_raw
            if "%s_display" % fld.name in list(naturalperson_dict.keys()):
                fld_from = naturalperson_dict.get("%s_display" % fld.name)
            elif "%s_unicode" % fld.name in list(naturalperson_dict.keys()):
                fld_from = naturalperson_dict.get("%s_unicode" % fld.name)
            if "%s_display" % fld.name in list(duplicated_dict.keys()):
                fld_to = duplicated_dict.get("%s_display" % fld.name)
            elif "%s_unicode" % fld.name in list(duplicated_dict.keys()):
                fld_to = duplicated_dict.get("%s_unicode" % fld.name)
            # DIFIRENÇA False to True é requerida
            if (
                fld_from != fld_to
                and (fld_from != "" and fld_from is not None)
                and (fld_to != "" and fld_to is not None)
            ):
                if isinstance(fld_from, bool):
                    fld_from = "SIM" if fld_from else "NÃO"
                if isinstance(fld_to, bool):
                    fld_to = "SIM" if fld_to else "NÃO"
                # log.debug('{} -> {} diff {}'.format(fld.name, fld_from, fld_to))
                diff.append(
                    {
                        "fieldSet": False,
                        "name": fld.name,
                        "label": fld.verbose_name,
                        "values": [
                            {"raw_value": fld_from_raw, "unicode": fld_from},
                            {"raw_value": fld_to_raw, "unicode": fld_to},
                        ],
                    }
                )

        diff.append(NaturalPerson._grid_diff(person=person))
        diff.append(NaturalPerson._available_merge(person=person))

        return diff

    def _fields_of(self, instance):
        fields = []
        exclude_fields = (
            "id",
            "created_at",
            "modified_at",
            "data_cadastro",
            "slug",
            "data_alteracao",
            "renda_familiar",
            "retired",
        )
        for fld in instance._meta.get_fields():
            if not fld.is_relation and fld.name not in exclude_fields:
                fields.append(fld)
        return fields

    def _get_value(self, instance, fld):
        value = None
        _type = fld.get_internal_type()
        if _type == "DecimalField":
            value = (
                float(getattr(instance, fld.name))
                if getattr(instance, fld.name) is not None
                else ""
            )
        elif _type == "DateTimeField":
            value = (
                DateUtils.datetime_to_str(getattr(instance, fld.name))
                if getattr(instance, fld.name)
                else ""
            )
        elif _type == "DateField":
            value = (
                DateUtils.date_to_str(getattr(instance, fld.name))
                if getattr(instance, fld.name)
                else ""
            )
        elif _type in ["ForeignKey", "OneToOneField"]:
            value = getattr(instance, fld.attname) or ""
        elif _type in (
            "BigIntegerField",
            "IntegerField",
            "PositiveIntegerField",
            "PositiveSmallIntegerField",
            "SmallIntegerField",
        ):
            value = (
                int(getattr(instance, fld.attname))
                if getattr(instance, fld.attname) is not None
                else None
            )
        else:
            value = getattr(instance, fld.name)
        if fld.choices:
            value = getattr(instance, "get_%s_display" % fld.name)() or ""
        if fld.rel:
            value = getattr(instance, fld.name) or ""
        return value

    def convert_person(self, args=[]):
        rst = {"success": False, "message": "", "result": []}
        params = self.get_params()
        try:
            father_id = self.request.POST.get("pk")
            name = self.request.POST.get("nome")
            created_by = get_current_user()
            created_at = datetime.now()
            natural_person = self.Model.objects.create(
                pk=father_id, nome=name, created_by=created_by, created_at=created_at
            )
        except Exception as err:
            log.exception(err)
            rst.update(message=str(err), success=False)
        else:
            rst.update(message="Conversão realizada com sucesso", success=True)

        self.response["Content-Type"] = "application/json"
        self.response.write(json.dumps(rst))


class RHNaturalPersonWithDocument(RHNaturalPersonRestful):

    def model_to_dict(self, instance):
        params = super(RHNaturalPersonRestful, self).model_to_dict(instance)

        cnh = instance.cnh
        cnh_categoria = cnh.cnh_category if cnh else None
        cnh_first_date = cnh.cnh_first_date if cnh else None
        ctps = instance.ctps
        serie_ctps = ctps.ctps_series if ctps else None
        pis_pasep = instance.pis_pasep
        reservista = instance.reservist
        classe_reservista = reservista.reservist_class if reservista else None
        professional_council = instance.professional_council
        professional_council_issuer = ""
        professional_council_number = ""
        professional_council_state = ""
        professional_council_expedition_date = ""
        professional_council_validity_date = ""
        if professional_council:
            professional_council_issuer = (
                professional_council.professional_council_issuer
            )
            professional_council_issuer = (
                professional_council_issuer.valor if professional_council_issuer else ""
            )
            professional_council_number = professional_council.numero
            professional_council_state = nil_pk(
                professional_council.estado_expedicao, None
            )
            professional_council_expedition_date = nil_date(
                professional_council.data_expedicao, None
            )
            professional_council_validity_date = nil_date(
                professional_council.data_validade, None
            )
        voter = instance.voter
        zona_titulo = voter.voter_zone if voter else None
        secao_titulo = voter.voter_section if voter else None
        municipio_titulo = voter.voter_city_local if voter else None
        disease = None
        if hasattr(instance, "molestia"):
            disease = instance.molestia

        params.update(
            {
                "foto_link": (
                    instance.foto.resizelink((85, 113)) if instance.foto else ""
                ),
                "cnh": cnh.numero if cnh else "",
                "cnh_categoria": cnh_categoria.valor if cnh_categoria else "",
                "cnh_expedition_date": nil_date(
                    cnh.data_expedicao if cnh else None, None
                ),
                "cnh_validity_date": nil_date(cnh.data_validade if cnh else None, None),
                "cnh_first_date": cnh_first_date.valor if cnh_first_date else "",
                "cnh_state": nil_pk(cnh.estado_expedicao if cnh else None, None),
                "ctps": ctps.numero if ctps else None,
                "serie_ctps": serie_ctps.valor if serie_ctps else None,
                "ctps_state": nil_pk(ctps.estado_expedicao if ctps else None, None),
                "pis_pasep": pis_pasep.numero if pis_pasep else "",
                "reservista": reservista.numero if reservista else "",
                "classe_reservista": (
                    classe_reservista.valor if classe_reservista else ""
                ),
                "professional_council": professional_council_number,
                "professional_council_state": professional_council_state,
                "professional_council_expedition_date": professional_council_expedition_date,
                "professional_council_validity_date": professional_council_validity_date,
                "professional_council_issuer": professional_council_issuer,
                "titulo_eleitor": voter.numero if voter else "",
                "zona_titulo": zona_titulo.valor if zona_titulo else "",
                "secao_titulo": secao_titulo.valor if secao_titulo else "",
                "municipio_titulo": nil_pk(municipio_titulo, None),
                "molestia": nil_pk(disease, None),
            }
        )
        return params


class RHSimplifiedNaturalPersonRestful(RestfulDRY):

    _model = NaturalPerson

    full_text_index = ("nome__icontains", "cpf__icontains", "rg__icontains")

    exclude_fields = RHPersonRestful.exclude_fields + []

    force_upper = True

    force_orm_single = True


class RHLegalPersonRestful(RestfulDRY):

    _model = LegalPerson

    full_text_index = ("nome__icontains", "cnpj__icontains", "razao_social__icontains")

    exclude_fields = RHPersonRestful.exclude_fields + []

    force_upper = True

    force_orm_single = True

    def convert_person(self, args=[]):
        rst = {"success": False, "message": "", "result": []}
        params = self.get_params()
        try:
            father_id = self.request.POST.get("pk")
            name = self.request.POST.get("nome")
            created_by = get_current_user()
            created_at = datetime.now()
            natural_person = self.Model.objects.create(
                pk=father_id, nome=name, created_by=created_by, created_at=created_at
            )
        except Exception as err:
            log.exception(err)
            rst.update(message=str(err), success=False)
        else:
            rst.update(message="Conversão realizada com sucesso", success=True)

        self.response["Content-Type"] = "application/json"
        self.response.write(json.dumps(rst))


class RHLawyerRestful(RHNaturalPersonRestful):

    _model = Lawyer

    full_text_index = RHNaturalPersonRestful.full_text_index + ("oab__icontains",)

    exclude_fields = RHNaturalPersonRestful.exclude_fields + ["pessoafisica_ptr"]

    force_persist_boolean_fields = (
        RHNaturalPersonRestful.force_persist_boolean_fields + []
    )


class RHSimplifiedLawyerRestful(RHSimplifiedNaturalPersonRestful):

    _model = Lawyer

    full_text_index = RHSimplifiedNaturalPersonRestful.full_text_index + (
        "oab__icontains",
    )

    exclude_fields = RHSimplifiedNaturalPersonRestful.exclude_fields + [
        "pessoafisica_ptr"
    ]


class RHAnonymousPersonRestful(RestfulDRY):

    _model = AnonymousPerson

    full_text_index = ("nome__icontains", "address__logradouro__icontains")

    exclude_fields = RHPersonRestful.exclude_fields + []

    force_upper = True

    force_orm_single = True


class RHNaturalPersonHistory(RestfulDRY):

    _model = NaturalPersonHistory

    full_text_index = (
        "natural_person__nome__icontains",
        "natural_person__cpf__icontains",
        "natural_person__servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.person.naturalpersonhistory.Manage")')
