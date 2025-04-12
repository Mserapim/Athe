# -*- coding:utf-8 -*-

from contrib.controller import JsonResponseController
from contrib.decorator import is_public
from edocs.protocolo.models import LegalSign


class ProtocolRPC(JsonResponseController):

    @is_public()
    def sign_check(self, args=[]):
        data = {
            "success": False,
            "message": "Nenhum documento eletrônico com essa assinatura.",
        }

        signature = self.request.POST.get("signature")

        legal_sign = LegalSign.objects.filter(content_sign=signature).first()
        if legal_sign:

            kind = "Movimentação"
            if hasattr(legal_sign, "protocollegalsign"):
                kind = "Protocolo"

            sign = {
                "kind": kind,
                "id": legal_sign.id,
                "who": legal_sign.who_person,
                "when": legal_sign.when,
                "content_sign": legal_sign.content_sign,
                "content": legal_sign.content,
            }

            data = {"success": True, "message": "Assinatura verdadeira.", "sign": sign}

        self.render(data)
