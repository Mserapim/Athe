# -*- coding: utf-8 -*-

from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.api.workplace import RHWorkplaceRestful
from rh.models import Replacement

log = getLogger(__name__)


class RHReplacement(RestfulDRY):

    _model = Replacement

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
        self.response.write("Ext._create('rh.replacement.Manage')")

    @login_required("JSON")
    def update_document(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            document = self.request.POST.get("document", None)
            if document:
                self._model.objects.filter().update(document=document)
                rst.update(
                    {
                        "success": True,
                        "message": "Tabela de Substituição Automática atualizada.",
                    }
                )
            else:
                rst.update(
                    {
                        "message": "Por favor escolha uma publicação.",
                    }
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": err})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class RHWorkplaceReplacement(RHWorkplaceRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('rh.replacement.WorkplaceReplacementManager')")
