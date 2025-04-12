# -*- coding: utf-8 -*-

# from django.db import transaction
from contrib.newrest import RestfulDRY
from web.models import Post, Area, ContentArea, Category
from contrib.utils import getLogger, DateUtils
from contrib.middleware import get_current_user

log = getLogger()


class PostRestful(RestfulDRY):
    _model = Post
    force_upper = False
    force_orm_single = True
    full_text_index = ["title__icontains"]
    exclude_fields = ["content_ptr", "post"]

    def __init__(self, *args, **kwargs):
        super(PostRestful, self).__init__(*args, **kwargs)
        self.set_restful("json")

    def years(self, args=[]):
        site_slug = self.request.session.get("site") or self.request.GET.get("site")
        category = self.request.GET.get("category")
        params = dict(
            active=True, areas__parent__slug=site_slug, ref_year__isnull=False
        )

        if category:
            params["categories"] = category

        years_qs = (
            Post.objects.filter(Post.if_published(), **params)
            .order_by("-ref_year")
            .values_list("ref_year", flat=True)
            .distinct()
        )

        self.render(
            dict(
                success=True, collection=list(years_qs), message="Concluído com sucesso"
            )
        )

    def months(self, args=[]):
        site_slug = self.request.session.get("site") or self.request.GET.get("site")
        months_qs = (
            Post.objects.filter(
                Post.if_published(),
                active=True,
                # areas__parent__slug='transparencia',
                areas__parent__slug=site_slug,
                ref_month__isnull=False,
            )
            .order_by("-ref_month")
            .values_list("ref_month", flat=True)
            .distinct()
        )

        self.render(
            dict(
                success=True,
                collection=list(months_qs),
                message="Concluído com sucesso",
            )
        )

    def publish(self, args=[]):
        self._read_special_verb()
        params = self.get_params()
        message = dict(success=False, message="Não foi possível concluir a operação.")
        try:
            post = self._model.objects.get(pk=params.get("pk"))
            if post.is_published():
                post.unpublish()
            else:
                post.publish()
            post.save()
        except Exception as e:
            message.update(message=str(e), extra=str(params))
        else:
            message.update(success=True, message="Operação concluída com sucesso.")

        self.render(message)

    def apply_category(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            self._read_special_verb()
            category = Category.objects.get(pk=self.get_params().get("category"))
            pkset = self.get_params().get("pkset")
            pkset = pkset if isinstance(pkset, tuple) else tuple(pkset)

            for post in self.get_query().filter(pk__in=pkset):
                post.categories.clear()
                post.categories.add(category)

            rst.update(success=True, message="Categoria atualizada com sucesso")
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.render(rst)

    def classify(self, args=[]):
        self._read_special_verb()
        params = self.get_params()
        message = dict(success=False, message="Não foi possível concluir a operação.")
        try:
            category = Category.objects.get(pk=params.get("category"))
            for post in Post.objects.filter(pk__in=params.get("pkset", [])):
                post.ref_year = int(params.get("year", 0))
                post.save()

                if not post.categories.filter(pk=category.pk).exists():
                    post.categories.add(category)

        except Exception as e:
            message.update(message=str(e), extra=str(params))
        else:
            message.update(success=True, message="Operação concluída com sucesso.")

        self.render(message)

    def get_query(self):

        qs = super(PostRestful, self).get_query()

        status = self.request.GET.get("status")
        if status == "published":
            qs = qs.filter(Post.if_published())

        intranet = self.request.GET.get("intranet", None)
        if intranet:
            areas = Area.objects.get(slug__iexact="intranet").descendants()
            return qs.filter(active=True, areas__in=areas).order_by("-create_date")

        user = get_current_user()
        if not user.is_superuser:
            qs = qs.filter(areas__groups__users=user)

        return qs.filter(active=True).order_by("-create_date")

    def get_params(self, *args, **kwargs):

        params = super(PostRestful, self).get_params(*args, **kwargs)

        if self.request.method in ["POST", "PUT"]:
            params.pop("files", None)

            if "area" in params:
                area = params.get("area")
                if not area:
                    raise Exception("É necessario escolher uma área de publicação")
        return params

    def fill_instance_m2m(self, instance, params):
        super(PostRestful, self).fill_instance_m2m(instance, params)

        if params.get("area"):
            area = Area.objects.get(pk=params.get("area"))

            qs = ContentArea.objects.filter(content=instance.content_ptr, area=area)
            if not qs.exists():
                ContentArea.objects.filter(content=instance.content_ptr).delete()
                ContentArea(content=instance.content_ptr, area=area).save()

    def model_to_dict(self, obj):

        areas = obj.areas.filter(active=True)
        area = areas.first()

        files_list = [
            {"title": f.title, "ref_month": f.ref_month, "url": f.get_link()}
            for f in obj.files.filter(active=True).order_by("ref_month")
        ]

        comments_list = [
            {
                "id": c.pk,
                "person_name": c.author_name,
                "person_email": c.author_email,
                "username": c.author_username,
                "created_at": DateUtils.datetime_to_str(c.created_at),
                "text": c.text,
            }
            for c in obj.comments.filter(active=True)
        ]

        images_list = [
            {
                "title": image.title,
                "src": image.get_absolute_url("width", 600),
                "max_size_src": image.get_absolute_url("width", 1280),
                "thumb_src": image.get_absolute_url("square", 54),
            }
            for image in obj.images.order_by("position")
        ]

        videos_list = [
            {
                "title": video.title,
                "embed": video.url_embed,
                "src": video.get_video_url(),
                "cover_src": video.get_absolute_url("width", 600),
                "cover_max_size_src": video.get_absolute_url("width", 1280),
                "cover_thumb_src": video.get_absolute_url("square", 54),
            }
            for video in obj.videos.order_by("position")
        ]

        cover_image = None
        if videos_list:
            video = videos_list[0]
            cover_image = {
                "title": video["title"],
                "src": video["cover_src"],
                "max_size_src": video["cover_max_size_src"],
                "thumb_src": video["cover_thumb_src"],
            }
        elif images_list:
            cover_image = images_list[0]

        m2d = super(PostRestful, self).model_to_dict(obj)
        m2d["site"] = area.parent.pk if area and area.parent else ""
        m2d["site_unicode"] = area.parent.__str__() if area and area.parent else ""
        m2d["area"] = area.id if area else ""
        m2d["area_unicode"] = area.__str__() if area else ""
        m2d["categories"] = [c.__str__() for c in obj.categories.all()]
        m2d["category_unicode"] = str(obj.categories.last() or "--------")
        m2d["files"] = [
            str(f) for f in obj.files.filter(active=True).order_by("ref_month")
        ]
        m2d["files_list"] = files_list
        m2d["images_list"] = images_list
        m2d["videos_list"] = videos_list
        m2d["cover_image"] = cover_image
        m2d["comments_list"] = comments_list
        m2d["published"] = obj.is_published()
        m2d["url"] = obj.get_absolute_url()
        return m2d

    def json(self, args=[]):
        site_slug = self.request.GET.get("site", "transparencia")
        self.request.session["site"] = site_slug
        site = Area.objects.filter(
            parent__isnull=True, active=True, slug=site_slug
        ).first()
        site_pk = site.pk if site else "null"

        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("web.cms.post.Manager", { initialState: { site: "%s", site_pk: %s } })'
            % (site_slug, site_pk)
        )
