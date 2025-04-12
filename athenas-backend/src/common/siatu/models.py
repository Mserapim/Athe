# -*- coding: utf-8 -*-

"""
Módulo que contém a definição dos modelos.

:Classes:
  :class:`Area`,
  :class:`Servico`,
  :class:`Atendente`,
  :class:`AtendentesServicos`,
  :class:`Gerente`,

"""
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.db.models import Q
from django.core.validators import validate_comma_separated_integer_list

from ged.models import Arquivo
from contrib.decorator import to_search
from contrib.utils import getLogger, DateUtils, employee_from_user
from standard.models import Configuration, Choice
from engine.notification.models import Message, Notification
from engine.models import ControllerPermission
from contrib.middleware import get_current_user
from rh.models import Servidor, OrgaoGeral
from django.template import loader
from dateutil.relativedelta import relativedelta

log = getLogger(__name__)


class ModeloManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, descricao):
        return self.get(descricao=descricao)


class Modelo(models.Model):
    """
    **Classe** que define o modelo/marca/especialidade de um objeto da base de conhecimento do sistema.
    """

    class Meta:
        db_table = "siatu_modelo"
        ordering = ("descricao",)

    descricao = models.CharField(max_length=100, unique=True)
    informatica = models.BooleanField(null=True, blank=True)

    objects = ModeloManager

    def natural_key(self):
        return (self.descricao,)

    def __str__(self):
        return str(self.descricao)

    def save(self, *args, **kwargs):
        if (
            self.pk is None
            and Modelo.objects.filter(descricao=self.descricao).exists() is True
        ):
            raise Exception("Modelo já está cadastrado")
        else:
            super(self.__class__, self).save(*args, **kwargs)


class ObjetoManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, descricao):
        return self.get(descricao=descricao)


class Objeto(models.Model):
    """
    **Classe** que define o objeto da base de conhecimento do sistema.
    """

    class Meta:
        db_table = "siatu_objeto"
        ordering = ("descricao",)

    descricao = models.CharField(max_length=100, unique=True)
    modelos = models.ManyToManyField(Modelo, related_name="objetos")
    informatica = models.BooleanField(default=False)

    objetos = ObjetoManager

    def natural_key(self):
        return (self.descricao,)

    def save(self, *args, **kwargs):
        if (
            self.pk is None
            and Objeto.objects.filter(descricao=self.descricao).exists() is True
        ):
            raise Exception("Objeto já está cadastrado")
        else:
            super(self.__class__, self).save(*args, **kwargs)


class BaseConhecimento(models.Model):
    """
    **Classe** que define a base de conhecimento do sistema, como os problemas e as soluções adotadas.
    """

    class Meta:
        db_table = "siatu_base_conhecimento"
        ordering = ("objeto__descricao",)

    objeto = models.ForeignKey(
        Objeto, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    modelo = models.ForeignKey(
        Modelo, null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    problema = models.CharField(max_length=500)
    solucao = models.TextField(null=True, blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    arquivo = models.OneToOneField(
        Arquivo, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        if self.modelo is None:
            texto = self.objeto.descricao + " -> " + self.problema
        else:
            texto = (
                self.objeto.descricao
                + " -> "
                + self.modelo.descricao
                + " -> "
                + self.problema
            )
        return texto


class ItemBaseConhecimento(models.Model):
    """
    **Classe** que define os itens base de conhecimento do chamado. Relacao entre Chamado e BaseConhecimento.
    """

    class Meta:
        db_table = "siatu_item_base_conhecimento"
        unique_together = (("chamado", "base_conhecimento"),)
        ordering = ("base_conhecimento__objeto__descricao",)

    # Parametro "on_delete" adicionado. (Django 2)
    chamado = models.ForeignKey(
        "Chamado", related_name="itens_base_conhecimento", on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    base_conhecimento = models.ForeignKey(
        BaseConhecimento,
        related_name="itens_base_conhecimento",
        on_delete=models.CASCADE,
    )
    info = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if (
            self.chamado.status_atual.status == Status.CONCLUIDO
            or self.chamado.status_atual.status == Status.AGUARDANDO_AVALIACAO
        ):
            raise Exception("Operação não permitida - chamado concluído.")
        else:
            super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if (
            self.chamado.status_atual.status == Status.CONCLUIDO
            or self.chamado.status_atual.status == Status.AGUARDANDO_AVALIACAO
        ):
            raise Exception("Operação não permitida - chamado concluído.")
        else:
            return super(self.__class__, self).delete(*args, **kwargs)


class FilaUnica(models.Model):
    """
    **Classe** que define a fila única para um serviço e localidade.
    """

    class Meta:
        db_table = "siatu_fila_unica"
        unique_together = (("servico", "localidade"),)
        # ordering = ('base_conhecimento__objeto__descricao',)

    servico = models.ForeignKey(
        "Servico", related_name="filas", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    localidade = models.CharField(max_length=50)

    def __str__(self):
        return "%s / %s" % (self.servico.nome, self.localidade)

    def dist_um_dos_proximos(self):
        # quantidade tentativas de distribuir um chamado da fila
        # começa com 1 pois o primeiro da fila era reincidente e não pôde ser associado
        # ao atendente disponivel - apos executar o metodo dist_primeiro_chamado_fila_unica
        qt_tentativas = 1
        continua = True
        # WHILE esse if    and continua == True
        while (self.chamados.count() > qt_tentativas) and (continua is True):
            chamado = self.chamados.order_by("-urgente", "data_fila_atendimento")[
                qt_tentativas
            ]
            qt_tentativas = qt_tentativas + 1
            if chamado.distribuicao_automatica() != 1:
                continua = False

    @classmethod
    def dist_primeiro_chamado_fila_unica(cls):
        """Distribui o primeiro chamado de cada fila unica - ou distribui um dos proximos da fila
        caso o atendente disponivel não possa receber o primeiro chamado, caso em que o primeiro chamado da fila
        é um chamado reincidente em que seu chamado anterior está associado ao atendente disponível
        """
        log.info("Evento distribuir primeiro chamado de cada fila unica")
        chamados_a_distribuir = []
        for fila in cls.objects.all():
            if (
                fila.chamados.order_by("-urgente", "data_fila_atendimento").exists()
                is True
            ):
                chamados_a_distribuir.append(
                    fila.chamados.order_by("-urgente", "data_fila_atendimento")[0]
                )

        chamados = Chamado.objects.filter(pk__in=[c.pk for c in chamados_a_distribuir])
        for c in chamados.order_by("-urgente", "data_fila_atendimento"):
            if c.distribuicao_automatica() == 1:
                # Se não distribuiu o chamado por causa de um atendente disponivel nao poder receber
                # chamado reincidente, entao tenta distribuir um da mesma fila até conseguir distribuir um
                # ou chegar no fim da fila (todos na fila seriam reincidentes e nao poderiam ser atribuido ao fulano)
                c.fila.dist_um_dos_proximos()


class DistribuicaoAutomatica(models.Model):
    """
    **Classe** que define as configurações para distribuição automática de um serviço.
    """

    class Meta:
        db_table = "siatu_distribuicao_automatica"
        # ordering = ('nome',)

    # Parametro "on_delete" adicionado. (Django 2)
    servico = models.OneToOneField(
        "Servico", related_name="distribuicao_automatica", on_delete=models.CASCADE
    )
    tipo_atendimento = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=15
    )
    solicitantes = models.ManyToManyField(User, related_name="+")

    def get_tipo_atendimento(self):
        """Retorna a configuração para tipo atendimento"""
        return self.tipo_atendimento.split(",")

    @classmethod
    def list_to_comma(cls, lista):
        """Converte uma lista de strings para o formato de armazenamento

        :param lista: Lista de configuração para cada tipo de atendimento
        :type lista: Lista de Strings

        :returns: Strings separadas por virgula
        """
        return ",".join(lista)

    def set_tipo_atendimento(self, lista):
        """Armazena uma lista de strings no formato de armazenamento

        :param lista: Lista de configuração para cada tipo de atendimento
        :type lista: Lista de Strings
        """
        self.tipo_atendimento = ",".join(lista)


class ServicoManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, nome, servico_superior):
        return self.get(nome=nome, servico_superior=servico_superior)


class Servico(models.Model):
    """
    **Classe** que define os serviços.
    """

    class Meta:
        db_table = "siatu_servico"
        ordering = ("nome",)

    nome = models.CharField(max_length=150)
    # Parametro "on_delete" adicionado. (Django 2)
    servico_superior = models.ForeignKey(
        "self",
        related_name="subservicos",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    lista_atendentes = models.ManyToManyField(
        "Atendente", related_name="servicos_vinculados", through="AtendentesServicos"
    )
    lista_gerentes = models.ManyToManyField(
        "Gerente", related_name="servicos_vinculados"
    )
    objects = ServicoManager

    def natural_key(self):
        return (self.nome, self.servico_superior)

    @property
    def leaf(self):
        return not self.subservicos.exists()

    @property
    def contains_chamado(self):
        if self.chamados.exists():
            return True
        all_sub_services = []
        all_sub_services.extend(self.subservicos.all())
        for i in all_sub_services:
            all_sub_services.extend(i.subservicos.all())
            if i.chamados.exists():
                return True
        return False

    @property
    def path(self):
        if self.servico_superior is None:
            return self.nome
        else:
            return ", ".join([self.nome, self.servico_superior.path])

    def lista_total_atendentes(self):
        all_sub_services = []
        lista = []
        all_sub_services.extend(self.subservicos.all())
        lista.extend(self.lista_atendentes.all())
        for i in all_sub_services:
            all_sub_services.extend(i.subservicos.all())
            lista.extend(i.lista_atendentes.all())

        return lista

    def lista_total_gerentes(self):
        all_servicos_sup = []
        lista_gerentes = []
        if self.servico_superior is not None:
            all_servicos_sup.append(self.servico_superior)
        lista_gerentes.extend(self.lista_gerentes.all())
        for i in all_servicos_sup:
            if i.servico_superior is not None:
                all_servicos_sup.append(i.servico_superior)
            lista_gerentes.extend(i.lista_gerentes.all())

        return lista_gerentes

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        insert = True if self.pk is None else False
        super(Servico, self).save(*args, **kwargs)
        if insert:
            tipo_atendimento = []
            for item in Solicitacao.TIPO_CHOICES:
                tipo_atendimento.append("1")
            dist = DistribuicaoAutomatica(servico=self)
            dist.set_tipo_atendimento(tipo_atendimento)
            dist.save()

    def delete(self, *args, **kwargs):
        if self.contains_chamado is False:
            return super(self.__class__, self).delete(*args, **kwargs)
        else:
            raise Exception("Operação não permitida - Serviço possui chamado.")


@to_search(
    [
        {"name": "usuario__servidor__pessoa_fisica__nome", "type": "text"},
    ]
)
class Atendente(models.Model):
    """
    **Classe** que define os atendentes.
    """

    class Meta:
        db_table = "siatu_atendente"
        ordering = ("usuario__username",)

    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    notificacao_receber_chamado = models.BooleanField(default=False)

    @property
    def icon_busy(self):
        translate = {
            True: {"iconCls": "icon-siatu icon-siatu-ocupado", "title": "Ocupado"},
        }

        return translate.get(
            self.is_busy(),
            {"iconCls": "icon-siatu icon-siatu-disponivel", "title": "Disponível"},
        )

    def __str__(self):
        return self.usuario.username

    def get_grupo(self):
        return Group.objects.get(name="siatu-atendente")

    def get_controller_permission(self):
        return ControllerPermission.objects.get(name="siatu-atendente")

    def is_busy(self):
        return self.chamados.filter(
            Q(status_atual__status=Status.EM_ATENDIMENTO)
            | Q(status_atual__status=Status.TERCEIRIZADA)
            | Q(status_atual__status=Status.GARANTIA)
            | Q(status_atual__status=Status.VIAGEM)
        ).exists()

    def tem_chamado_aguardando_atendimento(self):
        return self.chamados.filter(
            Q(status_atual__status=Status.AGUARDANDO_ATENDIMENTO)
        ).exists()

    def save(self, *args, **kwargs):
        if self.pk is None:
            grupo_atendente = self.get_grupo()
            controller_permission = self.get_controller_permission()
            self.usuario.groups.add(grupo_atendente)
            controller_permission.users.add(self.usuario)
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.chamados.exists():
            grupo_atendente = self.get_grupo()
            controller_permission = self.get_controller_permission()
            self.usuario.groups.remove(grupo_atendente)
            controller_permission.users.remove(self.usuario)
            return super(self.__class__, self).delete(*args, **kwargs)
        else:
            log.warn("Operação não permitida - atendente associado a chamado")
            raise Exception("Operação não permitida - Atendente associado a chamado.")


class AtendentesServicos(models.Model):
    """
    **Classe** que define a relação ManyToMany entre atendentes e serviços.
    """

    class Meta:
        db_table = "siatu_atendentes_servicos"
        unique_together = (("servico", "atendente"),)
        ordering = ("atendente__usuario__username", "servico__nome")

    # Parametro "on_delete" adicionado. (Django 2)
    servico = models.ForeignKey(
        Servico, related_name="relacaoAt_Serv", on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    atendente = models.ForeignKey(
        Atendente, related_name="relacaoAt_Serv", on_delete=models.CASCADE
    )
    distribuicao_automatica = models.BooleanField(default=True)

    @property
    def icon_dist_aut(self):
        translate = {
            True: {
                "iconCls": "icon-siatu icon-siatu-automatico",
                "title": "Distribuição automática",
            },
        }

        return translate.get(
            self.distribuicao_automatica,
            {"iconCls": "icon-siatu icon-siatu-manual", "title": "Distribuição manual"},
        )


class Gerente(models.Model):
    """
    **Classe** que define os gerentes.
    """

    class Meta:
        db_table = "siatu_gerente"
        ordering = ("usuario__username",)

    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def lista_total_servicos(self):
        lista = []
        lista.extend(self.servicos_vinculados.all())
        for i in lista:
            lista.extend(i.subservicos.all())

        return lista

    def __str__(self):
        return self.usuario.username

    def get_grupo(self):
        return Group.objects.get(name="siatu-gerente")

    def get_controller_permission(self):
        return ControllerPermission.objects.get(name="siatu-gerente")

    def save(self, *args, **kwargs):
        if self.pk is None:
            grupo_gerente = self.get_grupo()
            controller_permission = self.get_controller_permission()
            self.usuario.groups.add(grupo_gerente)
            controller_permission.users.add(self.usuario)
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        grupo_gerente = self.get_grupo()
        controller_permission = self.get_controller_permission()
        self.usuario.groups.remove(grupo_gerente)
        controller_permission.users.remove(self.usuario)
        return super(self.__class__, self).delete(*args, **kwargs)


class Solicitacao(models.Model):
    class Meta:
        db_table = "siatu_solicitacao"
        ordering = ("-pk",)

    TIPO_CHOICES = (
        (0, "Sistema"),
        (1, "Email"),
        (2, "Telefone"),
        (3, "Documento"),
        (4, "Verbal"),
    )

    usuario = models.ForeignKey(
        User, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    solicitante = models.ForeignKey(
        User, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    servico = models.ForeignKey(
        Servico, related_name="solicitacoes", on_delete=models.CASCADE
    )
    tipo = models.SmallIntegerField(choices=TIPO_CHOICES, default=0)
    telefone = models.CharField(max_length=25)
    descricao_problema = models.CharField(max_length=600)
    reincidencia = models.BooleanField(default=False)
    # Parametro "on_delete" adicionado. (Django 2)
    chamado_anterior = models.ForeignKey(
        "Chamado", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    orgao_geral_origem = models.ForeignKey(
        OrgaoGeral,
        verbose_name="Origem",
        related_name="orgao_origem",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        insert = not self.pk
        try:
            with transaction.atomic():
                if self.reincidencia == "off":
                    self.reincidencia = False
                super(Solicitacao, self).save(*args, **kwargs)
                cfg = Configuration.get_or_create("siatu")
                if cfg.items.count() == 0:
                    raise Exception("Falta configuração padrão de envio de emails")

                if insert:
                    config_solicitante = ConfigEmailSolicitante.objects.get_or_create(
                        aguardando_avaliacao=int(
                            cfg.get("solicitante_aguardando_avaliacao")
                        ),
                        transferido_atendente=int(
                            cfg.get("solicitante_transferido_atendente")
                        ),
                        garantia=int(cfg.get("solicitante_garantia")),
                        terceirizada=int(cfg.get("solicitante_terceirizada")),
                        viagem=int(cfg.get("solicitante_viagem")),
                    )[0]
                    config_atendente = ConfigEmailAtendente.objects.get_or_create(
                        transferido_atendente=int(
                            cfg.get("atendente_transferido_atendente")
                        ),
                        apos_avaliacao=int(cfg.get("atendente_apos_avaliacao")),
                    )[0]

                    c = Chamado(
                        solicitacao=self,
                        servico=self.servico,
                        cfg_email_solicitante=config_solicitante,
                        cfg_email_atendente=config_atendente,
                        chamado_anterior=self.chamado_anterior,
                    )

                    if self.reincidencia:
                        r = Reincidencia()
                        r.save()
                        c.reincidencia = r
                    c.save()
        except Exception as e:
            log.exception(e)
            raise (e)


class ConfigEmailSolicitante(models.Model):
    class Meta:
        db_table = "siatu_configemailsolicitante"

    aguardando_avaliacao = models.BooleanField(default=True)
    transferido_atendente = models.BooleanField(default=True)
    garantia = models.BooleanField(default=True)
    terceirizada = models.BooleanField(default=True)
    viagem = models.BooleanField(default=True)


class ConfigEmailAtendente(models.Model):

    class Meta:
        db_table = "siatu_configemailatendente"

    transferido_atendente = models.BooleanField(default=True)
    apos_avaliacao = models.BooleanField(default=True)


class Reincidencia(models.Model):
    class Meta:
        db_table = "siatu_reincidencia"

    opiniao_atendente = models.CharField(max_length=300, null=True, blank=True)
    confirm_atendente = models.BooleanField(default=True)
    motivo_gerente = models.CharField(max_length=300, null=True, blank=True)
    parecer = models.BooleanField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            if (
                self.chamado.status_atual.status == Status.CONCLUIDO
                or self.chamado.status_atual.status == Status.AGUARDANDO_AVALIACAO
            ):
                log.warn("Operação não permitida - chamado concluído")
                raise Exception("Operação não permitida - chamado concluído")
        super(Reincidencia, self).save(*args, **kwargs)
        if not self.confirm_atendente and not self.parecer:
            lista_gerentes = self.chamado.servico.lista_total_gerentes()
            lista_gerentes = Gerente.objects.filter(
                pk__in=[i.pk for i in lista_gerentes]
            ).exclude(usuario__servidor__isnull=True)

            try:
                servidores = [employee_from_user(g.usuario) for g in lista_gerentes]
                log.info(
                    "Enviando email para gerentes - notificar conflito reincidencia"
                )
                msg = Message.objects.get(mid="siatu-conflito-reincidencia")
                Notification.notify_all(
                    msg, servidores, chamado=self.chamado.cache_numero
                )
            except Exception as e:
                log.info("Email não enviado")
                log.exception(e)


class Terceirizada(models.Model):
    class Meta:
        db_table = "siatu_terceirizada"
        ordering = ("nome",)

    nome = models.CharField(max_length=80)
    cnpj = models.CharField(max_length=50)

    def delete(self, *args, **kwargs):
        if not self.chamados.exists():
            return super(self.__class__, self).delete(*args, **kwargs)
        else:
            log.warn("Operação não permitida - Terceirizada associada a chamado")
            raise Exception(
                "Operação não permitida - Terceirizada associada a chamado."
            )


class TerceiroInterno(models.Model):
    class Meta:
        db_table = "siatu_terceirointerno"
        ordering = ("nome",)

    STATUS = (
        (1, "ATIVO"),
        (2, "INATIVO"),
    )

    nome = models.CharField(max_length=80)
    cpf = models.CharField(max_length=50)
    telefone = models.CharField(max_length=50)
    endereco = models.CharField(max_length=150)
    status = models.SmallIntegerField(choices=STATUS, default=1)

    @property
    def icon_busy(self):
        translate = {
            True: {"iconCls": "icon-siatu icon-siatu-ocupado", "title": "Ocupado"},
        }

        return translate.get(
            self.is_busy(),
            {"iconCls": "icon-siatu icon-siatu-disponivel", "title": "Disponível"},
        )

    def __str__(self):
        return self.nome

    def is_busy(self):
        return self.chamados.filter(
            Q(status_atual__status=Status.EM_ATENDIMENTO)
            | Q(status_atual__status=Status.TERCEIRIZADA)
            | Q(status_atual__status=Status.GARANTIA)
        ).exists()

    def delete(self, *args, **kwargs):
        if not self.chamados.exists():
            return super(self.__class__, self).delete(*args, **kwargs)
        else:
            log.warn("Operação não permitida - terceiro associado a chamado")
            raise Exception("Operação não permitida - Terceiro associado a chamado.")


class Chamado(models.Model):
    class Meta:
        db_table = "siatu_chamado"
        ordering = ("nao_urgente", "-pk")
        permissions = (
            ("admin", "Visão administrativa"),
            ("gerente", "Visão de gerente"),
            ("atendente", "Visão de atendente"),
        )

    # Parametro "on_delete" adicionado. (Django 2)
    fila = models.ForeignKey(
        FilaUnica,
        related_name="chamados",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    data_fila_atendimento = models.DateTimeField(null=True, blank=True)

    numero = models.SmallIntegerField()
    ano = models.SmallIntegerField()
    cache_numero = models.CharField(db_index=True, max_length=10)

    solicitacao = models.OneToOneField(
        Solicitacao, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    servico = models.ForeignKey(
        Servico, related_name="chamados", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    cancelado = models.BooleanField(default=False)
    nao_institucional = models.BooleanField(default=False)
    motivo_cancelado = models.CharField(max_length=200, null=True, blank=True)
    base_conhecimento = models.ManyToManyField(
        BaseConhecimento, related_name="chamados", through=ItemBaseConhecimento
    )

    urgente = models.BooleanField(default=False)
    rank = models.IntegerField(default=0, db_index=True)
    motivo_urgencia = models.CharField(max_length=200, null=True, blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    status_atual = models.OneToOneField(
        "Status", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )

    atendentes = models.ManyToManyField(Atendente, related_name="chamados")
    # Parametro "on_delete" adicionado. (Django 2)
    cfg_email_solicitante = models.ForeignKey(
        ConfigEmailSolicitante, on_delete=models.CASCADE
    )
    cfg_email_atendente = models.ForeignKey(
        ConfigEmailAtendente, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    reincidencia = models.OneToOneField(
        Reincidencia, null=True, blank=True, on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    chamado_anterior = models.OneToOneField(
        "self",
        related_name="chamado_reincidente",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    terceirizada = models.ManyToManyField(Terceirizada, related_name="chamados")
    terceiro_interno = models.ManyToManyField(TerceiroInterno, related_name="chamados")

    relatorio = models.TextField(null=True, blank=True)

    nao_urgente = models.BooleanField(default=False)
    # Parametro "on_delete" adicionado. (Django 2)
    nao_urgente_por = models.ForeignKey(
        Servidor, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )

    @property
    def icons(self):
        lista = [self.icon_reincidente]

        if self.cancelado:
            lista.append(self.icon_cancelado)
        else:
            lista.append(self.icon_status)
        lista.extend(
            [
                self.icon_urgente,
                self.icon_avaliacao,
                self.icon_avaliacaoneutra,
                self.icon_nao_urgente,
            ]
        )
        return lista

    @property
    def icon_avaliacaoneutra(self):
        try:
            if self.avaliacao.avaliacao_neutra:
                return {
                    "iconCls": "icon-siatu icon-siatu-automatico",
                    "title": "Avaliação Neutralizada",
                }
        except Exception:
            return {"iconCls": "icon-siatu icon-siatu-empty", "title": ""}

    @property
    def icon_avaliacao(self):
        translate = {
            5: {"iconCls": "icon-siatu icon-siatu-otimo", "title": "Ótimo"},
            4: {"iconCls": "icon-siatu icon-siatu-bom", "title": "Bom"},
            3: {"iconCls": "icon-siatu icon-siatu-regular", "title": "Regular"},
            2: {"iconCls": "icon-siatu icon-siatu-ruim", "title": "Ruim"},
            1: {"iconCls": "icon-siatu icon-siatu-pessimo", "title": "Péssimo"},
        }
        try:
            avaliacao = self.avaliacao.satisfacao

        except Exception:
            avaliacao = 0

        return translate.get(
            avaliacao,
            {
                "iconCls": "icon-siatu icon-siatu-empty",
            },
        )

    @property
    def icon_status(self):
        translate = Status.ICONS

        return translate.get(
            self.status_atual.status,
            {
                "iconCls": "icon-siatu icon-siatu-empty",
            },
        )

    @property
    def icon_reincidente(self):
        translate = {
            True: {
                "iconCls": "icon-siatu icon-siatu-reincidente",
                "title": "Reincidente",
            },
        }

        return translate.get(
            self.solicitacao.reincidencia,
            {
                "iconCls": "icon-siatu icon-siatu-empty",
            },
        )

    @property
    def icon_cancelado(self):
        translate = {
            True: {
                "iconCls": "icon-siatu icon-siatu-cancelado",
                "title": "Cancelado: " + self.motivo_cancelado,
            },
        }

        return translate.get(
            self.cancelado,
            {
                "iconCls": "icon-siatu icon-siatu-empty",
            },
        )

    @property
    def icon_urgente(self):
        translate = {
            True: {"iconCls": "icon-siatu icon-siatu-urgente", "title": "Urgente"},
        }

        return translate.get(
            self.urgente,
            {
                "iconCls": "icon-siatu icon-siatu-empty",
            },
        )

    @property
    def icon_nao_urgente(self):
        servidor = Servidor.objects.get(user=get_current_user())

        if servidor.user.has_perm("siatu.admin"):
            translate = {
                True: {
                    "iconCls": "icon-siatu icon-siatu-move-down",
                    "title": "Não Urgente",
                },
            }
            return translate.get(
                self.nao_urgente,
                {
                    "iconCls": "icon-siatu icon-siatu-empty",
                },
            )
        else:
            return {"iconCls": "icon-siatu icon-siatu-empty", "title": ""}

    @classmethod
    def next_numero(cls):
        now = datetime.now()
        query = (
            Chamado.objects.filter(ano=now.year)
            .order_by("numero")
            .aggregate(maximo=models.Max("numero"))
        )
        numero = int(query.get("maximo") or 0)

        return numero + 1, now.year

    @property
    def _inicio_atendimento(self):
        s = Status.objects.filter(chamado=self).order_by("id")[0]
        return s.data_inicio.replace(second=0, microsecond=0)

    @property
    def _fim_atendimento(self):
        s = Status.objects.filter(chamado=self, status=4)
        if s.count():
            return s.latest("id").data_inicio.replace(second=0, microsecond=0)
        else:
            return datetime.now()

    def get_tempo_expediente(self):
        t = DateUtils.tempo_de_expediente(
            self._inicio_atendimento, self._fim_atendimento
        )
        return t

    def retirar_atendentes_ch_anterior(self, atendentes):
        # Atendentes do chamado anterior não entram na distribuição automática
        if self.chamado_anterior:
            atendentes = atendentes.exclude(
                pk__in=self.chamado_anterior.atendentes.values_list("pk", flat=True)
            )
        return atendentes

    @property
    def valida_localidade(self):
        # localidades_filtro = ['GURUPI', 'ARAGUAINA']
        localidades_filtro = [
            c.label
            for c in Choice.objects.filter(
                value__gt=1, name="LOCATION_OF_THE_ATTENDANT", app_label="siatu"
            )
        ]
        return localidades_filtro

    def possiveis_atendentes(self):
        # Seleciona os atendentes vinculados ao servico que estao marcados para distribuição automática
        atendentes = Atendente.objects.filter(
            pk__in=[
                a.atendente.pk
                for a in self.servico.relacaoAt_Serv.all()
                if a.distribuicao_automatica
            ]
        )

        atendentes = Servidor.objects.filter(
            pk__in=atendentes.all().values_list("usuario__servidor__id", flat=True)
        )
        now = datetime.now()
        pks = [
            serv.user.atendente.id
            for serv in atendentes
            if not serv.afastamento_ativo(now) or not serv.is_traveling(now)
        ]
        atendentes = Atendente.objects.filter(pk__in=pks)

        servidor_solicitante = employee_from_user(self.solicitacao.solicitante)
        if not servidor_solicitante:
            log.warn("Solicitante não é servidor ativo")
            return atendentes.none()
        if servidor_solicitante.workplace_current is None:
            log.warn("Solicitante não possui lotação atual")
            return atendentes.none()

        # Atendimento especifico para localidade do solicitante
        lista = []
        localidade_solicitante = (
            servidor_solicitante.workplace_current.localidade.nome.upper()
        )

        # Redirecionando solicitações para a Sede
        if localidade_solicitante not in self.valida_localidade:
            localidade_solicitante = Choice.objects.get(
                value=1, name="LOCATION_OF_THE_ATTENDANT", app_label="siatu"
            ).label

        for a in atendentes:
            servidor = employee_from_user(a.usuario)
            if not (servidor is None) and not (servidor.workplace_current is None):
                localidade_atendente = (
                    servidor.workplace_current.localidade.nome.upper()
                )
                log.info(
                    "Localidade Atendente: %s . Localidade Solicitante: %s"
                    % (localidade_atendente, localidade_solicitante)
                )
                if localidade_atendente == localidade_solicitante:
                    lista.append(a)

        possiveis_atendentes = Atendente.objects.filter(pk__in=[a.pk for a in lista])

        return possiveis_atendentes

    def atendentes_aptos(self):
        possiveis_atendentes = self.possiveis_atendentes()

        atendentes_aptos = self.retirar_atendentes_ch_anterior(possiveis_atendentes)

        return atendentes_aptos

    def verifica_regras_distribuicao(self):
        """Verifica se o chamado está autorizado a entrar na fila"""
        # Retorna True se o chamado está habilitado para entrar na Fila
        # Retorna False se o chamado não pode entrar na fila, porque o solicitante está desativado
        # na dist. autom.. ou o tipo de atendimento está desativado na dist. aut. do servico do chamado.
        # Configuracoes - Tipo atendimento
        dist = DistribuicaoAutomatica.objects.get(servico=self.servico)
        try:
            if dist.get_tipo_atendimento()[self.solicitacao.tipo] == "0":
                log.info("Distribuição automática desativada para tipo atendimento")
                return False
        except Exception as e:
            log.warn(
                "Falta adicionar tipo_atendimento choice na lista de conf.. da dist. aut. para o servico"
            )
            log.debug("Serviço: {}".format(dist.servico))
            log.debug(
                "tipo_atendimento: {}".format(self.solicitacao.get_tipo_display())
            )
            log.exception(e)
            return False

        # Solicitantes marcados para distribuição manual
        if self.solicitacao.solicitante in dist.solicitantes.all():
            log.info("Solicitante marcado para distribuicao manual de seus chamados")
            return False
        # fim configuracoes retorna o queryset de atendentes
        return True

    def distribuicao_automatica(self):
        log.info("Realizando distribuicao automatica - fila: {}".format(self.fila))

        possiveis_atendentes = self.possiveis_atendentes()
        if possiveis_atendentes.exists() is False:
            log.debug(
                "Não foi realizada a distribuição automática - não há atendentes habilitados para o servico {}".format(
                    self.servico
                )
            )
            return 0

        atendentes_disponiveis = []
        for atendente in possiveis_atendentes:
            if (
                atendente.is_busy() is False
                and atendente.tem_chamado_aguardando_atendimento() is False
            ):
                atendentes_disponiveis.append(atendente)

        atendentes_disponiveis = Atendente.objects.filter(
            pk__in=[a.pk for a in atendentes_disponiveis]
        )

        if atendentes_disponiveis.exists() is False:
            log.debug(
                "Não foi realizada a distribuição automática - não há atendentes disponiveis para o servico {}".format(
                    self.servico
                )
            )
            return 0

        # REMOVENDO OS ATENDENTES DO CHAMADO ANTERIOR
        atendentes_disponiveis_aptos = self.retirar_atendentes_ch_anterior(
            atendentes_disponiveis
        )
        if atendentes_disponiveis_aptos.exists() is False:
            log.debug(
                "Não foi realizada a distribuição automatica - há atendentes disponiveis, "
                "porém não aptos(ch reincidente) para receber o chamado "
            )
            # Retorna 1 - Pois irá disparar a distribuicao automatica para o proximo chamado da fila
            return 1

        selecionado = self.selecionar(atendentes_disponiveis_aptos)
        log.info("Atendente selecionado")
        log.debug(selecionado)
        self.atendentes.add(selecionado)
        # Enviar notificação para atendentes
        log.info("Enviando email para atendente - recebimento de chamado")
        try:
            if selecionado.notificacao_receber_chamado is True:
                msg = Message.objects.get(mid="siatu-atendente-recebe")
                servidor_atendente = employee_from_user(selecionado.usuario)
                Notification.notify(
                    msg,
                    servidor_atendente,
                    types=["SYS", "EMAIL"],
                    chamado=self.cache_numero,
                )
                log.info("Email enviado com sucesso")
            else:
                log.info("Envio de email desativado")
        except Exception as e:
            log.info("Email não enviado")
            log.exception(e)
        # Fim envio notificação
        # Altera a data fila atendimento, para ordenar a chegada na fila do atendente
        self.data_fila_atendimento = datetime.now()
        self.fila = None
        self.save(system=True)
        return 0

    def selecionar(self, atendentes):
        selecionado = None
        qtde_selecionado = 0
        for a in atendentes:
            qtde_atual = a.chamados.exclude(
                Q(
                    Q(status_atual__status=Status.CONCLUIDO)
                    | Q(status_atual__status=Status.AGUARDANDO_AVALIACAO)
                    | Q(status_atual__status=Status.TERCEIRIZADA)
                    | Q(status_atual__status=Status.GARANTIA)
                    | Q(status_atual__status=Status.AGUARDANDO_ENTREGA)
                )
            ).count()
            if (selecionado is None) or (qtde_atual < qtde_selecionado):
                selecionado = a
                qtde_selecionado = qtde_atual

        return selecionado

    def validate_changes(self, system):
        if self.cancelado is False and system is False:
            user = get_current_user()
            if user.has_perm("siatu.admin") is False:
                if user.has_perm("siatu.gerente") is False:
                    if user.has_perm("siatu.atendente") is False:
                        raise Exception(
                            "Você não tem permissão para modificar o chamado"
                        )

    @property
    def attachment_list(self):
        return self.anexos.filter(
            pk__in=self.anexos.order_by("arquivo").distinct("arquivo")
        ).order_by("id")

    @property
    def tempo_decorrido_chamado(self):
        t = self.get_tempo_expediente()
        tempo = relativedelta(days=t.days, seconds=t.seconds)
        # Um dia de 24 horas contém 3 dias de expediente
        tempo.days = tempo.days * 3
        # Converte as horas excedentes para dia de expediente
        tempo.days = tempo.days + int(tempo.hours / 8)
        tempo.hours = tempo.hours % 8
        dias = str(tempo.days) + "d " if tempo.days > 0 else ""
        horas = str(tempo.hours) + "h " if tempo.hours > 0 else ""
        minutos = str(tempo.minutes) + "min" if tempo.minutes > 0 else ""
        tempo_decorrido = dias + horas + minutos

        return tempo_decorrido

    @property
    def render_process(self):
        atendentes = [
            at.usuario.servidor.pessoa_fisica.nome.encode("ascii", "ignore")
            for at in self.atendentes.all()
        ]
        user = Servidor.objects.get(user=self.solicitacao.solicitante)
        workplace = user.workplace_by_date()

        lotacao = "SEM LOTAÇÃO VIGENTE"
        cidade = "NÃO ENCONTRADA"

        if workplace:
            lotacao = workplace.nome
            cidade = workplace.localidade.nome

        tempo_decorrido = self.tempo_decorrido_chamado

        tpl = loader.get_template("chamado/chamado.html")
        return tpl.render(
            {
                "chamado": self,
                "appends": [
                    {
                        "lotacao": lotacao,
                        "membro": "Sim" if (user.membro) else "Não",
                        "atendentes": atendentes,
                        "urgente": "Sim" if self.urgente else "Não",
                        "reincidencia": (
                            "Sim" if self.solicitacao.reincidencia else "Não"
                        ),
                        "cidade": cidade,
                        "status_chamado": self.status_atual.data_inicio.strftime(
                            "%d/%m/%Y %H:%M"
                        ),
                        "tempo_decorrido": tempo_decorrido,
                        "inicio": Status.objects.filter(chamado=self)
                        .first()
                        .data_inicio.strftime("%d/%m/%Y %H:%M"),
                        "fim": (
                            Status.objects.filter(chamado=self)
                            .last()
                            .data_inicio.strftime("%d/%m/%Y %H:%M")
                            if Status.objects.filter(chamado=self).last().status == 9
                            else ""
                        ),
                    }
                ],
            }
        )

    def save(self, *args, **kwargs):
        insert = not self.pk
        system = kwargs.get("system", False)
        if "system" in kwargs:
            del kwargs["system"]

        if self.reincidencia:
            if self.chamado_anterior and self.chamado_anterior.cancelado:
                raise Exception(
                    "Não é possível solicitar reincidência de um chamado cancelado!"
                )
        if insert:
            # Recebe o código do chamado
            self.numero, self.ano = self.next_numero()
            self.cache_numero = "%05d/%4d" % (self.numero, self.ano)

            servidor_solicitante = employee_from_user(self.solicitacao.solicitante)
            localidade_solicitante = (
                servidor_solicitante.workplace_current.localidade.nome.upper()
            )
            atendentes_aptos = self.atendentes_aptos()

            if not atendentes_aptos.filter(
                usuario__servidor__lotacoes__localidade__nome=localidade_solicitante
            ).exists():
                self.rank += 1

            if atendentes_aptos.exists() and self.verifica_regras_distribuicao():
                # Caso exista atendente apto, entao temos a certeza de que o solicitante é servidor e possui workplace_current
                # pois na execução do metodo atendentes_aptos é realizada esta verificação.
                # Inicio Gambiarra - Direcionando todos os chamados que não forem de Gurupi para Palmas
                # if localidade_solicitante != 'GURUPI':
                if localidade_solicitante not in self.valida_localidade:
                    localidade_solicitante = "PALMAS"
                # Fim Gambiarra
                # Entra na Fila
                self.fila, novo = FilaUnica.objects.get_or_create(
                    servico=self.servico, localidade=localidade_solicitante
                )
                self.data_fila_atendimento = datetime.now()
        else:
            if self.urgente:
                self.rank += 1

            self.validate_changes(system)
            old = Chamado.objects.get(pk=self.pk)
            if old.status_atual is not None:
                if old.status_atual.status == Status.CONCLUIDO:
                    log.warn("Operação não permitida - chamado concluído")
                    raise Exception("Operação não permitida - chamado concluido")
                if old.status_atual.status == Status.AGUARDANDO_AVALIACAO and int(
                    self.status_atual.status
                ) not in [Status.CONCLUIDO, Status.NAOAVALIADO]:
                    log.warn("Operação não permitida - chamado concluído")
                    raise Exception("Operação não permitida - chamado concluido")
            # Ao cancelar um chamado, ou atendê-lo, este deve sair da fila, se ainda não estiver fora.
            if (
                self.cancelado is True
                or int(self.status_atual.status) == Status.EM_ATENDIMENTO
                or int(self.status_atual.status) == Status.VIAGEM
            ):
                self.fila = None
            # Apenas para garantir que o chamado estará fora da fila quando o chamado for de fato concĺuído.
            # Em uma possível alteração do fluxo de estados. Quando estiver disparando evento distribuir chamado
            # havera a garantia de que o chamado que nao deveria estar mais na fila de fato saiu
            if int(self.status_atual.status) == Status.AGUARDANDO_ENTREGA:
                self.fila = None
            if (
                int(self.status_atual.status) == Status.AGUARDANDO_AVALIACAO
                or int(self.status_atual.status) == Status.CONCLUIDO
            ):
                self.fila = None
                # Ao encerrar o chamado - as transferencias pendentes são encerradas para evitar transtornos
                lista = self.transferencias.filter(
                    aceito_por__isnull=True, cancelado=False
                )
                for t in lista:
                    t.cancelado = True
                    t._status_atual = old.status_atual.status
                    t.save()
                    # Transferencia.objects.filter(pk=t.pk).update(cancelado=True)
            # Atribuindo uma data fila atendimento para chamados numa fila de terceiro interno
            # apenas atribui uma data para os chamados que estao associados apenas a terceiro interno
            # não entraram na fila unica nem foram atribuindo a atendente comum do sistema
            if (
                int(self.status_atual.status) == Status.AGUARDANDO_ATENDIMENTO
                and self.data_fila_atendimento is None
            ):
                if self.terceiro_interno.exists() is True:
                    self.data_fila_atendimento = datetime.now()
            if old.servico != self.servico and system is False:
                # Primeiro o chamado fica fora da fila atual - similar ao estado Aberto
                self.fila = None
                self.data_fila_atendimento = None
                # Caso modifique o serviço do chamado entao o chamado irá mudar de fila, indo para o final
                # Verifica se o novo servico possui atendentes aptos a receber o chamado
                if (
                    self.atendentes_aptos().exists() is True
                    and self.verifica_regras_distribuicao() is True
                ):
                    # No metodo atendentes_aptos tambem verifica se solicitante eh servidor ativo e possui lotacao
                    servidor_solicitante = employee_from_user(
                        self.solicitacao.solicitante
                    )
                    localidade_solicitante = (
                        servidor_solicitante.workplace_current.localidade.nome.upper()
                    )
                    # Inicio Gambiarra - Direcionando todos os chamados que não forem de Gurupi para Palmas
                    # if localidade_solicitante != 'GURUPI':
                    if localidade_solicitante not in self.valida_localidade:
                        localidade_solicitante = "PALMAS"
                    # Fim Gambiarra
                    # Entra na Fila - Mudando de Fila
                    self.fila, novo = FilaUnica.objects.get_or_create(
                        servico=self.servico, localidade=localidade_solicitante
                    )
                    self.data_fila_atendimento = datetime.now()
                    # Criando status aguardando atendimento com Observação de transferência de área ou serviço
                    # Status criado a partir de qualquer outro status, para facilitar auditoria
                    # necessario passar system=True para evitar verificação fluxo de status.
                    s = Status(
                        status=Status.AGUARDANDO_ATENDIMENTO,
                        data_inicio=datetime.now(),
                        chamado=self,
                        motivo="Transferência de área ou serviço",
                    )
                    s.save(system=True)
                    super(Chamado, self).save(*args, **kwargs)
                    # Disparar evento distribuir primeiro chamado de cada fila unica para todos servicos
                    FilaUnica.dist_primeiro_chamado_fila_unica()
                    return

        super(Chamado, self).save(*args, **kwargs)

        if insert:
            s = Status(status=Status.ABERTO, data_inicio=datetime.now(), chamado=self)
            s.save()

            if (
                atendentes_aptos.exists() is True
                and self.verifica_regras_distribuicao() is True
            ):
                s = Status(
                    status=Status.AGUARDANDO_ATENDIMENTO,
                    data_inicio=datetime.now(),
                    chamado=self,
                )
                s.save()

                # Disparar evento distribuir primeiro chamado de cada fila unica para todos servicos
                FilaUnica.dist_primeiro_chamado_fila_unica()

        if self.cancelado and self.status_atual.status != Status.CONCLUIDO:
            s = Status(
                status=Status.CONCLUIDO, data_inicio=datetime.now(), chamado=self
            )
            s.save()

    def delete(self, *args, **kwargs):
        log.warn("Não é permitida a exclusão de um chamado")

    def __str__(self):
        return str(self.cache_numero)


class Avaliacao(models.Model):
    class Meta:
        db_table = "siatu_avaliacao"

    SATISFACAO_CHOICES = (
        (1, "Péssimo"),
        (2, "Ruim"),
        (3, "Regular"),
        (4, "Bom"),
        (5, "Ótimo"),
        (6, "Não avaliado"),
    )

    chamado = models.OneToOneField(
        Chamado, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    presteza = models.SmallIntegerField(default=0, choices=SATISFACAO_CHOICES)
    esclarecimento = models.SmallIntegerField(default=0, choices=SATISFACAO_CHOICES)
    tempo = models.SmallIntegerField(default=0, choices=SATISFACAO_CHOICES)
    satisfacao = models.SmallIntegerField(choices=SATISFACAO_CHOICES)
    sugestao = models.CharField(max_length=2000, null=True, blank=True)
    replica = models.CharField(max_length=2000, null=True, blank=True)

    # Chamado marcado como Avaliação Neutra
    avaliacao_neutra = models.BooleanField(default=False)
    # Texto de justificativa da avaliação neutra
    justificativa_netra = models.TextField(null=True, blank=True)
    # quem marcou a avalicao como neutra
    # Parametro "on_delete" adicionado. (Django 2)
    neutralizado_por = models.ForeignKey(
        Servidor, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )

    def neutraliza_avalicao(self, text=""):
        """
        Grava avaliação como neutra.
        """
        user = Servidor.objects.get(user=get_current_user())
        self.neutralizado_por = user
        self.avaliacao_neutra = True
        self.justificativa_netra = text
        self.save()

    def save(self, *args, **kwargs):
        employee = Servidor.objects.get(user=get_current_user())
        if self.replica:
            Notification.notify(
                "siatu-replica",
                self.chamado.solicitacao.solicitante.servidor,
                types=("SYS",),
                **{
                    "chamado": str(self.chamado.cache_numero),
                    "replica": str(self.replica),
                }
            )

        if not self.replica and employee.user != self.chamado.solicitacao.solicitante:
            raise Exception(
                "Somente o solicitante do chamado pode realizar a avaliação do mesmo!"
            )

        if (
            self.replica
            and not self.chamado.atendentes.filter(usuario=employee.user).exists()
        ):
            raise Exception(
                "Você não é atendente deste chamado e não pode realizar a avaliação do mesmo!"
            )

        insert = True if self.pk is None else False

        super(Avaliacao, self).save(*args, **kwargs)
        if insert:
            s = Status(
                status=Status.CONCLUIDO,
                data_inicio=datetime.now(),
                chamado=self.chamado,
            )
            s.save()

    def __str__(self):
        return self.get_satisfacao_display()


class Anexo(models.Model):
    class Meta:
        db_table = "siatu_anexo"

    chamado = models.ForeignKey(
        Chamado, related_name="anexos", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    arquivo = models.OneToOneField(
        Arquivo, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def save(self, *args, **kwargs):
        status = self.chamado.status_atual.status
        if status == Status.CONCLUIDO or status == Status.AGUARDANDO_AVALIACAO:
            log.warn("Operação não permitida - chamado concluído")
            raise Exception("Operação não permitida - chamado concluido")

        return super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        servidor = Servidor.objects.get(user=get_current_user())

        if self.arquivo.user != servidor.user:
            raise Exception("Somente quem criou o arquivo pode excluí-lo")

        if (
            self.chamado.status_atual.status == Status.CONCLUIDO
            or self.chamado.status_atual.status == Status.AGUARDANDO_AVALIACAO
        ):
            log.warn("Operação não permitida - chamado concluído")
            raise Exception("Operação não permitida - chamado concluído")
        return super(self.__class__, self).delete(*args, **kwargs)


class Transferencia(models.Model):
    class Meta:
        db_table = "siatu_transferencia"
        ordering = ("pk",)

    atendente_anterior = models.ManyToManyField(
        Atendente, related_name="transferencias_como_remetente"
    )
    atendente_posterior = models.ManyToManyField(
        Atendente, related_name="transferencias_como_destinatario"
    )
    motivo = models.CharField(max_length=300)
    pedido_por = models.ForeignKey(
        User, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    aceito_por = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    data_pedido = models.DateTimeField()
    data_aceite = models.DateTimeField(null=True, blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    chamado = models.ForeignKey(
        Chamado, related_name="transferencias", on_delete=models.CASCADE
    )
    cancelado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if hasattr(self, "_status_atual"):
            status = self._status_atual
        else:
            status = self.chamado.status_atual.status
        if status == Status.CONCLUIDO or status == Status.AGUARDANDO_AVALIACAO:
            log.warn("Operação não permitida - chamado concluído")
            raise Exception("Operação não permitida - chamado concluido")
        # nao permite aceitar transferencia cancelada
        if (self.cancelado is True) and (self.aceito_por is not None):
            raise Exception("Operação não permitida - transferência encerrada")
        super(self.__class__, self).save(*args, **kwargs)


class Status(models.Model):
    class Meta:
        db_table = "siatu_status"
        ordering = ("data_inicio",)

    ABERTO = 1
    AGUARDANDO_ATENDIMENTO = 2
    EM_ATENDIMENTO = 3
    AGUARDANDO_AVALIACAO = 4
    TRANSFERIDO_ATENDENTE = 5
    TERCEIRIZADA = 6
    GARANTIA = 7
    VIAGEM = 8
    CONCLUIDO = 9
    AGUARDANDO_ENTREGA = 10
    MANUTENCAO = 11
    NAOAVALIADO = 12

    ICONS = {
        ABERTO: {"iconCls": "icon-siatu icon-siatu-aberto", "title": "Aberto"},
        AGUARDANDO_ATENDIMENTO: {
            "iconCls": "icon-siatu icon-siatu-aguardando-atendimento",
            "title": "Aguardando atendimento",
        },
        EM_ATENDIMENTO: {
            "iconCls": "icon-siatu icon-siatu-atendimento",
            "title": "Em atendimento",
        },
        AGUARDANDO_AVALIACAO: {
            "iconCls": "icon-siatu icon-siatu-aguardando-avaliacao",
            "title": "Aguardando avaliação",
        },
        TRANSFERIDO_ATENDENTE: {
            "iconCls": "icon-siatu icon-siatu-transferido-atendente",
            "title": "Transferido para outro atendente",
        },
        TERCEIRIZADA: {
            "iconCls": "icon-siatu icon-siatu-terceirizada",
            "title": "Terceirizada",
        },
        GARANTIA: {"iconCls": "icon-siatu icon-siatu-garantia", "title": "Garantia"},
        VIAGEM: {"iconCls": "icon-siatu icon-siatu-viagem", "title": "Viagem"},
        CONCLUIDO: {"iconCls": "icon-siatu icon-siatu-concluido", "title": "Concluído"},
        AGUARDANDO_ENTREGA: {
            "iconCls": "icon-siatu icon-siatu-entrega",
            "title": "Aguardando entrega",
        },
        MANUTENCAO: {
            "iconCls": "icon-siatu icon-siatu-manutencao",
            "title": "Em manutenção",
        },
        NAOAVALIADO: {
            "iconCls": "icon-siatu icon-siatu-concluido",
            "title": "Não Avaliado",
        },
    }

    STATUS_CHOICES = (
        (ABERTO, "Aberto"),
        (AGUARDANDO_ATENDIMENTO, "Aguardando atendimento"),
        (EM_ATENDIMENTO, "Em atendimento"),
        (AGUARDANDO_AVALIACAO, "Aguardando avaliação"),
        (TRANSFERIDO_ATENDENTE, "Transferido para outro atendente"),
        (TERCEIRIZADA, "Terceirizada"),
        (GARANTIA, "Garantia"),
        (VIAGEM, "Em Viagem"),
        (CONCLUIDO, "Concluído"),
        (AGUARDANDO_ENTREGA, "Aguardando entrega"),
        (MANUTENCAO, "Em manutenção"),
        (NAOAVALIADO, "Não Avaliado"),
    )

    STATUS_WORKFLOW = {
        ABERTO: tuple([AGUARDANDO_ATENDIMENTO]),
        AGUARDANDO_ATENDIMENTO: tuple([TRANSFERIDO_ATENDENTE, EM_ATENDIMENTO, VIAGEM]),
        EM_ATENDIMENTO: tuple(
            [
                GARANTIA,
                TERCEIRIZADA,
                AGUARDANDO_AVALIACAO,
                AGUARDANDO_ENTREGA,
                MANUTENCAO,
                TRANSFERIDO_ATENDENTE,
            ]
        ),
        AGUARDANDO_AVALIACAO: tuple([CONCLUIDO, NAOAVALIADO]),
        TRANSFERIDO_ATENDENTE: tuple([AGUARDANDO_ATENDIMENTO]),
        TERCEIRIZADA: tuple(
            [
                EM_ATENDIMENTO,
                GARANTIA,
                TERCEIRIZADA,
                AGUARDANDO_AVALIACAO,
                TRANSFERIDO_ATENDENTE,
            ]
        ),
        GARANTIA: tuple(
            [
                EM_ATENDIMENTO,
                GARANTIA,
                TERCEIRIZADA,
                AGUARDANDO_AVALIACAO,
                TRANSFERIDO_ATENDENTE,
            ]
        ),
        VIAGEM: tuple(
            [GARANTIA, TERCEIRIZADA, AGUARDANDO_AVALIACAO, TRANSFERIDO_ATENDENTE]
        ),
        AGUARDANDO_ENTREGA: tuple(
            [EM_ATENDIMENTO, AGUARDANDO_AVALIACAO, TRANSFERIDO_ATENDENTE]
        ),
        MANUTENCAO: tuple(
            [
                EM_ATENDIMENTO,
                AGUARDANDO_ENTREGA,
                AGUARDANDO_AVALIACAO,
                TRANSFERIDO_ATENDENTE,
            ]
        ),
        CONCLUIDO: tuple([]),
    }

    status = models.SmallIntegerField(choices=STATUS_CHOICES)
    data_inicio = models.DateTimeField()
    previsao_fim = models.DateField(null=True, blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    chamado = models.ForeignKey(
        Chamado, related_name="historico_status", on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    terceirizada = models.ForeignKey(
        Terceirizada, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    motivo = models.CharField(max_length=300, null=True, blank=True)

    @classmethod
    def get_all_status(self):
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    @property
    def icon(self):

        return self.ICONS.get(
            self.status,
            {
                "iconCls": "icon-siatu icon-siatu-empty",
            },
        )

    def validate_change_state(self):
        workflow = self.STATUS_WORKFLOW.get(self.chamado.status_atual.status, [])
        rel = dict(self.STATUS_CHOICES)
        next_state = int(self.status or 0)

        if next_state not in workflow:
            raise Exception(
                "Impossível mudar o estado de %s para %s"
                % (
                    rel.get(self.chamado.status_atual.status, "Desconhecido"),
                    rel.get(next_state, "Desconhecido"),
                )
            )

    def save(self, *args, **kwargs):
        system = kwargs.get("system", False)
        with transaction.atomic():
            if "system" in kwargs:
                del kwargs["system"]
            if self.chamado.status_atual is not None:
                status = self.chamado.status_atual.status
                if status == Status.CONCLUIDO:
                    log.warn("Operação não permitida - chamado concluído")
                    raise Exception("Operação não permitida - chamado concluido")

            insert = True if self.pk is None else False
            if insert is True:
                if (
                    self.chamado.status_atual is not None
                    and self.chamado.cancelado is False
                    and system is False
                ):
                    self.validate_change_state()
            else:
                old = Status.objects.get(pk=self.pk)
                if old.status != int(self.status):
                    log.warn("Operação não permitida")
                    raise Exception("Operação não permitida")
                if old.terceirizada is not None:
                    self.chamado.terceirizada.remove(old.terceirizada)

            super(Status, self).save(*args, **kwargs)

            if self.terceirizada is not None:
                self.chamado.terceirizada.add(self.terceirizada)
            if insert:
                self.chamado.status_atual = self
                self.chamado.save(system=True)
                if (
                    int(self.status) == self.AGUARDANDO_AVALIACAO
                    or int(self.status) == self.AGUARDANDO_ENTREGA
                    or int(self.status) == self.MANUTENCAO
                ):
                    # Disparar evento distribuir primeiro chamado de cada fila unica para todos servicos
                    FilaUnica.dist_primeiro_chamado_fila_unica()

            if insert and int(self.status) == self.EM_ATENDIMENTO:
                log.info(
                    "Notificando solicitante de chamado em atendimento, status aguardando_avaliacao"
                )
                solicitante = self.chamado.solicitacao.solicitante
                hj = datetime.today()
                Notification.notify(
                    "siatu-atendimento",
                    employee_from_user(solicitante, False),
                    types=("SYS",),
                    **{
                        "chamado": str(self.chamado.cache_numero),
                        "data": hj.strftime("%d/%m/%Y %H:%M:%S"),
                    }
                )

            if insert and int(self.status) == self.AGUARDANDO_AVALIACAO:
                log.info("Enviando email para solicitante, status aguardando_avaliacao")
                try:
                    if self.chamado.cfg_email_solicitante.aguardando_avaliacao:
                        msg = Message.objects.get(mid="siatu-aguardando-avaliacao")
                        solicitante = self.chamado.solicitacao.solicitante
                        Notification.notify(
                            msg,
                            employee_from_user(solicitante, False),
                            chamado=self.chamado.cache_numero,
                        )
                        log.info("Email enviado com sucesso")
                    else:
                        log.info("Envio de email desativado")
                except Exception as e:
                    log.info("Email não enviado")
                    log.exception(e)

            if insert and int(self.status) == self.TRANSFERIDO_ATENDENTE:
                log.info("Enviando email para solicitante, status Transferido")
                try:
                    # Solicitante
                    if self.chamado.cfg_email_solicitante.transferido_atendente:
                        msg = Message.objects.get(mid="siatu-transf-solicitante")
                        solicitante = self.chamado.solicitacao.solicitante
                        Notification.notify(
                            msg,
                            employee_from_user(solicitante, False),
                            chamado=self.chamado.cache_numero,
                        )
                        log.info("Email enviado com sucesso")
                    else:
                        log.info("Envio de email desativado")

                    # Atendente
                    transferencia = self.chamado.transferencias.latest("data_aceite")
                    atendente_user = transferencia.pedido_por
                    # prox_atendente = transferencia.aceito_por
                    if (
                        atendente_user != transferencia.aceito_por
                        and self.chamado.cfg_email_atendente.transferido_atendente
                    ):
                        log.info("Enviando email para atendente, status Transferido")
                        prox_atendente = transferencia.atendente_posterior.exclude(
                            pk__in=[
                                a.pk for a in transferencia.atendente_anterior.all()
                            ]
                        )[0]
                        prox_atendente_username = prox_atendente.usuario.username
                        msg = Message.objects.get(mid="siatu-transf-atendente")
                        Notification.notify(
                            msg,
                            employee_from_user(atendente_user, False),
                            chamado=self.chamado.cache_numero,
                            atendente=prox_atendente_username,
                        )
                        log.info("Email enviado com sucesso")
                    else:
                        log.info(
                            "Envio de email desativado ou transferencia por gerente"
                        )
                except Exception as e:
                    log.info("Email não enviado")
                    log.exception(e)

            if insert and int(self.status) == self.TERCEIRIZADA:
                log.info("Enviando email para solicitante, status Terceirizada")
                try:
                    if self.chamado.cfg_email_solicitante.terceirizada:
                        msg = Message.objects.get(mid="siatu-terceirizada")
                        solicitante = self.chamado.solicitacao.solicitante
                        Notification.notify(
                            msg,
                            employee_from_user(solicitante, False),
                            chamado=self.chamado.cache_numero,
                            terceirizada=self.terceirizada.nome,
                            previsao=DateUtils.date_to_str(self.previsao_fim),
                        )
                        log.info("Email enviado com sucesso")
                    else:
                        log.info("Envio de email desativado")
                except Exception as e:
                    log.info("Email não enviado")
                    log.exception(e)

            if insert and int(self.status) == self.GARANTIA:
                log.info("Enviando email para solicitante, status Garantia")
                try:
                    if self.chamado.cfg_email_solicitante.garantia:
                        msg = Message.objects.get(mid="siatu-garantia")
                        solicitante = self.chamado.solicitacao.solicitante
                        Notification.notify(
                            msg,
                            employee_from_user(solicitante, False),
                            chamado=self.chamado.cache_numero,
                            previsao=DateUtils.date_to_str(self.previsao_fim),
                        )
                        log.info("Email enviado com sucesso")
                    else:
                        log.info("Envio de email desativado")
                except Exception as e:
                    log.info("Email não enviado")
                    log.exception(e)

            if insert and int(self.status) == self.CONCLUIDO:
                log.info("Enviando notificação para atendentes (status CONCLUIDO).")
                try:
                    if (not self.chamado.cancelado) and (
                        self.chamado.cfg_email_atendente.apos_avaliacao
                    ):
                        employees = []
                        for atendente in self.chamado.atendentes.select_related(
                            "usuario__servidor"
                        ):
                            employee = employee_from_user(atendente.usuario)
                            if employee is not None:
                                employees.append(employee)

                        if len(employees) > 0:
                            msg = Message.objects.get(mid="siatu-concluido")
                            Notification.notify_all(
                                msg,
                                employees,
                                chamado=self.chamado.cache_numero,
                                avaliacao=self.chamado.avaliacao.get_satisfacao_display(),
                            )
                            log.info("Notificação ENVIADA com sucesso.")
                        else:
                            log.info(
                                "Notificação NÃO ENVIADA pois não há empregados ativos."
                            )
                    else:
                        log.info(
                            "Envio de notificação desativado ou chamado cancelado."
                        )
                except Exception as e:
                    log.info("Não foi possível enviar notificação para atendentes.")
                    log.exception(e)

            if (
                not insert
                and int(self.status) == self.TERCEIRIZADA
                and self.previsao_fim > old.previsao_fim
            ):
                log.info(
                    "Enviando email para solicitante, status Terceirizada - prazo estendido"
                )
                try:
                    if self.chamado.cfg_email_solicitante.terceirizada:
                        msg = Message.objects.get(mid="siatu-terceirizada-estendida")
                        solicitante = self.chamado.solicitacao.solicitante
                        Notification.notify(
                            msg,
                            employee_from_user(solicitante, False),
                            chamado=self.chamado.cache_numero,
                            previsao=DateUtils.date_to_str(self.previsao_fim),
                        )
                        log.info("Email enviado com sucesso")
                    else:
                        log.info("Envio de email desativado")
                except Exception as e:
                    log.info("Email não enviado")
                    log.exception(e)

            if (
                not insert
                and int(self.status) == self.GARANTIA
                and self.previsao_fim > old.previsao_fim
            ):
                log.info(
                    "Enviando email para solicitante, status Garantia - prazo estendido"
                )
                try:
                    if self.chamado.cfg_email_solicitante.garantia:
                        msg = Message.objects.get(mid="siatu-garantia-estendida")
                        solicitante = self.chamado.solicitacao.solicitante
                        Notification.notify(
                            msg,
                            employee_from_user(solicitante, False),
                            chamado=self.chamado.cache_numero,
                            previsao=DateUtils.date_to_str(self.previsao_fim),
                        )
                        log.info("Email enviado com sucesso")
                    else:
                        log.info("Envio de email desativado")
                except Exception as e:
                    log.info("Email não enviado")
                    log.exception(e)

    def delete(self, *args, **kwargs):
        if self.terceirizada is not None:
            self.chamado.terceirizada.remove(self.terceirizada)
        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        return self.get_status_display()
