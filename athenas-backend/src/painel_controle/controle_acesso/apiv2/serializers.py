from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework import status, serializers

from menu_permissoes.models import Modulo, MenuGrupo, Menu, MenuConfig, UsuarioGrupo
from rh.models import Servidor, ServidorLotacao, MovimentacaoPosse
from contrib.utils import getLogger

from apiv2.baseserializers import BaseSerializer

log = getLogger(__name__)


class ModuloSerializer(BaseSerializer):
    """
    Serializer do model Modulo
    """

    class Meta:
        model = Modulo
        fields = "__all__"


class GruposMenuSerializer(BaseSerializer):
    """
    Serializer do model MenuGrupo
    """

    class Meta:
        model = MenuGrupo
        fields = "__all__"


class MenuSerializer(BaseSerializer):
    """
    Serializer do model Menu
    """

    link_de_ajuda = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=True, required=False
    )

    class Meta:
        model = Menu
        fields = "__all__"
        extra_kwargs = {"servidores_favoritos": {"required": False}}

    def validate_link_de_ajuda(self, data):
        if not data:
            return data
        validador = URLValidator()
        try:
            validador(data)
        except ValidationError:
            raise Exception(
                "Link de Ajuda inválido, informe uma Link de Ajuda que seja válida."
            )
        return data


class MenuConfigSerializer(BaseSerializer):
    """
    Serializer do model MenuConfig
    """

    ORDER_BY_MAP = {
        "nome_menu": "menu__nome",
        "usuario_grupo_nome": "usuario_grupo__nome",
    }

    nome_menu = serializers.SerializerMethodField()
    usuario_grupo_nome = serializers.SerializerMethodField()
    modulo_id = serializers.SerializerMethodField()
    modulo_nome = serializers.SerializerMethodField()

    class Meta:
        model = MenuConfig
        fields = "__all__"

    def get_nome_menu(self, obj):
        return obj.menu.nome

    def get_usuario_grupo_nome(self, obj):
        return obj.usuario_grupo.nome

    def get_modulo_id(self, obj):
        return obj.menu.grupo.modulo.id

    def get_modulo_nome(self, obj):
        return obj.menu.grupo.modulo.nome


class UsuarioGrupoSerializer(BaseSerializer):
    """
    Serializer do model UsuarioGrupo
    """

    usuarios_qtd = serializers.SerializerMethodField()
    menus_qtd = serializers.SerializerMethodField()

    class Meta:
        model = UsuarioGrupo
        fields = "__all__"
        extra_kwargs = {"servidores": {"required": False}}

    def get_usuarios_qtd(self, instance):
        return instance.servidores.all().count()

    def get_menus_qtd(self, instance):
        return MenuConfig.objects.filter(usuario_grupo=instance).count()


class UsuarioSerializer(BaseSerializer):
    """
    Serializer do model Sevidor como Usuario
    """

    ORDER_BY_MAP = {
        "nome": "pessoa_fisica__social_name",
        "username": "user__username",
        "unicode": "matricula",
        "categoria_funcional": "type_by_possession",
    }

    nome = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    unicode = serializers.SerializerMethodField()
    qtd_grupos = serializers.SerializerMethodField()
    grupos = serializers.SerializerMethodField()
    qtd_menus = serializers.SerializerMethodField()
    lotacao = serializers.SerializerMethodField()
    categoria_funcional = serializers.SerializerMethodField()
    cargo = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = [
            "id",
            "matricula",
            "nome",
            "username",
            "status",
            "unicode",
            "qtd_grupos",
            "grupos",
            "qtd_menus",
            "lotacao",
            "categoria_funcional",
            "cargo",
        ]

    def get_nome(self, instance):
        return instance.pessoa_fisica.social_name

    def get_username(self, instance):
        return instance.user.username if instance.user else ""

    def get_status(self, instance):
        return instance.ativo

    def get_unicode(self, instance):
        return f"{instance.matricula} - {instance.pessoa_fisica.social_name} - {instance.get_type_by_possession_display()}"

    def get_qtd_grupos(self, instance):
        return instance.grupos_permissao.count()

    def get_grupos(self, instance):
        return [grupo.nome for grupo in instance.grupos_permissao.all()]

    def get_qtd_menus(self, instance):

        grupos = instance.grupos_permissao.all()

        configs = MenuConfig.objects.filter(usuario_grupo__in=grupos).distinct()

        menus = Menu.objects.filter(configs__in=configs).distinct()

        return menus.count()

    def get_lotacao(self, obj):

        lotacoes = ServidorLotacao.objects.filter(
            servidor=obj, designacao=False, ativo=True
        )
        if lotacoes.exists():
            return lotacoes.last().lotacao.nome
        return ""

    def get_categoria_funcional(self, instance):
        return instance.get_type_by_possession_display()

    def get_cargo(self, instance):
        mov_posse = MovimentacaoPosse.objects.filter(
            servidor=instance, ativo=True
        ).last()
        if mov_posse and mov_posse.quadro.cargo:
            return f"{mov_posse.quadro.cargo}"
        return ""


class UsuarioMinimoSerializer(BaseSerializer):
    nome = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = ["id", "nome"]

    def get_nome(self, instance):
        return instance.pessoa_fisica.social_name


class UsuarioGrupoPorUsuarioSerializer(BaseSerializer):
    """
    Serializer para a lista de UsuarioGrupo de um Usuario
    """

    class Meta:
        model = UsuarioGrupo
        fields = ["id", "nome", "descricao", "situacao", "grupo_padrao"]
