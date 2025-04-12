from contrib.newrest import RestfulDRY
from contrib.nil import nil_pk
from web.models import Category


class CategoryIntranet(RestfulDRY):
    _model = Category

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('web.intranet.category.Manage')")

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst = {
            "id": instance.pk,
            "name": instance.name,
            "slug": instance.slug,
            "parent": nil_pk(instance.parent, None),
            "parent_unicode": instance.parent.name if instance.parent else None,
            "path": instance.path,
            "no_root_path": instance.no_root_path,
            "position": instance.position,
            "computed_position": instance.computed_position,
            "url": instance.url,
            "area": nil_pk(instance.sites.all().first(), None),
        }

        return rst
