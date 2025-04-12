# -*- coding:utf-8 -*-
# from django.conf import settings
from django.db.models import Q

from contrib.utils import getLogger
from contrib.controller import DefaultController
from contrib.decorator import is_public

from rh.models import Localidade as City
from judicial.models import County, ExecutionOrgan

log = getLogger(__file__)


humanify = lambda x: str(x.first()) if x.first() else ""
strip = lambda x: x.split(":")[-1].strip() if x else ""
explode = lambda x: [strip(y) for y in x.split("|")] if x else ""


def replacement_render(replaced):
    job_position = humanify(replaced.substitute.cargo_responsavel)
    if not job_position:
        job_position = str(replaced.substitute)
    return {
        "organ": str(replaced.substitute),
        "order": replaced.order,
        "owner": strip(replaced.substitute.executionorgan.owner_unicode()),
        "job_position": job_position,
        "exercise": explode(
            replaced.substitute.executionorgan.employee_exercise_unicode()
        ),
    }


def attribution_act_render(qs):
    act_doc = qs.filter(end_document__isnull=True).first()
    if act_doc:
        area = area_render(act_doc)
        return area.get("document")


def area_render(dist):
    document = {"title": "Não informado", "url": ""}

    if hasattr(dist, "document"):
        document["title"] = str(dist.document)
        if getattr(dist.document, "arquivo"):
            document["url"] = dist.document.arquivo.no_logged_permalink()

    return {"matter": str(dist.matter), "document": document}


def attribution_document_render(eo):
    document = {"title": "Não informado", "url": ""}

    if hasattr(eo, "attribution_document"):
        document["title"] = str(eo.attribution_document)
        if getattr(eo.attribution_document, "arquivo", False):
            document["url"] = eo.attribution_document.arquivo.no_logged_permalink()

    return document


class ExecutionOrganRPC(DefaultController):

    def __init__(self, *args, **kwargs):
        super(ExecutionOrganRPC, self).__init__(*args, **kwargs)

        if self.response_format == "json":
            self.response["content-type"] = "text/javascript; charset=utf-8"

        self.__replacements = []
        self.__areas = []

    @is_public()
    def counties(self, args=[]):
        qs = County.objects.filter(~Q(locations=None)).values("id", "title")
        self.render({"total": qs.count(), "list": list(qs)})

    @is_public()
    def cities(self, args=[]):
        qs = City.objects.filter(estado__sigla="TO").order_by("nome")
        total = qs.count()

        city_list = []
        for city in qs:
            county = city.counties.all()
            county = county.first().id if county.exists() else ""

            city_list.append({"id": city.id, "name": city.nome, "county": county})

        self.render({"total": total, "list": city_list})

    def __render_data(self, qs):
        page = int(self.request.GET.get("page", 1))
        items_per_page = int(self.request.GET.get("items-per-page", 10))
        end = page * items_per_page
        start = end - items_per_page

        qs = (
            qs.select_related("lotacao_ptr__replacement_replaceds")
            .select_related("lotacao_ptr__cargo_responsavel")
            .select_related("instancia")
            .select_related("orgaogeral_ptr__phone")
            .select_related("orgaogeral_ptr__address")
            .select_related("localidade")
            .select_related("orgaogeral_ptr__in_distribution_tables")
            .filter(ativo=True)
        )

        total = qs.count()

        organs_list = []
        for eo in qs[start:end]:

            # areas_qs = eo.in_distribution_tables.select_related('document').all()
            # attribution_act = attribution_act_render(areas_qs)
            # areas = [area_render(a) for a in areas_qs]
            attribution_act = attribution_document_render(eo)

            replacements_qs = (
                eo.replacement_replaceds.select_related("substitute")
                .all()
                .order_by("order")
            )
            replacements = [replacement_render(r) for r in replacements_qs]

            occupation_area = eo.occupation_area or eo.descricao or ""
            for item in ["<!-- Correção de bug da ExtJS -->", "N/A"]:
                occupation_area = occupation_area.replace(item, "")

            # if county is None:
            county = eo.localidade.counties.first()

            owner_act_doc = None
            if eo.owner_publication:
                owner_act_doc = {
                    "title": str(eo.owner_publication),
                    "url": getattr(
                        eo.owner_publication.arquivo,
                        "no_logged_permalink",
                        lambda: None,
                    )(),
                }

            organs_list.append(
                {
                    "organ": str(eo),
                    "owner": strip(eo.owner_unicode()),
                    "owner_act_doc": owner_act_doc,
                    "exercise": explode(eo.employee_exercise_unicode()),
                    "phone": humanify(eo.phone.all()),
                    "address": humanify(eo.address.all()),
                    "job_position": humanify(eo.cargo_responsavel),
                    "instance": eo.instancia.nome if eo.instancia else "",
                    "entrance": eo.entrancia.nome if eo.entrancia else "",
                    "occupation_area": occupation_area,
                    "attribution": eo.attribution.replace("\n", " "),
                    "attribution_act": attribution_act,
                    # 'attributions': areas,
                    # 'assignments': [],
                    "replacements": replacements,
                    "business_hours": "Segunda à sexta. 9h00 às 18h00",
                    "range": [str(city) for city in county.locations.all()],
                }
            )

        return organs_list, total

    @is_public()
    def organs_by_entrance(self, args=[]):
        obj = dict(total="0", list=[])

        if args:
            qs = ExecutionOrgan.objects.filter(entrancia__nome__icontains=args[0])
            qs = qs.exclude(entrancia__isnull=True).order_by(
                "localidade__counties__title", "nome"
            )

            organs_list, total = self.__render_data(qs)
            obj = dict(total=total, list=organs_list)

        self.render(obj)

    @is_public()
    def organs_by_environmental_prosecution(self, args=[]):
        obj = dict(total="0", list=[])

        if args:
            qs = ExecutionOrgan.objects.filter(nome__icontains=args[0]).order_by(
                "localidade__counties__title", "nome"
            )

            organs_list, total = self.__render_data(qs)
            obj = dict(total=total, list=organs_list)

        self.render(obj)

    @is_public()
    def organs_by_environmental_prosecution(self, args=[]):
        obj = dict(total="0", list=[])

        if args:
            qs = ExecutionOrgan.objects.filter(nome__icontains=args[0]).order_by(
                "localidade__counties__title", "nome"
            )

            organs_list, total = self.__render_data(qs)
            obj = dict(total=total, list=organs_list)

        self.render(obj)

    @is_public()
    def organs_by_county(self, args=[]):
        obj = dict(total="0", list=[])
        if args:
            try:
                county = County.objects.get(id=args[0])
            except County.DoesNotExist:
                pass
            else:
                qs = ExecutionOrgan.objects.filter(
                    localidade__in=county.locations.all()
                ).order_by("localidade__counties__title", "nome")

                if "palmas" in county.title.lower():
                    qs = qs.exclude(nome__icontains="procuradoria")

                organs_list, total = self.__render_data(qs)
                obj = dict(total=total, list=organs_list)

        self.render(obj)

    @is_public()
    def organs_by_city(self, args=[]):
        obj = dict(total="0", list=[])
        if args:
            try:
                city = City.objects.filter(id=args[0]).last()
            except City.DoesNotExist:
                pass
            else:
                county = city.counties.last()
                qs = ExecutionOrgan.objects.filter(
                    localidade__in=county.locations.all()
                ).order_by("localidade__counties__title", "nome")

                if "palmas" in county.title.lower():
                    qs = qs.exclude(nome__icontains="procuradoria")

                organs_list, total = self.__render_data(qs)
                obj = dict(total=total, list=organs_list)

        self.render(obj)

    @is_public()
    def organs(self, args=[]):
        obj = dict(total="0", list=[])
        keyword = self.request.GET.get("keyword")

        qs = ExecutionOrgan.objects.exclude(entrancia__isnull=True)

        if keyword:
            params_base = dict(
                servidores_lotacao__ativo=True,
                servidores_lotacao__servidor__tipo="M",
                servidores_lotacao__servidor__pessoa_fisica__nome__icontains=keyword,
            )

            params_actives = dict(servidores_lotacao__designacao=True)
            params_actives.update(params_base)

            params_owner = dict(servidores_lotacao__owner=True)
            params_owner.update(params_base)

            # Q(in_distribution_tables__matter__title__icontains=keyword) |
            # Q(in_distribution_tables__matter__path_cache__icontains=keyword) |
            qs = qs.filter(
                Q(nome__icontains=keyword)
                | Q(attribution__icontains=keyword)
                | Q(**params_actives)
                | Q(**params_owner)
            ).distinct()

        county = None
        locations = []
        if args and args[0].isdigit():
            county = County.objects.filter(pk=args[0]).first()
            if county:
                locations = county.locations.all()
                qs = qs.filter(localidade__in=locations)

                if "palmas" in county.title.lower():
                    qs = qs.exclude(nome__icontains="procuradoria")

        qs = qs.order_by("entrancia__nome", "localidade__counties__title", "nome")

        organs_list, total = self.__render_data(qs)
        obj.update(total=total, list=organs_list)

        self.render(obj)

    @is_public()
    def all_organs(self, args=[]):
        obj = dict(total="0", list=[])
        keyword = self.request.GET.get("keyword")
        type_search = self.request.GET.get("tab")

        qs = ExecutionOrgan.objects.exclude(entrancia__isnull=True)

        if keyword:
            params_base = dict(
                servidores_lotacao__ativo=True,
                servidores_lotacao__servidor__tipo="M",
                servidores_lotacao__servidor__pessoa_fisica__nome__icontains=keyword,
            )

            params_actives = dict(servidores_lotacao__designacao=True)
            params_actives.update(params_base)

            params_owner = dict(servidores_lotacao__owner=True)
            params_owner.update(params_base)

            counties = County.objects.filter(
                (Q(title__icontains=keyword) | Q(locations__nome__icontains=keyword))
                & (~Q(locations=None))
            )

            locations = []
            for county in counties:
                locations.extend([c for c in county.locations.all()])

            qs = qs.filter(
                Q(nome__icontains=keyword)
                | Q(attribution__icontains=keyword)
                | Q(localidade__in=locations)
                | Q(**params_actives)
                | Q(**params_owner)
            ).distinct()

        if type_search != "all":
            qs = qs.exclude(nome__icontains="procuradoria")

        qs = qs.order_by("entrancia__nome", "localidade__counties__title", "nome")

        organs_list, total = self.__render_data(qs)
        obj.update(total=total, list=organs_list)

        self.render(obj)
