import json

from contrib.newrest import Restful, RestfulDRY
from contrib.utils import getLogger, get_json_engine
from contrib.nil import nil_date, nil_datetime

from rh.antiguidades.models import ListaAntiguidadeMembros

from rh.antiguidades.lista_antiguidades_membros_utils import ListaAntiguidades as LAM


log = getLogger(__name__)
json_engine = get_json_engine()


class ListaAntiguidadeRestfull(RestfulDRY):

    _model = ListaAntiguidadeMembros

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    def get_query(self):
        return super().get_query().filter(servidor__ativo=True)

    def model_to_dict(self, instance):
        # rst = Restful.model_to_dict(self, instance)
        rst = super(ListaAntiguidadeRestfull, self).model_to_dict(instance)

        rst.update(
            matricula=instance.matricula,
            nome=instance.nome,
            posicao_concurso=instance.posicao_concurso,
            tipo_cargo=instance.get_tipo_cargo_display(),
            tempo_afastamento_formatado=instance.tempo_afastamento_formatado,
            total_instancia_formatado=instance.total_instancia_formatado,
            efetivo_exercicio_formatado=instance.efetivo_exercicio_formatado,
            total_carreira_formatado=instance.total_carreira_formatado,
            ordem_antiguidade=instance.ordem_antiguidade,
            data_inicio_carreira=nil_date(instance.data_inicio_carreira, None),
            data_inicio_instancia=nil_date(instance.data_inicio_instancia, None),
            tempo_afastamento=instance.tempo_afastamento,
            tempo_total_instancia=instance.tempo_total_instancia,
            tempo_efetivo_exercicio=instance.tempo_efetivo_exercicio,
            tempo_total_carreira=instance.tempo_total_carreira,
            origem=instance.origem,
            modified_at=nil_datetime(instance.modified_at, None),
        )

        return rst

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.lista_antiguidade_membros.Manage")')

    def export(self, args=[]):
        rst = []
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)
        for record in query:
            rst.append(
                {
                    "Ordem Antiguidade": record.ordem_antiguidade,
                    "Tipo Membro": record.get_tipo_cargo_display(),
                    "Servidor": record.servidor,
                    "Posicao Concurso": record.posicao_concurso,
                    "Data início Carreira": nil_date(record.data_inicio_carreira, None),
                    "Data início Instância": nil_date(
                        record.data_inicio_instancia, None
                    ),
                    "Tempo Afastamento": record.tempo_afastamento_formatado,
                    "Tempo Total Instância": record.total_instancia_formatado,
                    "Tempo Efetivo Exercicio": record.efetivo_exercicio_formatado,
                    "total_carreira_formatado": record.total_carreira_formatado,
                    "Origem": record.origem,
                    "Processado em": record.modified_at.strftime("%d/%m/%Y %H:%m"),
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)

    def atualizar_lista_antiguidades_membros_manual(self, *args):
        obj = {
            "success": True,
            "message": "Lista de Antiguidades de Membros Atualizada",
        }

        lam = LAM()
        lam.atualizar_lista_antiguidades_membros("Manual")

        self.response.write(json_engine.encode(obj))
