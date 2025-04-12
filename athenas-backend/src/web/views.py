# -*- coding:utf-8 -*-

# General imports
import os, re, datetime, urllib.request

# Django imports
from django.conf import settings
from django.db import transaction
from django import forms
from django.db.models import Q, Sum
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify, addslashes, striptags
from django.shortcuts import get_object_or_404

try:
    from django.contrib.auth.hashers import check_password
except:
    from django.contrib.auth.models import check_password

# APP imports
import contrib.ezjson as json
from auditoria.models import LineLog
from contrib.controller import ContentType
from contrib.extjs import ExtWidget, ExtReportBuild
from contrib.decorator import login_required, is_public
from contrib.helpers import Resize, err2dict, capitalize_words
from contrib.utils import employee_from_user, person_from_user
from ged.models import Arquivo as GedFile
from rh.utils import format_situacao_funcional as format_position, getLogger

from rh.models import Servidor
from web.forms import (
    AreaForm,
    PostForm,
    PollForm,
    ChoiceForm,
    PublicationForm,
    LinkForm,
    MultimediaForm,
    RelateUserForm,
    GroupPermissionsForm,
    ProsecutorActionStatusForm,
    ProsecutorActionForm,
)

from web.models import (
    Common,
    Module,
    Area,
    WebGroup,
    Content,
    Post,
    Multimedia,
    Link,
    Image,
    Video,
    Audio,
    File,
    ContentArea,
    Tag,
    Poll,
    Choice,
    ProsecutorActionStatus,
    ProsecutorAction,
    County,
    MetaValue,
)

from web.auto import make_site
from standard.models import Configuration


# Fallback do modulo transaction entre o django 1.8 e versões anteriores
if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


def get_employee_name(user):
    qs = Servidor.objects.filter(user=user)
    return qs[0].pessoa_fisica.nome if qs.exists() else ""


log = getLogger(__name__)


class BaseCMS(ExtWidget):

    def __init__(self, *args, **kwargs):
        super(BaseCMS, self).__init__(*args, **kwargs)

        if self.request.user.is_superuser:
            self.user_areas = True
        else:
            if not self.request.user.is_anonymous:
                self.user_areas = [
                    g.area
                    for g in WebGroup.objects.filter(
                        users=self.request.user, area__active=True
                    )
                ]


class Polls(BaseCMS):

    def _qs_polls(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        kwargs = {"active": True}

        if R.get("area"):
            try:
                kwargs.update({"areas": int(R["area"])})
            except:
                kwargs.update({"areas__slug": R["area"]})

        return Poll.objects.filter(**kwargs).order_by(
            "position", "-published_date", "-id"
        )

    def _render_polls(self, polls, filter_check=lambda x: True):
        method = self.request.method
        R = getattr(self.request, method)

        start = int(R.get("start", 0))
        end = int(R.get("limit", 20)) + start

        return {
            "total": polls.count() or "0",
            "result": [
                {
                    "id": p.id,
                    "content": p.content_ptr_id,
                    "title": p.title,
                    "show_partial": p.show_partial,
                    "position": p.position,
                    "can_edit": not p.is_locked(),
                    "finished": p.is_finished(),
                    "publication_start": p.publication_start,
                    "publication_end": p.publication_end,
                    "published": p.is_published(),
                    "published_date": p.published_date,
                    "choices": [
                        {"id": c.id, "choice": c.choice}
                        for c in p.choices.filter(active=True)
                    ],
                }
                for p in polls[start:end]
                if filter_check(p)
            ],
        }

    def json(self, args=[]):
        self.render("ok")

    def list(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        if "area" in R:
            polls = self._qs_polls()

        self.render(self._render_polls(polls))

    def list_active(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        polls = self._qs_polls()
        _filter = lambda poll: poll.is_valid()

        if int(R.get("finished", 0)) == 1:
            _filter = lambda poll: _filter(poll) and poll.is_finished()
        else:
            polls = polls.filter(Poll.if_published())

        self.render(self._render_polls(polls, _filter))

    @login_required(type="JSON")
    def add_or_edit(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        log = LineLog(request=self.request, level=2034, status=0)

        if P:
            form = PollForm(P)
            if form.is_valid():
                vals = form.cleaned_data

                try:
                    p = None
                    if vals["id"]:
                        p = Poll.objects.get(id=vals["id"])
                        log.level = 2035
                    else:
                        p = Poll()

                    if not p.published_date:
                        p.title = addslashes(vals["title"].replace("\n", ""))
                        p.position = 9999
                        p.as_link = False
                        p.show_partial = vals["show_partial"]

                        user = Servidor.objects.filter(user=self.request.user)
                        if user.exists():
                            p.credits = addslashes(user[0].pessoa_fisica.nome)

                        with transaction.atomic():
                            p.save()

                            if not p.areas.filter(id=vals["area"]).exists():
                                ContentArea(
                                    area=Area.objects.get(id=vals["area"]),
                                    content=p.content_ptr,
                                ).save()
                    else:
                        raise Exception(
                            "Não é permitida alteração desta enquete porque já foi publicada"
                        )

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
                else:
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }

        log.save()

        self.render(rjson)

    def choices(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        rjson = {"total": "0", "result": []}
        if "poll" in R:
            kwargs = {"active": True, "poll": R["poll"]}
            choices = Choice.objects.filter(**kwargs).order_by("choice")
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start

            result = [
                {
                    "id": c.id,
                    "choice": c.choice,
                    "votes": c.votes or "0",
                    "percent": "%s%%" % c.percent or "-",
                    "can_edit": not c.poll.is_locked(),
                }
                for c in choices[start:end]
            ]

            rjson = {"total": choices.count() or "0", "result": result}
        self.render(rjson)

    @login_required(type="JSON")
    def add_or_edit_choice(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        log = LineLog(request=self.request, level=2037, status=0)

        if P:
            form = ChoiceForm(P)
            if form.is_valid():
                vals = form.cleaned_data

                try:
                    poll = Poll.objects.get(id=vals["poll"])
                    if not poll.is_finished():
                        c = None
                        if vals["id"]:
                            c = Choice.objects.get(id=vals["id"])
                            log.level = 2038
                        else:
                            c = Choice()

                        c.choice = addslashes(vals["choice"].replace("\n", ""))
                        c.poll_id = vals["poll"]

                        with transaction.atomic():
                            c.save()

                    else:
                        raise Exception(
                            "Não é permitida alteração desta enquete porque já foi publicada"
                        )

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
                else:
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }

        log.save()

        self.render(rjson)


class CMS(ExtWidget):
    user_areas = None

    def __init__(self, *args, **kwargs):
        super(ExtWidget, self).__init__(*args, **kwargs)
        if not self.user_areas:
            if self.request.user.is_superuser:
                self.user_areas = True
            else:
                if not self.request.user.is_anonymous:
                    self.user_areas = [
                        g.area
                        for g in WebGroup.objects.filter(
                            users=self.request.user, area__active=True
                        )
                    ]

    def json(self, args=[]):
        is_superuser = "true" if self.request.user.is_superuser else "false"
        self.render("getSiteManager(false, {is_superuser:%s})" % is_superuser)

    def get_modules(self, args=[]):
        modules = Module.objects.values("id", "name", "slug")
        self.render({"total": len(modules), "result": list(modules)})

    def get_site_url(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)
        site = R.get("site")
        site_url = (
            Area.objects.get(id=site).get_absolute_url()
            if site
            else "%s/portal" % settings.WEB
        )
        self.render({"total": "0", "result": [{"url": site_url}]})

    def get_sites(self, args=[]):
        sites = []
        if isinstance(self.user_areas, list):
            for a in self.user_areas:
                if a.parent and a.parent not in sites:
                    sites.append(a.parent)
            sites = sorted(sites, key=lambda site: site.name)
        else:
            sites = Area.objects.filter(active=True, parent__isnull=True).order_by(
                "name"
            )
        rjson = {
            "total": len(sites),
            "result": [
                {
                    "id": site.id,
                    "parent": site.parent.id if site.parent else None,
                    "fullname": str(site),
                    "name": site.name,
                    "slug": site.slug,
                    "active": site.active,
                    "as_link": site.as_link,
                    "modules": list(site.modules.values("id", "name", "slug")),
                    "url": site.get_absolute_url(),
                }
                for site in sites
            ],
        }
        self.render(rjson)

    def get_areas(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)
        pars = {
            "active": True,
            "parent__isnull": False,
            "parent__id": int(R["site"]),
            "kind_of_content__iexact": R["kind"],
        }

        if isinstance(self.user_areas, list):
            pars["id__in"] = [a.id for a in self.user_areas]

        areas = Area.objects.filter(**pars).order_by("fullname")
        rjson = {
            "total": len(areas),
            "result": [
                {
                    "id": area.id,
                    "parent": area.parent.id if area.parent else None,
                    "kind_of_content": area.kind_of_content,
                    "fullname": str(area),
                    "name": area.name,
                    "slug": area.slug,
                    "active": area.active,
                    "as_link": area.as_link,
                    "can_share": area.can_share,
                    "url": area.get_absolute_url(),
                    "items_no_searchable": area.items_no_searchable,
                }
                for area in areas
            ],
        }
        self.render(rjson)

    def get_posts(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        rjson = {"total": 0, "result": []}
        if "area" in R:
            kwargs = {"active": True, "areas": R["area"]}

            posts = Post.objects.filter(**kwargs).order_by(
                "position", "-published_date", "-id"
            )
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start

            rjson = {
                "total": posts.count() or "0",
                "result": [
                    {
                        "content": p.content_ptr_id,
                        "id": p.id,
                        "title": p.title,
                        "as_link": p.as_link,
                        "is_index": p.is_index,
                        "published": int(p.published),
                        "create_date": p.create_date,
                        "published_date": p.published_date or "Não publicado",
                        "publication_start": p.publication_start,
                        "publication_end": p.publication_end,
                        "marked_as_published": p.is_published(),
                        "position": p.position,
                        "text": p.text,
                        "link": p.get_domain_absolute_url(),
                        "no_searchable": p.no_searchable,
                        "can_share": any([a.can_share for a in p.areas.all()]),
                        "credits": p.credits,
                        "tags": ", ".join([tag.name for tag in p.tags.all()]),
                    }
                    for p in posts[start:end]
                ],
            }
        self.render(rjson)

    def _get_qs_links(self):
        method = self.request.method
        R = getattr(self.request, method)
        if "area" in R:
            qs = Link.objects.filter(active=True, areas=R["area"])
            if R.get("parent") == "root":
                qs = qs.filter(parent__isnull=True)
            elif R.get("parent"):
                qs = qs.filter(parent=R["parent"])
            return qs.order_by("position", "fullname")
        return Link.objects.empty()

    def get_links_for_menu(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        links = []

        if bool(int(R["posts"])):
            # now = datetime.datetime.now()
            # dynanmic = Q(publication_start__lte=now, publication_end__gte=now)
            # static = Q(published=True)
            links = Post.objects.filter(
                active=True, as_link=True, areas__parent=R["area"]
            ).order_by("-id")
        else:
            links = Area.objects.filter(
                active=True, as_link=True, parent__id=R["area"]
            ).order_by("-id")

        rjson = {
            "total": len(links) or "0",
            "result": [
                {
                    "id": link.id,
                    "fullname": str(link),
                    "slug": link.slug,
                    "url": link.get_absolute_url(),
                    "name": link.name if hasattr(link, "name") else link.title,
                }
                for link in links
            ],
        }

        self.render(rjson)

    def get_links(self, args=[]):
        links = self._get_qs_links()
        result = []
        for l in links:
            result.append(
                {
                    "content": l.content_ptr_id,
                    "id": l.id,
                    "title": l.title,
                    "published": int(l.published),
                    "create_date": l.create_date,
                    "published_date": l.published_date or "Não publicado",
                    "parent": l.parent.id if l.parent else None,
                    "parent_title": l.parent.title if l.parent else None,
                    "publication_start": l.publication_start,
                    "publication_end": l.publication_end,
                    "position": l.position,
                    "marked_as_published": l.is_published(),
                    "url": l.url_embed,
                    "fullname": str(l),
                    "kind": l.kind,
                    "image_url": addslashes(
                        l.get_link("square", 110)
                        or "/%s/static/web/icons/no-image.jpg" % settings.CONTEXT
                    ),
                    "credits": l.credits,
                }
            )
        rjson = {"total": len(links), "result": result}
        self.render(rjson)

    def get_superior_links(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)
        self.log.info(self._get_qs_links())
        links = (
            self._get_qs_links()
            .filter(kind=0)
            .values("id", "title", "fullname", "slug", "kind")
        )
        if R.get("exclude"):
            links = links.exclude(id=R["exclude"])
        self.render({"total": len(links), "result": list(links)})

    def get_links_by_level(self, args=[]):
        qs = self._get_qs_links()
        links = [
            {
                "nodeType": "async",
                "id": link.id,
                "text": link.title,
                "isSuperior": link.kind == 0,
                "leaf": link.kind > 0,
            }
            for link in qs
        ]
        self.render(links)

    def get_prosecutor_actions(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        rjson = {"total": 0, "result": []}
        if "area" in R:
            actions = ProsecutorAction.objects.filter(
                active=True, areas=R["area"]
            ).order_by("status__name", "-id")
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start

            result = []
            for a in actions[start:end]:
                result.append(
                    {
                        "id": a.id,
                        "title": a.title,
                        "content": a.content_ptr_id,
                        "filing": a.filing,
                        "text": a.text,
                        "marked_as_published": a.is_published(),
                        "publication_start": a.publication_start,
                        "publication_end": a.publication_end,
                        "published_date": a.published_date or "Não publicado",
                        "start_date": a.start_date,
                        "decision_date": a.decision_date,
                        "status": a.status.name,
                        "status_id": a.status.id,
                        "county": a.county.nome,
                        "county_id": a.county.id,
                    }
                )

            rjson = {"total": actions.count() or "0", "result": result}
        self.render(rjson)

    def get_metadatas(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        rjson = {"total": 0, "result": []}
        if "content" in R and "site" in R:
            metas = MetaValue.objects.filter(
                active=True, key__site=R.get("site")
            ).exclude(contents=R.get("content"))
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start

            result = []
            for m in metas[start:end]:
                result.append(
                    {
                        "id": m.id,
                        "unicode": str(m),
                        "key": m.key.title,
                        "value": m.value,
                        "fullname": "%s: %s" % (m.key.title, m.value),
                    }
                )

            rjson = {"total": metas.count() or "0", "result": result}
        self.render(rjson)

    def related_metadatas(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        rjson = {"total": 0, "result": []}
        if "content" in R:
            metas = MetaValue.objects.filter(active=True, contents=R.get("content"))
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start

            result = []
            for m in metas[start:end]:
                result.append(
                    {
                        "id": m.id,
                        "unicode": str(m),
                        "key": m.key.title,
                        "value": m.value,
                        "fullname": "%s: %s" % (m.key.title, m.value),
                    }
                )

            rjson = {"total": metas.count() or "0", "result": result}
        self.render(rjson)

    @login_required(type="JSON")
    def unrelate_metadata(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        # log = LineLog(request=self.request, level=2044, status=0)
        metas = P.getlist("metadatas")
        contents = P.getlist("contents")

        try:
            with transaction.atomic():
                for pk in contents:
                    c = Content.objects.get(pk=pk)
                    for mpk in metas:
                        qs = c.metadata.filter(pk=mpk)
                        if qs.exists():
                            m = MetaValue.objects.get(pk=mpk)
                            c.metadata.remove(m)
                    c.clear_cache()
        except Exception as e:
            self.log.exception(e)
            rjson["msg"] += " %s" % e
        else:
            rjson = {"success": True, "msg": "Realizado com sucesso.", "related": metas}
            # log.status = 1

        self.render(rjson)

    @login_required(type="JSON")
    def relate_metadata(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        # log = LineLog(request=self.request, level=2044, status=0)
        metas = P.getlist("metadatas")
        contents = P.getlist("contents")

        try:
            with transaction.atomic():
                for pk in contents:
                    c = Content.objects.get(pk=pk)
                    for mpk in metas:
                        qs = c.metadata.filter(pk=mpk)
                        if not qs.exists():
                            m = MetaValue.objects.get(pk=mpk)
                            c.metadata.add(m)
                    c.clear_cache()
        except Exception as e:
            self.log.exception(e)
            rjson["msg"] += " %s" % e
        else:
            rjson = {"success": True, "msg": "Realizado com sucesso.", "related": metas}
            # log.status = 1

        self.render(rjson)

    @login_required(type="JSON")
    def add_or_edit_prosecutor_action(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        log = LineLog(request=self.request, level=2044, status=0)

        if P:

            form = ProsecutorActionForm(P)
            if form.is_valid():
                vals = form.cleaned_data
                try:
                    action = None
                    if vals["id"]:
                        log.level = 2045
                        action = ProsecutorAction.objects.get(id=vals["id"])
                    else:
                        action = ProsecutorAction()

                    action.title = addslashes(vals["title"])
                    action.start_date = vals["start_date"]
                    action.decision_date = vals["decision_date"]
                    action.filing = addslashes(vals["filing"])
                    action.text = addslashes(vals["text"])
                    action.status = vals["status"]
                    action.county = vals["county"]

                    with transaction.atomic():
                        action.save()

                        params = dict(area=vals["area"], content=action.content_ptr)
                        if not ContentArea.objects.filter(**params).exists():
                            ContentArea(**params).save()

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] += " %s" % e
                else:
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }

        log.save()
        self.render(rjson)

    def get_prosecutor_action_statuses(self, args=[]):
        statuses = list(ProsecutorActionStatus.objects.values())
        self.render({"total": statuses.count() or "0", "result": list(statuses)})

    @login_required(type="JSON")
    def add_or_edit_prosecutor_action_status(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        log = LineLog(request=self.request, level=2041, status=0)

        if P:
            form = ProsecutorActionStatusForm(P)
            if form.is_valid():
                vals = form.cleaned_data
                try:
                    status = None
                    if vals["id"]:
                        log.level = 2042
                        status = ProsecutorActionStatus.objects.get(id=vals["id"])
                    else:
                        status = ProsecutorActionStatus()

                    status.name = addslashes(vals["name"])

                    with transaction.atomic():
                        status.save()

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] += " %s" % e
                else:
                    rjson = {
                        "success": True,
                        "msg": "Realizado com sucesso.",
                        "data": status.id,
                    }
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }
        log.save()

        self.render(rjson)

    def get_counties(self, args=[]):
        counties = (
            County.objects.filter(circunscricao__isnull=False)
            .values("id", "nome")
            .order_by("nome")
        )
        rjson = {"total": counties.count() or "0", "result": list(counties)}
        self.render(rjson)

    def get_attachments(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        rjson = {"total": 0, "result": []}
        if "post" in R and "kind" in R:
            medias = (
                eval(R["kind"])
                .objects.filter(active=True)
                .order_by("position", "title")
            )
            if int(R["exclude"]) == 0:
                medias = medias.filter(posts=R["post"])
            else:
                medias = medias.exclude(posts=R["post"])
            start = int(R.get("start", 0))
            end = int(R.get("limit", 100)) + start

            result = []
            for m in medias[start:end]:

                title = m.title
                if not m.is_public():
                    title = "(Acesso restrito) %s" % title
                else:
                    title = title.replace("(Acesso restrito) ", "")

                result.append(
                    {
                        "id": m.id,
                        "title": title,
                        "embed": m.url_embed,
                        "credits": m.credits,
                        "slug": m.slug,
                        "position": m.position,
                        "is_public": m.is_public(),
                        "url": addslashes(
                            m.get_link("square", 110)
                            if R["kind"] in ["Image", "Video"]
                            else m.get_link()
                        ),
                    }
                )

            rjson = {"total": len(medias), "result": result}

        self.render(rjson)

    @login_required(type="JSON")
    def get_related_users(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        rjson = {"total": 0, "result": []}
        if "area" in R:
            try:
                users = WebGroup.objects.get(area__id=R["area"]).users.all()
            except Exception as e:
                self.log.error("Não existe grupos relacionadas à área. #%s" % e)
            else:
                start = int(R.get("start", 0))
                end = int(R.get("limit", 20)) + start

                rjson = {
                    "total": len(users),
                    "result": [
                        {
                            "id": u.id,
                            "username": u.username,
                            "email": u.email,
                            "fullname": capitalize_words(u.servidor.pessoa_fisica.nome),
                        }
                        for u in users[start:end]
                    ],
                }
        self.render(rjson)

    @login_required(type="JSON")
    def get_users(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)

        rjson = {"total": 0, "result": []}
        if "query" in R and R["query"]:
            qs = Servidor.objects.filter(
                pessoa_fisica__nome__icontains=R["query"], ativo=True
            )
            rjson = {
                "total": len(qs),
                "result": [
                    {"id": i.user.id, "fullname": i.pessoa_fisica.nome}
                    for i in qs
                    if i.user is not None
                ],
            }
        self.render(rjson)

    @login_required(type="JSON")
    def share(self, args=[]):
        rjson = {"success": True, "msg": "Não foi possível realizar compartilhamento."}
        post_id = self.request.POST.get("post")
        if post_id:
            qs = Post.objects.filter(pk=post_id)
            if qs.exists():
                post = qs[0]
                rjson["msg"] = post.share()
        self.render(rjson)

    @login_required(type="JSON")
    def delete(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a deleção"}

        log = LineLog(request=self.request, status=0)
        log_levels = {
            "Area": 2002,
            "Link": 2005,
            "Post": 2008,
            "File": 2011,
            "Image": 2014,
            "Audio": 2017,
            "Video": 2020,
            # 'Category': 2025,
            "User": 2029,
            "Poll": 2036,
            "Choice": 2039,
            "ProsecutorActionStatus": 2043,
            "ProsecutorAction": 2046,
        }

        if "model" in P and P["id"]:
            log.level = log_levels.get(P["model"], "Post")
            for _id in P["id"].split(","):
                try:
                    with transaction.atomic():

                        instance = eval(P["model"]).objects.get(id=_id)

                        if type(instance) is User:
                            area = Area.objects.get(id=P["rel_id"])
                            for child in area.children.all():
                                web_group_qs = WebGroup.objects.filter(area=child)
                                if web_group_qs.exists():
                                    web_group_qs = web_group_qs.latest("id")
                                    web_group_qs.users.remove(instance)
                            WebGroup.objects.get(area=area).users.remove(instance)

                        elif (
                            type(instance) in [Image, Video, Audio, File]
                            and instance.posts.all().count() > 0
                        ):
                            post = Post.objects.get(id=P["rel_id"])
                            instance.posts.remove(post)
                            post.check_attachments()
                            post.save()
                        elif isinstance(instance, Common):
                            if P["model"] == "ProsecutorActionStatus":
                                if instance.prosecutor_actions.filter(
                                    active=True
                                ).exists():
                                    raise Exception(
                                        "Não é possível excluir esta fase de atuação, existem atuações utilizando-a."
                                    )
                            instance.delete()
                        else:
                            if (
                                isinstance(instance, Link)
                                and instance.children.filter(active=True).exists()
                            ):
                                raise Exception(
                                    "Este link possui sublinks, para excluí-lo mova ou exclua todos os seus sublinks."
                                )

                            if isinstance(instance, Area):
                                for child in instance.children.all():
                                    child.active = False
                                    child.save()
                            instance.active = False
                            instance.save()

                except Exception as e:
                    rjson.update(msg=str(e))
                    self.log.exception(e)

                else:
                    rjson = {"success": True, "msg": "Deletado com sucesso."}
                    log.status = 1
        log.save()

        self.render(rjson)

    @login_required(type="JSON")
    def add_or_edit_area(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        log = LineLog(request=self.request, level=2000, status=0)

        if P:
            form = AreaForm(P)
            if form.is_valid():
                vals = form.cleaned_data
                try:
                    area = None
                    if vals["id"]:
                        log.level = 2001
                        area = Area.objects.get(id=vals["id"])
                    else:
                        area = Area()

                    area.name = addslashes(vals["name"])
                    area.kind_of_content = addslashes(
                        vals.get("kind_of_content", "area")
                    )
                    area.as_link = bool(vals["as_link"])
                    area.can_share = bool(vals["can_share"])
                    area.parent_id = vals.get("parent")
                    area.items_no_searchable = vals["items_no_searchable"]

                    with transaction.atomic():
                        area.save()

                        # Retirar este trecho, quando evoluir o sistema de permissões do cms
                        if not WebGroup.objects.filter(area=area).exists():
                            WebGroup(
                                area=area,
                                name="Administração %s" % area,
                                can_add=True,
                                can_change=True,
                                can_delete=True,
                                can_publish=True,
                            ).save()
                        # ------------------------------------------------------------------

                        if area.kind_of_content == "area":
                            modules = vals.get("modules", [])
                            area.modules.clear()
                            for module in modules:
                                area.modules.add(module)

                    package = None
                    if vals["auto_create"]:
                        area.title = vals["title"]
                        package = make_site(area)

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] += " %s" % e
                else:
                    rjson = {
                        "success": True,
                        "msg": "Realizado com sucesso.",
                        "download": package,
                    }
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }

        log.save()

        self.render(rjson)

    @login_required(type="JSON")
    def create_permissions(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível criar permissões."}

        if P:
            form = GroupPermissionsForm(P)
            if form.is_valid():
                vals = form.cleaned_data
                try:
                    profiles = {
                        "adm": "Administração",
                        "rev": "Revisão",
                        "ali": "Alimentação",
                    }

                    area = Area.objects.get(id=int(vals["area"]))
                    children = [area]
                    if area.children.filter(active=True).exists():
                        children = area.children.filter(active=True)

                    profile = profiles[vals["profile"]]

                    with transaction.atomic():
                        for a in children:
                            group_name = "%s  %s" % (profile, a)
                            group, created = WebGroup.objects.get_or_create(
                                area=a,
                                defaults=dict(
                                    area=a,
                                    name=group_name,
                                    can_add=True,
                                    can_change=True,
                                    can_delete=True,
                                    can_publish=True,
                                ),
                            )

                            users = [
                                User.objects.get(id=int(user_id))
                                for user_id in vals["users"].split(",")
                                if not group.users.filter(id=int(user_id)).exists()
                            ]

                            group.users.add(*users)

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] += " %s" % e
                    raise e
                else:
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }
        else:
            rjson["msg"] += " A requisição deve ser feita via POST"

        self.render(rjson)

    @login_required(type="JSON")
    def create_permissions_subarea(self, args=[]):
        rjson = {"success": False, "msg": "Não foi possível criar permissões."}

        if self.request.user.is_superuser:
            try:
                P = self.request.POST
                webgroup = get_object_or_404(WebGroup, pk=P["id"])
                subareas = webgroup.area.descendants()
                users = webgroup.users.all()
                if subareas:
                    for item in subareas:
                        group, created = WebGroup.objects.get_or_create(
                            can_add=webgroup.can_add,
                            can_change=webgroup.can_change,
                            can_delete=webgroup.can_delete,
                            can_publish=webgroup.can_publish,
                            area=item,
                            defaults={
                                "can_add": webgroup.can_add,
                                "can_change": webgroup.can_change,
                                "can_delete": webgroup.can_delete,
                                "can_publish": webgroup.can_publish,
                                "area": item,
                                "name": "Administração %s" % item,
                            },
                        )
                        group.users.add(*users)
                        group.save()
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
                else:
                    rjson[
                        "msg"
                    ] += f"Não existe(m) subárea(s) cadastrada(s) para {webgroup.area}"
            except Exception as e:
                self.log.exception(e)
                rjson["msg"] += " %s" % e
                raise e
        else:
            rjson["msg"] += " Usuário não possuí permissão para esta ação"

        self.render(rjson)

    @login_required(type="JSON")
    def add_or_edit_post(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        log = LineLog(request=self.request, level=2006, status=0)

        if P:
            form = PostForm(P)
            if form.is_valid():
                vals = form.cleaned_data

                try:
                    p = None
                    if vals["id"]:
                        p = Post.objects.get(id=vals["id"])
                        log.level = 2007
                    else:
                        p = Post()

                    p.title = addslashes(vals["title"].replace("\n", ""))
                    p.text = addslashes(vals["text"].replace("\n", "<br/>"))
                    p.position = vals["position"]
                    p.as_link = vals["as_link"] or False
                    p.is_index = vals["is_index"] or False
                    p.no_searchable = vals["no_searchable"] or False
                    p.credits = get_employee_name(self.request.user)

                    area = Area.objects.get(id=vals["area"])
                    if "galeria" in area.slug:
                        p.as_gallery = True

                    with transaction.atomic():
                        p.save()

                        if not p.areas.filter(id=area.id).exists():
                            ContentArea(area=area, content=p.content_ptr).save()

                        if not vals["tags"]:
                            p.tags.clear()
                        else:
                            for tag in vals["tags"].split(","):
                                if slugify(tag) not in getattr(
                                    settings, "PROHIBITED_TAGS", []
                                ):
                                    tag = tag.strip()
                                    if not p.tags.filter(slug=slugify(tag)).exists():
                                        t, created = Tag.objects.get_or_create(
                                            slug=slugify(tag),
                                            defaults={
                                                "name": tag,
                                                "slug": slugify(tag),
                                            },
                                        )
                                        p.tags.add(t)

                            tags = p.tags.exclude(
                                slug__in=[
                                    slugify(tag) for tag in vals["tags"].split(",")
                                ]
                            )
                            if tags.exists():
                                p.tags.remove(*tags)

                except Exception as e:
                    self.log.exception(e)
                else:
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }

        log.save()

        self.render(rjson)

    @login_required(type="JSON")
    def add_or_edit_link(self, args=[]):
        P = self.request.POST
        F = self.request.FILES
        rjson = {"success": False, "msg": "Não foi possível realizar a operação"}

        log = LineLog(request=self.request, level=2003, status=0)

        if P:
            form = LinkForm(P)
            if form.is_valid():
                vals = form.cleaned_data
                try:

                    l = None
                    if vals["id"]:
                        l = Link.objects.get(id=vals["id"])
                        log.level = 2004
                    else:
                        l = Link()

                    l.title = addslashes(vals["title"])
                    l.position = vals["position"]
                    l.kind = vals["kind"]
                    l.url_embed = addslashes(vals["url"])
                    l.credits = get_employee_name(self.request.user)

                    if (
                        l.pk
                        and vals.get("parent")
                        and vals.get("parent") in l.descendants(pk_only=True)
                    ):
                        raise Exception(
                            "Link filho não pode ser link superior do próprio pai."
                        )

                    l.parent_id = vals.get("parent")

                    with transaction.atomic():
                        if "image" in F:
                            l.is_banner = True
                            l.ged = GedFile.create_ged(F["image"])
                        l.save()

                        if not l.areas.filter(id=vals["area"]).exists():
                            ContentArea(
                                area=Area.objects.get(id=vals["area"]),
                                content=l.content_ptr,
                            ).save()

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] = "%s #%s" % (rjson["msg"], e)
                else:
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }

        log.save()

        self.render(rjson)

    @login_required(type="JSON")
    def add_or_edit_attachment(self, args=[]):
        method = self.request.method
        R = getattr(self.request, method)
        P = R.copy()

        try:
            rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

            log_levels = {
                "File": (2009, 2010),
                "Image": (2012, 2013),
                "Audio": (2015, 2016),
                "Video": (2018, 2019),
            }

            log = LineLog(request=self.request, level=2009, status=0)

            if self.request.method == "POST":
                form = MultimediaForm(P, self.request.FILES)
                if form.is_valid():
                    vals = form.cleaned_data

                    media = None
                    if vals["id"]:
                        media = eval(vals["kind"]).objects.get(id=vals["id"])
                        log.level = log_levels[vals["kind"]][1]
                    else:
                        media = eval(vals["kind"])()
                        log.level = log_levels[vals["kind"]][0]

                    media.title = addslashes(vals["title"])
                    media.credits = vals.get("credits") or ""
                    media.position = addslashes(vals["position"])
                    media.public_access = vals.get("public_access")
                    media.url_embed = addslashes(vals["url_embed"])

                    with transaction.atomic():
                        ged = None
                        if vals["upfile"]:
                            ged = GedFile.create_ged(vals["upfile"])
                            # media.save_file(vals['upfile'], self.request.user)
                        elif isinstance(media, Video):

                            match = re.search(
                                r'<.+ src="([a-zA-Z0-9_:\-\./\?=]+)".*>.*</.+>',
                                vals["url_embed"],
                            )
                            if match and len(match.groups()) > 0:

                                key = match.groups()[0].split("/")[-1]
                                if "?" in key:
                                    key = key.split("?")[0]

                                url = "https://img.youtube.com/vi/%s/" % key

                                image = {}
                                try:
                                    image = urllib.request.urlopen(
                                        url + "maxresdefault.jpg"
                                    )
                                except:
                                    image = urllib.request.urlopen(
                                        url + "hqdefault.jpg"
                                    )

                                image.name = vals["title"]
                                image.content_type = "image/jpeg"
                                ged = GedFile.create_ged(image)
                                # media.ge.save_file(image, self.request.user)
                        if ged:
                            media.ged = ged
                        # media.publish()
                        media.save()

                        post = Post.objects.get(id=vals["post"])

                        media.posts.add(post)
                        post.check_attachments()
                        post.save()

                else:
                    rjson["errors"] = err2dict(form)
                    raise Exception("Formulário inválido! Ocorreram erros nos campos:")
            else:
                raise Exception("Requisição sem informações para inserção")

        except Exception as e:
            self.log.exception(e)
            rjson["msg"] = str(e)
        else:
            log.status = 1
            rjson = {"success": True, "msg": "Realizado com sucesso."}

        log.save()

        self.render(rjson)

    @login_required(type="JSON")
    def create_publication(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a publicação."}

        log = LineLog(request=self.request, level=2021, status=0)

        if P:
            form = PublicationForm(P)
            if form.is_valid():
                vals = form.cleaned_data
                try:
                    c = Content.objects.get(id=vals["content"])

                    params = {}
                    method_name = "publish"
                    if bool(vals["published"]) or vals["publication_start"]:

                        if vals["publication_start"] and vals["publication_end"]:
                            if vals["publication_start"] > vals["publication_end"]:
                                ex = Exception("Data de incio maior que a data final.")
                                self.log.exception(ex)
                                raise ex

                            params = {
                                "start": vals["publication_start"],
                                "end": vals["publication_end"],
                            }

                        elif bool(vals["published"]):
                            if vals["published_date"]:
                                params = {"start": vals["published_date"]}
                    else:
                        method_name = "unpublish"
                        log.level = 2022

                    with transaction.atomic():
                        if vals.get("cascade") and hasattr(c, "multimedia"):
                            media = c.multimedia
                            if hasattr(media, "link"):
                                link = media.link
                                link.cascade_publish(method_name, **params)
                        else:
                            getattr(c, method_name)(**params)
                            c.save()

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] += " #" + str(e)
                else:
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
                    if not c.is_published():
                        c.clear_cache()
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }

        log.save()

        self.render(rjson)

    @login_required(type="JSON")
    def relate_user(self, args=[]):
        P = self.request.POST
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        log = LineLog(request=self.request, level=2028, status=0)

        if P:
            form = RelateUserForm(P)
            if form.is_valid():
                vals = form.cleaned_data
                try:
                    group = WebGroup.objects.get(area=vals["area"])
                    if not group.users.filter(id=vals["user"]).exists():

                        with transaction.atomic():
                            group.users.add(User.objects.get(id=vals["user"]))

                except Exception as e:
                    self.log.exception(e)
                    rjson["msg"] += " #%s" % e
                else:
                    rjson = {"success": True, "msg": "Realizado com sucesso."}
                    log.status = 1
            else:
                rjson = {
                    "success": False,
                    "errors": err2dict(form),
                    "msg": "Ocorreram erros nos campos a seguir:",
                }

        log.save()

        self.render(rjson)

    @is_public()
    def download(self, args=[]):
        if args:
            try:

                slug = "/".join(args)
                self.log.info(slug)
                self.log.info(self.request.META.get("HTTP_REFERER"))
                f = Multimedia.objects.filter(active=True, slug=slug)
                if f.count() > 1:
                    self.log.info(
                        "CMSTRACK slug: %s - Returned %s objects. Getting the latest."
                        % (slug, f.count())
                    )
                f = f.latest("id")
                f.views += 1
                f.save()
                path = f.ged.file.absolute_path

                file_open = open(path)
                bin = file_open.read()
                file_open.close()

                ext = f.ged.filename.split(".")[-1]
                name = "%s.%s" % (f.slug.replace("/", "-"), ext)

                self.response["Content-Disposition"] = (
                    "attachment; filename=%s" % name.encode("u8")
                )
                self.response["Content-Type"] = f.ged.mimetype

                self.render(bin)

            except Exception as e:
                self.log.exception(e)

    def image(self, args=[]):
        post_slug = "/".join(args[:4])
        self.log.error("Post %s using deprecated CMS.image action." % post_slug)
        self.render("Deprecated action. Args: %s" % post_slug)


class CMSSetup(ExtWidget):

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render("new toolkit.web.cms.Setup()")

    @ContentType("text/javascript")
    def commit(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        cfg = Configuration.get_or_create("cms")
        for key in list(self.request.POST.keys()):
            cfg.set(key, self.request.POST.get(key))

        obj.update(success=True)

        self.render(json.encode(obj))

    @ContentType("text/javascript")
    def load(self, args=[]):
        cfg = Configuration.get_or_create("cms")
        cfg.save()

        obj = {
            "twitter_user": cfg.get("twitter_user"),
            "twitter_user_token": cfg.get("twitter_user_token"),
            "twitter_user_token_secret": cfg.get("twitter_user_token_secret"),
            "twitter_app": cfg.get("twitter_app"),
            "twitter_app_token": cfg.get("twitter_app_token"),
            "twitter_app_token_secret": cfg.get("twitter_app_token_secret"),
            "bitly_user": cfg.get("bitly_user"),
            "bitly_token": cfg.get("bitly_token"),
            "frontend": cfg.get("frontend"),
        }

        self.render(json.encode(obj))


from common.poll.models import Poll


class Intranet(ExtWidget):

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def json(self, args=[]):

        employee = employee_from_user(self.request.user)

        if employee:
            self.log.info("Intranet track => servidor: %s" % employee)
            self.log.info("Intranet track => servidor é membro: %s" % employee.membro)
            self.log.info(
                "Intranet track => servidor está afastado: %s"
                % employee.afastamento_ativo()
            )
            self.log.info(
                "Intranet track => servidor checagem de expressão booleana: %s"
                % (not employee.membro and employee.afastamento_ativo())
            )
        else:
            self.log.error("Nenhum servidor associado ao usuário %s", self.request.user)

        employee_removed = (
            None
            if not self._is_employee_removed()
            else {
                "name": person_from_user(self.request.user).nome,
                "reason": self._get_employee_status(),
            }
        )

        polls = Poll.polls_by_user(self.request.user)

        self.render(
            "new toolkit.web.intranet.App({employeeRemoved: %s, hasToVote: %s})"
            % (json.dump(employee_removed), json.dump(len(polls) > 0))
        )

    def _get_employee_restriction(self):
        employee = employee_from_user(self.request.user)
        return employee.get_afastamentos()[0].baselicencaafastamento

    def _get_employee_status(self):
        return format_position(self._get_employee_restriction().situacao_funcional)

    def _is_employee_removed(self):
        employee = employee_from_user(self.request.user)

        if employee and (not employee.membro and employee.afastamento_ativo()):
            restriction = self._get_employee_restriction().tipo
            return restriction not in [6, 26, 27, 40]
        return False

    def _is_employee_retired(self):
        employee = employee_from_user(self.request.user, only_active=False)
        return employee and employee.aposentado

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def get_menu(self, args=None):
        from default.views import Application
        from engine.models import Application as AppModel

        args = args or []
        menu_items = []
        title = "portal do servidor"

        try:
            if self._is_employee_retired():
                title = f"{title} aposentado"
            elif self._is_employee_removed():
                title = f"{title} afastado"

            root = AppModel.objects.get(title__iexact=title)
            menu_items = Application(self.request, self.response).get_leaf_menu(root)
        except Exception as e:
            log.exception(str(e))

        menu_items += [
            {
                "text": "Ponto Eletrônico",
                "href": "http://ifponto.mpto.mp.br/",
                "target": "_blank",
            }
        ]

        self.render(
            {
                "total": len(menu_items),
                "list": menu_items,
            }
        )

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def get_birthdays(self, args=[]):
        import calendar
        from rh.models import Servidor

        params = self.request.GET.dict()
        days = int(params.get("days", 7))
        start_date = datetime.date.today()
        limit_date = start_date + datetime.timedelta(days=days)

        qs = Servidor.objects.filter(
            pessoa_fisica__data_nascimento__month=start_date.month
        )

        if (limit_date.year > start_date.year) or (limit_date.month > start_date.month):
            start_day = start_date.day
            last_month_day = calendar.monthrange(start_date.year, start_date.month)[1]
            last_day = limit_date.day

            qs_first_month = qs
            qs_last_month = Servidor.objects.filter(
                pessoa_fisica__data_nascimento__month=limit_date.month
            )

            q_days_first = None
            for day in range(start_day, last_month_day + 1):
                q_days_first = (
                    Q(pessoa_fisica__data_nascimento__day=day)
                    if not q_days_first
                    else q_days_first | Q(pessoa_fisica__data_nascimento__day=day)
                )

            q_days_last = None
            for day in range(1, last_day + 1):
                q_days_last = (
                    Q(pessoa_fisica__data_nascimento__day=day)
                    if not q_days_last
                    else q_days_last | Q(pessoa_fisica__data_nascimento__day=day)
                )
            qs = list(qs_first_month.filter(q_days_first)) + list(
                qs_last_month.filter(q_days_last)
            )
        else:
            q_days = None
            for day in range(start_date.day, limit_date.day + 1):
                q_days = (
                    Q(pessoa_fisica__data_nascimento__day=day)
                    if not q_days
                    else q_days | Q(pessoa_fisica__data_nascimento__day=day)
                )
            qs = list(qs.filter(q_days))

        birthdays = []
        unique_check = []
        for employee in qs:

            if employee.aposentado:
                self.log.info("Aposentado: %s " % employee)

            if (
                hasattr(employee, "pessoa_fisica")
                and employee.ativo
                and employee.workplace_current
                and not employee.aposentado
            ):

                photo_url = ""
                if employee.pessoa_fisica.foto:
                    path = employee.pessoa_fisica.foto.absolute_path
                    mimetype = employee.pessoa_fisica.foto.mimetype
                    if os.path.exists(path) and mimetype in ["image/jpeg", "image/png"]:
                        photo_url = employee.pessoa_fisica.foto.complete_permalink()

                if employee.pessoa_fisica.nome not in unique_check:
                    unique_check.append(employee.pessoa_fisica.nome)

                    birthdays.append(
                        {
                            "photo_url": photo_url,
                            "name": capitalize_words(employee.pessoa_fisica.nome),
                            "department": capitalize_words(
                                str(employee.workplace_current or "[Sem lotação ativa]")
                            ),
                            "day": employee.pessoa_fisica.data_nascimento.strftime(
                                "%d"
                            ),
                            "month": employee.pessoa_fisica.data_nascimento.strftime(
                                "%m"
                            ),
                            "birthdate": employee.pessoa_fisica.data_nascimento.strftime(
                                "%d/%m"
                            ),
                        }
                    )

        birthdays = sorted(birthdays, key=lambda x: x["day"])
        if limit_date.year > start_date.year:
            birthdays = sorted(birthdays, key=lambda x: x["month"], reverse=True)
        else:
            birthdays = sorted(birthdays, key=lambda x: x["month"])

        self.render({"total": len(birthdays), "list": birthdays})

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def get_news(self, args=[]):
        from web.services.rpc import CMSServer

        params = self.request.GET.dict()
        reverse = params.pop("reverse") if "reverse" in params else False
        if "_dc" in params:
            params.pop("_dc")

        search_by = params.pop("search_by") if "search_by" in params else False
        if search_by:
            params["slug__icontains"] = slugify(search_by)

        data = CMSServer().get_posts(params)

        posts = data.get("list", [])
        for post in posts:
            post["date"] = post["published_date"].strftime("%d/%m/%Y")
            post["abstract"] = "%s..." % striptags(post["abstract"])
            post["front_image_url"] = (
                post["images"][0]["url"]
                if len(post["images"]) > 0 and "url" in post["images"][0]
                else ""
            )

        if reverse:
            posts.reverse()

        self.render(data)

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def get_today_mpe_episodes(self, args=[]):
        from web.services.rpc import CMSServer

        params = self.request.GET.dict()

        if "_dc" in params:
            params.pop("_dc")

        search_by = params.pop("search_by") if "search_by" in params else False
        if search_by:
            params["slug__icontains"] = slugify(search_by)

        data = CMSServer().get_posts(params)

        posts = data.get("list", [])
        for post in posts:
            post["date"] = post["published_date"].strftime("%d/%m/%Y")
        data["list"] = posts  # sorted(posts, key=lambda x: x['published_date'])

        self.render(data)

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def get_post(self, args=[]):
        from web.services.rpc import CMSServer

        params = self.request.GET.dict()

        if "_dc" in params:
            params.pop("_dc")

        post = CMSServer().get_post(params)
        if isinstance(post, dict):
            post["front_image_url"] = ""
            post["front_image_title"] = ""

            if len(post["images"]) > 0:
                post["front_image_url"] = post["images"][0]["url"]
                post["front_image_title"] = post["images"][0]["title"]
                post["images"][-1]["is_last"] = True

            post["more_images"] = False
            if len(post["images"]) > 1:
                post["more_images"] = True
                list([x.update(is_last=False) for x in post["images"][:-1]])

            post["has_files"] = len(post["files"]) > 0

        self.render(post)


# class Polls(ExtWidget):

#     @login_required(type='JSON')
#     @ContentType('text/javascript')
#     def json(self, args=[]):
#         self.render('new toolkit.web.cms.activePolls("intranet")')


class PollReport(ExtReportBuild):

    from django import forms

    report_src = "/to/mpe/web/enquete/resultado_enquete"

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/web/enquete/"}
    ]

    def get_generated_filename(self):
        filename = ""
        try:
            method = self.request.method
            R = getattr(self.request, method)
            poll = Content.objects.get(pk=R.get("enquete"))
        except Exception as e:
            filename = "enquete-indisponivel"
            self.log.exception(e)
        else:
            filename = "resultado-da-enquete-%(poll)s" % {"poll": poll.title}
        return "%s.pdf" % slugify(filename)

    class Form(forms.Form):
        enquete = forms.CharField()
