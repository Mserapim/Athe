from apiv2.baseserializers import BaseSerializer
from esocial.models import Configuration
from rest_framework import serializers
from rh.apiv2.serializers.servidor import ServidorListagemSerializer
from rh.models import PessoaFisica, UnidadeAdministrativa
from standard.models import Choice
from rest_framework import status
from contrib.utils import getLogger

log = getLogger(__name__)


class EventosChoiceSerializer(serializers.ModelSerializer):

    descricao = serializers.CharField(source="label")
    cod = serializers.IntegerField(source="value")

    class Meta:
        model = Choice
        fields = ["id", "cod", "descricao"]


class ConfiguracaoSerializer(BaseSerializer):

    ambiente = serializers.IntegerField(source="environment")
    ambiente_display = serializers.SerializerMethodField()
    layout_versao = serializers.CharField(source="layout_version")
    webservice_envio = serializers.CharField(source="ws_batch_submission")
    webservice_consulta = serializers.CharField(source="ws_batch_consult_process")
    inicio_vigencia = serializers.DateField(source="start_validity")
    fim_vigencia = serializers.DateField(
        source="end_validity", required=False, allow_null=True
    )
    data_corte_s2231 = serializers.DateField(source="cut_off_date_s2231")
    orgao_empregador_id = serializers.IntegerField(source="employer_id")
    orgao_empregador_display = serializers.SerializerMethodField()
    tabela_iniciais = serializers.DateField(source="initial_date_start_tables")
    nao_periodicos = serializers.DateField(source="initial_date_non_periodic_events")
    periodicos = serializers.DateField(source="initial_date_periodic_events")
    sst = serializers.DateField(source="initial_date_sst_events")
    envio_fila = serializers.BooleanField(source="queue_send")
    criado_em = serializers.DateTimeField(source="created_at", required=False)
    modificado_em = serializers.DateTimeField(source="modified_at", required=False)
    criado_por = serializers.SerializerMethodField(required=False)
    modificado_por = serializers.SerializerMethodField(required=False)
    responsavel_id = serializers.IntegerField(source="responsible_id")
    responsavel = serializers.CharField(
        source="responsible", required=False, allow_null=True
    )
    responsavel_sowfware_house_id = serializers.IntegerField(
        source="responsible_software_house_id"
    )
    responsavel_sowfware_house = serializers.CharField(
        source="responsible_software_house", required=False, allow_null=True
    )
    nome_schema_envio = serializers.CharField(source="xml_send_schema_name")
    nome_schema_consulta = serializers.CharField(source="xml_consult_schema_name")
    url_consulta = serializers.CharField(source="xmlns_consult")
    url_envio = serializers.CharField(source="xmlns_send")
    eventos_gerados_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    eventos_gerados_detalhes = EventosChoiceSerializer(
        source="generate_events", many=True, required=False, read_only=True
    )
    eventos_nao_enviados_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    eventos_nao_enviados_detalhes = EventosChoiceSerializer(
        source="interrupt_batch_events", many=True, required=False, read_only=True
    )
    servidores_gerados_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    servidores_gerados_detalhes = ServidorListagemSerializer(
        source="employee_filter", many=True, required=False, read_only=True
    )
    servidores_nao_gerados_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    servidores_nao_gerados_detalhes = ServidorListagemSerializer(
        source="employee_exclude", many=True, required=False, read_only=True
    )
    beneficiarios_gerados_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    baneficiarios_gerados_detalhes = ServidorListagemSerializer(
        source="employee_benefit", many=True, required=False, read_only=True
    )
    beneficiarios_nao_gerados_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    beneficiarios_nao_gerados_detalhes = ServidorListagemSerializer(
        source="employee_benefit_exclude", many=True, required=False, read_only=True
    )

    class Meta:
        model = Configuration
        fields = [
            "id",
            "ambiente",
            "ambiente_display",
            "layout_versao",
            "webservice_envio",
            "webservice_consulta",
            "inicio_vigencia",
            "fim_vigencia",
            "data_corte_s2231",
            "orgao_empregador_id",
            "orgao_empregador_display",
            "tabela_iniciais",
            "nao_periodicos",
            "periodicos",
            "sst",
            "envio_fila",
            "criado_em",
            "modificado_em",
            "criado_por",
            "modificado_por",
            "responsavel_id",
            "responsavel",
            "responsavel_sowfware_house_id",
            "responsavel_sowfware_house",
            "nome_schema_envio",
            "nome_schema_consulta",
            "url_consulta",
            "url_envio",
            "eventos_gerados_ids",
            "eventos_gerados_detalhes",
            "eventos_nao_enviados_ids",
            "eventos_nao_enviados_detalhes",
            "servidores_gerados_ids",
            "servidores_gerados_detalhes",
            "servidores_nao_gerados_ids",
            "servidores_nao_gerados_detalhes",
            "beneficiarios_gerados_ids",
            "baneficiarios_gerados_detalhes",
            "beneficiarios_nao_gerados_ids",
            "beneficiarios_nao_gerados_detalhes",
        ]

    def get_ambiente_display(self, obj):
        return obj.get_environment_display()

    def get_orgao_empregador_display(self, obj):
        return obj.employer.pessoa_juridica.nome

    def get_criado_por(self, obj):
        return obj.created_by.username

    def get_modificado_por(self, obj):
        return obj.modified_by.username

    def create(self, validated_data):
        orgao_empregador_id = validated_data.pop("employer_id")
        responsavel_id = validated_data.pop("responsible_id")
        responsavel_sowfware_house_id = validated_data.pop(
            "responsible_software_house_id"
        )

        eventos_gerados_ids = validated_data.pop("eventos_gerados_ids", [])
        eventos_nao_enviados_ids = validated_data.pop("eventos_nao_enviados_ids", [])
        servidores_gerados_ids = validated_data.pop("servidores_gerados_ids", [])
        servidores_nao_gerados_ids = validated_data.pop(
            "servidores_nao_gerados_ids", []
        )
        beneficiarios_gerados_ids = validated_data.pop("beneficiarios_gerados_ids", [])
        beneficiarios_nao_gerados_ids = validated_data.pop(
            "beneficiarios_nao_gerados_ids", []
        )

        orgao_empregador = None
        responsavel = None
        responsavel_sowfware_house = None

        if orgao_empregador_id is not None:
            orgao_empregador = UnidadeAdministrativa.objects.get(pk=orgao_empregador_id)

        if responsavel_id is not None:
            responsavel = PessoaFisica.objects.get(pk=responsavel_id)

        if responsavel_sowfware_house_id is not None:
            responsavel_sowfware_house = PessoaFisica.objects.get(
                pk=responsavel_sowfware_house_id
            )

        # Criar a configuração
        configuracao = Configuration.objects.create(
            employer=orgao_empregador,
            responsible=responsavel,
            responsible_software_house=responsavel_sowfware_house,
            **validated_data
        )

        # Associar Eventos
        configuracao.generate_events.set(eventos_gerados_ids)
        configuracao.interrupt_batch_events.set(eventos_nao_enviados_ids)

        # Associar Servidores
        configuracao.employee_filter.set(servidores_gerados_ids)
        configuracao.employee_exclude.set(servidores_nao_gerados_ids)

        # Associar beneficiarios
        configuracao.employee_benefit.set(beneficiarios_gerados_ids)
        configuracao.employee_benefit_exclude.set(beneficiarios_nao_gerados_ids)

        return configuracao

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "employer_id":
                orgao_empregador = UnidadeAdministrativa.objects.get(id=value)
                setattr(instance, "employer", orgao_empregador)
            elif attr == "responsible_id":
                responsavel = PessoaFisica.objects.get(id=value)
                setattr(instance, "responsible", responsavel)
            elif attr == "responsible_software_house_id":
                responsavel_sowfware_house = PessoaFisica.objects.get(id=value)
                setattr(
                    instance, "responsible_software_house", responsavel_sowfware_house
                )
            elif attr == "eventos_gerados_ids":
                instance.generate_events.set(value)
            elif attr == "eventos_nao_enviados_ids":
                instance.interrupt_batch_events.set(value)
            elif attr == "servidores_gerados_ids":
                instance.employee_filter.set(value)
            elif attr == "servidores_nao_gerados_ids":
                instance.employee_exclude.set(value)
            elif attr == "beneficiarios_gerados_ids":
                instance.employee_benefit.set(value)
            elif attr == "beneficiarios_nao_gerados_ids":
                instance.employee_benefit_exclude.set(value)
            else:
                # Atualizar os outros campos
                setattr(instance, attr, value)
        instance.save()
        return instance


class CertificaoEsocialSerializer(serializers.ModelSerializer):

    nome_certificado_a1 = serializers.SerializerMethodField()
    nome_certificado_cas = serializers.SerializerMethodField()

    class Meta:
        model = Configuration
        fields = [
            "certificado_a1_id",
            "certificado_cas_id",
            "nome_certificado_a1",
            "nome_certificado_cas",
        ]

    def get_nome_certificado_a1(self, obj):
        if obj.certificado_a1:
            return obj.certificado_a1.filename
        return None

    def get_nome_certificado_cas(self, obj):
        if obj.certificado_cas:
            return obj.certificado_cas.filename
        return None
