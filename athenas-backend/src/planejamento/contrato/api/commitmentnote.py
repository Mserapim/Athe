# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from planejamento.contrato.models import NotaEmpenho as CommitmentNote
from contrib.nil import nil_display

log = getLogger(__name__)


class PHACommitmentNote(RestfulDRY):

    _model = CommitmentNote

    full_text_index = (
        "numero_ne__icontains",
        "fornecedor__nome__icontains",
    )

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        try:
            tipo_saldo = instance.ref_valor_contrato.get_tipo_valor_contrato_display()
        except Exception:
            tipo_saldo = "-"

        rst.update(
            icons=instance.get_envio(),
            saldo=str(instance.get_saldo()),
            tipo_ne_display=nil_display(instance, "tipo", None) or "-",
            principal=tipo_saldo,
            fornecedor_display=instance.fornecedor.nome or "-",
        )

        return rst
