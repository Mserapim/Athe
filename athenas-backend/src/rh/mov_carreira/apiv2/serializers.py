from rest_framework import serializers
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import Servidor


class MembrosEstagioProbatorioSerializer(serializers.ModelSerializer):
    cargo = serializers.SerializerMethodField()
    data_primeira_posse = serializers.SerializerMethodField()
    data_exercicio = serializers.SerializerMethodField()
    dias_trabalhados = serializers.IntegerField(
        source="get_worked_days_if_employee_be_in_probationary_phase", read_only=True
    )
    dias_afastados = serializers.IntegerField(
        source="get_days_departure", read_only=True
    )
    data_fim_estagio = serializers.SerializerMethodField()
    dias_para_fim_estagio = serializers.IntegerField(
        source="days_for_complete_the_probationary_phase", read_only=True
    )
    lotacao = serializers.CharField(source="workplace_current", read_only=True)

    class Meta:
        model = Servidor
        fields = [
            "id",
            "name",
            "matricula",
            "cargo",
            "data_primeira_posse",
            "data_exercicio",
            "dias_trabalhados",
            "dias_afastados",
            "data_fim_estagio",
            "dias_para_fim_estagio",
            "lotacao",
        ]

    def get_cargo(self, obj):
        job_position = obj.job_position()
        return job_position.cargo.nome if job_position and job_position.cargo else None

    def get_data_primeira_posse(self, obj):
        return (
            obj.first_possession_date.strftime("%d/%m/%Y")
            if obj.first_possession_date
            else None
        )

    def get_data_exercicio(self, obj):
        return obj.data_exercicio.strftime("%d/%m/%Y") if obj.data_exercicio else None

    def get_data_fim_estagio(self, obj):
        return (
            obj.date_when_complete_the_probationary_phase().strftime("%d/%m/%Y")
            if obj.date_when_complete_the_probationary_phase()
            else None
        )


class MembroProbatorioAfastamentoSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="get_tipo_display")
    qtd_dias = serializers.IntegerField(source="days_amount")
    servidor_unicode = serializers.SerializerMethodField()
    afastamento_unicode = serializers.CharField(source="__str__")

    class Meta:
        model = BaseLicencaAfastamento
        fields = [
            "id",
            "tipo",
            "data_inicio",
            "data_fim",
            "qtd_dias",
            "servidor_unicode",
            "situation_unicode",
            "afastamento_unicode",
        ]

    def get_servidor_unicode(self, obj):
        return f"{obj.servidor.matricula} - {obj.servidor.pessoa_fisica.social_name}"
