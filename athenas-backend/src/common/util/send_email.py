import json
import requests

from django.template.loader import render_to_string

from app.settings import DOMAIN, HERMES_TOKEN, HERMES_URL, HERMES_URL_ANEXO
from requests_toolbelt.multipart.encoder import MultipartEncoder

LIMIT_CARACTERES = 400


class EmailNotification:

    def send_email_default(
        self,
        receivers,
        subject,
        rendered_email_template,
        hermes_token=HERMES_TOKEN,
        sistema="ATHENAS",
    ):
        """
        Função destinada ao envio de email.

        :param receivers: (list) Lista contendo dicionários cujas chaves são o email e nome do destinatário da mensagem.
        :param subject: (str) Campo assunto do email.
        :param rendered_email_template: (str) Template de email renderizado para string.

        :returns: (Response) retornar o código de status de respostas HTTP para a chamada
        """

        data = {
            "assunto": subject,
            "conteudo": rendered_email_template,
            "hostname": DOMAIN,
            "listaDestinatario": receivers,
            "sistema": sistema,
            "token": hermes_token,
        }

        header = {"content-type": "application/json", "accept": "application/json"}

        response = requests.post(HERMES_URL, data=json.dumps(data), headers=header)

        return response

    def send_email_pvf(
        self,
        subject=None,
        message=None,
        solicitation=None,
        code=None,
        date=None,
        requester=None,
        receivers=None,
        receivers_rh_person_ids=None,
        observation="",
    ):
        """
        Envio de emails padrões do Portal Vida Funcional.

        :param subject: (str) Campo assunto do email.
        :param message: (str) Mensagem preambular do email.
        :param solicitation: (str) Campo contendo o tipo da solicitação.
        :param code: (str) Campo contendo o código da solicitação.
        :param date: (str) Campo contendo a data da solicitação.
        :param requester: (str) Nome do solicitante.

        :param receivers: (list) Lista contendo dicionários cujas chaves são o email e nome do destinatário da mensagem.
        :param receivers_rh_person_ids: (list) lista de ids do model Pessoa
        """
        from rh.models import PessoaFisica

        receivers_list = []

        if receivers_rh_person_ids is not None:

            for id in receivers_rh_person_ids:
                try:
                    receiver = {}
                    person = PessoaFisica.objects.get(pk=id)
                    if person.email:
                        receiver["email"] = person.email_institucional
                        receiver["nome"] = person.nome
                        receiver["idUsuario"] = (
                            person.servidor_set.last().id_usuario_mastiff
                        )
                        receivers_list.append(receiver)

                except Exception as e:
                    continue

            if receivers_list == []:

                receivers_list = receivers
        else:
            receivers_list = receivers

        if observation and len(observation) > LIMIT_CARACTERES:
            observation = f"{observation[:LIMIT_CARACTERES]} ..."

        html_content = render_to_string(
            "util/template_email_default.html",
            {
                "message": message,
                "solicitation": solicitation,
                "code": code,
                "date": date,
                "requester": requester,
                "observation": observation,
            },
        )

        EmailNotification().send_email_default(receivers_list, subject, html_content)

    def send_email_anexo(
        self,
        receivers,
        subject,
        rendered_email_template,
        anexos=None,
        files=[],
        hermes_token=HERMES_TOKEN,
        sistema="ATHENAS",
    ):
        """
        Função destinada ao envio de email.

        :param receivers: (list) Lista contendo dicionários cujas chaves são o email e nome do destinatário da mensagem.
        :param subject: (str) Campo assunto do email.
        :param rendered_email_template: (str) Template de email renderizado para string.

        :returns: (Response) retornar o código de status de respostas HTTP para a chamada
        """

        solicitacao = {
            "assunto": subject,
            "conteudo": rendered_email_template,
            "hostname": DOMAIN,
            "listaDestinatario": receivers,
            "sistema": sistema,
            "token": hermes_token,
        }
        payload = {"solicitacao": json.dumps(solicitacao)}

        if anexos:
            for i, anexo in enumerate(anexos):
                files.append(
                    ("file", (anexo.filename, open(anexo.absolute_path, "rb")))
                )

        # Configura o MultipartEncoder com os campos e arquivos
        fields = list(payload.items()) + files
        m = MultipartEncoder(fields=fields)

        # Envia a requisição
        response = requests.post(
            HERMES_URL_ANEXO, data=m, headers={"Content-Type": m.content_type}
        )

        return response
