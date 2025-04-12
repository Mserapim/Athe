from datetime import datetime

from contrib.utils import getLogger
from rh.models import (
    PessoaFisica,
    Localidade,
    Servidor,
    SocialSecurityEmployee,
    SocialSecurityConfig,
)
from apiv2.baseserializers import BaseSerializer
from rh.models import (
    PessoaFisica,
    Localidade,
    Servidor,
    SocialSecurityEmployee,
    SocialSecurityConfig,
)
from apiv2.baseserializers import BaseSerializer
from rest_framework import status
from apiv2.const import MSG_SUCCESS_METHOD

from rh.defin.models import PFProviderEntry

from django.db import transaction
from decimal import Decimal
from rh.gfp.models import Folha
from rest_framework.serializers import SerializerMethodField


from rh.defin.pagamentos_utils import calculate_inss, calculate_irrf
from rh.apiv2.serializers.endereco import EnderecoSerializer
from rh.apiv2.serializers.telefone import TelefoneSerializer
from diarias.models import CargoDiarias

from rh.gfp.models import IRRF

log = getLogger(__name__)


class PagamentoColaboradorSerializer(BaseSerializer):

    lotacao_display = SerializerMethodField()
    cbo_display = SerializerMethodField()
    folha_display = SerializerMethodField()
    contra_cheque_display = SerializerMethodField()
    natureza_atividade_display = SerializerMethodField()

    class Meta:
        model = PFProviderEntry
        fields = [
            "id",
            "pessoa",
            "folha",
            "folha_display",
            "contra_cheque",
            "contra_cheque_display",
            "cbo",
            "cbo_display",
            "lotacao",
            "lotacao_display",
            "data_pagamento",
            "valor_bruto",
            "valor_inss",
            "isento_inss",
            "natureza_atividade",
            "natureza_atividade_display",
            "contribuicao_parcial",
            "contribuido",
            "valor_ir",
            "valor_liquido",
            "aplicado_folha",
        ]

        extra_kwargs = {
            "id": {"source": "pk"},
            "pessoa": {"source": "natural_person"},
            "folha": {"source": "payroll"},
            "lotacao": {"source": "workplace"},
            "contra_cheque": {"source": "paycheck"},
            "data_pagamento": {"source": "pay_day"},
            "valor_bruto": {"source": "gross_value"},
            "valor_inss": {"source": "inss_value"},
            "isento_inss": {"source": "inss_exempt"},
            "natureza_atividade": {"source": "nature_activity"},
            "contribuicao_parcial": {"source": "partial_contribution"},
            "contribuido": {"source": "contributed"},
            "valor_ir": {"source": "ir_value", "read_only": True},
            "valor_liquido": {"source": "liquid_value", "read_only": True},
            "aplicado_folha": {"source": "applied_payroll", "read_only": True},
        }

    def get_lotacao_display(self, obj):
        if obj.workplace:
            return obj.workplace.nome
        return ""

    def get_cbo_display(self, obj):
        if obj.cbo:
            return obj.cbo.__str__()
        return ""

    def get_folha_display(self, obj):
        if obj.payroll:
            return obj.payroll.__str__()
        return ""

    def get_contra_cheque_display(self, obj):
        if obj.paycheck:
            return obj.paycheck.__str__()
        return ""

    def get_natureza_atividade_display(self, obj):
        if obj.nature_activity:
            return obj.get_nature_activity_display()
        return ""

    @transaction.atomic
    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            deducao_benefica = (
                IRRF.objects.order_by("-data_vigencia").first().deducao_benefica
            )

            self.is_valid(raise_exception=True)
            self.save()

            inst = self.instance

            if not inst.gross_value:
                raise Exception("Favor preencher o Valor Bruto")

            employee = inst.natural_person.servidor_set.filter(
                type_by_possession="COE"
            ).first()
            periodo_filtro = datetime.now().date()
            payroll = Folha.objects.get(
                periodo__mes=periodo_filtro.month,
                periodo__ano=periodo_filtro.year,
                tipo_folha__titulo="NORMAL",
            )

            gross_value = float(inst.gross_value)
            valor_base = 0

            inss_value = calculate_inss(inst, employee, payroll, gross_value)

            if inst.inss_exempt:
                valor_base = gross_value - float(deducao_benefica)
                liquid_value = gross_value
            else:
                liquid_value = gross_value - inss_value
                valor_base = liquid_value

            irrf_value = calculate_irrf(inst, employee, payroll, valor_base)

            liquid_value -= irrf_value

            inst.inss_value = round(Decimal(inss_value), 2)
            inst.ir_value = round(Decimal(irrf_value), 2)
            inst.liquid_value = round(Decimal(liquid_value), 2)

            inst.full_clean()

            inst.save()

            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["post"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst

    @transaction.atomic
    def perform_update(self, inst):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_200_OK,
        }
        try:
            deducao_benefica = (
                IRRF.objects.order_by("-data_vigencia").first().deducao_benefica
            )
            self.is_valid(raise_exception=True)
            self.save()

            if not inst.gross_value:
                raise Exception("Favor preencher o Valor Bruto")

            employee = inst.natural_person.servidor_set.filter(
                type_by_possession="COE"
            ).first()
            periodo_filtro = datetime.now().date()
            payroll = Folha.objects.get(
                periodo__mes=periodo_filtro.month,
                periodo__ano=periodo_filtro.year,
                tipo_folha__titulo="NORMAL",
            )

            gross_value = float(inst.gross_value)
            valor_base = 0

            inss_value = calculate_inss(inst, employee, payroll, gross_value)

            if inst.inss_exempt:
                valor_base = gross_value - float(deducao_benefica)
                liquid_value = gross_value
            else:
                liquid_value = gross_value - inss_value
                valor_base = liquid_value

            irrf_value = calculate_irrf(inst, employee, payroll, valor_base)

            liquid_value -= irrf_value

            inst.inss_value = round(Decimal(inss_value), 2)
            inst.ir_value = round(Decimal(irrf_value), 2)
            inst.liquid_value = round(Decimal(liquid_value), 2)

            inst.full_clean()

            inst.save()

            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["put"],
                    "data": self.data,
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


class ColaboradorPfSerializer(BaseSerializer):
    """
    Serializer para o modelo de Colaborador de Serviços Eveitoais PF
    """

    sexo_display = SerializerMethodField()
    raca_cor_display = SerializerMethodField()
    modified_by_display = SerializerMethodField()
    created_by_display = SerializerMethodField()
    status = SerializerMethodField()
    pais_nacionalidade_display = SerializerMethodField()
    pais_naturalidade_display = SerializerMethodField()

    categoria_esocial = SerializerMethodField()
    categoria_esocial_display = SerializerMethodField()

    cargo_eventual = SerializerMethodField()
    cargo_eventual_display = SerializerMethodField()

    pagamentos = PagamentoColaboradorSerializer(
        source="pf_providers", many=True, read_only=True
    )
    enderecos = EnderecoSerializer(source="address", many=True, read_only=True)
    telefones = TelefoneSerializer(source="phone", many=True, read_only=True)

    class Meta:
        model = PessoaFisica
        fields = [
            "id",
            "nome_social",
            "data_nascimento",
            "sexo",
            "sexo_display",
            "raca_cor",
            "raca_cor_display",
            "cpf",
            "email",
            "status",
            "pais_nacionalidade",
            "pais_nacionalidade_display",
            "pais_naturalidade",
            "pais_naturalidade_display",
            "pagamentos",
            "enderecos",
            "telefones",
            "categoria_esocial",
            "categoria_esocial_display",
            "cargo_eventual",
            "cargo_eventual_display",
            "modified_at",
            "modified_by",
            "modified_by_display",
            "created_at",
            "created_by",
            "created_by_display",
        ]

        extra_kwargs = {
            "id": {"source": "pk"},
            "nome_social": {"source": "social_name"},
            "email": {"source": "email_pessoal"},
            "pais_nacionalidade": {"source": "nationality"},
            "pais_naturalidade": {"source": "nationality_birth"},
        }

    def get_sexo_display(self, obj):
        if obj.sexo:
            return obj.get_sexo_display()
        return ""

    def get_raca_cor_display(self, obj):
        if obj.raca_cor:
            return obj.get_raca_cor_display()
        return ""

    def get_modified_by_display(self, obj):
        try:
            return obj.modified_by.servidor.pessoa_fisica.social_name
        except:
            return ""

    def get_created_by_display(self, obj):
        try:
            return obj.created_by.servidor.pessoa_fisica.social_name
        except:
            return ""

    def get_status(self, obj):
        return obj.servidor_set.first().ativo

    def get_pais_nacionalidade_display(self, obj):
        if obj.nationality:
            return obj.nationality.nome
        return ""

    def get_pais_naturalidade_display(self, obj):
        if obj.nationality_birth:
            return obj.nationality_birth.nome
        return ""

    def get_categoria_esocial(self, obj):
        servidor = obj.servidor_set.first()
        if servidor and servidor.category_esocial:
            return servidor.category_esocial
        return ""

    def get_categoria_esocial_display(self, obj):
        servidor = obj.servidor_set.first()
        if servidor and servidor.category_esocial:
            return servidor.get_category_esocial_display()
        return ""

    def get_cargo_eventual(self, obj):
        servidor = obj.servidor_set.first()
        if servidor and servidor.cargo_eventual:
            return servidor.cargo_eventual.id
        return None

    def get_cargo_eventual_display(self, obj):
        servidor = obj.servidor_set.first()
        if servidor and servidor.cargo_eventual:
            return servidor.cargo_eventual.nome
        return ""

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            self.is_valid(raise_exception=True)
            self.save()

            inst = self.instance

            inst.nome = inst.social_name
            inst.grau_instrucao = 18
            inst.municipio_naturalidade = Localidade.objects.get(
                pk=12360
            )  # NÃO INFORMADO/NA
            inst.full_clean()
            PessoaFisica.validate_coe_employee(inst)

            inst.save()

            servidor = Servidor()
            servidor.pessoa_fisica = inst
            servidor.type_by_possession = "COE"
            servidor.type_by_possession = "COE"
            servidor.ativo = True
            servidor.save()

            previdencia = SocialSecurityEmployee()
            previdencia.employee = servidor
            previdencia.mass_segregation_plan = 2
            # "RGPS, Plano previdenciário ou único - INSTITUTO NACIONAL DE SEGURIDADE SOCIAL
            rgps = SocialSecurityConfig.objects.get(pk=1)
            previdencia.social_security_config = rgps
            previdencia.start_validity = datetime.today()
            previdencia.save()

            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["post"],
                    "data": self.data,
                }
            )
            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["post"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst

    @transaction.atomic
    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_200_OK,
        }
        try:

            self.is_valid(raise_exception=True)
            self.save()

            request = self.context.get("request")

            servidor = instance.servidor_set.first()
            cargo_eventual_id = request.data.get("cargo_eventual")

            cargo_eventual = None
            if cargo_eventual_id:
                cargo_eventual = CargoDiarias.objects.get(pk=cargo_eventual_id)

            servidor.cargo_eventual = cargo_eventual

            servidor.category_esocial = request.data.get("categoria_esocial")
            servidor.save()

            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["put"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst
