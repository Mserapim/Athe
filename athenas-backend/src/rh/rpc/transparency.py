# -*- coding: utf-8 -*-

from contrib.controller import DefaultController
from contrib.decorator import is_public
from contrib.helpers import capitalize_words
from contrib.utils import getLogger
from rh.models import Employee, Workplace
from django.db.models import Q

log = getLogger(__file__)

# CLASSIFICAÇÃO DO ORGANOGRAMA
# Órgão da Sede e Capital
SEDE_E_PROMOTORIA = 6  # Sede não possue promotorias neste contexto.
ORG_ADM_SUP_EXECUCAO = 7
ORG_ADM_SUP_EXECUCAO_N2 = 8
ORG_AUX_DG = 9
ORG_AUX_DG_N2 = 10
ORG_AUX_DG_N3 = 13
ORG_AUX_DG_N4 = 14

# Promotorias Interior
PRIMEIRA_ENTRANCIA = 2
SEGUNDA_ENTRANCIA = 3
SEDE_TERCEIRA_ENTRANCIA = 4
TERCEIRA_ENTRANCIA = 5
PRIMEIRA_ENTRANCIA_N2 = 11
SEGUNDA_ENTRANCIA_N2 = 12


class EmployeeRPC(DefaultController):

    def __init__(self, *args, **kwargs):
        super(EmployeeRPC, self).__init__(*args, **kwargs)

        self.__all = self.params.get("all")
        self.__page_items = int(self.params.get("page_items", 20))
        self.__page = int(self.params.get("page", 1))

        if self.response_format == "json":
            self.response["content-type"] = "text/javascript; charset=utf-8"

    @property
    def params(self):

        if not getattr(self, "__params", False):
            self.__params = {}
            self.__params.update(self.request.GET.dict())
            self.__params.update(self.request.POST.dict())

        return self.__params

    def __limits(self):
        limit = self.__page * self.__page_items
        start = limit - self.__page_items

        return start, limit

    def __prepare(self, qs):

        self.__pages = 1
        self.__total = qs.count()

        if not self.__all:
            start, limit = self.__limits()
            rest = 0 if self.__total % self.__page_items == 0 else 1
            self.__pages = int(self.__total / self.__page_items) + rest

            qs = qs[start:limit]

        return qs

    def __list_renderer(self, obj_list):
        self.render(
            {
                "total": self.__total or "0",
                "list": obj_list,
                "page": self.__page,
                "pages": self.__pages,
            }
        )

    @is_public()
    def members_emails(self, args=[]):
        members_list = []
        qs = self.__prepare(
            Employee.objects.filter(tipo="M", ativo=True).order_by(
                "pessoa_fisica__nome"
            )
        )

        for member in qs:
            workplace = "Não informado"
            work_assignment = member.get_work_assignment()
            if member.workplace_by_date():
                workplace = member.workplace_by_date()
            elif work_assignment.exists():
                member_workplace = work_assignment.latest("data_vigencia_inicio")
                if hasattr(member_workplace, "lotacao"):
                    workplace = member_workplace.lotacao

            members_list.append(
                {
                    "name": capitalize_words("%s" % member.pessoa_fisica.nome),
                    "job_position": (
                        "Procurador de Justiça"
                        if member.is_procurador
                        else "Promotor de Justiça"
                    ),
                    "workplace": capitalize_words("%s" % workplace),
                    "email": getattr(
                        getattr(member, "user", {}), "email", "Não informado"
                    ),
                }
            )

        self.__list_renderer(members_list)

    @is_public()
    def workplaces_info(self, args=[]):
        workplaces_list = []
        keyword = self.request.GET.get("keyword")
        unit_type = self.request.GET.get("unit_type")
        query = Workplace.objects.filter(ativo=True, is_contact_displayed=True)

        if keyword:
            query = query.filter(
                Q(nome__icontains=keyword)
                | Q(sigla__icontains=keyword)
                | Q(address__municipio__nome__icontains=keyword)
                | Q(address__logradouro__icontains=keyword)
            )

        if unit_type:
            if unit_type == "1":
                query = query.filter(Q(nome__icontains="Procuradoria"))
            elif unit_type == "2":
                query = query.filter(
                    Q(localidade__nome="PALMAS")
                    & Q(nome__icontains="Promotoria")
                    & Q(organizational_classification=SEDE_E_PROMOTORIA)
                )
            elif unit_type == "3":
                query = query.filter(
                    ~Q(localidade__nome="PALMAS") & Q(nome__icontains="Promotoria")
                )
            elif unit_type == "4":
                query = query.filter(
                    Q(localidade__nome="PALMAS")
                    & ~Q(nome__icontains="Promotoria")
                    & ~Q(nome__icontains="Procuradoria")
                )
            else:
                query = query.none()

        qs = self.__prepare(query)

        for place in qs:
            phones = [str(phone) for phone in place.phone.filter(publico=True)]

            workplaces_list.append(
                {
                    "name": capitalize_words(place.nome),
                    "sigla": str(place.sigla),
                    "phones": phones,
                    "address": str(place.address.first() or "Não informado"),
                    "building_kind": str(place.characteristic or "Não informado"),
                    "office_hours": str(place.office_hours or "Não informado"),
                }
            )

        self.__list_renderer(workplaces_list)
