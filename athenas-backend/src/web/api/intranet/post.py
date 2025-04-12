from app import settings
from contrib.newrest import RestfulDRY
from edocs.processo.verifying_digit import ValidationError
from web.models import Post, Tag
from contrib.utils import getLogger
from django.template.defaultfilters import slugify

log = getLogger(__name__)


class PostIntranet(RestfulDRY):
    _model = Post

    full_text_index = ("title__unaccent__icontains",)

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('web.intranet.post.Manage')")

    def do_put(self, pk=None):
        """Executa uma requisição PUT.

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name
            )

        elif not self.request.user.web_groups.filter(
            area_id=int(self.request.PUT["areas"]), can_change=True, active=True
        ).exists():
            rst.update(message="Você não tem permissão para editar posts desta área.")
        else:
            rst.update(
                self.do_put_multi()
                if "filter" in self.request.PUT
                else self.do_put_single(pk)
            )

        post = Post.objects.get(pk=pk)
        tags = self.request.PUT.get("tags_display")
        if tags:
            for tag in tags.split(","):
                if slugify(tag) not in getattr(settings, "PROHIBITED_TAGS", []):
                    tag = tag.strip()
                    if not post.tags.filter(slug=slugify(tag)).exists():
                        defaults = {"name": tag, "slug": slugify(tag)}
                        t, created = Tag.objects.get_or_create(
                            slug=slugify(tag), defaults=defaults
                        )
                        post.tags.add(t)
        tags = post.tags.exclude(slug__in=[slugify(tag) for tag in tags.split(",")])
        if tags.exists():
            post.tags.remove(*tags)

        return rst

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        params = self.get_params(self.request.POST, check_case=True)

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        elif not self.request.user.web_groups.filter(
            area__in=params["areas"], can_add=True, active=True
        ).exists():
            rst.update(message="Você não tem permissão para criar posts desta área.")
        else:
            try:
                inst = self.factoryModel(**params)

                if self.use_full_clean:
                    inst.full_clean()

                inst.save()
                self.fill_instance_m2m(inst, params)
                if self.request.POST.get("tags_display"):
                    tags = self.request.POST.get("tags_display")
                    for tag in tags.split(","):
                        if slugify(tag) not in getattr(settings, "PROHIBITED_TAGS", []):
                            tag = tag.strip()
                            if not inst.tags.filter(slug=slugify(tag)).exists():
                                defaults = {"name": tag, "slug": slugify(tag)}
                                t, created = Tag.objects.get_or_create(
                                    slug=slugify(tag), defaults=defaults
                                )
                                inst.tags.add(t)

            except ValidationError as e:
                log.exception(e)
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistido com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst

    def do_delete(self, pk=None):
        """Executa uma requisição DELETE."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "delete",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para remover %s."
                % self.Model._meta.object_name
            )
        elif not self.request.user.web_groups.filter(
            area__post__pk=pk, can_delete=True, active=True
        ).exists():
            rst.update(message="Você não tem permissão para remover posts desta área")
        else:
            rst.update(
                self.do_delete_multi()
                if "filter" in self.request.DELETE
                else self.do_delete_single(pk)
            )

        return rst

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)
        path_icon = "/athenas/static/web/icons/"
        rst = {
            **rst,
            "tags_display": ", ".join(
                instance.tags.all().values_list("name", flat=True)
            ),
            "area": instance.areas.first().pk,
            "marked_as_published": instance.is_published(),
            "marked_as_published_icon": (
                f"{path_icon}published.png"
                if instance.is_published()
                else f"{path_icon}no-published.png"
            ),
            "link": instance.get_domain_absolute_url(),
        }

        return rst
