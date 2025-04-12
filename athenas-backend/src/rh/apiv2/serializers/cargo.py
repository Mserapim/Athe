from apiv2.baseserializers import BaseSerializer
from rest_framework.serializers import ModelSerializer
from rh.models import Cargo, ConfigJobPosition
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from rest_framework import status
from apiv2.const import MSG_SUCCESS_METHOD
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from contrib.utils import getLogger


log = getLogger(__name__)


class JobPositionSerializer(ModelSerializer):
    """
    Serializer do model Lotação
    """

    name = serializers.CharField(source="__str__")

    class Meta:
        model = Cargo
        fields = ["pk", "name"]


class ConfiguracaoCargoSerializer(BaseSerializer):

    class Meta:
        model = ConfigJobPosition
        fields = [
            "id",
            "ativo",
            "nome",
            "codigo",
            "designa_exercicio",
            "chefia",
            "substituivel",
            "remunerado",
            "acumulacao",
            "qtd_vagas",
            "cbo",
            "nivel_escolaridade",
            "carga_horaria",
            "tipo_carga_horaria",
            "inicio_vigencia",
            "fim_vigencia",
            "saude",
            "professor",
        ]

        extra_kwargs = {
            "nome": {"source": "name"},
            "codigo": {"source": "code"},
            "designa_exercicio": {"source": "designates_exercise"},
            "chefia": {"source": "boss"},
            "substituivel": {"source": "replaceable"},
            "remunerado": {"source": "remunerated"},
            "acumulacao": {"source": "cumulative"},
            "qtd_vagas": {"source": "quantity"},
            "nivel_escolaridade": {"source": "educational_level"},
            "carga_horaria": {"source": "workload"},
            "tipo_carga_horaria": {"source": "type_workload"},
            "inicio_vigencia": {"source": "start_validity"},
            "fim_vigencia": {"source": "end_validity"},
            "ativo": {"source": "active"},
            "saude": {"source": "health"},
            "professor": {"source": "teacher"},
        }
        campos_choices = ["nivel_escolaridade", "tipo_carga_horaria", "acumulacao"]
        campos_relacionados = {"cbo": {"campo_id": "id", "campo_display": "descricao"}}


class CargoSerializer(BaseSerializer):
    """
    Serializer para o modelo de cargos
    """

    descricao = serializers.SerializerMethodField()
    qtd_vagas = serializers.SerializerMethodField()
    nivel_escolaridade = serializers.SerializerMethodField()
    inicio_vigencia = serializers.SerializerMethodField()
    fim_vigencia = serializers.SerializerMethodField()
    configs = ConfiguracaoCargoSerializer(many=True)

    class Meta:
        model = Cargo
        fields = [
            "id",
            "descricao",
            "criado_em",
            "modificado_em",
            "nome",
            "indicativo",
            "tipo_lei_cargo",
            "codigo",
            "qtd_vagas",
            "nivel_escolaridade",
            "inicio_vigencia",
            "fim_vigencia",
            "ativo",
            "poder",
            "chefia",
            "substituivel",
            "cargo_arquimedes",
            "peso_ordenacao",
            "acumulacao",
            "code_tce",
            "criado_por",
            "modificado_por",
            "lotacao_responsavel",
            "unidade_administrativa",
            "publicacao",
            "publicacao_alteracao",
            "publicacao_extincao",
            "professor",
            "configs",
        ]
        extra_kwargs = {
            "criado_em": {"source": "created_at"},
            "modificado_em": {"source": "modified_at"},
            "criado_por": {"source": "created_by", "required": False},
            "modificado_por": {"source": "modified_by", "required": False},
            "peso_ordenacao": {"source": "order_weight"},
            "acumulacao": {"source": "cumulative"},
            "publicacao": {"source": "publication"},
            "publicacao_alteracao": {"source": "publication_change"},
            "publicacao_extincao": {"source": "publication_extinction"},
        }

        campos_choices = ["tipo_lei_cargo", "indicativo", "poder", "acumulacao"]
        campos_relacionados = {
            "criado_por": {"campo_id": "id", "campo_display": "username"},
            "modificado_por": {"campo_id": "id", "campo_display": "username"},
            "lotacao_responsavel": {"campo_id": "id", "campo_display": "nome"},
            "unidade_administrativa": {"campo_id": "id", "campo_display": "nome"},
            "publicacao": {"campo_id": "id", "campo_display": "cache_unicode"},
            "publicacao_alteracao": {
                "campo_id": "id",
                "campo_display": "cache_unicode",
            },
            "publicacao_extincao": {"campo_id": "id", "campo_display": "cache_unicode"},
        }

    @extend_schema_field(OpenApiTypes.STR)
    def get_descricao(self, obj):
        return obj.__str__()

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas(self, obj):
        config = obj.configs.last()
        if config:
            return config.quantity
        return None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_nivel_escolaridade(self, obj):
        config = obj.configs.last()
        if config:
            return {
                "valor": config.educational_level,
                "display": config.get_educational_level_display(),
            }
        return None

    @extend_schema_field(OpenApiTypes.DATE)
    def get_inicio_vigencia(self, obj):
        config = obj.configs.last()
        if config:
            return config.start_validity
        return None

    @extend_schema_field(OpenApiTypes.DATE)
    def get_fim_vigencia(self, obj):
        config = obj.configs.last()
        if config:
            return config.end_validity
        return None

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            with transaction.atomic():
                self.is_valid(raise_exception=True)
                configs = self.validated_data.pop("configs", [])
                instance = self.save()
                for config in configs:
                    config_create = instance.configs.first()
                    if config_create:
                        config_obj = ConfigJobPosition.objects.get(pk=config_create.pk)
                        for campo, valor in config.items():
                            setattr(config_obj, campo, valor)
                        config_obj.save(update_fields=config.keys())
                    else:
                        ConfigJobPosition.objects.create(
                            job_position=instance, **config
                        )
                rst.update(
                    {
                        "success": True,
                        "message": MSG_SUCCESS_METHOD["post"],
                        "data": self.data,
                    }
                )
        except ValidationError as e:
            log.error(f"Erro de validação: {str(e)}")
            rst.update(
                {
                    "message": f"Erro de validação: {str(e)}",
                    "code": status.HTTP_400_BAD_REQUEST,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst

    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_200_OK,
        }
        try:
            with transaction.atomic():
                self.is_valid(raise_exception=True)
                configs = self.validated_data.pop("configs", [])
                self.save()
                for i, config in enumerate(configs):
                    config_id = self.initial_data.get("configs", [])[i].get("id")
                    if config_id:
                        config_obj = ConfigJobPosition.objects.get(pk=config_id)
                        for campo, valor in config.items():
                            setattr(config_obj, campo, valor)
                        config_obj.save(update_fields=config.keys())
                    else:
                        ConfigJobPosition.objects.create(
                            job_position=instance, **config
                        )
                rst.update(
                    {
                        "success": True,
                        "message": MSG_SUCCESS_METHOD["put"],
                        "data": self.data,
                    }
                )
        except ObjectDoesNotExist as e:
            log.error(f"Erro ao encontrar o objeto: {str(e)}")
            rst.update(
                {
                    "message": f"Objeto não encontrado: {str(e)}",
                    "code": status.HTTP_404_NOT_FOUND,
                }
            )
        except ValidationError as e:
            log.error(f"Erro de validação: {str(e)}")
            rst.update(
                {
                    "message": f"Erro de validação: {str(e)}",
                    "code": status.HTTP_400_BAD_REQUEST,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


class AreaTrabalhoCargoSerializer(BaseSerializer):
    """
    Serializer para área de trabalho de cargo
    """

    descricao_cargo = serializers.SerializerMethodField()
    qtd_vagas_total = serializers.SerializerMethodField()
    qtd_vagas_ocupadas = serializers.SerializerMethodField()
    qtd_vagas_servidor = serializers.SerializerMethodField()
    qtd_vagas_membro = serializers.SerializerMethodField()
    qtd_vagas_comissionado = serializers.SerializerMethodField()
    qtd_vagas_efetivo_funcao = serializers.SerializerMethodField()
    qtd_vagas_efetivo_comissao = serializers.SerializerMethodField()
    qtd_vagas_sem_vinculo = serializers.SerializerMethodField()
    qtd_vagas_disponivel = serializers.SerializerMethodField()
    qtd_nomeacao_deferido = serializers.SerializerMethodField()
    qtd_exoneracao_deferido = serializers.SerializerMethodField()
    qtd_pedido_nomeacao = serializers.SerializerMethodField()
    qtd_pedido_exoneracao = serializers.SerializerMethodField()
    saldo_disponivel = serializers.SerializerMethodField()
    saldo_disponivel_estimado = serializers.SerializerMethodField()

    class Meta:
        model = Cargo
        fields = [
            "id",
            "descricao_cargo",
            "qtd_vagas_total",
            "qtd_vagas_ocupadas",
            "qtd_vagas_disponivel",
            "qtd_vagas_servidor",
            "qtd_vagas_membro",
            "qtd_vagas_comissionado",
            "qtd_vagas_efetivo_funcao",
            "qtd_vagas_efetivo_comissao",
            "qtd_vagas_sem_vinculo",
            "qtd_nomeacao_deferido",
            "qtd_exoneracao_deferido",
            "qtd_pedido_nomeacao",
            "qtd_pedido_exoneracao",
            "saldo_disponivel",
            "saldo_disponivel_estimado",
        ]

    def get_stat(self, cargo_id, field):
        """Busca o valor da contagem pré-calculada no contexto."""
        cargo_stats = self.context.get("cargo_stats", {})  # Obtém os dados do contexto
        return cargo_stats.get(cargo_id, {}).get(field, 0)

    @extend_schema_field(OpenApiTypes.STR)
    def get_descricao_cargo(self, obj):
        return obj.__str__()

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_total(self, obj):
        config = obj.configs.last()
        if config:
            return config.quantity
        return 0

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_ocupadas(self, obj):
        return self.get_stat(obj.id, "qtd_vagas_ocupadas")

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_disponivel(self, obj):
        return self.get_qtd_vagas_total(obj) - self.get_qtd_vagas_ocupadas(obj)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_servidor(self, obj):
        return self.get_stat(obj.id, "qtd_vagas_servidor")

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_membro(self, obj):
        return self.get_stat(obj.id, "qtd_vagas_membro")

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_comissionado(self, obj):
        return self.get_stat(obj.id, "qtd_vagas_comissionado")

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_efetivo_funcao(self, obj):
        return self.get_stat(obj.id, "qtd_vagas_efetivo_funcao")

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_efetivo_comissao(self, obj):
        return self.get_stat(obj.id, "qtd_vagas_efetivo_comissao")

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_vagas_sem_vinculo(self, obj):
        return self.get_stat(obj.id, "qtd_vagas_sem_vinculo")

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_nomeacao_deferido(self, obj):
        return 0

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_exoneracao_deferido(self, obj):
        return 0

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_pedido_nomeacao(self, obj):
        return 0

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_qtd_pedido_exoneracao(self, obj):
        return 0

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_saldo_disponivel(self, obj):
        return (
            self.get_qtd_vagas_disponivel(obj)
            + self.get_qtd_exoneracao_deferido(obj)
            - self.get_qtd_nomeacao_deferido(obj)
        )

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_saldo_disponivel_estimado(self, obj):
        return (
            self.get_saldo_disponivel(obj)
            + self.get_qtd_pedido_exoneracao(obj)
            - self.get_qtd_pedido_nomeacao(obj)
        )
