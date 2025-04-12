from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers
from rest_framework import status

from apiv2.const import MSG_SUCCESS_METHOD
from contrib.utils import getLogger
import rest_framework.serializers

log = getLogger(__name__)

from rh.models import Banco, DadoBancarioPessoa, Pessoa
from standard.models import Choice


class BancoSerializer(BaseSerializer):

    unicode = serializers.SerializerMethodField()

    class Meta:
        model = Banco
        fields = "__all__"

    def get_unicode(self, obj):
        return obj.__str__()


class DadoBancarioPessoaSerializer(BaseSerializer):

    unicode = serializers.SerializerMethodField()
    servidor = serializers.SerializerMethodField()
    tipo_conta_display = serializers.SerializerMethodField()

    class Meta:
        model = DadoBancarioPessoa
        fields = "__all__"

    def get_unicode(self, obj):
        if obj.agencia_numero and obj.conta_numero:

            ag = obj.agencia_numero
            conta = obj.conta_numero

            if obj.agencia_dv and obj.agencia_dv != "":
                ag += obj.agencia_dv
            if obj.conta_dv and obj.conta_dv != "":
                conta += obj.conta_dv

            return f"{obj.banco.nome} - {ag} - {conta}"

        return f"{obj.banco.nome} - {obj.agencia} - {obj.conta_corrente_completa}"

    def get_servidor(self, obj):
        return obj.pessoa.pessoafisica.servidor_set.last().id

    def get_tipo_conta_display(self, obj):
        return obj.get_tipo_conta_display()

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            request = self.context.get("request")
            servidor_id = request.data.get("servidor", None)
            tipo_conta = request.data.get("tipo_conta", None)
            banco_id = request.data.get("banco", None)
            agencia_numero = request.data.get("agencia_numero", None)
            agencia_dv = request.data.get("agencia_dv", None)
            conta_numero = request.data.get("conta_numero", None)
            conta_dv = request.data.get("conta_dv", None)
            principal = request.data.get("principal", False)

            pessoa = Pessoa.objects.get(pessoafisica__servidor__pk=servidor_id)
            banco = Banco.objects.get(pk=banco_id)

            agencia = f"{agencia_numero}{agencia_dv}"
            conta_completa = f"{conta_numero}{conta_dv}"

            if type(principal) == "str":
                if principal == "True" or principal == "TRUE" or principal == "true":
                    principal = True
                elif (
                    principal == "False" or principal == "FALSE" or principal == "false"
                ):
                    principal = False

            data = DadoBancarioPessoa.objects.create(
                pessoa=pessoa,
                principal=principal,
                banco=banco,
                tipo_conta=tipo_conta,
                agencia=agencia,
                conta_corrente_completa=conta_completa,
                conta_numero=conta_numero,
                conta_dv=conta_dv,
                agencia_numero=agencia_numero,
                agencia_dv=agencia_dv,
            )

            serializer = DadoBancarioPessoaSerializer(data)

            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["post"],
                    "data": serializer.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


class TipoContaSerializer(BaseSerializer):

    id = serializers.SerializerMethodField()
    descricao = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["id", "descricao"]

    def get_id(self, obj):
        return obj.value

    def get_descricao(self, obj):
        return obj.label
