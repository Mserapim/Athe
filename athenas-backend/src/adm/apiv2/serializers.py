from rest_framework import serializers

from apiv2.baseserializers import BaseSerializer

from rh.models import Servidor


class UsuarioAdmSerializer(BaseSerializer):
    """
    Serializer do model Sevidor como Usuario
    """

    username = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    cpf = serializers.SerializerMethodField()
    email_pessoal = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = ["username", "nome", "cpf", "matricula", "email_pessoal"]

    def get_username(self, instance):
        return instance.user.username if instance.user else ""

    def get_nome(self, instance):
        return instance.pessoa_fisica.social_name

    def get_cpf(self, instance):
        return instance.pessoa_fisica.cpf

    def get_email_pessoal(self, instance):
        return (
            instance.pessoa_fisica.email_pessoal
            if instance.pessoa_fisica.email_pessoal
            else ""
        )
