from contrib.utils import getLogger

from django.conf import settings

from standard.models import Choice
from nomeacao.cadastramento.models import ConviteNomeacao


from nomeacao.sinc_form_nomeacao import SincFormNomeacao

from nomeacao.utils.sinc_form_nomeacao_utils import cadastrar_convite
from nomeacao.utils.sinc_form_nomeacao_utils import apagar_registros_convite

log = getLogger(__name__)


class SincFormNomeacaoResidentes(SincFormNomeacao):
    """
    Classe com métodos e lógicas específicos para realizar sincronização com API de formulários para nomeação de residentes.
    """

    def __init__(self, *args, **kargs):
        super(SincFormNomeacaoResidentes, self).__init__(*args, **kargs)
        self.tipo_nomeacao = (
            Choice.objects.filter(
                app_label="nomeacao", name="TIPO_NOMEACAO", label="Residente"
            )
            .first()
            .value
        )

    def buscar_base_url(self):
        return "https://residentes.mpmt.mp.br/api/v1/residentes"

    def buscar_headers(self):
        token = settings.TOKEN_API_NOMEACAO_RESIDENTES
        headers = {
            "User-Agent": "Python3",
            "Authorization": f"Bearer {token}",
        }

        return headers

    def buscar_lista_cpfs(self, cpfs_nao_buscar=[]):
        url = self.url
        res = self.realizar_req(url=url)

        response = res.json()
        return set(response).difference(set(cpfs_nao_buscar))

    def req_detalhe_cpf(self, cpf):
        cpf = cpf.replace("-", "").replace(".", "")
        url = f"{self.buscar_base_url()}/{cpf}/show"

        try:
            res = self.realizar_req(url=url)
            res = res.json()

            if res == "Unauthorized":
                log.info(">>> Erro de permissão na requisição. Não autorizado.")
                return None

            return res
        except Exception as e:
            log.info(f">>> Erro na requisição para o cpf: {cpf}")
            log.error(e)
            return None

    def buscar_anexo_url(self, arquivo_path):
        return f"{self.buscar_base_url()}/serveFile/{arquivo_path}"

    def req_arquivo_anexo(self, arquivo_path):
        url = self.buscar_anexo_url(arquivo_path)

        res = self.realizar_req(url=url)

        return res

    def sinc_cpf(self, cpf):
        q_convite = ConviteNomeacao.objects.filter(
            tipo_nomeacao=self.tipo_nomeacao,
            convidado__documentacao__cpf=cpf,
        )

        atualizar_convite = q_convite.exists() and q_convite.first().sinc_form is True
        if atualizar_convite:
            convite = q_convite.first()
            log.info(
                f">>> Realizando atualização do convite de nomeação para: {convite.convidado}."
            )
            apagar_registros_convite(convite)

        if q_convite.exists() is False or atualizar_convite:
            log.info(
                f">>> Buscando dados na API do formulário de residentes para o CPF: {cpf}."
            )
            res_detalhe_cpf = self.req_detalhe_cpf(cpf)
            if res_detalhe_cpf:
                log.info(f">>> Criando convite para o CPF: {cpf}")
                cadastrar_convite(self.tipo_nomeacao, res_detalhe_cpf)
