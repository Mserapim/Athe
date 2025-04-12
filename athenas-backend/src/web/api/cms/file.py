# -*- coding: utf-8 -*-

# from django.db import transaction
import base64, datetime
from django.db.models import Q
from contrib.utils import getLogger
from contrib.newrest import RestfulDRY
from web.models import File, Post

log = getLogger()


class FileRestful(RestfulDRY):
    _model = File
    force_upper = False
    force_orm_single = True
    full_text_index = ["title__icontains"]
    # exclude_fields = ['created_by', 'modified_by', 'modified_at']

    def __init__(self, *args, **kwargs):
        super(FileRestful, self).__init__(*args, **kwargs)
        self.set_restful("json")

    def months(self, args=[]):
        site_slug = self.request.session.get("site") or self.request.GET.get("site")
        category = self.request.GET.get("category")
        year = self.request.GET.get("year")

        params = dict(
            active=True, posts__areas__parent__slug=site_slug, ref_month__isnull=False
        )

        if category:
            params["posts__categories"] = category

        if year:
            params["posts__ref_year"] = year

        months_qs = (
            File.objects.filter(**params)
            .order_by("-ref_month")
            .values_list("ref_month", flat=True)
            .distinct()
        )

        months = [(k, v) for k, v in File.MONTH_CHOICES if k in list(months_qs)]

        self.render(
            dict(success=True, collection=months, message="Concluído com sucesso")
        )

    def get_params(self, *args, **kwargs):
        params = super(FileRestful, self).get_params(*args, **kwargs)
        if params.get("published_date"):
            params["published"] = True
        else:
            params["published"] = False
        return params

    def apply_month(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            self._read_special_verb()
            self.get_query().filter(pk__in=self.get_params().get("pkset")).update(
                ref_month=int(self.get_params().get("ref_month")) or None
            )

            rst = {"success": True, "message": "Itens atualizados com sucesso."}
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.render(rst)

    def model_to_dict(self, obj):
        m2d = super(FileRestful, self).model_to_dict(obj)

        post = obj.posts.filter(Post.if_published(), active=True).first()

        # m2d['unicode'] = '%s - %s' % (obj.ref_month, obj)

        m2d["post"] = (
            {
                "id": post.id,
                "slug": post.slug,
                "title": post.title,
                "ref_year": post.ref_year,
                "text": (
                    base64.b64encode(post.text.encode()).decode() if post.text else ""
                ),
            }
            if post
            else None
        )

        m2d["url"] = obj.get_absolute_url()
        m2d["ref_month_name"] = (
            obj.get_ref_month_display()
            if obj.ref_month and obj.ref_month > 0
            else "Não classificado"
        )

        m2d["user_date"] = m2d.get("published_date") or m2d.get("updated_at")

        return m2d

    def get_query(self):
        qs = super(FileRestful, self).get_query()

        today = datetime.date.today()
        post_pub_dynamic = Q(
            posts__publication_start__lte=today, posts__publication_end__gte=today
        )
        post_pub_static = Q(posts__published=True)

        return qs.filter(
            post_pub_dynamic | post_pub_static, posts__active=True, active=True
        ).order_by("-posts__ref_year", "ref_month", "position")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("web.cms.file.Manager")')
