# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.api.movimentacao import RHMovimentacaoPessoalRestful
from rh.models import DeclaracaoAtividade
from contrib.decorator import login_required
from contrib.utils import getLogger

log = getLogger(__name__)


class RHDeclarationActivityRestful(RestfulDRY):

    _model = DeclaracaoAtividade

    full_text_index = (
        "servidor__matricula__icontains",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__user__username__icontains",
        "servidor__pessoa_fisica__cpf__icontains",
        "servidor__pessoa_fisica__rg__icontains",
        "servidor__matricula_origem__icontains",
    )

    exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + [
        "movimentacaopessoal_ptr"
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.declarationactivity.Manage")')

    @login_required("JSON")
    def set_main(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        log.debug("set_main")
        try:
            pk = self.request.POST.get("pk", False)
            if pk:
                inst = self.Model.objects.get(pk=pk)
                log.debug("call set_main")
                inst.action_set_main(not inst.main)
                rst.update(
                    {
                        "success": True,
                        "message": "Principal modificado com sucesso.",
                    }
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": err})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def model_to_dict(self, instance):
        params = super(RHDeclarationActivityRestful, self).model_to_dict(instance)
        situation_icons = {
            True: "icon-core-success",
            False: "icon-core-delete",
        }
        obj = []
        icon_situation = {
            "iconCls": "icon-core %s" % situation_icons.get(instance.ativo),
            "title": "Ativo" if instance.ativo else "Encerrado",
        }
        icon_main = {
            "iconCls": (
                "icon-core %s" % "icon-core-document-arrow"
                if instance.main
                else "icon-core-blank"
            ),
            "title": "Principal" if instance.main else "",
        }
        obj.append(icon_situation)
        obj.append(icon_main)
        params.update({"icons": obj})
        return params
