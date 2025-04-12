# -*- coding: utf-8 -*-
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from rh.pvf.const import GROUPS_PVF
from rh.pvf.models import PortalRequestHistory


log = getLogger(__name__)


class PortalRequestHistoryApi(RestfulDRY):

    _model = PortalRequestHistory

    full_text_index = (
        "observation__icontains",
        "action__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.portalrequesthistory.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(PortalRequestHistoryApi, self).model_to_dict(instance)
        employee = employee_from_user(get_current_user())
        is_ascoger = employee.user.groups.filter(
            name="mpmt-perfil-vdf-aprovador-assessoria-coger"
        ).exists()

        _dict_.update(
            user_history=str(
                instance.user.servidor if hasattr(instance.user, "servidor") else ""
            ),
            group_name=instance.get_group_name,
            is_ascoger=is_ascoger,
        )
        return _dict_

    def retificate_annotation(self, params):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        observation = self.request.POST.get("obs")
        pk = self.request.POST.get("pk")
        try:
            can = self.check_permission(
                self.request.user,
                "add",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para criar %s."
                    % self.Model._meta.object_name
                )
            else:
                if observation and pk:
                    history = self._model.objects.filter(pk=pk)
                    history.update(observation=observation)
                    rst = {
                        "success": True,
                        "message": "Histórico atualizado com sucesso!",
                    }
        except Exception as e:
            log.error(
                f"ERROR PVF - Erro ao retificar anotação do histório de requisições: {e}"
            )
            rst = {
                "success": False,
                "message": "Erro ao atualizar histórico da requisição!",
            }

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
