from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers

from diarias.models import GrupoAprovador
from rh.models import Servidor
from standard.models import Choice


class GrupoAprovadorSerializer(BaseSerializer):
    """
    Serializer do model GrupoAprovador
    """

    quantidade_grupos = serializers.SerializerMethodField()
    quantidade_servidores = serializers.SerializerMethodField()
    criado_por_username = serializers.SerializerMethodField()
    modificado_por_username = serializers.SerializerMethodField()

    class Meta:
        model = GrupoAprovador
        fields = "__all__"

    def get_quantidade_grupos(self, obj):
        return len(obj.grupos) if obj.grupos else 0

    def get_quantidade_servidores(self, obj):
        return obj.servidores.count()

    def get_criado_por_username(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_modificado_por_username(self, obj):
        return obj.modified_by.username if obj.modified_by else None

    def update(self, instance, validated_data):
        servidores_data = validated_data.pop("servidores", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if servidores_data is not None:
            instance.servidores.set(servidores_data)

        return instance


class UsuarioDiariasSerializer(BaseSerializer):
    """
    Serializer do model Servidor como Usuario
    """

    ORDER_BY_MAP = {
        "nome": "pessoa_fisica__social_name",
        "username": "user__username",
        "unicode": "matricula",
    }

    nome = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    unicode = serializers.SerializerMethodField()
    grupos_aprovadores_viagens = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = [
            "id",
            "matricula",
            "nome",
            "username",
            "status",
            "unicode",
            "grupos_aprovadores_viagens",
        ]

    def get_nome(self, instance):
        return instance.pessoa_fisica.social_name

    def get_username(self, instance):
        return instance.user.username if instance.user else ""

    def get_status(self, instance):
        return instance.ativo

    def get_unicode(self, instance):
        return f"{instance.matricula} - {instance.pessoa_fisica.social_name} - {instance.get_type_by_possession_display()}"

    def get_grupos_aprovadores_viagens(self, instance):
        return [grupo.nome for grupo in instance.grupos_aprovadores_viagens.all()]


class PerfilAprovadorDiariasSerializer(BaseSerializer):
    """
    Serializer do model Servidor como Perfil Aprovador
    """

    ORDER_BY_MAP = {
        "nome": "pessoa_fisica__social_name",
        "unicode": "matricula",
    }

    nome = serializers.SerializerMethodField()
    unicode = serializers.SerializerMethodField()
    grupos = serializers.SerializerMethodField()
    etapas_aprovador = serializers.SerializerMethodField()
    etapas_aprovador_obj = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = [
            "id",
            "matricula",
            "nome",
            "unicode",
            "grupos",
            "etapas_aprovador",
            "etapas_aprovador_obj",
        ]

    def get_nome(self, instance):
        return instance.pessoa_fisica.social_name

    def get_unicode(self, instance):
        return f"{instance.matricula} - {instance.pessoa_fisica.social_name}"

    def get_grupos(self, instance):
        return [grupo.nome for grupo in instance.grupos_aprovadores_viagens.all()]

    def get_etapas_aprovador(self, instance):

        grupos = instance.grupos_aprovadores_viagens.all()
        lista_etapas = set()

        for grupo in grupos:
            lista_etapas.update(grupo.grupos)

        return lista_etapas

    def get_etapas_aprovador_obj(self, instance):

        grupos = instance.grupos_aprovadores_viagens.all()
        lista_etapas = set()

        for grupo in grupos:
            lista_etapas.update(grupo.grupos)

        lista_obj = (
            Choice.objects.filter(
                value__in=lista_etapas,
                app_label="diarias",
                name="ETAPA_SOLICITACAO_VIAGEM",
            )
            .order_by("label")
            .values("value", "label")
        )

        return lista_obj
