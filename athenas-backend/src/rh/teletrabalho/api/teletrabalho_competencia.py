import json
from datetime import datetime, date, timedelta

from django.db.models import (
    Q,
    F,
    fields,
    Case,
    Value,
    When,
    CharField,
    ExpressionWrapper,
)

from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger

from rh.models import MovimentacaoTeletrabalho
from rh.teletrabalho.teletrabalho_competencia_utils import (
    get_query_teletrabalho_periodo,
)

from rh.pvf.const import (
    STS_EFFECTIVE,
    STS_WAI_SUBS_SCIENCE,
    STS_WAI_APPROVER,
    STS_WAI_EFFECTIVENESS,
    STS_REJECTED,
    STS_CORREGEDORIE_ADVISORY,
    STS_STAND_BY,
    STS_ESCALA_ENVIADA,
)

from contrib.utils import QuerySetChain


json_engine = get_json_engine()
log = getLogger(__name__)


class TeletrabalhoCompetenciaRestful(RestfulDRY):

    _model = MovimentacaoTeletrabalho

    status_display_mapping = {
        STS_EFFECTIVE: "Efetivado",
        STS_WAI_SUBS_SCIENCE: "Aguardando Ciência do Substituto",
        STS_WAI_APPROVER: "Aguardando Aprovador",
        STS_WAI_EFFECTIVENESS: "Aguardando Efetivação",
        STS_REJECTED: "Indeferido",
        STS_CORREGEDORIE_ADVISORY: "Aguardando Assessoria da Corregedoria",
        STS_STAND_BY: "Aguardando Envio",
        STS_ESCALA_ENVIADA: "Escala Enviada",
        None: "Não Enviado",
    }

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.teletrabalho.teletrabalho_competencia.Manage")'
        )

    def get_query(self):

        periodo_ano = int(self.request.GET.get("periodo_ano", datetime.today().year))
        periodo_mes = int(self.request.GET.get("periodo_mes", datetime.today().month))

        # Construa as datas de início e fim do período
        inicio_periodo = date(periodo_ano, periodo_mes, 1)
        if periodo_mes == 12:
            fim_periodo = date(periodo_ano + 1, 1, 1) - timedelta(
                days=1
            )  # Próximo mês no primeiro dia, menos um
        else:
            fim_periodo = date(periodo_ano, periodo_mes + 1, 1) - timedelta(
                days=1
            )  # Próximo mês no primeiro dia, menos um

        # Consulte todas as instâncias de MovimentacaoTeletrabalho que atendem à condição
        query = MovimentacaoTeletrabalho.objects.filter(
            Q(data_inicio__lte=fim_periodo, data_fim__gte=inicio_periodo)
        )

        return query

    def get_params_query(self):
        params = {}
        params["periodo_ano"] = int(
            self.request.GET.get("periodo_ano", datetime.today().year)
        )
        params["periodo_mes"] = int(
            self.request.GET.get("periodo_mes", datetime.today().month)
        )
        params["filtro"] = self.request.GET.get("filtro", "todos")
        params["busca"] = self.request.GET.get("keyword")

        return params

    def do_full_text_filter(self, query):
        """Realiza pesquisa com valor de keyword do Request nos campos adicionados em full_text_index.

        :param query: QuerySet a ser aplicada o filtro com keyword.

        :returns: QuerySet com filtro aplicado.
        """
        query = self.get_query()

        if self.full_text_index:
            qf = None

            for index in self.full_text_index:
                q = Q(**{index: self.request.GET.get("keyword")})
                qf = q if qf is None else Q(qf | q)

            query = query.filter(qf)

        return get_query_teletrabalho_periodo(
            query=query, params=self.get_params_query()
        )

    def do_get(self, pk=None):
        """Executa uma requisição GET

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância ou conjunto de instâncias.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        if pk is not None:
            # Buscar um item
            try:
                inst = get_query_teletrabalho_periodo(
                    query=self.get_query().get(pk=pk), params=self.get_params_query()
                )
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Processo com sucesso!",
                        "instance": self.model_to_dict(inst),
                    }
                )
        else:
            # Trazer a lista de itens
            try:
                query = get_query_teletrabalho_periodo(
                    query=self.get_query(), params=self.get_params_query()
                )
                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                query = self.remove_projection(query)

                rst.update(count=query.count())
                query = self.do_page(query)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                log.exception(str(e))
                rst.update(message=str(e))
            else:
                rst.update(
                    {
                        "collection": [self.model_to_dict(record) for record in query],
                        "success": True,
                        "message": "Processado com sucesso!",
                    }
                )

        return rst

    def model_to_dict(self, instance):
        params = super(TeletrabalhoCompetenciaRestful, self).model_to_dict(instance)

        f = []
        if "filter" in self.request.GET:
            try:
                f = json.loads(self.request.GET.get("filter"))
            except Exception:
                f = []

        periodo_filtro = datetime.now().date()
        if f:
            periodo_filtro = datetime.strptime(f[0]["value"], "%Y-%m-%d").date()

        params.update(
            {
                "matricula": instance.servidor.matricula,
                "servidor": instance.servidor.pessoa_fisica.social_name,
                "lotacao": instance.lotacao.lotacao.nome if instance.lotacao else "",
                "categoria_funcional": instance.servidor.get_type_by_possession_display(),
                "aprovador": instance.aprovador.pessoa_fisica.social_name,
                "email": instance.servidor.pessoa_fisica.email_institucional,
                "gedoc": instance.gedoc,
                "ato": instance.get_tipo_ato_display(),
                "solicitacao": instance.solicitacao,
                "status": instance.status if hasattr(instance, "status") else "",
                "periodo_ano": periodo_filtro.year,
                "periodo_mes": periodo_filtro.month,
            }
        )

        return params

    def export(self, args=[]):

        periodo_ano = self.request.GET.get("periodo_ano", datetime.today().year)
        periodo_mes = self.request.GET.get("periodo_mes", datetime.today().month)
        nome_arqruivo = (
            f"Relatório de Teletrabalho da Competência {periodo_mes}-{periodo_ano}"
        )

        rst = []

        query = get_query_teletrabalho_periodo(
            query=self.get_query(), params=self.get_params_query()
        )
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        if isinstance(query, QuerySetChain):
            query = query._all()

        for record in query:
            if record:
                rst.append(
                    {
                        "matricula": record.servidor.matricula,
                        "servidor": record.servidor.pessoa_fisica.social_name,
                        "lotacao": (
                            record.lotacao.lotacao.nome if record.lotacao else ""
                        ),
                        "email": record.servidor.pessoa_fisica.email_institucional,
                        "categoria_funcional": record.servidor.get_type_by_possession_display(),
                        "aprovador": record.aprovador.pessoa_fisica.social_name,
                        "gedoc": record.gedoc,
                        "ato": record.get_tipo_ato_display(),
                        "solicitacao": record.solicitacao,
                        "status": record.status if hasattr(record, "status") else "",
                        "data_inicio": record.data_inicio.strftime("%d/%m/%Y"),
                        "data_fim": record.data_fim.strftime("%d/%m/%Y"),
                    }
                )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = (
            f"attachment; filename={nome_arqruivo}.csv"
        )
        renderer(rst)
