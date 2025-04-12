from datetime import datetime

from contrib.middleware import get_current_user, set_current_user
from contrib.utils import getLogger

from rh.gfp.models import Servidor
from rh.folhaponto.models import GeraHistoricoeventos
from rh.registerpoint.models import MarkPoint

from rh.folhaponto.folhaponto_import_utils import (
    normalizar_cpf_origem,
    normalizar_dados_registro_folhaponto_batida,
)
from django.db.models import Q


log = getLogger(__name__)


class FolhaPontoImportBatidas(object):
    """
    Classe com métodos e lógicas para importação de dados de Justificativas do Folha Ponto (banco Oracle - MDC4WEB)
    para o Athenas (módulo registerpoint, tabela MarkPoint)
    """

    def __init__(self, *args, **kwargs):
        usuario = get_current_user()
        if usuario is None:
            set_current_user("athenas")

        self.servidor = None

    def buscar_registro_batida(self, batida_id):
        """
        Método para buscar o registro de Batida do FolhaPonto no banco Oracle (MDC4WEB) na tabela 'gera_historicoeventos',
        utilizando o campo 'codigo'.
        """

        try:
            folha_ponto_batida = GeraHistoricoeventos.objects.only(
                "pk", "matricula", "data"
            ).get(pk=batida_id)
        except:
            folha_ponto_batida = None

        return folha_ponto_batida

    def buscar_servidor(self, folha_ponto_batida):
        """
        Método para buscar o Servidor no Athenas para criar a Batida na estrutura do Athenas (MarkPoint).
        """

        try:
            cpf = normalizar_cpf_origem(folha_ponto_batida.matricula)
            q_servidor = Servidor.objects.filter(
                Q(pessoa_fisica__cpf=cpf),
                Q(exercise_date__lte=folha_ponto_batida.data.date()),
                Q(termination_date__gte=folha_ponto_batida.data.date())
                | Q(termination_date__isnull=True),
            )

            if q_servidor.exists() is False:
                self.servidor = None
            elif q_servidor.count() > 1:
                q_servidor_ativo = q_servidor.filter(ativo=True)
                self.servidor = (
                    q_servidor_ativo.first()
                    if q_servidor_ativo.exists()
                    else q_servidor.first()
                )
            else:
                self.servidor = q_servidor.first()

        except:
            self.servidor = None

    def criar_mark_point_batida(self, dados_marcacao_batida):
        """
        Método para criar registro de batida no model MarkPoint
        """

        log.info(
            f"# Criando Batida de Folha Ponto no Athenas para o Servidor: {self.servidor}"
        )
        try:
            params = {
                "mark": dados_marcacao_batida["marcacao_time"],
                "employee": self.servidor,
                "day": dados_marcacao_batida["marcacao_dia"],
                "marcacao": dados_marcacao_batida["marcacao"],
                "marcacao_valida": True,
                "tabela_import": "gera_historicoeventos",
                "codigo_import": dados_marcacao_batida["codigo_import"],
            }

            q_markpoint = MarkPoint.objects.filter(
                mark__hour=dados_marcacao_batida["marcacao_hora"],
                mark__minute=dados_marcacao_batida["marcacao_minuto"],
                day=dados_marcacao_batida["marcacao_dia"],
                employee=self.servidor,
            )
            if not q_markpoint.exists():
                MarkPoint.objects.create(**params)

        except Exception as e:
            log.info(
                f">>> Erro ao criar Batida no Athenas para o Servidor: {self.servidor}"
            )
            log.error(e)

    def validar_data_batida(self, folha_ponto_batida):
        try:
            datetime(
                folha_ponto_batida.data.year,
                folha_ponto_batida.data.month,
                folha_ponto_batida.data.day,
                folha_ponto_batida.data.hour,
                folha_ponto_batida.data.minute,
                folha_ponto_batida.data.second,
            )
            return True
        except:
            return False

    def importar_registro_batida_folhaponto(self, batida_id):
        """
        Método geral que fará a importação do registro de batida do Folha Ponto para o Athenas
        """

        folha_ponto_batida = self.buscar_registro_batida(batida_id)
        if folha_ponto_batida is None:
            msg_erro = f">>> Registro de Batida do Folha Ponto não encontrado na tabela GeraHistoricoeventos, pk: {batida_id}"
            log.info(msg_erro)
            log.error(msg_erro)
        elif self.validar_data_batida(folha_ponto_batida) is False:
            msg_erro = f">>> Registro de Batida do Folha Ponto com data inválida, pk: {batida_id} - data: {batida_id.data}"
            log.info(msg_erro)
            log.error(msg_erro)
        else:
            log.info(
                f"# Iniciando importação de Justificativa do Folha Ponto para Athenas do pk: {batida_id}"
            )

            self.buscar_servidor(folha_ponto_batida)
            if self.servidor is None:
                msg_erro = f""">>> Servidor não encontrado para o registro de Batida do Folha Ponto,
                pk do registro: {batida_id} - matricula utilizada na busca: {folha_ponto_batida.matricula}"""
                log.info(msg_erro)
                log.error(msg_erro)
            else:
                log.info(
                    f"# Normalizando dados de Batida do Folha Ponto para Athenas do Servidor: {self.servidor}"
                )
                dados_normalizados_batida = normalizar_dados_registro_folhaponto_batida(
                    folha_ponto_batida
                )

                if dados_normalizados_batida is False:
                    log.info(
                        f"# Não foi possível normalizar os dados - Servidor: {self.servidor} - pk: {batida_id}"
                    )
                else:
                    self.criar_mark_point_batida(dados_normalizados_batida)
