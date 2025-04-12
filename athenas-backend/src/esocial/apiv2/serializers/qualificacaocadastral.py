from esocial.models import RegistrationQualification
from rest_framework import serializers
from contrib.utils import getLogger


log = getLogger(__name__)


class QualificacaoCadastralSerializer(serializers.ModelSerializer):

    data_nascimento = serializers.CharField(source="dn")
    servidor = serializers.SerializerMethodField()
    ultima_qualificacao = serializers.CharField(source="last_qualification_at")
    ultima_qualificacao_por = serializers.CharField(source="last_qualification_by")
    ultima_mofificacao = serializers.CharField(source="last_modified_person_at")
    ultima_mofificacao_por = serializers.CharField(source="last_modified_person_by")
    tipo_pessoa = serializers.IntegerField(source="type_of_person")
    tipo_pessoa_display = serializers.SerializerMethodField()
    qualificado = serializers.BooleanField(source="qualified")
    status_display = serializers.SerializerMethodField()
    tipo_ultima_qualificacao = serializers.IntegerField(
        source="type_of_last_qualification"
    )
    tipo_ultima_qualificacao_display = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationQualification
        fields = [
            "id",
            "nome",
            "cpf",
            "nis",
            "data_nascimento",
            "servidor",
            "cod_cpf_inv",
            "cod_nis_inv",
            "cod_nome_inv",
            "cod_dn_inv",
            "cod_cnis_nis",
            "cod_cnis_dn",
            "cod_cnis_obito",
            "cod_cnis_cpf",
            "cod_cnis_cpf_nao_inf",
            "cod_cpf_nao_consta",
            "cod_cpf_nulo",
            "cod_cpf_cancelado",
            "cod_cpf_suspenso",
            "cod_cpf_dn",
            "cod_cpf_nome",
            "cod_orientacao_cpf",
            "cod_orientacao_nis",
            "ultima_qualificacao",
            "ultima_qualificacao_por",
            "ultima_mofificacao",
            "ultima_mofificacao_por",
            "tipo_pessoa",
            "tipo_pessoa_display",
            "qualificado",
            "status",
            "status_display",
            "tipo_ultima_qualificacao",
            "tipo_ultima_qualificacao_display",
            "info",
        ]

    def get_servidor(self, obj):
        return str(obj.employee) if obj.employee else None

    def get_tipo_pessoa_display(self, obj):
        return obj.get_type_of_person_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_tipo_ultima_qualificacao_display(self, obj):
        return obj.get_type_of_last_qualification_display()


class ConfigFiltrosEsocialSerializer(serializers.Serializer):
    """
    classe serializer da config de filtros esocial
    """

    texto = serializers.CharField()
    valor = serializers.IntegerField()
