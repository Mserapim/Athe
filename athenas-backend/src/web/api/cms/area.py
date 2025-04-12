# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from web.models import Area

log = getLogger()


class AreaRestful(RestfulDRY):
    _model = Area
    force_upper = False
    force_orm_single = True
    full_text_index = ["name__icontains"]
    # exclude_fields = ['created_by', 'modified_by', 'modified_at']

    def __init__(self, *args, **kwargs):
        super(AreaRestful, self).__init__(*args, **kwargs)
        self.set_restful("json")

    def model_to_dict(self, instance):
        rst = super(AreaRestful, self).model_to_dict(instance)
        descendants = []
        for desc in instance.descendants():
            descendants.append(RestfulDRY.model_to_dict(self, desc))

        rst.update(descendants=descendants)

        return rst

    def get_query(self):
        qs = super(AreaRestful, self).get_query()
        user = get_current_user()
        if not user.is_superuser:
            qs = qs.filter(groups__users=user)
        return qs.filter(active=True).order_by("fullname")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("web.cms.area.Manager")')


class IntranetMenuRestful(AreaRestful):

    def json(self, args=[]):
        site_slug = self.request.GET.get("site", "intranet")
        self.request.session["site"] = site_slug
        site = Area.objects.filter(
            parent__isnull=True, active=True, slug=site_slug
        ).first()
        site_pk = site.pk if site else "null"

        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("web.cms.intranet.MenuManager", { initialState: { site: "%s", site_pk: %s } })'
            % (site_slug, site_pk)
        )
