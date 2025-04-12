# -*- coding: utf-8 -*-
from contrib.decorator import is_public
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from web.media_indoor.models import Device


log = getLogger(__name__)


class MIDevice(RestfulDRY):

    _model = Device

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    # force_orm_single = False

    # primary_key = 'pk'

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    # force_persist_boolean_fields = []

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)
        data.update(last_contact_age=instance.last_contact_age)

        return data

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("media_indoor.device.Manager")')

    @is_public()
    def my_campaigns(self, args=[]):
        result = {"success": False}

        try:
            device = self.get_query().get(ingress_code=args[0])
            device.register_contact()

            result.update(
                success=True,
                campaigns=[
                    campaign.video_permalink for campaign in device.my_campaigns
                ],
            )
        except self.Model.DoesNotExist:
            result.update(message="device not found")
            self.response.status_code = 404
        except Exception as e:
            self.response.status_code = 502
            result.update(message=str(e))

        self.renderer(result)

    @is_public()
    def is_valid(self, args=[]):
        result = {"success": False}

        try:
            device = self.get_query().get(ingress_code=args[0])
            device.register_contact()

            result.update(
                success=True,
                message="Dispositivo encontrado",
                device=self.model_to_dict(device),
            )
        except self.Model.DoesNotExist:
            self.response.status_code = 404
            result.update(message="Registro de dispositivo não encontrado.")

        self.renderer(result)
