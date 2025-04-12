from django.db import models
from django.contrib.postgres.fields import ArrayField
from colorfield.fields import ColorField

from standard.models import AuditTimestampModel
from rh.gfp.models import Servidor

from painel_controle.controle_acesso.utils import atualizar_favoritos

from contrib.utils import getLogger

log = getLogger(__name__)


class ModuloMenu(AuditTimestampModel):
    """
    Modelo abstrato para ser utilizado pelos modelos de Módulo e Menus.
    """

    SITUACAO = (
        ("ATIVO", "Ativo"),
        ("INATIVO", "Inativo"),
        ("PAUSADO", "Pausado"),
    )

    nome = models.CharField("Nome", max_length=150)
    descricao = models.TextField("Descrição", null=True, blank=True)
    situacao = models.CharField(
        "Ativo", max_length=20, choices=SITUACAO, default="ATIVO", db_index=True
    )
    ordem = models.SmallIntegerField("Ordem", null=True, blank=True, db_index=True)
    icone = models.CharField(
        max_length=255, verbose_name="Ícone", null=True, blank=True
    )
    cor = ColorField(default="#64748B")

    class Meta:
        abstract = True
        ordering = ("ordem", "nome")

    def __str__(self):
        return self.nome

    def validar_situacao(self):
        situacoes_lista = [x[0] for x in Modulo.SITUACAO]
        if self.situacao not in situacoes_lista:
            raise Exception(
                f"Valor do campo situação é inválida. Os valores aceitos são: {situacoes_lista}."
            )

    def validate(self):
        self.validar_situacao()

    def save(self, *args, **kwargs):
        self.validate()
        super(ModuloMenu, self).save(*args, **kwargs)


class Modulo(ModuloMenu):
    """
    Modelo para armazenar informações de Módulos
    """

    sigla = models.CharField("Sigla", max_length=50, null=True, db_index=True)

    def __str__(self):
        return f"Módulo: {self.nome}"

    def save(self, *args, **kargs):
        self.validate()
        super(Modulo, self).save(*args, **kargs)
        atualizar_favoritos()

    def delete(self, *args, **kargs):
        super(Modulo, self).delete(*args, **kargs)
        atualizar_favoritos()

    def validar_nome_duplicado(self):
        q = Modulo.objects.filter(nome=self.nome)
        if self.pk:
            q = q.exclude(pk=self.pk)
        if q.exists():
            raise Exception("Já existe um Módulo cadastrado com o Nome informado!")

    def validar_sigla_duplicada(self):
        q = Modulo.objects.filter(sigla=self.sigla)
        if self.pk:
            q = q.exclude(pk=self.pk)
        if q.exists():
            raise Exception("Já existe um Módulo cadastrado com a Sigla informada!")

    def validate(self):
        super().validate()
        self.validar_ordem_duplicada()
        self.validar_nome_duplicado()
        self.validar_sigla_duplicada()

    def validar_ordem_duplicada(self):
        q_modulos = Modulo.objects.filter(ordem=self.ordem, situacao="ATIVO")
        if self.pk:
            q_modulos = q_modulos.exclude(pk=self.pk)
        if q_modulos.exists():
            raise Exception("Já existe um Modulo cadastrado com a Ordem informada!")


class MenuGrupo(ModuloMenu):
    """
    Modelo para armazenar informações para Grupos de Menus
    """

    modulo = models.ForeignKey(Modulo, related_name="grupos", on_delete=models.PROTECT)

    def __str__(self):
        return f"Grupo de Menus: {self.nome}"

    def save(self, *args, **kargs):
        self.validate()
        super(MenuGrupo, self).save(*args, **kargs)
        atualizar_favoritos()

    def delete(self, *args, **kargs):
        super(MenuGrupo, self).delete(*args, **kargs)
        atualizar_favoritos()

    def validate(self):
        super().validate()
        self.validar_ordem_duplicada()
        self.validar_nome_duplicado()

    def validar_ordem_duplicada(self):
        q_menus_grupos = MenuGrupo.objects.filter(
            ordem=self.ordem, modulo=self.modulo, situacao="ATIVO"
        )

        if self.pk:
            q_menus_grupos = q_menus_grupos.exclude(pk=self.pk)

        if q_menus_grupos.exists():
            raise Exception("Já existe um Grupo cadastrado com a Ordem informada!")

    def validar_nome_duplicado(self):
        q = MenuGrupo.objects.filter(nome=self.nome)
        if self.pk:
            q = q.exclude(pk=self.pk)
        if q.exists():
            raise Exception(
                "Já existe um Grupo de Menu cadastrado com o Nome informado!"
            )


class Menu(ModuloMenu):
    """
    Modelo para armazenar informações de Menus
    """

    grupo = models.ForeignKey(MenuGrupo, related_name="menus", on_delete=models.PROTECT)
    url = models.CharField(max_length=255, verbose_name="url", null=True, blank=True)
    servidores_favoritos = models.ManyToManyField(
        Servidor, verbose_name="Servidores favoritos", related_name="menus_favoritos"
    )
    link_de_ajuda = models.URLField("Link de Ajuda", null=True, max_length=500)

    def __str__(self):
        return f"Menu: {self.nome}"

    def save(self, *args, **kargs):
        self.validate()
        super(Menu, self).save(*args, **kargs)
        atualizar_favoritos()

    def delete(self, *args, **kargs):
        super(Menu, self).delete(*args, **kargs)
        atualizar_favoritos()

    def validate(self):
        self.validar_ordem_duplicada()
        self.validar_quantidade_favoritos()
        self.validar_nome_duplicado()

    def validar_ordem_duplicada(self):
        q_menus = Menu.objects.filter(
            ordem=self.ordem, grupo=self.grupo, situacao="ATIVO"
        )

        if self.pk:
            q_menus = q_menus.exclude(pk=self.pk)

        if q_menus.exists():
            raise Exception("Já existe um Menu cadastrado com a Ordem informada!")

    def validar_nome_duplicado(self):
        q = Menu.objects.filter(nome=self.nome, grupo=self.grupo)
        if self.pk:
            q = q.exclude(pk=self.pk)
        if q.exists():
            raise Exception(
                "Já existe um Menu cadastrado com o Nome informado no mesmo Grupo de Menu!"
            )

    def validar_quantidade_favoritos(self):
        qtd_maxima = 10

        if self.pk and self.servidores_favoritos.count() > qtd_maxima:
            raise Exception(f"Só é possível favoritar {qtd_maxima} menus!")


class UsuarioGrupo(AuditTimestampModel):
    """
    Modelo para armazenar informações para Grupos de Usuários

    AVISO: Ao utilizar os métodos de adicionar/remover do campo: servidores, através desse model
    ou do model Servidor, adicione o método: atualizar_favoritos disponível em:
    painel_controle/controle_acesso/utils.py
    """

    SITUACAO = (
        ("ATIVO", "Ativo"),
        ("INATIVO", "Inativo"),
        ("PAUSADO", "Pausado"),
    )

    nome = models.CharField("Nome", max_length=150)
    descricao = models.TextField("Descrição", null=True, blank=True)
    servidores = models.ManyToManyField(Servidor, related_name="grupos_permissao")
    situacao = models.CharField(
        "Ativo", max_length=20, choices=SITUACAO, default="ATIVO", db_index=True
    )
    grupo_padrao = models.BooleanField(verbose_name="Grupo Padrão", default=False)

    class Meta:
        ordering = ("nome",)

    def __str__(self):
        return (
            f"Grupo de Usuários: {self.nome} - Qtd usuários: {self.servidores.count()}"
        )

    def save(self, *args, **kargs):
        self.nome = self.nome.lower()
        self.validate()
        super(UsuarioGrupo, self).save(*args, **kargs)
        atualizar_favoritos()

    def delete(self, *args, **kargs):
        super(UsuarioGrupo, self).delete(*args, **kargs)
        atualizar_favoritos()

    def validate(self):
        self.validar_nome_duplicado()

    def validar_nome_duplicado(self):
        q = UsuarioGrupo.objects.filter(nome=self.nome)
        if self.pk:
            q = q.exclude(pk=self.pk)
        if q.exists():
            raise Exception(
                "Já existe um Grupo de Usuários cadastrado com o Nome informado!"
            )


class MenuConfig(models.Model):
    """
    Modelo para armazenar informações de Configurações de Permissões aos Grupos de Usuários e Menus
    """

    usuario_grupo = models.ForeignKey(
        UsuarioGrupo, related_name="configs", on_delete=models.PROTECT
    )
    menu = models.ForeignKey(Menu, related_name="configs", on_delete=models.PROTECT)
    acoes = ArrayField(models.CharField(max_length=50), null=True, blank=True)

    def __str__(self):
        return f"Grupo de Usuário: {self.usuario_grupo.nome} - Menu: {self.menu.nome} - Ações: {', '.join(self.acoes)}"

    def save(self, *args, **kargs):
        super(MenuConfig, self).save(*args, **kargs)
        atualizar_favoritos()

    def delete(self, *args, **kargs):
        super(MenuConfig, self).delete(*args, **kargs)
        atualizar_favoritos()
