# -*- coding: utf-8 -*-

from datetime import datetime

from adm.patrimonio.models import (
    BaixaAjusteInventario,
    BaixaAlienacao,
    BaixaDoacao,
    BaixaExtravio,
    BaixaInservibilidade,
    BaixaItem,
    BaixaMudancaClassificacao,
    BaixaSinistro,
    BaixaTransferencia,
    Conta,
    NotaBaixa,
    NotaEntrada,
    Patrimonio,
)
from contrib.newrest import Restful
from contrib.nil import nil_date, nil_pk, nil_unicode
from contrib.utils import DateUtils, getLogger
from django.db import transaction
from rh.models import Pessoa

log = getLogger(__name__)


class PATItemBaixa(Restful):

    full_text_index = ("patrimonio__plaqueta__icontains",)

    _model = BaixaItem

    force_orm_single = True

    def import_from_inputnotes(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        try:
            down_note = NotaBaixa.objects.get(pk=self.request.POST.get("nota"))
            with transaction.atomic():
                for input_note in NotaEntrada.objects.filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    down_note.import_from_inputnote(input_note)
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Patrimonios importados com sucesso.")

        self.renderer(rst)

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        def nil_display(x, f, v):
            return getattr(x, f)() if x else v

        params.update(
            icons=instance.icons,
            patrimonio=nil_pk(instance.patrimonio, ""),
            patrimonio_plaqueta=(
                instance.patrimonio.plaqueta if instance.patrimonio else None
            ),
            patrimonio_unicode=nil_unicode(instance.patrimonio, ""),
            data_tombo=nil_date(instance.patrimonio.data_tombo, ""),
            conservacao=nil_display(instance.patrimonio, "get_conservacao_display", ""),
            valor_baixa=float(instance.valor_baixa or 0),
            valor_atual=float(instance.patrimonio.valor_atual or 0),
            observacao=instance.observacao,
        )

        params.update(avaliacao=params.get("valor_baixa") - params.get("valor_atual"))

        return params

    def get_params(self, querydict=None, **kargs):
        params = super(PATItemBaixa, self).get_params(querydict, **kargs)

        if "nota" in params:
            params.update(nota=NotaBaixa.objects.get(pk=params.get("nota")))

        if "patrimonio" in params:
            params.update(
                patrimonio=Patrimonio.objects.get(pk=params.get("patrimonio"))
            )

        log.debug(params)

        return params


class PATNotaBaixa(Restful):

    _model = NotaBaixa

    full_text_index = (
        "processo__icontains",
        "cache_numero__icontains",
        "itens__patrimonio__plaqueta__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.baixa.Manage")')

    def get_params(self, querydict=None, **kwargs):
        params = super().get_params(querydict, **kwargs)

        if "conta" in params:
            params.update(conta=Conta.objects.get(pk=params.get("conta")))

        if params.get("data_documento", "") not in ("", None):
            params.update(
                data_documento=DateUtils.str_to_date(params.get("data_documento"))
            )
        elif "data_documento" in params:
            del params["data_documento"]

        if params.get("data_liquidacao", "") not in ("", None):
            params.update(
                data_liquidacao=DateUtils.str_to_date(params.get("data_liquidacao"))
            )
        elif "data_liquidacao" in params:
            del params["data_liquidacao"]

        return params

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        def nil_date(x, v):
            return DateUtils.date_to_str(x) if x else v

        params.update(
            conta=instance.conta.pk if instance.conta is not None else "",
            conta_unicode=str(instance.conta) if instance.conta is not None else "",
            state=instance.state,
            state_display=instance.get_state_display(),
            documento=instance.documento,
            processo=instance.processo,
            numero=instance.numero,
            cache_numero=instance.cache_numero,
            liquidacao=instance.liquidacao,
            data_documento=nil_date(instance.data_documento, ""),
            data_baixa=nil_date(instance.data_baixa, ""),
            data_cadastro=nil_date(instance.data_cadastro, ""),
            data_liquidacao=nil_date(instance.data_liquidacao, ""),
            unicode=str(instance.my_origin),
            type=str(instance.cache_type),
            icons=instance.my_origin.icons,
            pre_baixa=nil_pk(instance.pre_baixa, None),
            pre_baixa_unicode=nil_unicode(instance.pre_baixa, "Sem preparação"),
            subtype=instance.subtype,
        )
        return params


class PATBaixaAlienacao(PATNotaBaixa):

    _model = BaixaAlienacao

    def model_to_dict(self, instance):
        params = PATNotaBaixa.model_to_dict(self, instance)

        params.update(
            arrematante=(
                instance.arrematante.pk if instance.arrematante is not None else ""
            ),
            arrematante_unicode=(
                str(instance.arrematante) if instance.arrematante is not None else ""
            ),
        )
        return params

    def get_params(self, querydict=None, **kargs):
        params = super(PATBaixaAlienacao, self).get_params(querydict, **kargs)

        if "arrematante" in params:
            params.update(arrematante=Pessoa.objects.get(pk=params.get("arrematante")))

        return params


class PATBaixaDoacao(PATNotaBaixa):

    _model = BaixaDoacao

    def model_to_dict(self, instance):
        params = PATNotaBaixa.model_to_dict(self, instance)

        params.update(
            favorecido=(
                instance.favorecido.pk if instance.favorecido is not None else ""
            ),
            favorecido_unicode=(
                str(instance.favorecido) if instance.favorecido is not None else ""
            ),
        )
        return params

    def get_params(self, querydict=None, **kargs):
        params = super(PATBaixaDoacao, self).get_params(querydict, **kargs)

        if "favorecido" in params:
            params.update(favorecido=Pessoa.objects.get(pk=params.get("favorecido")))

        return params


class PATBaixaTransferencia(PATNotaBaixa):

    _model = BaixaTransferencia

    def model_to_dict(self, instance):
        params = PATNotaBaixa.model_to_dict(self, instance)

        params.update(
            favorecido=(
                instance.favorecido.pk if instance.favorecido is not None else ""
            ),
            favorecido_unicode=(
                str(instance.favorecido) if instance.favorecido is not None else ""
            ),
        )
        return params

    def get_params(self, querydict=None, **kargs):
        params = super(PATBaixaTransferencia, self).get_params(querydict, **kargs)

        if "favorecido" in params:
            params.update(favorecido=Conta.objects.get(pk=params.get("favorecido")))

        return params


class PATBaixaSinistro(PATNotaBaixa):

    _model = BaixaSinistro


class PATBaixaExtravio(PATNotaBaixa):

    _model = BaixaExtravio


class PATBaixaInservibilidade(PATNotaBaixa):

    _model = BaixaInservibilidade


class PATMudancaClassificacao(PATNotaBaixa):

    _model = BaixaMudancaClassificacao


class PATAjusteInventario(PATNotaBaixa):

    _model = BaixaAjusteInventario
