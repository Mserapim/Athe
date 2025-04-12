from django.core.management.base import BaseCommand
from rh.models import OrdemServicoAthenas
from rh.sisdias.models import Sdia01OrdemServico

import sys

# import oracledb

# sys.modules["cx_Oracle"] = oracledb


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá realizar o carregamento das movimentações de diárias para do Banco de Dados Oracle Database SISDIAS para o banco Postgres"""

    def handle(self, *args, **options):
        self.get_ordem_servico()

    def get_ordem_servico(self):
        import os

        os.environ.setdefault("LD_LIBRARY_PATH", "/app/oracle/client/21c/")
        query = Sdia01OrdemServico.objects.using("sisdias")

        for q in query:
            try:
                print(f"Ordem de Serviço: {q.nome_servidor} {q.numero}")
                OrdemServicoAthenas.objects.update_or_create(
                    numero=q.numero,
                    defaults={
                        "data": q.data,
                        "local": q.local,
                        "chapa_servidor": q.chapa_servidor,
                        "nome_servidor": q.nome_servidor,
                        "cargo_servidor": q.cargo_servidor,
                        "num_diaria_estado": q.num_diaria_estado,
                        "valor_unit_estado": q.valor_unit_estado,
                        "num_diaria_pais": q.num_diaria_pais,
                        "valor_unit_pais": q.valor_unit_pais,
                        "num_diaria_exterior": q.num_diaria_exterior,
                        "valor_unit_exterior": q.valor_unit_exterior,
                        "chapa_ordenador": q.chapa_ordenador,
                        "valor_importancia": q.valor_importancia,
                        "data_setor_pessoal": q.data_setor_pessoal,
                        "chapa_resp_pessoal": q.chapa_resp_pessoal,
                        "num_empenho": q.num_empenho,
                        "data_empenho": q.data_empenho,
                        "data_setor_financeiro": q.data_setor_financeiro,
                        "data_cancelamento": q.data_cancelamento,
                        "data_protocolo_banco": q.data_protocolo_banco,
                        "relatorio_entregue": q.relatorio_entregue,
                        "descricao_resultado": q.descricao_resultado,
                        "observacoes": q.observacoes,
                        "data_relatorio": q.data_relatorio,
                        "meiadiaria": q.meiadiaria,
                        "data_recebido": q.data_recebido,
                        "auxilios_devolvidos": q.auxilios_devolvidos,
                        "valor_devolucao": q.valor_devolucao,
                        "numerounicocnmp": q.numerounicocnmp,
                        "totaldescontos": q.totaldescontos,
                        "totalareceber": q.totalareceber,
                        "qtd_auxilios": q.qtd_auxilios,
                        "qtd_transportes": q.qtd_transportes,
                        "valor_total_bruto": q.valor_total_bruto,
                        "valor_total_liquido": q.valor_total_liquido,
                        "comprovante_arquivo": q.comprovante_arquivo,
                        "relatorio_viagem_arquivo": q.relatorio_viagem_arquivo,
                        "data_pagamento": q.data_pagamento,
                        "empenho": q.empenho,
                        "data_valor_devolvido": q.data_valor_devolvido,
                        "valor_devolvido": q.valor_devolvido,
                    },
                )
            except Exception as e:
                print(e)
