# -*- coding: utf-8 -*-

# from django.db import transaction
from contrib.newrest import RestfulDRY
from web.models import Category
from contrib.utils import getLogger

log = getLogger()


class CategoryRestful(RestfulDRY):
    _model = Category
    force_upper = False
    force_orm_single = True
    full_text_index = ["path__icontains"]
    # exclude_fields = ['created_by', 'modified_by', 'modified_at']

    def __init__(self, *args, **kwargs):
        super(CategoryRestful, self).__init__(*args, **kwargs)
        self.set_restful("json")

    def get_query(self):
        qs = super(CategoryRestful, self).get_query()
        return qs.order_by("computed_position", "path")

    def model_to_dict(self, obj):
        m2d = super(CategoryRestful, self).model_to_dict(obj)

        post = obj.posts.first()
        if post:
            post = {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "url": post.get_absolute_url(),
            }
        m2d["post"] = post

        site = obj.sites.first()
        m2d["sites"] = site.pk if site else ""
        m2d["sites_unicode"] = str(site) if site else ""

        m2d["root_category_name"] = obj.root_category_name()

        return m2d

    def descendants(self, args=[]):

        parent = self.request.GET.get("parent")
        collection = []

        category = None
        if parent:
            category = Category.objects.filter(pk=parent).first()

        if category:
            for child in category.descendants():
                m2d = self.model_to_dict(child)
                collection.append(m2d)

        self.render(dict(count=len(collection), collection=collection))

    def months(self, args=[]):

        months_qs = (
            Category.objects.filter(
                Category.if_published(),
                active=True,
                posts__areas__parent__slug="transparencia",
                ref_month__isnull=False,
            )
            .order_by("-ref_month")
            .values_list("ref_month", flat=True)
            .distinct()
        )

        months = [(k, v) for k, v in Category.MONTH_CHOICES if k in list(months_qs)]

        self.render(
            dict(success=True, collection=months, message="Concluído com sucesso")
        )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("web.cms.category.Manager")')
