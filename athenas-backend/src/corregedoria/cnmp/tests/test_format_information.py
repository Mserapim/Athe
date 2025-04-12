import unittest
from rh.models import Servidor, MovimentacaoPosse
from corregedoria.cnmp.workflow import ExportDataEmployee


class SCNMPTest(unittest.TestCase):

    def test_data_structure(self):

        employee = Servidor.objects.get(matricula=97909)
        data = ExportDataEmployee.prepare_data_to_send(pk=employee.pk)
        print(data)

    def test_data_nomeacao(self):
        for s in Servidor.objects.filter(tipo="M", ativo=True):
            employee = s

            movimentacoes = MovimentacaoPosse.objects.filter(
                servidor=employee, quadro__cargo__tipo_lei_cargo="EF"
            ).order_by("data_exercicio")

            mov_primeira = movimentacoes.first()
            mov_ultima = movimentacoes.last()

            def get_data_nomeacao():
                data_publicacao = None
                data_expedicao = None
                data_posse = mov_primeira.data_posse

                if mov_primeira.publicacao_movimentacao:
                    data_publicacao = (
                        mov_primeira.publicacao_movimentacao.data_publicacao
                    )
                    data_expedicao = mov_primeira.publicacao_movimentacao.data_expedicao
                else:
                    return data_posse

                if data_publicacao and data_publicacao <= data_posse:
                    return data_publicacao
                elif data_expedicao and data_expedicao <= data_posse:
                    return data_expedicao
                else:
                    return data_posse

            nomeacao = get_data_nomeacao()
            posse = mov_primeira.data_posse
            exercicio = mov_primeira.data_exercicio
            print(employee)
            if nomeacao > posse:
                print("Erro nomeacao maior que posse")
                print(employee)

            if posse > exercicio:
                print("Erro exercicio maior que posse")
                print(employee)
