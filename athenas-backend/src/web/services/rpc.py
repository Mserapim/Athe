# -*- coding:utf-8 -*-

import datetime  # , time
import math
import random
import re
from html.parser import HTMLParser
from threading import Thread

from django.db.models import Count, Q
from django.template.defaultfilters import addslashes, striptags

from contrib.helpers import capitalize_words
from contrib.utils import getLogger
from rh.models import Comarca as County
from standard.models import Choice
from web.models import (
    Area,
    Content,
    File,
    Image,
    Link,
    Post,
    ProsecutorAction,
    Tag,
    Video,
)

log = getLogger(__name__)


def get_abstract(text):
    length = 180
    text = striptags(HTMLParser().unescape(text or ""))
    match = re.search(".+[a-z]{1}[A-Z]{1}", text)
    if match:
        token = match.group()[:-1]
        text = text.replace(token, "")
    if len(text) > length:
        text = text[:length]
    return text


class CMSServer(object):

    def __init__(self):
        self.__threads = []
        self.__control_params = [
            "filling",
            "image-width",
            "image-zoom-width",
            "image-sizes",
            "image-cut-mode",
            "length",
            "limit",
            "page",
            "start",
        ]

    def __normalize_values(self, values):
        params = values.copy() if isinstance(values, dict) else dict(values)

        for k, v in list(params.items()):
            if v == "None":
                params[k] = None
            if isinstance(v, str) and v.capitalize() == "True":
                params[k] = True
            if isinstance(v, str) and v.capitalize() == "False":
                params[k] = False
            if "__in" in k and isinstance(v, str):
                params[k] = eval(v)
            if k.startswith("areas") and not v:
                del params[k]
            if "image-sizes" in k and isinstance(v, str):
                sizes = []
                v = v.replace(" ", "")
                for part in v.split(","):
                    if "|" in part:
                        coord, size = part.split("|")
                        part = [coord, int(size)]
                    else:
                        part = ["width", int(part)]
                    sizes.append(part)
                params[k] = sizes
        return params

    def __extract(self, prefix, values):
        extracted = {}

        for k, v in list(values.items()):
            if k.startswith(prefix):
                key = k.replace(prefix, "")
                val = values.pop(k)
                extracted[key] = val

        return extracted

    def __extract_order(self, values):
        pass

    def __filter_by(self, values, filter_lambda):
        values = self.__normalize_values(values)
        return dict([[k, v] for k, v in list(values.items()) if filter_lambda(k)])

    def __get_query_params(self, values):
        values = self.__filter_by(values, lambda k: k not in self.__control_params)
        values["active"] = True
        return values

    def __get_control_params(self, values):
        values = self.__filter_by(values, lambda k: k in self.__control_params)

        values["length"] = int(values.get("length", values.get("limit", 15)))

        if "start" in values:
            values["start"] = int(values["start"])
            values["end"] = values["length"] + values["start"]
        else:
            page = values.get("page", 1)
            if not isinstance(page, int):
                token = "?page="
                if token in page:
                    page = page.split(token)[-1]

            page = float(page)
            values["page"] = int(page) if page.is_integer() else math.floor(page)
            values["end"] = values["page"] * values["length"]
            values["start"] = values["end"] - values["length"]

        return values

    def __get_slice(self, mixed, func=None):
        if func:
            mixed = list(filter(func, mixed))
        return mixed

    def __sort_links(
        self, links, img_mode, img_w, func=lambda x: x.parent_id is None, iteration=0
    ):
        iteration += 1
        level = self.__get_slice(list(links), func)
        if not level and iteration == 1:
            level = list(links)

        for i in range(len(level)):
            areas = self.get_areas(
                {"contents": level[i].content_ptr_id, "page": 1, "length": 1}
            )["list"]

            level[i] = {
                "id": level[i].id,
                "title": level[i].title,
                "url": level[i].url_embed,
                "has_child": level[i].has_child(),
                "has_parent": True if level[i].parent else False,
                "kind": level[i].kind or "0",
                "url_image": level[i].get_link(img_mode or "width", img_w),
                "area": areas[0] if areas else None,
                "children": self.__sort_links(
                    links,
                    img_mode,
                    img_w,
                    lambda x: level[i].id == x.parent_id,
                    iteration,
                ),
            }
        return level

    def get_links(self, values={}):
        query_params = self.__get_query_params(values)
        controls = self.__get_control_params(values)

        qs = Link.objects.filter(Link.if_published(), **query_params).order_by(
            "position", "fullname"
        )

        sorted_links = self.__sort_links(
            qs[controls["start"] : controls["end"]],
            controls.get("image-cut-mode"),
            controls.get("image-width"),
        )

        return {"total": qs.count() or "0", "list": sorted_links}

    def pong(self, values={}):
        return dict(success=True, message="Pong.")

    def get_areas(self, values={}):
        query_params = self.__get_query_params(values)
        controls = self.__get_control_params(values)

        qs = Area.objects.filter(**query_params).order_by("fullname")
        data = {
            "total": qs.count(),
            "list": [
                {
                    "name": area.name,
                    "slug": area.slug,
                    "url": area.get_absolute_url(),
                    "kind_of_content": area.kind_of_content,
                    "amount_content": area.contents.filter(
                        Content.if_published(), active=True
                    ).count(),
                    "parent": (
                        {
                            "name": area.parent.name,
                            "slug": area.parent.slug,
                            "url": area.parent.get_absolute_url(),
                        }
                        if area.parent
                        else None
                    ),
                }
                for area in qs[controls["start"] : controls["end"]]
            ],
        }

        return data

    def __get_posts_base_qs(self, values, exclude={}, order=[]):
        query_params = self.__get_query_params(values)
        # controls = self.__get_control_params(values)

        qs = Post.objects.filter(Post.if_published(), **query_params)

        if exclude:
            exclude_params = self.__get_query_params(exclude)
            if "active" in exclude_params:
                exclude_params.pop("active")
            qs = qs.exclude(**exclude_params)

        if not order:
            order = ["position", "-published_date", "-id"]
        return qs.order_by(*order)

    def __posts_parser(self, qs, values={}):

        controls = self.__get_control_params(values)
        data = {"total": qs.count() or "0", "list": []}

        unique_list = []

        for post in qs[controls["start"] : controls["end"]]:
            if post.pk not in unique_list:
                unique_list.append(post.pk)
                # abstract = get_abstract(post.text)

                videos = self.get_videos(
                    {
                        "posts": post.id,
                        "page": 1,
                        "length": 1,
                        "image-width": controls.get("image-width"),
                        "image-cut-mode": controls.get("image-cut-mode"),
                        "image-zoom-width": controls.get("image-zoom-width"),
                        "image-sizes": controls.get("image-sizes"),
                    }
                )["list"]

                images = self.get_images(
                    {
                        "posts": post.id,
                        "page": 1,
                        "length": 1,
                        "image-width": controls.get("image-width"),
                        "image-cut-mode": controls.get("image-cut-mode"),
                        "image-zoom-width": controls.get("image-zoom-width"),
                        "image-sizes": controls.get("image-sizes"),
                    }
                )["list"]

                data["list"].append(
                    {
                        "id": post.id,
                        "title": post.title,
                        "abstract": post.abstract,
                        "full_title": "%s[:sep:]%s" % (post.title, post.abstract),
                        "slug": post.slug,
                        # 'text': striptags(post.text),
                        "published_date": post.published_date,
                        "url": post.get_absolute_url(),
                        "as_gallery": post.as_gallery,
                        # 'tags': self.get_tags({'contents': post.content_ptr_id})['list'],
                        "files": self.get_files({"posts": post.id})[
                            "list"
                        ],  # Não remover porque usa no extrato e requerimentos da intranet
                        "images": images,
                        "media": videos + images,
                        "area": self.get_areas(
                            {
                                "page": 1,
                                "length": 1,
                                "contents": post.content_ptr_id,
                            }
                        )["list"][0],
                    }
                )

        return data

    def get_posts(self, values={}):
        exclude = self.__extract("_exclude_", values)
        order = self.__extract("_order", values).get("_") or ""
        if order:
            order = order.split(",")
        qs = self.__get_posts_base_qs(values, exclude, order)
        return self.__posts_parser(qs, values)

    def get_related_posts(self, post, values={}):

        qs = self.__get_posts_base_qs(values).exclude(
            Q(id=post) | Q(areas__parent__slug="intranet")
        )
        return self.__posts_parser(qs, values)

    def get_tags(self, values={}):
        query_params = self.__get_query_params(values)
        controls = self.__get_control_params(values)

        qs = Tag.objects.filter(**query_params)
        data = {
            "total": qs.count() or "0",
            "list": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "slug": tag.slug,
                    "url": tag.get_absolute_url(),
                }
                for tag in qs[controls["start"] : controls["end"]]
            ],
        }

        return data

    def get_files(self, values={}):
        return self.get_attachments(values, File)

    def get_images(self, values={}):
        return self.get_attachments(values, Image)

    def get_videos(self, values={}):
        return self.get_attachments(values, Video)

    def __create_thread(self, target, *args):
        t = Thread(target=target, args=args)
        self.__threads.append(t)
        t.run()

    def __create_image(self, url_box, attachment, mode, size):
        url_box["url_size_%s" % size] = addslashes(attachment.get_link(mode, size))

    # def __there_are_threads_running(self):
    #     for t in self.__threads:
    #         if t.is_alive():
    #             return True
    #     return False

    def get_attachments(self, values={}, kind=Image):
        query_params = self.__get_query_params(values)
        controls = self.__get_control_params(values)

        # log.info(controls)

        qs = kind.objects.filter(**query_params).order_by("position", "title")

        attachments = []
        for item in qs[controls["start"] : controls["end"]]:

            urls = {}
            if controls.get("image-width"):
                urls["url"] = addslashes(
                    item.get_link(
                        controls.get("image-cut-mode") or "width",
                        controls["image-width"],
                    )
                )
            else:
                urls["url"] = addslashes(item.get_link())

            if controls.get("image-zoom-width"):
                urls["url_zoom"] = addslashes(
                    item.get_link(
                        controls.get("image-cut-mode") or "width",
                        controls["image-zoom-width"],
                    )
                )

            for image_size in controls.get("image-sizes") or []:
                mode, size = image_size
                self.__create_image(urls, item, mode, size)

            attachment = {
                "id": item.id,
                "slug": item.slug,
                "title": item.title,
                "credits": item.credits,
                "embed": "",
            }

            match = re.search(
                r'<.+ src="([a-zA-Z0-9_:\-\./\?=]+)".*>.*</.+>',
                item.url_embed.replace("\\", ""),
            )
            if match and len(match.groups()) > 0:
                attachment.update(embed=match.groups()[0])

            attachment.update(urls)
            attachments.append(attachment)

        return {"total": qs.count() or "0", "list": attachments}

    def get_post(self, values={}):
        data = None

        query_params = self.__get_query_params(values)
        controls = self.__get_control_params(values)

        try:
            post = Post.objects.filter(Post.if_published(), **query_params).last()
            if not post:
                raise Exception("Post not found")
        except Exception as e:
            data = "%s. Params: %s" % (e, query_params)
            log.error(data)
        else:
            tags = self.get_tags({"contents": post.content_ptr_id})["list"]
            tag_ids = [tag["id"] for tag in tags]

            images = self.get_images(
                {
                    "posts": post.id,
                    "page": 1,
                    "length": 100,
                    "image-width": controls.get("image-width"),
                    "image-cut-mode": controls.get("image-cut-mode"),
                    "image-zoom-width": controls.get("image-zoom-width"),
                    "image-sizes": controls.get("image-sizes"),
                }
            )["list"]

            videos = self.get_videos(
                {
                    "posts": post.id,
                    "page": 1,
                    "length": 100,
                    "image-width": controls.get("image-width"),
                    "image-cut-mode": controls.get("image-cut-mode"),
                    "image-zoom-width": controls.get("image-zoom-width"),
                    "image-sizes": controls.get("image-sizes"),
                }
            )["list"]

            data = {
                "title": post.title,
                "slug": post.slug,
                "text": post.text,
                "url": post.get_absolute_url(),
                "as_gallery": post.as_gallery,
                "published_date": post.published_date,
                "breadcrumb": post.breadcrumb(),
                "tags": tags,
                "related": self.get_related_posts(
                    post.id,
                    {
                        "tags__in": tag_ids,
                        "length": 6,
                        "image-sizes": controls.get("image-sizes"),
                    },
                )["list"],
                "area": self.get_areas(
                    {
                        "page": 1,
                        "length": 1,
                        "contents": post.content_ptr_id,
                    }
                )["list"][0],
                "files": self.get_files({"posts": post.id, "page": 1, "length": 300})[
                    "list"
                ],
                "images": images,
                "videos": videos,
                "media": videos + images,
            }

        return data

    def get_cloud_tags(self, values={}):
        query_params = self.__get_query_params(values)

        obj = {}

        now = datetime.datetime.now()
        dynanmic = Q(
            contents__publication_start__lte=now, contents__publication_end__gte=now
        )
        static = Q(contents__published=True)
        not_null = Q(contents__isnull=False, contents__active=True)

        tags = (
            Tag.objects.filter(dynanmic | static, not_null, **query_params)
            .distinct()
            .annotate(count=Count("contents"))
            .order_by("-count")[:50]
        )

        relevances = (
            (10, "relevance_0"),
            (15, "relevance_1"),
            (30, "relevance_2"),
            (45, "relevance_3"),
            (60, "relevance_4"),
            (75, "relevance_5"),
            (90, "relevance_6"),
            # (55, 'relevance_7'),
            # (60, 'relevance_8'),
            # (65, 'relevance_9'),
            # (70, 'relevance_10')
        )

        total = Post.objects.filter(tags__in=[tag.pk for tag in tags]).count()

        collection = []
        for tag in tags:
            relevance = "relevance_0"
            for k, v in relevances:
                if tag.count <= k:
                    relevance = v
                    break
                if tag.count > relevances[-1][0]:
                    relevance = "relevance_6"
            collection.append(
                {
                    "slug": tag.slug,
                    "name": tag.name.lower(),
                    "relevance": relevance,
                    "count": tag.count,
                }
            )
        random.shuffle(collection)
        obj.update(
            {"list": collection, "total": tags.count() or "0", "totalPosts": total}
        )

        return obj

    def get_official_docs(self, values={}):
        """
        Ato => 1, Portarias => 3, Despachos => 5
        """
        from rh.models import Publicacao as OfficialDocs

        DOCS = Choice.get_dict_choices_for("rh", "TIPO_DOCUMENTO")

        query_params = self.__get_query_params(values)
        controls = self.__get_control_params(values)

        year, kind = query_params.get("year"), query_params.get("kind")
        keyword = query_params.get("keyword")
        conditions = dict(interno=True, arquivo__isnull=False, tipo__in=[1, 3, 5])

        years = (
            OfficialDocs.objects.filter(
                interno=True, arquivo__isnull=False, tipo__in=(1, 3, 5)
            )
            .order_by("-ano")
            .values("ano")
            .annotate(total=Count("ano"))
        )

        if year:
            conditions["ano"] = year
        if kind:
            conditions["tipo__in"] = [kind]

        qs = OfficialDocs.objects.filter(**conditions).order_by("-ano", "-numero")

        if keyword:
            qs = qs.filter(
                Q(numero__icontains=keyword) | Q(observacao__icontains=keyword)
            )

        count = qs.count() or "0"

        docs_list = []
        for item in qs[controls["start"] : controls["end"]]:
            if item.data_publicacao:
                if item.get_veiculo_publicacao_display() and item.numero_publicacao:
                    info = (
                        f"PUBLICAÇÂO EM: {item.data_publicacao:%d/%m/%Y} "
                        f"({item.get_veiculo_publicacao_display()} Nº {item.numero_publicacao})"
                    )
                else:
                    info = f"PUBLICAÇÂO EM: {item.data_publicacao:%d/%m/%Y}"
            else:
                info = f"PUBLICAÇÂO EM: Indisponível"

            docs_list.append(
                {
                    "title": "%s %s/%s"
                    % (capitalize_words(DOCS[item.tipo]), item.numero, item.ano),
                    "published_date": item.data_publicacao or "",
                    "number": item.numero,
                    "year": item.ano,
                    "url": item.arquivo.no_logged_permalink(),
                    "abstract": str(
                        striptags(
                            re.sub("[\\t\\n\\r\\f\\v]", "", item.observacao or "")
                        )
                    ).replace("&nbsp;", " "),
                    "info": info,
                }
            )

        data = {
            "total": count,
            "list": docs_list,
            "list_years": [y["ano"] for y in years],
        }

        return data

    def search(self, values={}):
        query_params = self.__get_query_params(values)
        controls = self.__get_control_params(values)

        by_title = Q(title__icontains=query_params["terms"])
        by_tag = Q(tags__name__icontains=query_params["terms"])
        query_params["areas__active"] = True
        query_params.pop("terms")

        args = [
            Post.if_published(),
            Q(no_searchable=False),
            Q(areas__items_no_searchable=False),
            by_title | by_tag,
        ]
        if "areas__parent__slug" not in query_params:
            args.insert(0, ~Q(areas__parent__slug="intranet"))

        data = [
            {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "published_date": post.published_date,
                "url": post.get_absolute_url(),
                "area": self.get_areas(
                    {"contents": post.content_ptr_id, "page": 1, "length": 1}
                )["list"][0],
                "images": self.get_images(
                    {
                        "posts": post.id,
                        "page": 1,
                        "length": 1,
                        "image-width": controls.get("image-width"),
                        "image-cut-mode": controls.get("image-cut-mode"),
                        "image-sizes": controls.get("image-sizes"),
                    }
                )["list"],
            }
            for post in Post.objects.defer("text")
            .filter(*args, **query_params)
            .order_by("-published_date")
            .distinct()[0:100]
        ]

        # reduced = []
        # for post in data:
        #     if post not in reduced:
        #         reduced.append(post)

        return {"total": len(data) or "0", "list": data}

    def search_docs(self, values={}):
        now = datetime.datetime.now()
        dynamic = Q(posts__publication_start__lte=now, posts__publication_end__gte=now)
        static = Q(posts__published=True)

        query_params = self.__get_query_params(values)
        query_params["title__icontains"] = query_params["terms"]
        query_params["posts__areas__active"] = True
        query_params["posts__active"] = True
        query_params.pop("terms")

        qs = File.objects.filter(static | dynamic, **query_params).distinct()[0:200]
        data = {
            "total": len(qs) or "0",
            "list": [
                {
                    "title": f.title,
                    "url": f.get_link(),
                    "published_date": f.published_date,
                    "post": {
                        "title": f.posts.all()[0].title,
                        "slug": f.posts.all()[0].slug,
                        "url": f.posts.all()[0].get_absolute_url(),
                        "published_date": f.posts.all()[0].published_date,
                    },
                }
                for f in qs
            ],
        }
        return data

    def pgj_actions_amount_by_county(self, values={}):
        """Get the amount of PGJ actions by county
        return a dict with total and list properties

        :param values:  the object environment where are extracted
            the request paramenters to perform a query.

            The request paramenters should have
            -- prosecutor_actions__areas__parent__slug
            -- prosecutor_actions__areas__slug

        """
        query_params = self.__get_query_params(values)
        if "active" in query_params:
            query_params.pop("active")

        today = datetime.date.today()
        static = Q(prosecutor_actions__published=True)
        dynamic = Q(
            prosecutor_actions__publication_start__lte=today,
            prosecutor_actions__publication_end__gte=today,
        )

        query_params.update(
            circunscricao__isnull=False, prosecutor_actions__active=True
        )

        qs = (
            County.objects.filter(static | dynamic, **query_params)
            .values(
                "id",
                "nome",
                "county_marker__marker__maps__slug",
                "county_marker__marker__latitude",
                "county_marker__marker__longitude",
                "prosecutor_actions__areas__slug",
            )
            .annotate(amount_docs=Count("prosecutor_actions"))
        )

        data = {"total": qs.count(), "list": []}
        for action in qs:
            data["list"].append(
                {
                    "id": action["id"],
                    "name": action["nome"],
                    "amount_docs": action["amount_docs"],
                    "area_slug": action["prosecutor_actions__areas__slug"],
                    "map_slug": action["county_marker__marker__maps__slug"],
                    "latitude": action["county_marker__marker__latitude"],
                    "longitude": action["county_marker__marker__longitude"],
                }
            )

        return data

    def pgj_actions_by_county(self, values={}):
        """Get the PGJ actions by county and area.
        Return a dict with total and list properties

        :param values:  the object environment where are extracted
            the request paramenters to perform a query.

            The request paramenters should have
            -- areas__parent__slug
            -- areas__slug
            -- county__id

        """
        query_params = self.__get_query_params(values)
        controls = self.__get_control_params(values)

        today = datetime.date.today()
        static = Q(published=True)
        dynamic = Q(publication_start__lte=today, publication_end__gte=today)

        qs = ProsecutorAction.objects.filter(static | dynamic, **query_params).order_by(
            "status__name", "-id"
        )

        data = {"total": 0, "list": []}
        if qs.exists():
            data = {
                "county": {"id": qs[0].county.id, "name": qs[0].county.nome},
                "total": qs.count(),
                "list": [
                    {
                        "id": p.id,
                        "slug": p.slug,
                        "doc": p.title,
                        "filing": p.filing,
                        "text": p.text,
                        "status": p.status.name,
                        "start_date": p.start_date,
                        "decision_date": p.decision_date,
                    }
                    for p in qs[controls["start"] : controls["end"]]
                ],
            }

        return data

    def batch(self, values={}):
        procedures = eval(self.__get_query_params(values)["procedures"])
        batches = {}

        for p in procedures:
            proc, alias, pars = p.split("|")
            if proc != "search":
                proc = "get_%s" % proc
            batches[alias] = eval("self.%s" % proc)(eval(pars))

        return batches
