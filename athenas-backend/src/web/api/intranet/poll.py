from contrib.newrest import RestfulDRY
from web.models import Poll


class PollIntranet(RestfulDRY):
    _model = Poll

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('web.intranet.poll.Manage')")

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        # rst = {
        #     **rst,
        #     'departament_display': instance.departament_display
        # }

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
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
            raise Exception(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            try:
                params = self.get_params(self.request.POST, check_case=True)
                inst = self.factoryModel(**params)
                inst.full_clean()

                inst.save()
            except Exception as e:
                rst.update(message=f"Erro ao tentar salvar a ação. {e}.")
            else:
                rst.update(success=True, message="Área cadastrada com sucesso")
        return rst
