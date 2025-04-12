from contrib.utils import get_json_engine, get_json_engine, getLogger

from engine.mq.models import Task
from contrib.newrest import RestfulDRY

from nomeacao.cadastramento.models import ConviteNomeacao

from nomeacao.cadastramento.tasks_sinc_form_nomeacao_residente import (
    sinc_cpf_nomeacao_residente_task,
)

json_engine = get_json_engine()
log = getLogger(__name__)


class NOMConviteNomeacao(RestfulDRY):

    _model = ConviteNomeacao

    full_text_index = (
        "convidado__nome_completo__icontains",
        "convidado__nome_social__icontains",
        "convidado__documentacao__cpf",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("nomeacao.cadastramento.Manage")')

    def model_to_dict(self, instance):
        params = super(NOMConviteNomeacao, self).model_to_dict(instance)

        params.update(
            {
                "cpf": instance.convidado.documentacao.cpf,
                "nome": instance.convidado.nome_completo,
                "nome_social": instance.convidado.nome_social,
            }
        )

        return params

    def sincronizar_convidado(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        try:
            cpf = self.request.POST.get("cpf")
            Task.start(
                sinc_cpf_nomeacao_residente_task,
                description=f"Processamento para sincronizar dados de nomeação de residente para o CPF: {cpf}.",
                user=self.request.user.id,
                cpf=cpf,
            )

            obj["message"] = (
                f"Iniciando sincronização de nomeação à convite de residente para o CPF: {cpf}."
            )
        except:
            obj["success"] = False
            obj["message"] = "Erro no processamento para calcular os registros."

        self.response.write(json_engine.encode(obj))
