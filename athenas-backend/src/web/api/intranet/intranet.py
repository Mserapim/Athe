from app import settings
from contrib.middleware import get_current_user
from contrib.newrest import RestfulTreeDRY, Restful
from contrib.nil import nil_unicode, nil_pk
from contrib.utils import getLogger
from web.models import Area, WebGroup

from ged.models import Arquivo as GedFile

log = getLogger(__name__)


class WebIntranet(RestfulTreeDRY):
    _model = Area

    folder_index = "parent"

    force_upper = False

    full_text_index = ("name__icontains", "fullname__icontains")

    def intranet_colaboration(self, args=[]):
        obj = {"success": False, "message": "Nada foi processado ainda."}

        query = (
            self.Model.objects.filter(pk=67)
            | self.Model.objects.filter(pk=67).first().children.all()
        )

        obj.update(
            success=True,
            count=query.count(),
            collection=[self.model_to_dict(inst) for inst in query],
        )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/javascript")
        )
        rendererer(obj)

    def get_query(self):
        areas = self.Model.objects.get(pk=67).descendants(pk_only=True)
        queryset = self.Model.objects.filter(pk__in=areas)

        if not self.request.user.is_superuser:
            permitidos = self.request.user.web_groups.filter(active=True).values_list(
                "area__pk", flat=True
            )
            queryset = queryset.filter(pk__in=permitidos)
        return self.Model.objects.filter(pk=67) | queryset.order_by("parent", "name")

    def json(self, args=[]):
        user = get_current_user()
        is_superuser = "true" if user.is_superuser else "false"
        self.response["content-type"] = "text/javascript"
        self.response.write(
            "Ext._create('web.intranet.Manage', {is_superuser: %s})" % is_superuser
        )

    def model_to_node(self, node):
        rst = RestfulTreeDRY.model_to_node(self, node)
        return {
            **rst,
            "icon_area": nil_pk(node.icon_area, None),
            "image_url": nil_unicode(node.icon_area, None),
            # 'icon': nil_unicode(node.icon_area, None),
        }

    def childs(self, args=[]):
        obj = {"success": False, "message": "Nada foi processado ainda."}

        root = args[0]
        query = Area.objects.filter(
            name__regex=r"^(\.\d+|)+\.%s(\.\d+)+$"
            % (root if root not in ["", None] else "")
        )

        obj.update(
            success=True,
            count=query.count(),
            collection=[self.model_to_dict(inst) for inst in query],
        )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/javascript")
        )
        rendererer(obj)

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
            area_id=67, can_change=True, active=True
        ).exists():
            rst.update(message="Você não tem permissão para editar áreas da intranet.")
        else:
            rst.update(self.do_put_single(pk))

        return rst

    def do_post(self, *args, **kwargs):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "responseText": "Teste teste teste",
        }

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            message = (
                "Você não tem permissão para criar %s." % self.Model._meta.object_name
            )
            rst.update(message=message)
            # raise Exception(message=message)
        elif not self.request.user.web_groups.filter(
            area_id=67, can_change=True, active=True
        ).exists():
            message = "Você não tem permissão para criar áreas em intranet."
            rst.update(message=message)
            # raise Exception(message=message)
        else:
            try:
                params = self.get_params(self.request.POST, check_case=True)

                if not params.get("parent"):
                    params["parent"] = Area.objects.get(pk=67)

                if params.get("icon_area"):
                    params["icon_area"] = GedFile.objects.get(pk=params["icon_area"])
                else:
                    params.pop("icon_area")

                inst = self.factoryModel(**params)

                inst.save()
                # Retirar este trecho, quando evoluir o sistema de permissões do cms
                if not WebGroup.objects.filter(area=inst).exists():
                    WebGroup(
                        area=inst,
                        name="Administração %s" % inst,
                        can_add=True,
                        can_change=True,
                        can_delete=True,
                        can_publish=True,
                    ).save()
            except Exception as e:
                rst.update(message=f"Erro ao tentar salvar a ação. {e}.")
            else:
                rst.update(success=True, message="Área cadastrada com sucesso")
        return rst
