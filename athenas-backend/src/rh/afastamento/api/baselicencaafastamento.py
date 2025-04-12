# -*- coding: utf-8 -*-

from rh.dayoff.signals.departure import usufruct_cancel
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from rh.api.movimentacao import RHMovimentacaoPessoalRestful
from rh.afastamento.models import BaseLicencaAfastamento


log = getLogger(__name__)


class AFABaseLicencaAfastamentoRestful(RHMovimentacaoPessoalRestful):

    _model = BaseLicencaAfastamento

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__cpf__iexact",
    )

    exclude_fields = [
        "afastamento_ptr",
        "baselicencasaudejuntamedica_ptr",
        "licencasaude_ptr",
        "licenca_ptr",
        "baselicencaafastamento_ptr",
        "movimentacaopessoal_ptr",
    ] + RHMovimentacaoPessoalRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + RHMovimentacaoPessoalRestful.force_persist_boolean_fields
    )

    def json(self, args=[]):
        departament = "rh"
        if (
            get_current_user().has_perm("afastamento.ver_membros")
            and get_current_user().has_perm("afastamento.ver_servidores") is False
        ):
            departament = "expediente"
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.baselicencaafastamento.Manage", {departament: "%s"})'
            % departament
        )

    def get_query(self):
        return super(AFABaseLicencaAfastamentoRestful, self).get_query()

    def model_to_dict(self, instance):
        _dict_ = super(AFABaseLicencaAfastamentoRestful, self).model_to_dict(instance)

        icons = []
        scheduled = instance.pending_period
        days = instance.pending_period_days
        if not scheduled and days == float("-inf"):
            days = "Período com data fim não definida."
        icons.append(
            {
                "iconCls": (
                    "icon-core icon-core-users"
                    if scheduled
                    else "icon-core icon-core-warn"
                ),
                "title": (
                    "Possui Substituição/Inativação"
                    if scheduled
                    else ("Substituição/Inativação período pendente: %s" % days)
                ),
            }
        )
        for substitution in instance.substituicao.filter():
            if not substitution.designation_substituted:
                icons.append(
                    {
                        "iconCls": "icon-core icon-core-warn",
                        "title": "Designação de servidor substituído não encontrado %s"
                        % substitution.servidor_substituido,
                    }
                )
                break
            if (
                substitution.substituicao_finalizada() or substitution.is_active()
            ) and not substitution.designation_substitute:
                icons.append(
                    {
                        "iconCls": "icon-core icon-core-warn",
                        "title": "Designação de servidor substituto não encontrado %s"
                        % (substitution.servidor),
                    }
                )
                break
            if (
                substitution.substituicao_finalizada()
                and substitution.designation_substitute
                and not substitution.designation_substitute.is_finished()
            ):
                icons.append(
                    {
                        "iconCls": "icon-core icon-core-warn",
                        "title": "Designação de servidor substituto não finalizada %s"
                        % (substitution.designation_substitute),
                    }
                )
                break

        _dict_.update(
            {
                "icons": icons,
                "type": instance.instancia_modelo.__class__.__name__.lower(),
                "annotation_class": instance.annotation_class,
            }
        )

        return _dict_
