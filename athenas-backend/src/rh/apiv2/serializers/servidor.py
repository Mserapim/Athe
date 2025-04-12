import random

from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import status
from contrib.utils import getLogger
from contrib.middleware import get_current_user

from rh.dayoff.models import Usufruct
from rh.models import PessoaFisica, Servidor, ServidorLotacao, MovimentacaoPosse
from rh.utils import envia_cod_validacao

from standard.models import Choice
from datetime import datetime, timedelta
from rh.const import TEMPO_COD_EMAIL


log = getLogger(__name__)


class SMCMembrosSerializer(ModelSerializer):
    """
    Serializer do model Servidor
    """

    class Meta:
        model = PessoaFisica
        fields = ["social_name", "cpf", "rg", "data_nascimento", "sexo"]


class AtualizaEmailPessoalSerializador(ModelSerializer):
    """
    Classe serializer para atualização do e-mail pessoal
    """

    class Meta:
        model = PessoaFisica
        fields = []

    def registrar_email_pessoal(self, dados):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        email_pessoal = dados.get("email_pessoal")

        if "@mpmt" in email_pessoal:
            rst.update(
                {"message": "Não é permitido inserir e-mail pessoal com domínio: @mpmt"}
            )
            return rst

        try:
            pf = PessoaFisica.objects.get(servidor=get_current_user().servidor)
            pf_data_cod_email = pf.data_codigo_email if pf.data_codigo_email else None
            diff_hora = None
            if pf_data_cod_email:
                diff_hora = datetime.now() - pf_data_cod_email
            if (
                diff_hora
                and diff_hora > timedelta(minutes=TEMPO_COD_EMAIL)
                or diff_hora is None
            ):
                pf.email_pessoal = email_pessoal
                pf.codigo_email = random.randint(100000, 999999)
                pf.email_pessoal_verificado = False
                pf.data_codigo_email = datetime.now()
                pf.save()

                envia_cod_validacao(pessoa=pf)
                rst.update(
                    {
                        "success": True,
                        "message": f"E-mail pessoal atualizado com sucesso: {pf.email_pessoal}",
                    }
                )
            else:
                rst.update(
                    {
                        "success": False,
                        "message": f"Último envio recente! Aguarde 5 minutos para solicitar um novo código",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class ValidaEmailPessoalSerializador(ModelSerializer):
    """
    Classe serializer para validar do e-mail pessoal
    """

    class Meta:
        model = PessoaFisica
        fields = []

    def validar_email_pessoal(self, dados):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            pf = PessoaFisica.objects.get(servidor=get_current_user().servidor)
            if pf.codigo_email == dados.get("codigo_email").replace(" ", ""):
                pf.email_pessoal_verificado = True
                pf.save()
                rst.update(
                    {
                        "success": True,
                        "message": f"E-mail pessoal validado com sucesso: {pf.email_pessoal}!",
                    }
                )
            else:
                rst.update(
                    {
                        "success": False,
                        "message": f"O código informado está incorreto!",
                    }
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class ServidorListagemSerializer(ModelSerializer):

    tipo_posse = SerializerMethodField()
    data_posse = SerializerMethodField()
    nome = SerializerMethodField()

    class Meta:
        model = Servidor
        fields = ["pk", "nome", "matricula", "tipo_posse", "ativo", "data_posse"]

    def get_fields(self):
        """
        Pega os query_params da requisição para definir a lista de campos que seram retornados pela API.
        Já existe uma lista com os campos minimos que seram retornado, mas caso exista o valor para dados
        complestos nos paramentros  'tipo_dados_pessoais' e 'tipo_dados_pessoais' mais camposss seram acrescentados,
        lembrando que cada campo possivel deve ser criado um metodo para buscar o valor do campo.
        """

        request = self.context.get("request")

        if request:
            dados_pessoais = request.query_params.get("tipo_dados_pessoais", "basico")
            dados_servidor = request.query_params.get("tipo_dados_servidor", "basico")
        else:
            dados_pessoais = "completo"
            dados_servidor = "completo"

        fields = super().get_fields()

        lista_fields = [
            "pk",
            "nome",
            "matricula",
            "tipo_posse",
            "ativo",
            "data_posse",
            "unicode",
        ]

        if dados_pessoais == "completo":
            lista_fields = lista_fields + [
                "cpf",
                "sexo",
                "sangue",
                "email_pessoal",
            ]
        if dados_servidor == "completo":
            lista_fields = lista_fields + [
                "email_institucional",
                "chefe_imediato",
                "lotacao",
                "lotacao_display",
                "cargo",
                "contato_institucional",
            ]

        for field in lista_fields:
            fields[field] = SerializerMethodField()

        return fields

    def get_pk(self, obj):
        return obj.pk

    def get_unicode(self, obj):
        return f"{obj.matricula} - {self.get_nome(obj)} - {self.get_cargo(obj)}"

    def get_matricula(self, obj):
        return obj.matricula

    def get_tipo_posse(self, obj):
        return obj.get_type_by_possession_display()

    def get_data_posse(self, obj):
        if obj.posses.exists():
            return obj.posses.first().data_posse
        return None

    def get_nome(self, obj):
        return obj.pessoa_fisica.social_name

    def get_ativo(self, obj):
        return obj.ativo

    def get_cpf(self, obj):
        return obj.pessoa_fisica.cpf

    def get_sexo(self, obj):
        return obj.pessoa_fisica.get_sexo_display()

    def get_sangue(self, obj):
        return obj.pessoa_fisica.get_sangue_display()

    def get_estado_civil(self, obj):
        return obj.pessoa_fisica.get_estado_civil_display()

    def get_raca_cor(self, obj):
        return obj.pessoa_fisica.get_raca_cor_display()

    def get_email_pessoal(self, obj):
        return obj.pessoa_fisica.email_pessoal

    def get_email_institucional(self, obj):
        return obj.pessoa_fisica.email_institucional

    def get_chefe_imediato(self, obj):
        if obj.chefe_imediato:
            return obj.chefe_imediato.pessoa_fisica.social_name
        return None

    def get_lotacao(self, obj):
        lotacoes = obj.servidor_lotacao.filter(designacao=False)
        if lotacoes.exists():
            return lotacoes.first().lotacao.id
        return ""

    def get_lotacao_display(self, obj):
        lotacoes = obj.servidor_lotacao.filter(designacao=False)
        if lotacoes.exists():
            return lotacoes.first().lotacao.nome
        return ""

    def get_cargo(self, obj):
        mov_posse = MovimentacaoPosse.objects.filter(servidor=obj, ativo=True).last()
        if mov_posse and mov_posse.quadro.cargo:
            return f"{mov_posse.quadro.cargo}"

        return ""

    def get_contato_institucional(self, obj):
        return obj.pessoa_fisica.telefone_institucional


class TipoPosseSerializer(ModelSerializer):

    cod = SerializerMethodField()
    descricao = SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["cod", "descricao"]

    def get_cod(self, obj):
        return obj.cvalue

    def get_descricao(self, obj):
        return obj.label


class UsufrutoFeriasSerializer(ModelSerializer):

    matricula = SerializerMethodField()
    nome = SerializerMethodField()
    cargo = SerializerMethodField()
    data_inicio = SerializerMethodField()
    data_fim = SerializerMethodField()

    ORDER_BY_MAP = {
        "nome": "activity__acquisition_period__employee__pessoa_fisica__nome",
        "data_inicio": "start_date",
    }

    class Meta:
        model = Usufruct
        fields = ["matricula", "nome", "cargo", "data_inicio", "data_fim"]

    def get_matricula(self, obj):
        return obj.activity.acquisition_period.employee.matricula

    def get_nome(self, obj):
        return obj.activity.acquisition_period.employee.pessoa_fisica.nome

    def get_cargo(self, obj):
        servidor = obj.activity.acquisition_period.employee
        mov_posse = MovimentacaoPosse.objects.filter(servidor=servidor).last()
        if mov_posse and mov_posse.quadro.cargo:
            return f"{mov_posse.quadro.cargo}"
        return None

    def get_data_inicio(self, obj):
        return obj.start_date

    def get_data_fim(self, obj):
        return obj.end_date
