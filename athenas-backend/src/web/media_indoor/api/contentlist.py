# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from web.media_indoor.models import ContentList

log = getLogger(__name__)


class MIContentList(RestfulDRY):

    _model = ContentList

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
        self.response.write('Ext._create("media_indoor.content_list.Manager")')

    def move_content(self, args=[]):
        """Movimenta a posição de um conteúdo na campanha"""

        rst = {"success": False, "message": "Nada foi feito ainda."}

        content_id = self.request.POST.get("content_id")
        direction = self.request.POST.get("direction")

        try:
            content = self._model.objects.get(pk=content_id)
            self._model.reorder_content(content.campaign)
            content.move_position(direction)
        except self._model.DoesNotExist as e:
            self.log.exception(e)
            rst.update(message="Não foi possível encontrar o conteúdo")
        except Exception as e:
            self.log.exception(e)
            rst.update(message="Não foi possível alterar a posição do conteúdo")
        else:
            rst.update(success=True, message="Posição alterada com sucesso")

        self.renderer(rst)
