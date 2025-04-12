from app import settings
from contrib.newrest import RestfulDRY, Restful
from contrib.nil import nil_unicode, nil_pk, nil_datetime, nil_date
from web.models import Link
from django.template.defaultfilters import slugify, addslashes, striptags


class LinkIntranet(RestfulDRY):
    _model = Link

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('web.intranet.link.Manage')")

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst = {
            "id": instance.pk,
            "title": instance.title,
            "slug": instance.slug,
            "credits": instance.credits,
            "create_date": nil_datetime(instance.create_date, None),
            "updated_at": nil_datetime(instance.updated_at, None),
            "ref_year": instance.ref_year,
            "ref_month": instance.ref_month,
            "published_date": nil_datetime(instance.published_date, "Não publicado"),
            "publication_start": nil_datetime(instance.publication_start, None),
            "publication_end": nil_date(instance.publication_end, None),
            "active": instance.active,
            "position": instance.position,
            "has_comment": instance.has_comment,
            "has_tag": instance.has_tag,
            "has_meta": instance.has_meta,
            "as_link": instance.as_link,
            "as_gallery": instance.as_gallery,
            "views": instance.views,
            "areas": list(instance.areas.all().values_list("pk", flat=True)),
            "url_embed": instance.url_embed,
            "ged": nil_pk(instance.ged, None),
            "public_access": instance.public_access,
            "is_banner": instance.is_banner,
            "fullname": instance.fullname,
            "parent": nil_pk(instance.parent, None),
            "kind": instance.kind,
            # customs
            "tags_display": ", ".join(
                instance.tags.all().values_list("name", flat=True)
            ),
            "area": instance.areas.first().pk,
            "marked_as_published": instance.is_published(),
            "name": instance.fullname,
            "content": instance.content_ptr_id,
            "parent_title": instance.parent.title if instance.parent else None,
            "image_url": addslashes(
                instance.get_link("square", 110)
                or "/%s/static/web/icons/no-image.jpg" % settings.CONTEXT
            ),
        }

        return rst
