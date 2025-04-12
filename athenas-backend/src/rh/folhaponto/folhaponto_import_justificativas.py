from contrib.middleware import get_current_user, set_current_user
from contrib.utils import getLogger

from rh.gfp.models import Servidor
from rh.folhaponto.models import MpFpjustificativa
from rh.pvf.models import PointJustification
from rh.registerpoint.const import (
    ORIGEM_JUSTIFICATIVA_IMPORTACAO_TRIELLO,
    TIPO_JUSTIFICATIVA_MAP,
)
from rh.registerpoint.models import MarkPoint

from rh.folhaponto.folhaponto_import_utils import (
    normalizar_cpf_origem,
    normalizar_dados_registro_folhaponto_justif,
)
from django.db.models import Q


log = getLogger(__name__)


class FolhaPontoImportJustificativa(object):
    """
    Classe com métodos e lógicas para importação de dados de Justificativas do Folha Ponto (banco Oracle - MDC4WEB)
    para o Athenas (módulo registerpoint, tabela MarkPoint)
    """

    def __init__(self, *args, **kwargs):
        usuario = get_current_user()
        if usuario is None:
            set_current_user("athenas")

        self.servidor = None

    def buscar_registro_justificativa(self, justif_codigo):
        """
        Método para buscar o registro de Justificativa do FolhaPonto no banco Oracle (MDC4WEB) na tabela 'mp_fpjustificativa',
        utilizando o campo 'codigo'.
        """

        try:
            folha_ponto_justif = MpFpjustificativa.objects.only(
                "pk", "matricula", "data", "justificativa", "codigo"
            ).get(codigo=justif_codigo)
        except:
            folha_ponto_justif = None

        return folha_ponto_justif

    def buscar_servidor(self, folha_ponto_batida):
        """
        Método para buscar o Servidor no Athenas para criar a Justificativa na estrutura do Athenas (MarkPoint).
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

    def criar_justificativa_folha_ponto(self, dados_marcacao_justif):
        """
        Método para criar registro de marcação justificada no model MarkPoint
        """

        log.info(
            f"# Criando Marcação de Folha Ponto Justificada no Athenas para o Servidor: {self.servidor}"
        )
        try:
            params = {
                "reason_type": TIPO_JUSTIFICATIVA_MAP.get(
                    int(dados_marcacao_justif["tipo"])
                ),
                "number_hours": "00:00",
                "start_date": dados_marcacao_justif["marcacao_dia"],
                "end_date": dados_marcacao_justif["marcacao_dia"],
                "employee": self.servidor,
                "origem": ORIGEM_JUSTIFICATIVA_IMPORTACAO_TRIELLO,
                "tipo_justificativa_origem": dados_marcacao_justif["tipo"],
            }

            just_ponto = PointJustification.objects.filter(
                start_date=dados_marcacao_justif["marcacao_dia"],
                end_date=dados_marcacao_justif["marcacao_dia"],
                employee=self.servidor,
            )
            if not just_ponto.exists():
                PointJustification.objects.create(**params)

        except Exception as e:
            log.info(
                f">>> Erro ao criar Marcação Justificada no Athenas para o Servidor: {self.servidor}"
            )
            log.error(e)

            return None

    def importar_registro_justif_folhaponto(self, justif_codigo):
        """
        Método geral que fará a importação do registro de justificativa do Folha Ponto para o Athenas
        """

        folha_ponto_justif = self.buscar_registro_justificativa(justif_codigo)
        if folha_ponto_justif is None:
            msg_erro = f">>> Registro de Justificativa do Folha Ponto não encontrado na tabela MpFpjustificativa, código: {justif_codigo}"
            log.info(msg_erro)
            log.error(msg_erro)
        else:
            log.info(
                f"# Iniciando importação de Justificativa do Folha Ponto para Athenas do código: {justif_codigo}"
            )

            self.buscar_servidor(folha_ponto_justif)
            if self.servidor is None:
                msg_erro = f""">>> Servidor não encontrado para o registro de Justificativa do Folha Ponto,
                código do registro: {justif_codigo} - matricula utilizada na busca: {folha_ponto_justif.matricula}"""
                log.info(msg_erro)
                log.error(msg_erro)
            else:
                log.info(
                    f"# Normalizando dados de Justificativa do Folha Ponto para Athenas do Servidor: {self.servidor}"
                )
                dados_normalizados_justif = normalizar_dados_registro_folhaponto_justif(
                    folha_ponto_justif
                )

                if dados_normalizados_justif is False:
                    log.info(
                        f"# Não foi possível normalizar os dados - Servidor: {self.servidor} código: {justif_codigo}"
                    )
                else:
                    mark_point_justif = self.criar_justificativa_folha_ponto(
                        dados_normalizados_justif
                    )
