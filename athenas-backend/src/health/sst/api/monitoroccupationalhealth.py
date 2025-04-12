# -*- coding: utf-8 -*-
from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from health.sst.models import MonitorOccupationalHealth


log = getLogger(__name__)


class SSTMonitorOccupationalHealth(RestfulDRY):

    _model = MonitorOccupationalHealth

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "employee__matricula__icontains",
        "employee__pessoa_fisica__nome__icontains",
    )

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    # force_upper = True

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

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("health.sst.MonitorOccupationalHealthManage")')

    @login_required(type="JSON")
    def release(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            monitor_occupational_health = self.request.POST.get(
                "monitor_occupational_health", False
            )

            if monitor_occupational_health:
                inst = self.Model.objects.get(pk=monitor_occupational_health)
                inst.release()
                rst.update(
                    {
                        "success": True,
                        "message": "Apto com sucesso.",
                    }
                )
            else:
                msg = "Monitoração não informada."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class SSTMonitoringHealthManage(SSTMonitorOccupationalHealth):

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    # force_upper = True

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

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("health.sst.MonitoringHealthManage")')
