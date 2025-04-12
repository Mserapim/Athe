from django.db import migrations
from contrib.middleware import set_current_user
from django.contrib.auth.models import User


from contrib.utils import getLogger
from menu_permissoes.models import UsuarioGrupo, Menu, MenuConfig
from rh.models import Servidor

log = getLogger(__name__)


def criar_grupo_padrao_vdf(apps, schema_editor):
    """
    Cria um grupo de acesso padrão para o vdf;
    Adiciona todos os menus  que estão cadastrados no vdf ao grupo;
    Adiciona todos os usuarios ao grupo
    """

    set_current_user(User.objects.get(username="athenas"))

    grupo_acesso, _ = UsuarioGrupo.objects.get_or_create(
        nome="perfil-vdf-padrao", grupo_padrao=True
    )

    menus = Menu.objects.filter(grupo__id=1)

    for menu in menus:
        menu_config, _ = MenuConfig.objects.get_or_create(
            usuario_grupo=grupo_acesso, menu=menu, acoes=["ler", "criar"]
        )

    servidores = Servidor.objects.all()
    grupo_acesso.servidores.add(*servidores)


class Migration(migrations.Migration):

    dependencies = [
        ("menu_permissoes", "0012_menu_servidores_favoritos"),
    ]

    operations = [
        migrations.RunPython(criar_grupo_padrao_vdf),
    ]
