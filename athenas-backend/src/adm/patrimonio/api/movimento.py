# -*- coding: utf-8 -*-

import json

from adm.patrimonio.models import (
    Localizacao,
    Movimento,
    MovimentoItem,
    MovimentoLogStatus,
    Patrimonio,
)
from contrib.newrest import Restful
from contrib.utils import DateUtils, employee_from_user, getLogger
from django.db import transaction
from django.db.models import Q
from rh.models import Servidor

log = getLogger(__name__)

if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


class PATMovimentoLogStatus(Restful):

    _model = MovimentoLogStatus

    force_upper = False

    force_orm_single = True

    def manifestate_status_change(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            self._read_special_verb()
            with transaction.atomic():
                for m in Movimento.objects.filter(
                    pk__in=self.request.PUT.getlist("pkset")
                ):
                    MovimentoLogStatus(
                        movimento=m,
                        status=self.request.PUT.get("status", None),
                        comentario=self.request.PUT.get("comentario", "")
                        or "O usuário optou por não fezer nenhum comentário",
                    ).save()
        except Exception as e:
            message = "%s %s" % (
                "Ao menos uma carga não teve seu estado alterado.<br/>",
                "Movimentação " + m.numero_cache + "<br/>",
            )

            log.exception(e)
            response.update(message=message)
        else:
            response.update(success=True, message="Mudanças realizadas com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))

    def model_to_dict(self, instance, *args, **kargs):
        _dict = super(PATMovimentoLogStatus, self).model_to_dict(
            instance, *args, **kargs
        )

        _dict.update(
            icons=instance.icons,
            atribuido_por_unicode=str(instance.atribuido_por),
            atribuido_por=instance.atribuido_por.pk,
            movimento=instance.movimento.pk,
            status_display=instance.get_status_display(),
            status=instance.status,
            atribuido=DateUtils.datetime_to_str(instance.atribuido),
            comentario=instance.comentario,
        )

        return _dict

    def get_params(self, querydict=None, **kargs):
        params = super(PATMovimentoLogStatus, self).get_params(querydict, **kargs)

        if params.get("movimento", "") != "":
            params.update(
                {"movimento": Movimento.objects.get(pk=params.get("movimento"))}
            )
        elif "movimento" in params:
            del params["movimento"]

        if params.get("comentario", "") in (""):
            params.update(comentario="O usuário optou por não fezer nenhum comentário.")

        return params


class PATMovimento(Restful):

    _model = Movimento

    full_text_index = (
        "numero_cache__icontains",
        "movimentado_por__username__icontains",
        "recebido_por__username__icontains",
        "validado_por__username__icontains",
        "responsavel_origem__matricula__icontains",
        "responsavel_origem__pessoa_fisica__nome__icontains",
        "responsavel_destino__matricula__icontains",
        "responsavel_destino__pessoa_fisica__nome__icontains",
        "origem__titulo__icontains",
        "origem__endereco__icontains",
        "destino__titulo__icontains",
        "destino__endereco__icontains",
        "destino__path_cache__iendswith",
    )

    force_orm_single = True

    def authorize(self, args=[]):
        rst = {"message": "nada feito ainda", "success": False}

        log.info("-" * 80)
        log.debug(self.get_params().get("pk__in", []))
        log.info("-" * 80)

        if self.request.method == "POST":
            try:
                with transaction.atomic():
                    pk__in = self.get_params().get("pk__in", [])
                    query = (
                        Movimento.objects.filter(pk__in=pk__in)
                        if isinstance(pk__in, (tuple, list)) is True
                        else Movimento.objects.filter(pk=pk__in)
                    )
                    for mov in query:
                        mov.authorize()
            except Exception as e:
                transaction.rollback()
                log.exception(e)
                rst.update(message=str(e))
            else:
                transaction.commit()
                rst.update(message="Autorizações dadas com sucesso.", success=True)
        else:
            rst.update(message="Chamada indevida!")

        self.renderer(rst)

    def perms(self, args=[]):
        user = self.request.user

        rst = {
            "can_authorize": user.has_perm("patrimonio.authorize_has_pgj")
            or user.has_perm("patrimonio.authorize_has_cgpgj")
            or user.has_perm("patrimonio.authorize_has_dg")
        }

        self.renderer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.movimento.TabManage", {})')

    def model_to_dict(self, instance, *args, **kargs):
        _dict = super(PATMovimento, self).model_to_dict(instance, *args, **kargs)
        tpl = """
<span style="display:block;text-align:center">%(username)s</span>
<span style="display:block;text-align:center">%(momento)s</span>
<span style="display:block;text-align:center;font-weight:bold">%(posicao)s</span>
"""

        _dict.update(
            icons=instance.icons,
            id=instance.id,
            identificacao="%05d/%4d" % (instance.numero, instance.ano),
            origem=instance.origem.pk if instance.origem else None,
            origem_unicode=(
                str(instance.origem)
                if instance.origem
                else str(Servidor.from_user(instance.movimentado_por))
            ),
            status=instance.status,
            status_display=instance.get_status_display(),
            destino=instance.destino.pk if instance.destino else None,
            destino_unicode=(
                instance.destino.path
                if instance.destino
                else str(instance.responsavel_destino)
            ),
            movimentado_por=instance.movimentado_por.pk,
            movimentado_por_unicode=str(instance.movimentado_por),
            validado_por=instance.validado_por.pk if instance.validado_por else None,
            validado_por_unicode=(
                str(instance.validado_por) if instance.validado_por else "ninguem"
            ),
            responsavel_destino=(
                instance.responsavel_destino.pk
                if instance.responsavel_destino
                else None
            ),
            responsavel_destino_unicode=(
                str(instance.responsavel_destino)
                if instance.responsavel_destino
                else "ninguem"
            ),
            recebido_por=instance.recebido_por.pk if instance.recebido_por else None,
            recebido_por_unicode=(
                str(instance.recebido_por) if instance.recebido_por else "ninguem"
            ),
            assinatura_entrega=tpl
            % {
                "username": instance.movimentado_por.username,
                "momento": (
                    DateUtils.datetime_to_str(instance.movimentado)
                    if instance.movimentado
                    else "00/00/00 00:00"
                ),
                "posicao": "Entrega",
            },
            assinatura_recebimento=tpl
            % {
                "username": (
                    instance.recebido_por.username
                    if instance.recebido_por
                    else "ninguem"
                ),
                "momento": (
                    DateUtils.datetime_to_str(instance.recebido)
                    if instance.recebido
                    else "00/00/00 00:00"
                ),
                "posicao": "Recebido",
            },
            assinatura_patrimonio=tpl
            % {
                "username": (
                    instance.validado_por.username
                    if instance.validado_por
                    else "ninguem"
                ),
                "momento": (
                    DateUtils.datetime_to_str(instance.validado)
                    if instance.validado
                    else "00/00/00 00:00"
                ),
                "posicao": "Patrimonio",
            },
            autorizado=[str(sign.quem) for sign in instance.autorizacoes.all()],
            has_notifications=instance.notifications.exists(),
        )

        return _dict

    def get_params(self, querydict=None, **kargs):
        params = super(PATMovimento, self).get_params(querydict, **kargs)

        if params.get("origem", "") != "":
            params.update({"origem": Localizacao.objects.get(pk=params.get("origem"))})
        elif "origem" in params:
            params.update(origem=None)

        if params.get("destino", "") != "":
            params.update(
                {"destino": Localizacao.objects.get(pk=params.get("destino"))}
            )
        elif "destino" in params:
            params.update(destino=None)

        if params.get("responsavel_destino", "") != "":
            params.update(
                {
                    "responsavel_destino": Servidor.objects.get(
                        pk=params.get("responsavel_destino")
                    )
                }
            )
        elif "responsavel_destino" in params:
            params.update(responsavel_destino=None)

        return params

    def get_query(self):
        query = super(PATMovimento, self).get_query()

        if not self.request.user.has_perm("patrimonio.admin_movimento"):
            servidor = employee_from_user(self.request.user)

            criterios = [
                Q(movimentado_por=self.request.user),
                Q(
                    origem__in=Localizacao.objects.filter(
                        lotacao_relacionada__responsavel=servidor
                    )
                ),
                Q(
                    Q(
                        destino__in=Localizacao.objects.filter(
                            lotacao_relacionada__responsavel=servidor
                        )
                    ),
                    Q(status__gte=2),
                ),
                Q(Q(responsavel_destino=servidor), Q(status__gte=2)),
            ]

            if self.request.user.has_perm("patrimonio.auth_movimento_view") is True:
                criterios.append(Q(status__in=[4, 5, 6]))

            filtro = None
            for criterio in criterios:
                filtro = criterio if filtro is None else Q(criterio | filtro)

            query = query.filter(filtro)

        return query


class PATMovimentoItem(Restful):

    _model = MovimentoItem

    full_text_index = ("patrimonio__plaqueta__icontains",)

    force_orm_single = True

    def model_to_dict(self, instance, *args, **kargs):
        _dict = super(PATMovimentoItem, self).model_to_dict(instance, *args, **kargs)

        _dict.update(
            icons=instance.icons,
            patrimonio=instance.patrimonio.pk,
            patrimonio_plaqueta=instance.patrimonio.plaqueta,
            patrimonio_unicode=instance.patrimonio.item_entrada.especie.titulo,
            patrimonio_conservacao=instance.patrimonio.get_conservacao_display(),
            patrimonio_descricao=instance.patrimonio.item_entrada.descricao,
        )

        return _dict

    def get_params(self, querydict=None, **kargs):
        params = super(PATMovimentoItem, self).get_params(querydict, **kargs)

        if params.get("patrimonio", "") != "":
            params.update(
                patrimonio=Patrimonio.objects.get(pk=params.get("patrimonio"))
            )
        elif "patrimonio" in params:
            del params["patrimonio"]

        if params.get("movimento", "") != "":
            params.update(movimento=Movimento.objects.get(pk=params.get("movimento")))
        elif "movimento" in params:
            del params["movimento"]

        return params
