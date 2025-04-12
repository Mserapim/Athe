# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from edocs.protocolo.models import Protocolo, Movimentacao
from contrib.utils import user_from_person
from contrib.nil import nil_display, nil_pk, nil_unicode, nil_datetime
from django.db.models import Q
from django.template import loader


log = getLogger(__name__)


class EDOCProtocoloRestful(Restful):

    _model = Protocolo

    full_text_index = (
        "codigo__icontains",
        "assunto__icontains",
        "protocolo_externo__icontains",
        "chancela__icontains",
    )

    def renderer_protocol_reference(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem informações", "appends": []},
        }

        try:
            # protocol = self.get_query().filter(pk=args[0]).first()
            protocol = self.Model.objects.filter(pk=args[0]).first()
            if protocol:
                rst.update(
                    success=True, document={"content": protocol.rendered, "appends": []}
                )
            else:
                rst.update(
                    success=True,
                    document={
                        "content": "<h3>Esse protocolo não foi compartilhado com você.</h3>",
                        "appends": [],
                    },
                )

        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def renderer_document_to_print(self, args=[]):
        try:
            protocol = (
                self.get_query()
                .filter(movimentacoes=self.request.GET.get("movement"))
                .first()
            )
        except Protocolo.DoesNotExist:
            self.response.write(
                "<h1>Este doumento não existe ou nunca foi compartilhado com você.</h1>"
            )
        except Exception:
            self.response.write("<h1>Not found</h1>")
        else:
            if protocol:
                tpl = loader.get_template("protocolo/print/base.html")
                movement = protocol.movimentacoes.filter(
                    pk=self.request.GET.get("movement")
                ).first()
                if not movement.is_received:
                    self.response.write(
                        tpl.render(
                            {
                                "document": loader.get_template(
                                    "protocolo/not-preview.html"
                                ).render({"protocol": protocol, "movement": movement}),
                                "appends": [],
                            }
                        )
                    )
                else:
                    self.response.write(
                        tpl.render(
                            {
                                "document": protocol.rendered,
                                "appends": protocol.appends_of_document,
                            }
                        )
                    )
            else:
                self.response.write("<h1>Not found</h1>")

    def renderer_document(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        movement = self.request.POST.get("movement")

        context = self.request.POST.get("context")

        try:
            if context in ("inbox", "inbox_person"):
                protocol = (
                    self.Model.objects.filter(
                        Q(movimentacoes__in=Movimentacao.inbox_queryset())
                    )
                    .filter(movimentacoes=movement)
                    .first()
                )
            elif context == "outbox":
                protocol = (
                    self.Model.objects.filter(
                        Q(movimentacoes__in=Movimentacao.outbox_queryset())
                    )
                    .filter(movimentacoes=movement)
                    .first()
                )
            elif context == "closedbox":
                protocol = (
                    self.Model.objects.filter(
                        Q(movimentacoes__in=Movimentacao.closedbox_queryset())
                    )
                    .filter(movimentacoes=movement)
                    .first()
                )
            else:
                protocol = (
                    self.get_query()
                    .filter(movimentacoes=self.request.POST.get("movement"))
                    .first()
                )
        except Protocolo.DoesNotExist:
            rst.update(
                message="Este doumento não existe ou nunca foi compartilhado com você."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            if protocol:
                movement = protocol.movimentacoes.filter(
                    pk=self.request.POST.get("movement")
                ).first()

                # _FIXME_ Log recebido pelo e-mail institucional: Exception Value: 'NoneType' object has no attribute 'is_received'
                if not movement.is_received and context != "outbox":
                    rst.update(
                        success=True,
                        content=loader.get_template(
                            "protocolo/not-preview.html"
                        ).render(
                            {"protocol": movement.protocolo, "movement": movement}
                        ),
                        appends=[],
                    )
                else:
                    rst.update(
                        success=True,
                        content=protocol.rendered,
                        appends=protocol.appendix_cache(
                            int(self.request.POST.get("movement") or 0)
                        ),
                    )
            else:
                rst.update(
                    success=True,
                    content="Este documento não está mais em sua caixa. Verifique na caixa de saída.",
                    appends=[],
                )

        self.renderer(rst)

    def get_query(self):
        # Alternative way of doing OR operation by separating queries for inbox, outbox and closedbox
        movements = []
        movements.extend(Movimentacao.inbox_queryset().values_list("pk", flat=True))
        movements.extend(Movimentacao.outbox_queryset().values_list("pk", flat=True))
        movements.extend(Movimentacao.closedbox_queryset().values_list("pk", flat=True))
        return self.Model.objects.filter(Q(movimentacoes__pk__in=movements))

    def __do_not_allow(self):
        rst = {"success": False, "message": "Operação proibida"}

        self.renderer(rst)

    def do_post(self):
        self.__do_not_allow()

    def do_put(self):
        self.__do_not_allow()

    def do_delete(self):
        self.__do_not_allow()

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)
        user = user_from_person(instance.interessado)
        rst.update(
            midia=instance.midia,
            midia_display=nil_display(instance, "midia", None),
            data_finalizado=nil_datetime(instance.data_finalizado, None),
            deferido=instance.deferido,
            sigiloso=instance.sigiloso,
            orgao_geral_origem=nil_pk(instance.orgao_geral_origem, None),
            orgao_geral_origem_unicode=nil_unicode(instance.orgao_geral_origem, None),
            resumo=instance.resumo,
            lotacao_criacao=nil_pk(instance.lotacao_criacao, None),
            lotacao_criacao_unicode=nil_unicode(instance.lotacao_criacao, None),
            orgao_geral_destino=nil_pk(instance.orgao_geral_destino, None),
            orgao_geral_destino_unicode=nil_unicode(instance.orgao_geral_destino, None),
            data_criacao=nil_datetime(instance.data_criacao, None),
            protocolo_externo=instance.protocolo_externo,
            encaminhado=instance.encaminhado,
            chancela=instance.chancela,
            grupo=instance.grupo,
            serial=instance.serial,
            tipo_documento=nil_pk(instance.tipo_documento, None),
            tipo_documento_unicode=nil_unicode(instance.tipo_documento, None),
            habilitado=instance.habilitado,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            assunto=instance.assunto,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            servidor_origem=nil_pk(instance.servidor_origem, None),
            servidor_origem_unicode=nil_unicode(instance.servidor_origem, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            # com_workflow=instance.com_workflow,
            codigo=instance.codigo,
            interessado=nil_pk(instance.interessado, None),
            interessado_unicode=nil_unicode(instance.interessado, None),
            excluido=instance.excluido,
            user=nil_pk(user, None),
            user_unicode=nil_unicode(user, None),
        )

        return rst
