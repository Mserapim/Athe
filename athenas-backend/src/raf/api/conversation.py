# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from raf.models import Conversation, ActivityAdjustment, DataAdjustment
from rh.models import Lotacao as Location
from . import util
from standard.models import Configuration

log = getLogger(__name__)


class RAFConversation(RestfulDRY):

    _model = Conversation

    def create_conversation_content(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        try:
            params = util.request_params(self)
            if not params.get("conversation"):
                raise Exception("Ocorreu um erro. Conversa não foi iniciada.")
            if not params.get("message"):
                raise Exception("É necessário informar o conteúdo da conversa.")
            conversation = Conversation.objects.get(pk=int(params.get("conversation")))
            situation = int(params.get("situation"))
            origin = None
            if params.get("origin"):
                origin = Location.objects.get(pk=int(params.get("origin", 0)))
            else:
                cfg = Configuration.get_or_create("raf")
                origin = Location.objects.get(pk=int(cfg.get("location", 0)))
            if ActivityAdjustment.objects.filter(conversation=conversation).exists():
                conversation.activityadjustment.validate_raf()
            if DataAdjustment.objects.filter(conversation=conversation).exists():
                conversation.dataadjustment.activityadjustment.validate_raf()
            conversation.create_content(
                message=params.get("message", ""), origin=origin, situation=situation
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Criado com sucesso!")
        self.renderer(rst)
