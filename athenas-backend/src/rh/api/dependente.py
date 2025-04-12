# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import DateUtils
from rh.models import Dependencia, Dependente

from contrib.utils import getLogger

log = getLogger(__name__)


class RHDependenteRestful(RestfulDRY):

    _model = Dependente

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "responsavel__nome__icontains",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__iexact",
    )

    def get_query(self):
        query = super(RHDependenteRestful, self).get_query()
        if "servidor_id" in self.request.GET:
            query = query.filter(servidor_id=self.request.GET.get("servidor_id"))
        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dependente.DependenteManage")')


class RHDependenciaRestful(RestfulDRY):

    _model = Dependencia

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dependente.DependenciaManage")')

    def get_state_icons(self, instance):
        status = []
        if instance.is_ativo and not instance.suspenso:
            status.append(
                {"iconCls": "icon-progressoes icon-progressoes-status", "alt": "Ativo"}
            )
        else:
            status.append(
                {
                    "iconCls": "icon-progressoes icon-progressoes-status-busy",
                    "alt": "Inativo",
                }
            )
        conflicts = instance.conflicts()
        if conflicts:
            status.append(
                {
                    "iconCls": "icon-core icon-core-warn",
                    "alt": "O depedente possui a mesma dependência com o(s) seguinte(s) servidor(es):<br /> %s"
                    % "".join(["%s<br />" % d.dependente.servidor for d in conflicts]),
                }
            )
        return status

    def model_to_dict(self, instance):
        params = super(RHDependenciaRestful, self).model_to_dict(instance)

        params.update(
            status=self.get_state_icons(instance),
        )

        return params

    def do_put_single(self, pk):
        rst = super(RHDependenciaRestful, self).do_put_single(pk)
        dp = Dependencia.objects.get(pk=pk)
        criado_no_vdf = dp.validar_origem_aux_creche(vdf=True)
        if criado_no_vdf:
            raise Exception(
                """ Registro gerado através do Vida Funcional!
            Caso necessário alterar dados, remover o registro e realizar um novo cadastro."""
            )
        return rst


class RHByUserDependentRestful(RHDependenteRestful):
    """API de Dependente (RH) com filtro para usuário

    Ao usar o mixin FilterEvalValueMixin, as filtragens passam a funcionar baseadas em
    usuário logado (__USER__), bem como e pessoa logada (__USER_PERSON__).
    """

    def get_query(self, *args, **kwargs):
        return (
            super().get_query(*args, **kwargs).filter(servidor__user=self.request.user)
        )

    def do_post(self, *args, **kwargs):
        self.response.status = 405

    def do_put(self, *args, **kwargs):
        self.response.status = 405

    def do_delete(self, *args, **kwargs):
        self.response.status = 405
