# -*- coding: utf-8 -*-
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from ..models import Campaign, Content, ContentList


log = getLogger(__name__)


class MICampaign(RestfulDRY):

    _model = Campaign

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

    def toggle_active(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        pk = args[0] if args else 0
        emitter = False

        try:
            obj = self._model.objects.get(pk=pk)
            activated = obj.toggle_active()
        except self._model.DoesNotExist:
            rst.update(message="Não foi possível encontrar uma campanha.")
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            if activated:
                emitter = True
                msg = "O conteúdo da campanha está sendo preparado. Você será informado quando terminar"
            else:
                msg = "A campanha foi desativada"

            rst.update(success=True, message=msg, emitter=emitter)

        self.renderer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("media_indoor.campaign.Manager")')


class MICampaignManager(MICampaign):

    def get_params(self, *args, **kwargs):
        params = super().get_params(*args, **kwargs)

        if "contents" in params:
            if not isinstance(params.get("contents"), list):
                params.update(contents=params.get("contents").split())

        return params

    def add_content(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        params = self.get_params(self.request.POST)

        user = get_current_user()
        try:
            campaign = self._model.objects.get(pk=params.get("campaign"))
            if campaign.active:
                raise Exception(
                    "Não posso adicionar conteúdos para uma campanha ativa."
                )

            contents = Content.objects.filter(pk__in=params.get("contents"))

            for content in contents:
                ContentList.objects.create(
                    campaign=campaign,
                    content=content,
                    created_by=user,
                    modified_by=user,
                )

        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Conteúdos adicionados")

        self.renderer(rst)

    def remove_content(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        params = self.get_params(self.request.POST)

        try:
            campaign = self._model.objects.get(pk=params.get("campaign"))
            if campaign.active:
                raise Exception("Não posso remover conteúdos para uma campanha ativa.")

            param_contents = (
                [params.get("contents")]
                if not isinstance(params.get("contents"), list)
                else params.get("contents")
            )
            contents = ContentList.objects.filter(pk__in=param_contents)

            if contents:
                campaign.campaign_lists.filter(pk__in=contents).delete()
                ContentList.reorder_content(campaign)
                message = "Conteúdos Removidos"
            else:
                message = "Não foram informados conteúdos para remover"

        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message=message)

        self.renderer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("media_indoor.campaign.CampaignManager")')
