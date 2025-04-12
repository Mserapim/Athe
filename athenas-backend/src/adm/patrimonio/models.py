# -*- coding: utf-8 -*-
import locale
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from functools import partial
import os
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum
from django.template import loader
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags

from adm.contabilidade.models import NE as NotaEmpenho
from adm.patrimonio.const import MOVIMENTO_STATUS_PERMISSION, STATE_WORKFLOW
from contrib.daterange import NewDateRange
from contrib.helpers import roundf
from contrib.jasper import Client
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, employee_from_user, getLogger, person_from_user
from edocs.protocolo.models import Attachment, Movimentacao, Protocolo, TipoDocumento
from engine.mq.models import Task
from ged.models import Arquivo
from rh.models import Pessoa, PessoaFisica, Publicacao, Servidor
from standard.models import AuditableMixins, AuditTimestampModel, Choice

log = getLogger()

if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


class Documento(models.Model):
    titulo = models.CharField(max_length=100)
    # Parametro "on_delete" adicionado. (Django 2)
    data = models.ForeignKey(
        Arquivo, related_name="como_documento_contabil", on_delete=models.CASCADE
    )
    criado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("criado", "titulo")


class Sequencia(models.Model):
    titulo = models.CharField(max_length=100, unique=True)
    proximo = models.IntegerField(default=1)

    class Meta:
        ordering = ("titulo", "proximo")

    def get_next(self, register=True):
        value = int(self.proximo)

        if register is True:
            self.proximo += 1
            self.save()

        return value

    def __str__(self):
        return self.titulo


class Conta(models.Model):

    tipo = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "ACCOUNT_TYPE"),
        db_index=True,
        default=1,
        verbose_name="Tipo",
    )
    principal = models.BooleanField(default=False, verbose_name="Principal")
    titulo = models.CharField(max_length=100, verbose_name="Título")
    sequencia = models.ForeignKey(
        Sequencia, related_name="contas", null=True, on_delete=models.PROTECT
    )
    sufix = models.CharField(max_length=10, null=True, blank=True)
    prefix = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        permissions = (("can_change_sequence", "Pode mudar a sequencia"),)
        ordering = ("tipo", "titulo")

    def __str__(self):
        return self.titulo

    def get_next_sequence(self, register=True):
        return (
            None
            if self.sequencia is None
            else "%(prefix)s%(number)s%(sufix)s"
            % {
                "prefix": self.prefix if self.prefix else "",
                "number": self.sequencia.get_next(register=register),
                "sufix": self.sufix if self.sufix else "",
            }
        )

    def _validate(self):
        if self.pk is None and self.principal is True:
            Conta.objects.filter(principal=True, tipo=self.tipo).update(principal=False)
        elif self.pk is not None and self.principal is True:
            Conta.objects.filter(principal=True, tipo=self.tipo).exclude(
                pk=self.pk
            ).update(principal=False)

    def save(self, *args, **kargs):
        self._validate()
        super(Conta, self).save(*args, **kargs)


class ClassificacaoContabil(models.Model):
    title = models.CharField(max_length=60)
    classfication = models.CharField(max_length=20, db_index=True)


class GrupoContabil(models.Model):
    contabil_classification = models.ForeignKey(
        ClassificacaoContabil,
        on_delete=models.CASCADE,
        related_name="groups",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=80)
    cache_number = models.CharField(
        max_length=10, db_index=True, unique=True, blank=True
    )
    consolidacao = models.CharField(max_length=8)
    classificacao = models.CharField(max_length=2)

    def save(self, *args, **kwags):
        self.cache_number = "".join([self.consolidacao, self.classificacao])
        super(GrupoContabil, self).save(*args, **kwags)

    def __str__(self):
        return "%s - %s " % (self.consolidacao, self.classificacao)


class GrupoEspecie(models.Model):
    codigo = models.SmallIntegerField(db_index=True, unique=True)
    titulo = models.CharField(max_length=200)
    grupo_contabil = models.ForeignKey(
        GrupoContabil,
        related_name="grupo_especies",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("codigo", "titulo")

    def save(self, *args, **kwags):
        super(GrupoEspecie, self).save(*args, **kwags)

        for e in self.especies.all():
            e.save()

    def __str__(self):
        return self.titulo


class Especie(models.Model):
    codigo = models.SmallIntegerField(db_index=True, unique=True)
    codigo_cache = models.CharField(db_index=True, null=True, max_length=30, blank=True)
    titulo = models.CharField(max_length=200)
    grupo = models.ForeignKey(
        GrupoEspecie, related_name="especies", on_delete=models.PROTECT
    )
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "SPECIE_STATUS"),
        default=1,
        db_index=True,
    )

    class Meta:
        ordering = ("codigo", "titulo")
        permissions = (("mov_grupoespecie", "Movimentar Grupo Especie"),)

    def __str__(self):
        return " - ".join(
            [
                self.codigo_cache,
                self.titulo,
                self.get_status_display() if self.status == 2 else "",
            ]
        )

    @property
    def icons(self):
        return [self.icon_status()]

    def icon_status(self):
        if int(self.status) == 1:
            return {
                "iconCls": "icon-patrimonio icon-pat-conservacao-novo",
                "title": "Ativo",
            }
        else:
            return {
                "iconCls": "icon-patrimonio icon-pat-conservacao-inservivel",
                "title": "Inativo",
            }

    def save(self, *args, **kargs):
        self.codigo_cache = "{0}.{1}".format(self.grupo.codigo, self.codigo)
        created = self.pk is None
        super(Especie, self).save(*args, **kargs)

        if created or not self.itens_avaliacao.exists():
            base = None
            try:
                tabela = TabelaAvaliacao.objects.get()
                base = ItemAvaliacao.objects.get(grupo=self.grupo, especie=None)
            except ItemAvaliacao.DoesNotExist:
                pass
            finally:
                ItemAvaliacao(
                    tabela=tabela,
                    grupo=self.grupo,
                    especie=self,
                    vida_util=base.vida_util if base else 0,
                    depreciacao=base.depreciacao if base else 0,
                    residual=base.residual if base else 0,
                ).save()


class NotaEntrada(models.Model):
    note_number = models.SmallIntegerField(null=True, blank=True, db_index=True)
    note_year = models.SmallIntegerField(null=True, blank=True, db_index=True)
    formated_number = models.CharField(
        max_length=12, null=True, blank=True, db_index=True
    )
    documentos = models.ManyToManyField(Documento, related_name="documentos_de_entrada")
    fornecedor = models.ForeignKey(
        Pessoa, related_name="movimentos_entrada_patrimonio", on_delete=models.PROTECT
    )
    conta = models.ForeignKey(Conta, related_name="entradas", on_delete=models.PROTECT)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_nota = models.DateTimeField(null=True, blank=True, db_index=True)
    data_compra = models.DateTimeField(null=True, blank=True)
    processo = models.CharField(db_index=True, max_length=20, null=True, blank=True)
    empenho = models.ForeignKey(
        NotaEmpenho,
        related_name="movimentos_entrada_patrimonio",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    execucao_orcamentaria = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "BUDGETARY_EXECUTION"),
        default=1,
        db_index=True,
    )
    state = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "ENTRANCE_NOTE_STATE"),
        default=1,
        db_index=True,
    )
    liquidacao = models.CharField(db_index=True, max_length=15, null=True, blank=True)
    data_liquidacao = models.DateField(null=True, blank=True)
    cache_type = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    tombado = models.DateTimeField(null=True, blank=True, db_index=True)
    # Parametro "on_delete" adicionado. (Django 2)
    tombado_por = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )

    the_type = "nota-entrada"

    class Meta:
        # ordering = ('-data_compra', '-data_nota', '-data_cadastro')
        ordering = ("-note_year", "-note_number")

    @property
    def empenhado(self):
        return self.empenho is not None

    @property
    def liquidado(self):
        return self.data_liquidacao is not None and date.today() >= self.data_liquidacao

    @property
    def icons(self):
        return [
            self.icon_state(),
            self.my_origin.icon_type(),
            # self.icon_liquido()
            self.icon_suspenso(),
        ]

    @property
    def provider_name(self):
        return (
            self.fornecedor.pessoajuridica.razao_social
            if hasattr(self.fornecedor, "pessoajuridica")
            else self.fornecedor.nome
        )

    def icon_liquido(self):
        if self.liquidado:
            return {
                "iconCls": "icon-patrimonio icon-pat-contabilizado",
                "title": "Nota Contabilizada",
            }
        else:
            return {
                "iconCls": "icon-patrimonio icon-pat-nao-contabilizado",
                "title": "Nota não Contabilizada",
            }

    def icon_suspenso(self):
        suspended = self.itens.filter(incorporacoes__suspenso=True)
        not_suspended = self.itens.filter(incorporacoes__suspenso=False)

        if suspended.exists() and not_suspended.exists():
            return {
                "iconCls": "icon-patrimonio icon-pat-cancelado",
                "title": "Nota suspensa parcialmente",
            }
        if suspended.exists() and not not_suspended.exists():
            return {
                "iconCls": "icon-patrimonio icon-pat-cancelado",
                "title": "Nota suspensa completamente",
            }
        else:
            return {"iconCls": "icon-patrimonio icon-pat-empty", "title": ""}

    def icon_state(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-%s"
            % slugify(self.get_state_display()),
            "title": self.get_state_display(),
        }

    def icon_type(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-nota-entrada",
            "title": "Nota de Entrada",
        }

    @property
    def my_origin(self):
        def related_is_subclass(a, b):
            return issubclass(getattr(a, b).__class__, a.__class__)

        def auto_foreign_key(a, b):
            return getattr(a, b).__class__ == a.__class__

        for related_object in [
            f for f in self.__class__._meta.get_fields() if f.is_relation
        ]:
            try:
                related_name = related_object.get_accessor_name()
                if (
                    hasattr(self, related_name) is True
                    and auto_foreign_key(self, related_name) is False
                    and related_is_subclass(self, related_name) is True
                ):
                    return getattr(self, related_name)
            except AttributeError:
                pass
        else:
            return self

    def __str__(self):
        if self.__class__ == self.my_origin.__class__:
            return str(self.fornecedor).upper()
        else:
            return str(self.my_origin)

    def _validade_change_state(self, f, t):
        log.info("mudando de %d para %d" % (f, t))
        workflow = STATE_WORKFLOW.get(f, [])
        rel = dict(Choice.get_choices_for("patrimonio", "ENTRANCE_NOTE_STATE"))

        if t not in workflow:
            raise Exception(
                "Não posso mudar o estado de %s para %s"
                % (rel.get(f, "Desconhecido"), rel.get(t, "Desconhecido"))
            )

    def _do_generate_patrimonio(self):
        try:
            with transaction.atomic():
                for item in self.itens.all():
                    log.info(
                        "Gerando patrimonio para o item %s no valor %0.2f"
                        % (str(item.especie), float(item.valor_unitario or 0))
                    )

                    item.build_incorporacoes()
        except Exception as e:
            log.exception(e)
            raise e

    def delete(self, *args, **kargs):
        if self.state == 2:
            raise Exception("Não posso remover uma nota finalizada.")
        super(NotaEntrada, self).delete(*args, **kargs)

    def next_number(self, year=None):
        if year:
            self.note_year = year

        return (
            int(
                self.__class__.objects.filter(data_cadastro__year=self.note_year)
                .exclude(models.Q(note_year=None) | models.Q(note_number=None))
                .aggregate(total=models.Max("note_number"))
                .get("total")
                or 0
            )
            + 1
        )

    def validate_active_itens(self):
        if self.itens.filter(especie__status=2).exists():
            raise Exception(
                "Não foi possível realizar a operação. Alguns itens da nota estão inativos!"
            )

    def save(self, *args, **kargs):
        old = None

        if not self.note_year or not self.note_number:
            self.note_year = (
                self.data_cadastro.year if self.data_cadastro else datetime.today().year
            )
            self.note_number = self.next_number()
            self.formated_number = "%04d/%d" % (self.note_number, self.note_year)

        if self.pk is not None:
            old = self.__class__.objects.get(pk=self.pk)
            if int(old.state or 0) != int(self.state or 0):
                self._validade_change_state(
                    f=int(old.state or 0), t=int(self.state or 0)
                )

        if (old and old.state == 2) and not getattr(self, "apontado", False):
            raise Exception("Não posso modificar uma nota fechada.")

        if (self.liquidacao not in (None, "") and self.data_liquidacao is None) or (
            self.liquidacao in (None, "") and self.data_liquidacao is not None
        ):
            raise Exception("Verifique as informações de Nota de Lançamento.")

        if int(self.state or 0) == 2 and old.state != 2:
            self.validate_active_itens()
            self._do_generate_patrimonio()
            self.tombado = datetime.now()
            self.tombado_por = get_current_user()

        self.cache_type = self.the_type
        super(NotaEntrada, self).save(*args, **kargs)


class CriticarNotaEntrada(models.Model):
    nota = models.ForeignKey(
        NotaEntrada, related_name="criticas", on_delete=models.PROTECT
    )
    conta = models.ForeignKey(
        Conta, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    por = models.ForeignKey(
        User, related_name="+", blank=True, on_delete=models.PROTECT
    )
    quando = models.DateTimeField(auto_now_add=True, blank=True)
    respondido_por = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    respondido_quando = models.DateTimeField(null=True, blank=True)
    resposta = models.TextField(null=True, blank=True)
    state = models.SmallIntegerField(
        default=1,
        choices=Choice.get_choices_for("patrimonio", "CRITICIZE_ENTRANCE_NOTE_STATE"),
    )
    fornecedor = models.ForeignKey(
        Pessoa, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    data_nota = models.DateField(null=True, blank=True, db_index=True)
    data_compra = models.DateField(null=True, blank=True)
    processo = models.CharField(db_index=True, max_length=20, null=True, blank=True)
    empenho = models.ForeignKey(
        NotaEmpenho, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    execucao_orcamentaria = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "BUDGETARY_EXECUTION"),
        default=1,
        db_index=True,
        null=True,
        blank=True,
    )
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ("-quando", "-respondido_quando")
        permissions = (
            ("entrada_julgar_critica", "Julgar criticas de notas de entrada."),
        )

    def change_state(self, to, justify):
        who = get_current_user()

        workflow = {
            1: {"need": False, "edges": (2, 3)},
            2: {"need": False, "edges": tuple()},
            3: {"need": True, "edges": tuple()},
        }

        state_ref = dict(
            Choice.get_choices_for("patrimonio", "CRITICIZE_ENTRANCE_NOTE_STATE")
        )

        if who.has_perm("patrimonio.entrada_julgar_critica"):
            log.info(
                'Usuário "%s" tem permissão para julgar a critica da nota de entrada.',
                who,
            )
            older = workflow.get(self.state, None)

            if to in older.get("edges", tuple()) or to == self.state:
                log.info(
                    'É possivel mudar do estado "%s" para "%s"',
                    state_ref.get(self.state),
                    state_ref.get(to),
                )

                if workflow.get(to, {}).get("need", False) and (
                    not justify or justify == ""
                ):
                    raise Exception("É necessário fazer uma justificativa.")
                else:
                    self.state = to
                    self.respondido_por = who
                    self.respondido_quando = datetime.now()
                    self.resposta = justify
                    self.save()

            else:
                log.error(
                    'Não é possivel mudar do estado "%s" para "%s"',
                    state_ref.get(self.state),
                    state_ref.get(to),
                )

                raise Exception(
                    'Não é possivel mudar do estado "%s" para "%s"'
                    % (state_ref.get(self.state), state_ref.get(to))
                )
        else:
            log.info(
                'Usuário "%s" não tem permissão para julgar a critica da nota de entrada.',
                who,
            )
            raise Exception("Você não tem permissão para executar este recurso.")

    def delete(self, *args, **kargs):
        if self.state != 1:
            raise Exception("Não posso remover um apontamento com desfecho definido.")
        super(CriticarNotaEntrada, self).delete(*args, **kargs)

    def _do_change(self):
        def nvl(value, default_value):
            return value if value else default_value

        self.nota.conta = nvl(self.conta, self.nota.conta)
        self.nota.fornecedor = nvl(self.fornecedor, self.nota.fornecedor)
        self.nota.data_compra = nvl(self.data_compra, self.nota.data_compra)
        self.nota.data_nota = nvl(self.data_nota, self.nota.data_nota)
        self.nota.processo = nvl(self.processo, self.nota.processo)
        self.nota.empenho = nvl(self.empenho, self.nota.empenho)
        self.nota.execucao_orcamentaria = nvl(
            self.execucao_orcamentaria, self.nota.execucao_orcamentaria
        )
        self.nota.apontado = True
        self.nota.save()

    def save(self, *args, **kargs):
        self.state = int(self.state or 0)

        if self.pk is None:
            self.por = get_current_user()
        elif self.state == 2:
            self._do_change()

        super(CriticarNotaEntrada, self).save(*args, **kargs)


class ItemEntrada(models.Model):
    nota = models.ForeignKey(
        NotaEntrada, related_name="itens", on_delete=models.PROTECT
    )
    especie = models.ForeignKey(Especie, related_name="itens", on_delete=models.PROTECT)
    descricao = models.TextField()
    conservacao = models.IntegerField(
        choices=Choice.get_choices_for("patrimonio", "CONSERVATION"), db_index=True
    )
    valor_unitario = models.DecimalField(max_digits=16, decimal_places=2)
    quantidade = models.IntegerField()
    meses_garantia = models.IntegerField()

    class Meta:
        ordering = ("especie__titulo", "valor_unitario")

    @property
    def locked(self):
        return self.nota.state == 2

    @property
    def icon_estoque(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-estoque-resta",
            "title": "Ainda há unidades deste item não incorporados.",
        }

    @property
    def icon_status(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-status-%s"
            % ("liberado" if not self.locked else "bloqueado"),
            "title": "Liberado" if not self.locked else "Bloqueado",
        }

    @property
    def icon_suspenso(self):
        if (
            self.incorporacoes.filter(suspenso=True).exists()
            and self.incorporacoes.filter(suspenso=False).exists()
        ):
            return {
                "iconCls": "icon-patrimonio icon-pat-cancelado",
                "title": "Item suspenso parcialmente",
            }
        if (
            self.incorporacoes.filter(suspenso=True).exists()
            and not self.incorporacoes.filter(suspenso=False).exists()
        ):
            return {
                "iconCls": "icon-patrimonio icon-pat-cancelado",
                "title": "Item suspenso completamente",
            }
        else:
            return {"iconCls": "icon-patrimonio icon-pat-empty", "title": ""}

    @property
    def icons(self):
        return [
            self.icon_status,
            {
                "iconCls": "icon-patrimonio icon-pat-conservacao-%s"
                % self.get_conservacao_display().lower(),
                "title": self.get_conservacao_display(),
            },
            self.icon_estoque,
            self.icon_suspenso,
        ]

    @property
    def prazo_garantia(self):
        if self.nota.data_nota is None:
            raise Exception(
                "Não posso concluir uma nota de entrada sem a data da nota."
            )
        elif self.meses_garantia > 0:
            return self.nota.data_nota + relativedelta(months=self.meses_garantia)
        else:
            return self.nota.data_nota

    def build_incorporacoes(self):
        log.info("Construindo incorportações para item %s." % self)
        incs = []
        if int(self.quantidade or 0) - self.incorporacoes.count() > 0:
            for x in range(int(self.quantidade or 0) - self.incorporacoes.count()):
                plaqueta = self.nota.conta.get_next_sequence()

                pat = Patrimonio(
                    item_entrada=self,
                    plaqueta=plaqueta,
                    conservacao=self.conservacao,
                    descricao=self.descricao,
                    valor_atual=self.valor_unitario,
                    prazo_garantia=self.prazo_garantia,
                    data_tombo=datetime.now(),
                    valor_base=self.valor_unitario,
                )

                log.debug(vars(pat))
                incs.append(pat)

            Patrimonio.objects.bulk_create(incs)
        else:
            log.info("Sem itens para incorporar.")

    def save(self, *args, **kargs):
        if self.nota.state == 2:
            raise Exception("Não posso modificar os itens de uma nota fechada.")
        super(ItemEntrada, self).save(*args, **kargs)


class Patrimonio(models.Model, AuditableMixins):
    item_entrada = models.ForeignKey(
        ItemEntrada, related_name="incorporacoes", on_delete=models.PROTECT
    )
    plaqueta = models.CharField(db_index=True, max_length=10, null=False, blank=True)
    observacao = models.CharField(max_length=100, null=False, blank=True)
    conservacao = models.IntegerField(
        choices=Choice.get_choices_for("patrimonio", "CONSERVATION"), db_index=True
    )
    utilizacao = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "UTILIZATION"),
        default=1,
        db_index=True,
    )
    descricao = models.TextField()
    valor_atual = models.DecimalField(max_digits=20, decimal_places=6)
    valor_residual = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    valor_base = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    prazo_garantia = models.DateField()
    vida_util = models.DateField(null=True, blank=True)
    localizacao = models.ForeignKey(
        "Localizacao",
        related_name="patrimonios",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    responsavel = models.ForeignKey(
        "rh.Servidor",
        related_name="patrimonios",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    utilizado_por = models.ForeignKey(
        "rh.Servidor",
        related_name="utilizando_patrimonios",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    data_baixa = models.DateField(null=True, blank=True, db_index=True)
    documentos = models.ManyToManyField(
        Documento, related_name="documentos_do_patrimonio"
    )
    data_tombo = models.DateTimeField(auto_now_add=True, db_index=True)
    suspenso = models.BooleanField(default=False)
    suspenso_tipo = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "SUSPENSION_TYPE"), default=1
    )

    AUDITABLE = {
        "fields": [
            "item_entrada",
            "plaqueta",
            "conservacao",
            "utilizacao",
            "descricao",
            "valor_atual",
            "valor_base",
            "prazo_garantia",
            "vida_util",
            "localizacao",
            "responsavel",
            "utilizado_por",
            "data_baixa",
            "data_tombo",
        ]
    }

    class Meta:
        ordering = ("-data_tombo",)
        permissions = (
            ("admin", "Visão administrativa"),
            ("control", "Visão de Controle"),
        )

    def __str__(self):
        return " - ".join([self.plaqueta, self.item_entrada.especie.titulo])

    @property
    def rendered(self):
        tpl = loader.get_template("patrimony.html")
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        try:
            movimentacao = self.movement_items.last() or None
            _identificacao_mov = movimentacao.movimento.numero_cache
            _destino_mov = movimentacao.movimento.destino
            _responsavel_destino_mov = (
                movimentacao.movimento.responsavel_destino.pessoa_fisica.nome
            )
            _data_movimento_mov = movimentacao.movimento.movimentado.strftime(
                "%d/%m/%Y"
            )
        except Exception:
            _identificacao_mov = "-"
            _destino_mov = "-"
            _responsavel_destino_mov = "-"
            _data_movimento_mov = "-"

        return tpl.render(
            {
                "patrimonio": {
                    "plaqueta": self.plaqueta,
                    "especie": self.item_entrada.especie.titulo,
                    "descricao": strip_tags(self.descricao),
                    "localizacao": (
                        self.localizacao.path if self.localizacao else "Sem localização"
                    ),
                    "responsavel": (
                        self.responsavel.pessoa_fisica.nome
                        if self.responsavel
                        else "Sem responsável"
                    ),
                    "utilizado_por": (
                        self.utilizado_por.pessoa_fisica.nome
                        if self.utilizado_por
                        else "Sem utilizador"
                    ),
                    "conservacao": Choice.objects.get(
                        app_label="patrimonio",
                        name="CONSERVATION",
                        value=self.conservacao,
                    ),
                    "prazo_garantia": self.prazo_garantia.strftime("%d/%m/%Y") or "-",
                    "data_tombo": self.data_tombo.strftime("%d/%m/%Y") or "-",
                    "identificacao_mov": _identificacao_mov,
                    "destino_mov": _destino_mov,
                    "responsavel_destino_mov": _responsavel_destino_mov,
                    "data_movimento_mov": _data_movimento_mov,
                    "valor_aquisicao": locale.currency(
                        self.item_entrada.valor_unitario, grouping=True, symbol=None
                    )
                    or 0.00,
                    "total_depreciacao": locale.currency(
                        self.get_total_depreciado(), grouping=True, symbol=None
                    ),
                    "total_reavaliacao": locale.currency(
                        self.get_total_reavaliado(), grouping=True, symbol=None
                    ),
                    "valor_base": locale.currency(
                        self.valor_base, grouping=True, symbol=None
                    ),
                    "valor_atual": locale.currency(
                        self.valor_atual, grouping=True, symbol=None
                    ),
                },
            }
        )

    def change_consevation(self, conservation):
        if self.data_baixa:
            raise Exception(
                "Não posso modificar o estado de um bem que já foi baixado."
            )
        elif get_current_user().has_perm("patrimonio.change_patrimonio"):
            self.conservacao = conservation
            self.save()
        else:
            raise Exception(
                "Você não tem permissão para alterar o estado de conservação dos bens."
            )

    def is_read_only(self, user):
        read_only = True

        if user.is_authenticated:
            if self.responsavel and self.responsavel.user == user:
                read_only = False
            if user.has_perm("patrimonio.admin"):
                read_only = False

        return read_only

    def icon_conservacao(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-conservacao-%s"
            % self.get_conservacao_display().lower(),
            "title": self.get_conservacao_display(),
        }

    def icon_tipo_patirmonio(self):
        tipo = self.item_entrada.nota.conta.get_tipo_display()
        return {
            "iconCls": "icon-patrimonio icon-pat-patrimonio-%s" % tipo.lower(),
            "title": str(self.item_entrada.nota.conta),
        }

    def icon_contabilizado(self):
        def icon_fn(x):
            return (
                "icon-patrimonio icon-pat-contabilizado"
                if x
                else "icon-patrimonio icon-pat-nao-contabilizado"
            )

        def title_fn(x):
            return "Patrimonio contabilizado" if x else "Patrimonio não contabilizado"

        return {
            "iconCls": icon_fn(self.item_entrada.nota.liquidado),
            "title": title_fn(self.item_entrada.nota.liquidado),
        }

    def icon_movimentando(self):

        if self.movement_items.filter(movimento__status__in=(1, 2, 3, 4)).exists():
            return {
                "iconCls": "icon-patrimonio icon-pat-em-movimento",
                "title": "Item em movimentação.",
            }
        elif self.baixas.filter(nota__state=1).exists():
            return {
                "iconCls": "icon-patrimonio icon-pat-nota-baixa",
                "title": "Item em baixa.",
            }
        else:
            return {"iconCls": "icon-patrimonio icon-pat-empty", "title": "nada ainda."}

    def icon_suspenso(self):
        if self.suspenso:
            return {
                "iconCls": "icon-patrimonio icon-pat-cancelado",
                "title": self.get_suspenso_tipo_display(),
            }
        else:
            return {}

    def icon_principal(self):
        if self.item_entrada.nota.conta.principal:
            return {
                "iconCls": "icon-patrimonio icon-pat-principal",
                "title": "Principal",
            }
        else:
            return {}

    @property
    def icons(self):
        return [
            self.icon_tipo_patirmonio(),
            self.icon_principal(),
            self.icon_conservacao(),
            self.icon_suspenso(),
            self.icon_movimentando(),
        ]

    @property
    def downloaded(self):
        return "Baixado" if self.data_baixa else "Ativo"

    def get_total_depreciado(self):
        _reversao = (
            self.avaliacoes.filter(avaliacao__tipo=4)
            .aggregate(Sum("depreciacao"))
            .get("depreciacao__sum")
            or 0
        )
        _depreciacao = (
            self.avaliacoes.filter(avaliacao__tipo__in=[1, 2], discarded=False)
            .aggregate(Sum("depreciacao"))
            .get("depreciacao__sum")
            or 0
        )
        _total_depreciado = Decimal(_depreciacao) + Decimal(_reversao)

        return _total_depreciado

    def get_total_reavaliado(self):
        _depreciacao = (
            self.avaliacoes.filter(avaliacao__tipo=3, discarded=False)
            .aggregate(Sum("depreciacao"))
            .get("depreciacao__sum")
            or 0
        )
        return _depreciacao

    @property
    def is_written_off(self):
        """Já foi dado baixa neste patrimônio?"""

        return self.baixas.filter(nota__state=NotaBaixa.Status.CLOSED).exists()

    @property
    def is_being_moved(self):
        """Este patrimônio está em processo de movimentação?"""

        return self.movement_items.exclude(
            movimento__status__in=(
                Movimento.Status.CANCELED,
                Movimento.Status.AUTHORIZED,
            )
        ).exists()


class PatrimonioHistorico(models.Model):
    patrimonio = models.ForeignKey(
        Patrimonio, related_name="historico", on_delete=models.PROTECT
    )
    conservacao = models.IntegerField(
        choices=Choice.get_choices_for("patrimonio", "CONSERVATION"),
        null=True,
        db_index=True,
    )
    utilizacao = models.SmallIntegerField(null=True)
    valor_atual = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    valor_residual = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    valor_base = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    prazo_garantia = models.DateField(null=True)
    vida_util = models.DateField(null=True)
    localizacao = models.ForeignKey(
        "Localizacao", related_name="+", null=True, on_delete=models.PROTECT
    )
    responsavel = models.ForeignKey(
        Servidor, related_name="+", null=True, on_delete=models.PROTECT
    )
    data_baixa = models.DateField(null=True)
    data_tombo = models.DateField(null=True)
    utilizado_por = models.ForeignKey(
        Servidor, related_name="+", null=True, on_delete=models.PROTECT
    )
    who = models.ForeignKey(User, related_name="+", on_delete=models.PROTECT)
    when = models.DateTimeField(auto_now_add=True)
    suspenso = models.BooleanField(null=True, blank=True)
    suspenso_tipo = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "SUSPENSION_TYPE"), default=1
    )


class NotaFiscal(NotaEntrada):
    numero = models.CharField(db_index=True, max_length=100)

    def __str__(self):
        if self.__class__ == self.my_origin.__class__:
            return str(self.fornecedor).upper()
        else:
            return str(self.my_origin)

    def icon_type(self):
        if self.my_origin.__class__ == self.__class__:
            return {
                "iconCls": "icon-patrimonio icon-pat-nota-fiscal",
                "title": "Nota de Fiscal",
            }
        else:
            return self.my_origin.icon_type()

    @property
    def the_type(self):
        if self.my_origin.__class__ == self.__class__:
            return "nota-fiscal"
        else:
            return self.my_origin.the_type

    @property
    def my_origin(self):
        for related_object in [
            f for f in self.__class__._meta.get_fields() if f.is_relation
        ]:
            try:
                related_name = related_object.get_accessor_name()
                if (
                    hasattr(self, related_name) is True
                    and getattr(self, related_name).__class__ != self.__class__
                    and issubclass(
                        getattr(self, related_name).__class__, self.__class__
                    )
                ):
                    return getattr(self, related_name)
            except AttributeError:
                pass
        else:
            return self


class NotaConvenio(NotaFiscal):
    conveniada = models.ForeignKey(
        Pessoa, related_name="convenios", on_delete=models.PROTECT
    )
    codigo_convenio = models.CharField(db_index=True, max_length=100)
    data_convenio = models.DateField()
    data_fim_convenio = models.DateField()

    the_type = "nota-convenio"

    def icon_type(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-nota-fiscal-convenio",
            "title": "Nota de Convenio",
        }

    def __str__(self):
        return "%s com %s" % (
            str(self.conveniada).upper(),
            str(self.fornecedor).upper(),
        )


class NotaDoacao(NotaEntrada):
    the_type = "nota-doacao"

    def icon_type(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-nota-doacao",
            "title": "Nota de Doação",
        }

    def save(self, *args, **kargs):
        self.execucao_orcamentaria = 3
        super(NotaDoacao, self).save(*args, **kargs)


class Localizacao(models.Model):
    titulo = models.CharField(max_length=150)
    dentro_de = models.ForeignKey(
        "self",
        related_name="sub_espacos",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    endereco = models.TextField(blank=True, null=True)
    lotacao_relacionada = models.ForeignKey(
        "rh.Lotacao",
        related_name="localizacoes_patrimoniais",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    ativo = models.BooleanField(default=True)
    folder_index = models.CharField(max_length=45, db_index=True, blank=True)
    height = models.SmallIntegerField(default=0)
    path_cache = models.CharField(max_length=300, null=True, blank=True, db_index=True)

    class Meta:
        ordering = ("titulo",)

    @property
    def leaf(self):
        return not self.sub_espacos.exists()

    def calculate_height(self):
        if self.dentro_de is None:
            return 0
        else:
            return 1 + self.dentro_de.calculate_height()

    @property
    def path(self):
        if self.dentro_de is None:
            return self.titulo
        else:
            return ", ".join([self.titulo, self.dentro_de.path])

    def _folder_index(self):
        if self.dentro_de is None:
            return ".%d" % self.pk
        else:
            return "%s.%d" % (self.dentro_de._folder_index(), self.pk)

    def __str__(self):
        return self.titulo

    def save(self, *args, **kargs):
        if (
            self.lotacao_relacionada is None
            and self.dentro_de is not None
            and self.dentro_de.lotacao_relacionada is not None
        ):
            self.lotacao_relacionada = self.dentro_de.lotacao_relacionada

        self.height = self.calculate_height()
        self.path_cache = self.path
        super(Localizacao, self).save(*args, **kargs)
        Localizacao.objects.filter(pk=self.pk).update(
            folder_index=self._folder_index(), path_cache=self.path
        )


class Movimento(models.Model):
    documentos = models.ManyToManyField(
        Documento, related_name="documentos_de_movimentacao"
    )
    numero = models.SmallIntegerField(blank=True)
    ano = models.SmallIntegerField(blank=True)
    movimentado_por = models.ForeignKey(
        User, related_name="movimentos", blank=True, on_delete=models.PROTECT
    )
    movimentado = models.DateTimeField(null=True, blank=True)
    recebido_por = models.ForeignKey(
        User,
        related_name="recebimentos",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    recebido = models.DateTimeField(null=True, blank=True)
    validado_por = models.ForeignKey(
        User, related_name="validacoes", null=True, blank=True, on_delete=models.PROTECT
    )
    validado = models.DateTimeField(null=True, blank=True)
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "MOVEMENT_STATUS"),
        default=1,
        db_index=True,
    )
    origem = models.ForeignKey(
        Localizacao,
        related_name="como_origem_em_movimentos",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    destino = models.ForeignKey(
        Localizacao,
        related_name="como_destino_em_movimentos",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    responsavel_origem = models.ForeignKey(
        Servidor, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    responsavel_destino = models.ForeignKey(
        Servidor, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    itens = models.ManyToManyField(
        Patrimonio, related_name="movimentacoes", through="patrimonio.MovimentoItem"
    )
    numero_cache = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ("-ano", "-numero")
        permissions = (
            ("admin_movimento", "Visualização administrativa."),
            ("auth_movimento_view", "Visualização de pendentes de autorização."),
            ("validate_movimento", "Valida movimentações."),
            ("authorize_has_pgj", "Autoriza como Procurador Geral."),
            ("authorize_has_cgpgj", "Autoriza como Chefe de Gabinete."),
            ("authorize_has_dg", "Autoriza como Diretor Geral."),
        )

    class Status:
        OPENED = 1
        AWAITING_TO_BE_RECEIVED = 2
        RECEIVED = 3
        VIEWED = 4
        CANCELED = 5
        AUTHORIZED = 6

    def __str__(self):
        return " - ".join([self.id_number, self.get_status_display()])

    @property
    def id_number(self):
        return "%05d/%04d" % (int(self.numero or 0), int(self.ano or 0))

    def _icon_status(self):
        translate = {
            1: {
                "iconCls": "icon-patrimonio icon-pat-aberto",
                "title": "Movimento em aberto",
            },
            2: {
                "iconCls": "icon-patrimonio icon-pat-aguardando-recebimento",
                "title": "Movimento aguardando o recebimento",
            },
            3: {
                "iconCls": "icon-patrimonio icon-pat-concluido",
                "title": "Movimento finalizado ou concluido",
            },
            4: {
                "iconCls": "icon-patrimonio icon-pat-ciencia",
                "title": "Ciente do Patrimonio",
            },
            5: {
                "iconCls": "icon-patrimonio icon-pat-cancelado",
                "title": "Movimento cancelado",
            },
            6: {
                "iconCls": "icon-patrimonio icon-pat-autorizado",
                "title": "Movimento autorizado pela chefia superior",
            },
        }

        return translate.get(
            int(self.status or 0),
            {
                "iconCls": "icon-patrimonio icon-pat-bug",
                "title": "Movimento desconhecido",
            },
        )

    def _icon_empty(self):
        return {"iconCls": "icon-patrimonio icon-pat-empty"}

    def _icon_mudanca_destino(self):
        if self.destino is not None:
            return {
                "iconCls": "icon-patrimonio icon-pat-mudar-localizacao",
                "title": "Houve mudança de localização",
            }
        else:
            return self._icon_empty()

    def _icon_mudanca_responsavel(self):
        if self.responsavel_destino is not None:
            return {
                "iconCls": "icon-patrimonio icon-pat-mudar-responsavel",
                "title": "Houve mudança de responsável",
            }
        else:
            return self._icon_empty()

    @property
    def icons(self):
        return [
            self._icon_status(),
            self._icon_mudanca_destino(),
            self._icon_mudanca_responsavel(),
        ]

    @classmethod
    def next_numero(cls):
        now = datetime.now()
        query = (
            cls.objects.filter(ano=now.year)
            .order_by("numero")
            .aggregate(maximo=models.Max("numero"))
        )
        numero = int(query.get("maximo") or 0)

        return numero + 1, now.year

    def _validate_permission_over_localizacao(self):
        servidor = employee_from_user(get_current_user())
        """
        Modificado para ficar de acordo com Art. 47 do Ato 0002/2014 da PGJ
        """
        flag = self.responsavel_destino == servidor

        log.debug([flag, get_current_user().has_perm("patrimonio.admin_movimento")])

        if not flag and not get_current_user().has_perm("patrimonio.admin_movimento"):
            raise Exception(
                "Você não tem permissão para movimentar os bens desta localização."
            )

    def who_is(self, user=None):
        user = user if user is not None else get_current_user()
        servidor = self._user_to_servidor(user)

        return (
            self._who_is_origem(user, servidor)
            + self._who_is_destino(user, servidor)
            + self._who_is_admin(user)
            + self._who_is_dg(user)
            + self._who_is_cgpgj(user)
            + self._who_is_pgj(user)
        )

    def _user_to_servidor(self, user):
        if user.servidor and user.servidor.ativo:
            return user.servidor
        else:
            return None

    def _is_origem_for_user(self, user):
        return user == self.movimentado_por

    def _is_origem_for_servidor(self, servidor):
        return servidor and self.origem in servidor.responsavel_por.all()

    def _is_destino_for_servidor(self, servidor):
        if servidor and servidor in servidor.responsavel_por.all():
            return True
        elif servidor == self.responsavel_destino:
            return True
        elif not self.responsavel_destino and (
            servidor.ativo and servidor == self.movimentado_por.servidor
        ):
            return True
        else:
            return False

    def _is_admin_for_user(self, user):
        return user.has_perm("patrimonio.admin_movimento") or user.has_perm(
            "patrimonio.validate_movimento"
        )

    def _is_diretor_geral_for_user(self, user):
        return user.has_perm("patrimonio.authorize_has_dg")

    def _is_chefe_gabinete_for_user(self, user):
        return user.has_perm("patrimonio.authorize_has_cgpgj")

    def _is_pgj_for_user(self, user):
        return user.has_perm("patrimonio.authorize_has_pgj")

    def _who_is_origem(self, user, servidor):
        rst = []

        self._is_origem_for_user(user) and rst.append("ORIGEM")
        "ORIGEM" not in rst and self._is_origem_for_servidor(servidor) and rst.append(
            "ORIGEM"
        )

        return rst

    def _who_is_destino(self, user, servidor):
        rst = []

        self._is_destino_for_servidor(servidor) and rst.append("DESTINO")

        return rst

    def _who_is_admin(self, user):
        return ["ADMIN"] if self._is_admin_for_user(user) else []

    def _who_is_dg(self, user):
        return ["HAS_DG"] if self._is_diretor_geral_for_user(user) else []

    def _who_is_cgpgj(self, user):
        return ["HAS_CGPGJ"] if self._is_chefe_gabinete_for_user(user) else []

    def _who_is_pgj(self, user):
        return ["HAS_PGJ"] if self._is_pgj_for_user(user) else []

    def _validate_workflow(self, older):
        self.status = int(self.status or 0)
        wf = {
            1: tuple([2, 5, [3, lambda m: m.responsavel_destino in (None, "")]]),
            2: tuple([1, 3]),
            3: tuple([4]),
            4: tuple([6]),
            5: tuple([1]),
            6: tuple([]),
        }

        if (self.pk and self.status not in (1, 5)) and not self.itens.exists():
            log.debug([self.status, type(self.status)])
            raise Exception(
                "A movimentação deve ter pelo menos um item para poder continuar."
            )

        if older is None and self.status != 1:
            raise Exception("Só posso criar uma nova movimentação com estado aberto.")
        elif (
            older is not None
            and older.status != self.status
            and self.status not in wf.get(older.status)
        ):
            dest = [i for i in wf.get(older.status) if isinstance(i, (tuple, list))]
            flag = False

            log.debug([self.status, older.status])

            for status, fn in dest:
                if status == self.status:
                    flag = fn(self)
                if flag is True:
                    break

            if self.status == 5 and get_current_user() != self.movimentado_por:
                raise Exception(
                    "Só quem pode cancelar uma movimentação é quem a criou."
                )

            if flag is False:
                raise Exception(
                    'Não é possivel mudar do estado "%(from)s" para o estado "%(to)s".'
                    % {
                        "from": older.get_status_display(),
                        "to": self.get_status_display(),
                    }
                )

        perms = MOVIMENTO_STATUS_PERMISSION.get(self.status)
        whos = self.who_is()

        if True not in [me in perms for me in whos]:
            raise Exception(
                "Você não tem permissão para executar esta mudança de estado."
            )
        else:
            if older is not None and older.status != self.status:
                if self.status == 2:
                    """Aguardando recebimento"""
                    self.movimentado_por = (
                        get_current_user()
                        if self.movimentado_por is None
                        else self.movimentado_por
                    )
                    self.movimentado = (
                        datetime.now() if self.movimentado is None else self.movimentado
                    )

                    self.recebido = self.recebido_por = None
                    self.validado = self.validado_por = None
                elif self.status == 3:
                    """Recebido"""
                    self.recebido_por = (
                        get_current_user()
                        if self.recebido_por is None
                        else self.recebido_por
                    )
                    self.recebido = (
                        datetime.now() if self.recebido is None else self.recebido
                    )

                    self.validado = self.validado_por = None
                elif self.status == 4:
                    """Ciência"""
                    self.validado_por = (
                        get_current_user()
                        if self.validado_por is None
                        else self.validado_por
                    )
                    self.validado = (
                        datetime.now() if self.validado is None else self.validado
                    )
                elif self.status == 6:
                    """Autorizado"""
                    try:
                        with transaction.atomic():
                            for patrimonio in self.itens.all():
                                if self.destino is not None:
                                    patrimonio.localizacao = self.destino
                                if self.responsavel_destino is not None:
                                    patrimonio.responsavel = self.responsavel_destino
                                patrimonio.save()
                    except Exception as e:
                        log.exception(e)
                        raise e

    def _validate_can_be_changed(self, older):
        if older is not None:
            if (
                older.status > 2
                and self.responsavel_destino != older.responsavel_destino
            ):
                raise Exception(
                    "Não posso modificar o responsável pelo recebimento dos bens neste momento"
                )
            elif older.status > 2 and self.origem != older.origem:
                raise Exception("Não posso modificar a origem dos bens neste momento")
            elif older.status > 2 and self.destino != older.destino:
                raise Exception("Não posso modificar o destino dos bens neste momento")

    def validate_changes(self):
        old = None
        if self.pk is not None:
            old = Movimento.objects.get(pk=self.pk)
            log.info("Modificando movimentação de bens.")
        else:
            log.info("Criando movimentação de bens.")

        if self.origem is not None and int(self.status or 0) in (1, 2, 3):
            self._validate_permission_over_localizacao()

        self._validate_workflow(old)
        self._validate_can_be_changed(old)

    def delete(self, *args, **kargs):
        self.logs.add(
            MovimentoLogStatus(
                comentario="Cancelado pelo usuário através do comando remover.",
                status=5,
            ),
            bulk=False,
        )

    def authorize(self):
        user = get_current_user()

        log.debug("Movimento: %s", self)
        whos = self.who_is()

        if "HAS_PGJ" in whos:
            self.autorizacoes.add(MovimentoAssinatura(quem=user, score=10), bulk=False)
        else:
            flag = False

            if "HAS_DG" in whos:
                flag = True
                self.autorizacoes.add(
                    MovimentoAssinatura(quem=user, score=9), bulk=False
                )

            if flag is False:
                raise Exception("Você não tem permissão para autorizar movimentações.")

    def save(self, *args, **kargs):
        if self.pk is None:
            if self.numero is None or self.ano is None:
                self.numero, self.ano = self.next_numero()
                self.movimentado_por = get_current_user()

        self.validate_changes()
        self.numero_cache = self.id_number

        if not self.responsavel_destino:
            if self.destino and self.destino.lotacao_relacionada:
                self.responsavel_destino = self.destino.lotacao_relacionada.responsavel
            else:
                raise Exception(
                    "Não foi possivel determinar a mudança que a movimentação irá realizar."
                )

        if self.destino and not self.destino.ativo:
            raise Exception(
                "O destino do movimento não está apto a receber itens patrimoniais!"
            )

        super(Movimento, self).save(*args, **kargs)


class MovimentoAssinatura(models.Model):
    movimento = models.ForeignKey(
        Movimento, related_name="autorizacoes", on_delete=models.PROTECT
    )
    quem = models.ForeignKey(User, related_name="+", on_delete=models.PROTECT)
    quando = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(
        choices=Choice.get_choices_for("patrimonio", "MOVEMENT_SIGNATURE_SCORE")
    )

    class Meta:
        unique_together = ("movimento", "score")

    def validate_can_authorize(self):
        self.score = int(self.score or 0)
        whos = self.movimento.who_is(self.quem)

        if self.score == 10 and "HAS_PGJ" not in whos:
            raise Exception("Esta autorização requer permissão de Procurador Geral")
        elif self.score == 9 and "HAS_DG" not in whos:
            raise Exception("Esta autorização requer permissão de Diretor Geral")

    def dispatch_authorization(self):
        completo = (
            self.movimento.autorizacoes.all()
            .values("movimento_id")
            .annotate(total=models.Sum("score"))
            .filter(total__gte=8)
        )

        log.debug(completo)
        log.debug(
            self.movimento.autorizacoes.all()
            .values("movimento_id")
            .annotate(total=models.Sum("score"))
        )

        if completo.exists():
            log.info("Esta movimentação foi completamente autorizada.")
            self.movimento.status = 6
            self.movimento.save()
        else:
            log.info("Esta movimentação ainda não foi completamente autorizada.")

    def save(self, *args, **kargs):
        self.validate_can_authorize()
        super(MovimentoAssinatura, self).save(*args, **kargs)
        self.dispatch_authorization()


class MovimentoItem(models.Model):
    patrimonio = models.ForeignKey(
        Patrimonio, related_name="movement_items", on_delete=models.PROTECT
    )
    movimento = models.ForeignKey(Movimento, related_name="+", on_delete=models.PROTECT)

    @property
    def icons(self):
        return [self.movimento._icon_status(), self.patrimonio.icon_conservacao()]

    def validate_create(self):
        if self.movimento.status not in (1,):
            raise Exception(
                "Não posso adicionar mais nenhum item neste estado da movimentação."
            )

        if self.patrimonio.movement_items.exclude(
            movimento__status__in=(5, 6)
        ).exists():
            raise Exception("Este item já esta em uma movimentação em processamento.")
        elif self.patrimonio.baixas.filter(nota__state=2).exists():
            raise Exception("Este item já foi baixado.")
        elif self.patrimonio.baixas.filter(nota__state=1).exists():
            raise Exception("Este item encontra-se em um processo de baixa.")

    def validate_delete(self):
        if self.movimento.status not in (1,):
            raise Exception(
                "Não posso remover mais nenhum item neste estado da movimentação."
            )

    def delete(self, *args, **kargs):
        log.info("Deletando item da movimentação.")
        self.validate_delete()
        super(MovimentoItem, self).delete(*args, **kargs)

    def save(self, *args, **kargs):
        log.info("Adicionando item da movimentação.")
        self.pk is None and self.validate_create()

        super(MovimentoItem, self).save(*args, **kargs)


class MovimentoLogStatus(models.Model):
    movimento = models.ForeignKey(
        Movimento, related_name="logs", on_delete=models.PROTECT
    )
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "MOVEMENT_STATUS"), db_index=True
    )
    atribuido_por = models.ForeignKey(
        User, related_name="+", blank=True, on_delete=models.PROTECT
    )
    atribuido = models.DateTimeField(auto_now_add=True, blank=True)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ("-atribuido",)

    def save(self, *args, **kargs):
        self.atribuido_por = get_current_user()
        self.movimento.status = self.status
        self.movimento.save()

        super(MovimentoLogStatus, self).save(*args, **kargs)

    @property
    def icons(self):
        translate = {
            1: {
                "iconCls": "icon-patrimonio icon-pat-aberto",
                "title": "Movimento em aberto",
            },
            2: {
                "iconCls": "icon-patrimonio icon-pat-aguardando-recebimento",
                "title": "Movimento aguardando o recebimento",
            },
            3: {
                "iconCls": "icon-patrimonio icon-pat-concluido",
                "title": "Movimento finalizado ou concluido",
            },
            4: {
                "iconCls": "icon-patrimonio icon-pat-ciencia",
                "title": "Ciente do Patrimonio",
            },
            5: {
                "iconCls": "icon-patrimonio icon-pat-cancelado",
                "title": "Movimento cancelado",
            },
        }

        return [
            translate.get(
                int(self.status or 0),
                {
                    "iconCls": "icon-patrimonio icon-pat-bug",
                    "title": "Movimento desconhecido",
                },
            )
        ]


class PreBaixa(models.Model):
    portaria_commissao = models.ForeignKey(Publicacao, on_delete=models.PROTECT)
    memorando = models.CharField(max_length=100)


class NotaBaixa(models.Model):
    pre_baixa = models.ForeignKey(
        PreBaixa,
        related_name="notas_baixa",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    conta = models.ForeignKey(Conta, related_name="baixas", on_delete=models.PROTECT)
    numero = models.SmallIntegerField(blank=True)
    ano = models.SmallIntegerField(blank=True)
    cache_numero = models.CharField(db_index=True, max_length=10, blank=True)
    liquidacao = models.CharField(max_length=20, blank=True)
    data_liquidacao = models.DateField(null=True, blank=True)
    processo = models.CharField(max_length=40)
    documento = models.CharField(max_length=50)
    data_documento = models.DateField(null=True)
    data_baixa = models.DateField(null=True, blank=True)
    data_cadastro = models.DateField(auto_now_add=True)
    state = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "WRITEOFF_STATE"), default=1
    )
    cache_type = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    subtype = models.SmallIntegerField(
        verbose_name="Subtipo",
        choices=Choice.get_choices_for("patrimonio", "WRITEOFF_SUBTYPES"),
        null=True,
        blank=True,
    )

    the_type = "nota-baixa"

    class Meta:
        ordering = ("-ano", "-numero")

    class Status:
        OPENED = 1
        CLOSED = 2
        CANCELED = 3

    @property
    def allow_subtype_blank(self):
        return True

    def import_from_inputnote(self, inputnote):
        for p in Patrimonio.objects.filter(item_entrada__nota=inputnote):
            self.itens.add(
                BaixaItem(
                    patrimonio=p, valor_atual=p.valor_atual, valor_baixa=p.valor_atual
                ),
                bulk=False,
            )

    def icon_type(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-%s" % self.cache_type,
            "title": self.the_type,
        }

    @property
    def icons(self):
        return [self.my_origin.icon_type(), self.icon_state(), self.icon_liquido()]

    def icon_liquido(self):
        if self.liquidado:
            return {
                "iconCls": "icon-patrimonio icon-pat-contabilizado",
                "title": "Baixa Contabilizada",
            }
        else:
            return {
                "iconCls": "icon-patrimonio icon-pat-nao-contabilizado",
                "title": "Baixa não Contabilizada",
            }

    def icon_state(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-%s"
            % slugify(self.get_state_display()),
            "title": self.get_state_display(),
        }

    @property
    def liquidado(self):
        return self.data_liquidacao is not None and date.today() >= self.data_liquidacao

    @property
    def my_origin(self):
        def related_is_subclass(a, b):
            return issubclass(getattr(a, b).__class__, a.__class__)

        def auto_foreign_key(a, b):
            return getattr(a, b).__class__ == a.__class__

        for related_object in [
            f for f in self.__class__._meta.get_fields() if f.is_relation
        ]:
            try:
                related_name = related_object.get_accessor_name()
                if (
                    hasattr(self, related_name) is True
                    and auto_foreign_key(self, related_name) is False
                    and related_is_subclass(self, related_name) is True
                ):
                    return getattr(self, related_name)
            except AttributeError:
                pass
        else:
            return self

    @classmethod
    def next_numero(cls):
        now = datetime.now()
        query = (
            NotaBaixa.objects.filter(ano=now.year)
            .order_by("numero")
            .aggregate(maximo=models.Max("numero"))
        )
        numero = int(query.get("maximo") or 0)

        return numero + 1, now.year

    def _validade_change_state(self, f, t):
        log.info("mudando de %d para %d" % (f, t))
        workflow = STATE_WORKFLOW.get(f, [])
        rel = dict(Choice.get_choices_for("patrimonio", "WRITEOFF_STATE"))

        if t not in workflow:
            raise Exception(
                "Não posso mudar o estado de %s para %s"
                % (rel.get(f, "Desconhecido"), rel.get(t, "Desconhecido"))
            )

    def delete(self, *args, **kargs):
        if self.is_closed:
            raise Exception("Não posso remover uma nota finalizada.")
        self.state = self.Status.CANCELED
        self.save()

    def do(self):
        Patrimonio.objects.filter(baixas__nota=self).update(data_baixa=datetime.now())

    def _perform_writeoff(self):
        try:
            with transaction.atomic():
                self.my_origin.do()
                self.data_baixa = date.today()
        except Exception as e:
            log.exception(e)
            raise e

    def _validate_writeoff(self):
        """
        Foi removida a regra de negocio uma vez que não é mais necessária a nota de liquidação.
        Isto foi decidido junto com:
         - Controladoria Interna
         - Contabilidade (Financeiro)
         - Área de Patrimonio
        """

    def validate_add_item(self, item):
        if self.conta != item.patrimonio.item_entrada.nota.conta:
            raise Exception(
                "O item adicionado não pertence a conta de origem dos bens."
            )

    def _format_cache_number(self):
        if self.pk is None:
            self.numero, self.ano = self.next_numero()
            self.cache_numero = "%03d/%d" % (self.numero, self.ano)

    def _validate_subtype(self):
        if not self.subtype and not self.allow_subtype_blank:
            raise Exception("Favor, preencher o subtipo da baixa")

        if self.subtype == 1000:
            raise Exception("Não é permitido utilizar o subtipo 'Não informado'")

    def _validate_state(self):
        self.state = int(self.state or 0)

        if self.pk is not None:
            old = self.__class__.objects.get(pk=self.pk)

            if old.is_closed:
                raise Exception("Não é possível alterar uma Nota Fechada.")

            if old.state != self.state:
                self._validade_change_state(
                    f=int(old.state or 0), t=int(self.state or 0)
                )
                if self.is_closed:
                    self._validate_writeoff()
                    self._perform_writeoff()

    def _validate_nota_lancamento(self):
        if (self.liquidacao not in (None, "") and self.data_liquidacao is None) or (
            self.liquidacao in (None, "") and self.data_liquidacao is not None
        ):
            raise Exception("Verifique as informações de Nota de Lançamento.")

    def save(self, *args, **kargs):
        self._validate_subtype()
        self._validate_nota_lancamento()
        self._validate_state()
        self._format_cache_number()
        self.cache_type = self.my_origin.the_type
        super(NotaBaixa, self).save(*args, **kargs)

    def __str__(self):
        return "Baixa Generica"

    @property
    def is_opened(self):
        return self.state == self.Status.OPENED

    @property
    def is_closed(self):
        return self.state == self.Status.CLOSED

    @property
    def is_canceled(self):
        return self.state == self.Status.CANCELED


class BaixaItem(models.Model):
    nota = models.ForeignKey(NotaBaixa, related_name="itens", on_delete=models.PROTECT)
    patrimonio = models.ForeignKey(
        Patrimonio, related_name="baixas", on_delete=models.PROTECT
    )
    valor_atual = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    valor_baixa = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    valor_avaliacao = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    observacao = models.TextField(default="", blank=True)

    def save(self, *args, **kargs):
        self.validate_save()
        self.valor_baixa = float(self.patrimonio.valor_atual or 0)
        self.valor_avaliacao = float(self.valor_baixa or 0) - float(
            self.patrimonio.valor_atual or 0
        )
        super(BaixaItem, self).save(*args, **kargs)

    def delete(self, *args, **kargs):
        self.validate_delete()
        super(BaixaItem, self).delete(*args, **kargs)

    def is_already_in_writeoff_process(self):
        writeoff_assets = self.patrimonio.baixas

        is_adding_item = self.pk is None
        is_updating_item = self.pk is not None

        item_in_any_opened_receipts = writeoff_assets.filter(
            nota__state=NotaBaixa.Status.OPENED
        )

        item_in_another_opened_receipts = writeoff_assets.exclude(
            nota=self.nota
        ).filter(nota__state=NotaBaixa.Status.OPENED)

        return (
            is_adding_item
            and item_in_any_opened_receipts.exists()
            or is_updating_item
            and item_in_another_opened_receipts.exists()
        )

    def validate_save(self):
        writeoffs = self.patrimonio.baixas

        if self.nota.is_closed:
            raise Exception(
                "Não é possível adicionar ou editar itens em uma nota de baixa fechada."
            )

        if self.patrimonio.is_written_off:
            raise Exception(
                "Não é possível dar baixa em um item que já foi dado baixa."
            )

        if self.is_already_in_writeoff_process():
            raise Exception(
                f"Este item {self.patrimonio.plaqueta} já se encontra em processo de baixa."
            )

        if self.patrimonio.is_being_moved:
            raise Exception(
                f"Este item {self.patrimonio.plaqueta} encontra-se em uma movimentação de bem, finalize-a mesma primeiro."
            )

        if hasattr(self.nota.my_origin, "validate_add_item"):
            self.nota.my_origin.validate_add_item(self)

    def validate_delete(self):
        if self.locked is True:
            raise Exception("Não posso modificar uma baixa finalizada.")

    @property
    def locked(self):
        return self.nota.state == 2

    @property
    def icon_conservacao(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-conservacao-%s"
            % self.patrimonio.get_conservacao_display().lower(),
            "title": self.patrimonio.get_conservacao_display(),
        }

    @property
    def icon_avaliacao(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-avaliacao-%s"
            % ("positiva" if float(self.valor_avaliacao or 0) >= 0 else "negativa"),
            "title": "Avaliação foi %s"
            % ("positiva" if self.valor_avaliacao > 0 else "negativa"),
        }

    @property
    def icon_status(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-status-%s"
            % ("liberado" if not self.locked else "bloqueado"),
            "title": "Liberado" if not self.locked else "Bloqueado",
        }

    @property
    def icons(self):
        return [
            self.icon_status,
            self.patrimonio.icon_principal(),
            self.icon_conservacao,
            self.icon_avaliacao,
        ]


class BaixaDoacao(NotaBaixa):
    favorecido = models.ForeignKey(Pessoa, related_name="+", on_delete=models.PROTECT)

    the_type = "nota-baixa-doacao"

    def __str__(self):
        return "DOAÇÃO EM FAVOR DE %s" % str(self.favorecido)


class BaixaSinistro(NotaBaixa):

    the_type = "nota-baixa-sinistro"

    def __str__(self):
        if self.data_documento:
            return "SINISTRO REGISTRADO NA DATA %s" % DateUtils.date_to_str(
                self.data_documento
            )
        else:
            return "SINISTRO REGISTRADO NA DATA NÃO INFORMADA"


class BaixaExtravio(NotaBaixa):
    the_type = "nota-baixa-extravio"

    @property
    def allow_subtype_blank(self):
        return False

    def __str__(self):
        if self.data_documento:
            return "EXTRAVIO REGISTRADO NA DATA %s" % DateUtils.date_to_str(
                self.data_documento
            )
        else:
            return "EXTRAVIO REGISTRADO NA DATA NÃO INFORMADA" % DateUtils.date_to_str(
                self.data_documento
            )


class BaixaInservibilidade(NotaBaixa):
    the_type = "nota-baixa-inservibilidade"

    @property
    def allow_subtype_blank(self):
        return False

    def __str__(self):
        if self.data_documento:
            return "INSERVIBILIDADE REGISTRADO NA DATA %s" % DateUtils.date_to_str(
                self.data_documento
            )
        else:
            return "INSERVIBILIDADE REGISTRADO NA DATA NÃO INFORMADA"


class BaixaMudancaClassificacao(NotaBaixa):

    the_type = "nota-mudanca-classificacao"

    def __str__(self):
        return "MUDANÇA DE CLASSIFICAÇÃO REGISTRADO NA DATA %s" % DateUtils.date_to_str(
            self.data_documento
        )


class BaixaObsolescencia(NotaBaixa):

    the_type = "nota-baixa-obsolescencia"

    def __str__(self):
        return "OBSOLESCÊNCIA REGISTRADO NA DATA %s" % DateUtils.date_to_str(
            self.data_documento
        )


class BaixaDeterioracao(NotaBaixa):

    the_type = "nota-baixa-deterioracao"

    def __str__(self):
        return "DETERIORAÇÃO REGISTRADO NA DATA %s" % DateUtils.date_to_str(
            self.data_documento
        )


class BaixaAlienacao(NotaBaixa):
    # Parametro "on_delete" adicionado. (Django 2)
    arrematante = models.ForeignKey(
        Pessoa, related_name="como_arrematantes", on_delete=models.CASCADE
    )

    the_type = "nota-baixa-alienacao"

    def __str__(self):
        return "ALIENAÇÃO EM FAVOR DE %s" % str(self.arrematante)


class BaixaTransferencia(NotaBaixa):
    # Parametro "on_delete" adicionado. (Django 2)
    favorecido = models.ForeignKey(
        Conta, related_name="favorecido_em_transferencias", on_delete=models.CASCADE
    )

    the_type = "nota-baixa-transferencia"

    def do(self):
        NotaEntrada.objects.filter(
            pk__in=self.itens.values("patrimonio__item_entrada__nota")
        ).update(conta=self.favorecido)

    def __str__(self):
        return "EM FAVOR DA CONTA %s" % str(self.favorecido)


class BaixaAjusteInventario(NotaBaixa):

    the_type = "nota-baixa-ajuste-inventario"

    def __str__(self):
        if self.data_documento:
            return "AJUSTE DE INVENTÁRIO NA DATA %s" % DateUtils.date_to_str(
                self.data_documento
            )
        else:
            return "AJUSTE DE INVENTÁRIO EM DATA NÃO INFORMADA"


class TabelaAvaliacao(models.Model, AuditableMixins):
    numero = models.IntegerField(blank=True)
    ano = models.IntegerField(blank=True)
    publicacao = models.ForeignKey(
        Publicacao, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    data_vigencia = models.DateField()
    data_fim_vigencia = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("-data_vigencia",)

    def __str__(self):
        return "%s - %s" % (self.number_display(), self.publicacao)

    def proximo_numero(self):
        query = self.__class__.objects.filter(ano=self.ano).aggregate(
            max_number=models.Max("numero")
        )

        number = int(query.get("max_number") or 0)
        return number + 1

    def number_display(self):
        return "%02d/%d" % (self.numero, self.ano)

    def create_table(self):
        log.info("-" * 60)
        log.info("Gerando a tebala de grupo e especie")

        for grupo in GrupoEspecie.objects.order_by("codigo"):
            item = None

            try:
                item = ItemAvaliacao.objects.get(tabela=self, grupo=grupo, especie=None)
                log.info(
                    "Item de avaliação encontrado para o grupo %s" % item.grupo.codigo
                )
            except ItemAvaliacao.DoesNotExist:
                item = ItemAvaliacao(
                    tabela=self, grupo=grupo, vida_util=0, depreciacao=0, residual=0
                )
                log.info("Item de avaliação criado para o grupo %s" % item.grupo.codigo)
            except Exception as e:
                log.exception(e)
            finally:
                if item is not None:
                    item.indirect = True
                    item.save()

        log.info("-" * 60)

    def _change_dates(self):
        query = self.__class__.objects.filter(data_vigencia__gt=self.data_vigencia)
        query = query if self.pk is None else query.exclude(pk=self.pk)

        if query.exists() and getattr(self, "indirect", False) is False:
            log.debug([m.number_display() for m in query])
            raise Exception(
                "Já existe uma tabela que tem vigencia maior que %s."
                % DateUtils.date_to_str(self.data_vigencia)
            )

        query = self.__class__.objects.filter(
            data_vigencia__lt=self.data_vigencia
        ).order_by("-data_vigencia")

        if query.exists():
            tab = query.latest("data_vigencia")
            tab.indirect = True
            tab.data_fim_vigencia = self.data_vigencia
            tab.save()

    def _validate(self):
        if self.data_vigencia is None:
            raise Exception("Não posso criar a tabela sem uma data de vigencia.")
        # elif self.data_vigencia <= datetime.today().date():
        #     raise Exception('Não posso alterar uma tabela que já esta em vigencia.')

    def save(self, *args, **kargs):
        if self.ano is None:
            self.ano = date.today().year
            self.numero = self.proximo_numero()

        self._validate()
        self._change_dates()

        super(TabelaAvaliacao, self).save(*args, **kargs)
        getattr(self, "indirect", False) is False and self.create_table()


class ItemAvaliacao(models.Model):
    tabela = models.ForeignKey(
        TabelaAvaliacao, related_name="itens", on_delete=models.PROTECT
    )
    grupo = models.ForeignKey(
        GrupoEspecie, related_name="itens_avaliacao", on_delete=models.PROTECT
    )
    # Parametro "on_delete" adicionado. (Django 2)
    especie = models.ForeignKey(
        Especie,
        related_name="itens_avaliacao",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    vida_util = models.SmallIntegerField()
    depreciacao = models.DecimalField(decimal_places=2, max_digits=5)
    residual = models.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        ordering = ("tabela", "grupo__titulo", "id", "especie__titulo")

    def __str__(self):
        return str(self.especie if self.especie is not None else self.grupo)

    def save(self, *args, **kargs):
        super(ItemAvaliacao, self).save(*args, **kargs)
        self.especie is None and self.create_items()

    def create_items(self):
        log.info("Complementando a tabela para o Grupo %s" % self.grupo.codigo)

        for especie in self.grupo.especies.order_by("codigo"):
            item = None
            try:
                item = ItemAvaliacao.objects.get(
                    tabela=self.tabela, grupo=self.grupo, especie=especie
                )
                # log.info('Item de avaliação encontrado para a especie %s' % item.especie.codigo)
            except ItemAvaliacao.DoesNotExist:
                item = ItemAvaliacao(
                    tabela=self.tabela,
                    grupo=self.grupo,
                    especie=especie,
                    vida_util=self.vida_util,
                    depreciacao=self.depreciacao,
                    residual=self.residual,
                )
                # log.info('Item de avaliação criado para a especie %s' % item.especie.codigo)
            except Exception as e:
                log.exception(e)
            finally:
                if getattr(self, "indirect", False) is False:
                    item.vida_util = self.vida_util
                    item.depreciacao = self.depreciacao
                    item.residual = self.residual
                item is not None and item.save()


class ParametroAvaliacao(models.Model):
    tabela = models.ForeignKey(
        TabelaAvaliacao, related_name="valores_concervacao", on_delete=models.PROTECT
    )
    valor = models.SmallIntegerField()
    variavel = models.CharField(max_length=100)
    tipo = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "ASSESSMENT_PARAMETER_TYPE"),
        db_index=True,
    )

    class Meta:
        ordering = ("tipo", "valor", "variavel")

    def get_variavel_display(self):
        choice_conservacao = (
            (1, "Novo"),
            (2, "Bom"),
            (3, "Regular"),
            (4, "Inservivel"),
        )
        choice_ano = (
            (1, "Menos de um ano"),
            (2, "1 ano"),
            (3, "2 anos"),
            (4, "3 anos"),
            (5, "4 anos"),
            (6, "5 anos"),
            (7, "6 anos"),
            (8, "7 anos"),
            (9, "8 anos"),
            (10, "9 anos"),
            (11, "10 anos ou mais"),
        )

        self.tipo = int(self.tipo or 0)
        self.variavel = int(self.variavel or 0)

        if self.tipo == 1:
            return dict(choice_conservacao).get(self.variavel, "undefined")
        else:
            return dict(choice_ano).get(self.variavel, "undefined")


class Avaliacao(models.Model):
    ano = models.SmallIntegerField(blank=True)
    mes = models.SmallIntegerField(blank=True)
    numero = models.SmallIntegerField(blank=True)
    tabela = models.ForeignKey(
        TabelaAvaliacao, related_name="avaliacoes", on_delete=models.PROTECT, blank=True
    )
    tipo = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "ASSESSMENT_TYPE"), db_index=True
    )
    executor = models.ForeignKey(
        User, related_name="+", null=True, on_delete=models.PROTECT, blank=True
    )
    data_execucao = models.DateTimeField(null=True, blank=True)
    de = models.DateTimeField(null=True, blank=True)
    ate = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-ano", "-mes", "numero")
        permissions = (
            ("executa_auto_depreciacao", "Pode executar depreciação automática"),
            ("executa_avalicao", "Pode executar avaliacao"),
        )

    @classmethod
    def next(cls, ano=None):
        now = datetime.now()
        query = (
            cls.objects.filter(ano=now.year if ano is None else ano)
            .order_by("numero")
            .aggregate(maximo=models.Max("numero"))
        )
        numero = int(query.get("maximo") or 0)

        return numero + 1, now.year if ano is None else ano

    def __str__(self):
        return "%(numero)04d/%(ano)d - %(tipo)s" % {
            "numero": int(self.numero if self.numero is not None else 0),
            "ano": int(self.ano if self.ano is not None else 0),
            "tipo": self.get_tipo_display(),
        }

    @property
    def icons(self):
        return [self.icon_lock, self.icon_tipo]

    @property
    def icon_lock(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-status-{0}".format(
                "bloqueado" if self.executor is not None else "liberado"
            ),
            "title": "Bloqueado" if self.executor is not None else "Liberado",
        }

    @property
    def icon_tipo(self):
        return {
            "iconCls": "icon-patrimonio icon-pat-status-{0}".format(
                slugify(self.get_tipo_display())
            ),
            "title": self.get_tipo_display(),
        }

    def can_execute(self):
        perm = "patrimonio.{0}".format(
            "executa_auto_depreciacao" if self.tipo == 1 else "executa_avalicao"
        )

        self.can_analize()

        if get_current_user().has_perm(perm) is False:
            raise Exception("Voce nao tem permissao para executar esta acao.")

        return True

    def can_analize(self):
        if self.executor or self.data_execucao:
            raise Exception("Nao posso reanalizar uma avalicao que foi executada.")

    def analize(self, execute=False):
        log.info("Analizando avaliação de patrimonio [ %s ]" % self)
        # log.debug('begin')

        try:
            with transaction.atomic():
                self.can_analize() if not execute else self.can_execute()

                total = self.itens.count()
                number = 0

                for item in self.itens.order_by("patrimonio__plaqueta"):
                    if execute is True:
                        item.executa()
                    else:
                        item.analize()

                    if hasattr(self, "feedback"):
                        number += 1
                        self.feedback(
                            "%(action)s %(number)d de %(of)d",
                            action="Executando" if execute else "Analizando",
                            number=number,
                            of=total,
                            pct=((number * 100.0) / float(total)),
                        )

                if execute is True:
                    self.executor = get_current_user()
                    self.data_execucao = datetime.now()
                    self.save()
        except Exception as e:
            log.exception(e)
            raise e

        # log.debug('end')

    def populate(self):
        if int(self.tipo or 0) == 1:
            with transaction.atomic():
                self._popula_rotina()

    def _popula_rotina(self):
        log.info("Populando avaliação de patrimonio [ %s ]" % self)
        log.info("begin")

        query = Patrimonio.objects.all()

        if self.de is not None:
            query = query.filter(data_tombo__gte=self.de)
        if self.ate is not None:
            query = query.filter(data_tombo__lte=self.ate)

        self.itens.exclude(patrimonio__pk__in=query.values("pk")).delete()

        query = query.exclude(pk__in=self.itens.all().values("patrimonio"))

        total = float(query.count())
        pos = 0.0

        for pat in query.exclude(baixas__nota__state__in=(1, 2)).order_by("plaqueta"):
            pos += 1
            if hasattr(self, "feedback"):
                self.feedback(
                    message="Item %(pos)d de %(total)d.",
                    pos=int(pos),
                    total=int(total),
                    pct=round((pos / total) * 100.0, 2),
                )

            self.itens.add(AvaliacaoItem(patrimonio=pat), bulk=False)
            log.info(
                "Adicionado o patrimonio %s na avaliação %s" % (pat.plaqueta, self)
            )

        log.info("end")

    def define_tabela(self):
        tabelas = TabelaAvaliacao.objects.filter(
            data_vigencia__lte=datetime.now()
        ).order_by("data_vigencia")
        if tabelas.exists():
            self.tabela = tabelas.latest("data_vigencia")
        else:
            raise Exception("Não existe nenhuma tabela vigente para a avaliação.")

    def delete(self, *args, **kargs):
        if self.executor is not None:
            raise Exception("Não posso remover uma avaliação que já foi executada.")
        super(Avaliacao, self).delete(*args, **kargs)

    def save(self, *args, **kargs):
        if self.numero is None:
            self.numero, self.ano = self.next(self.ano)

        self.tipo = int(self.tipo or 0)
        self.define_tabela()

        super(Avaliacao, self).save(*args, **kargs)

        try:
            from adm.patrimonio.tasks import avaliation_populate
        except Exception:
            self.populate()
        else:
            if not getattr(self, "without_task", False):
                Task.start(avaliation_populate, avaliation=self.pk)
            else:
                self.populate()


class AvaliacaoItem(models.Model):
    avaliacao = models.ForeignKey(
        Avaliacao, related_name="itens", on_delete=models.PROTECT
    )
    patrimonio = models.ForeignKey(
        Patrimonio, related_name="avaliacoes", on_delete=models.PROTECT
    )
    valor_atual = models.DecimalField(
        decimal_places=6, max_digits=20, default=0.00, blank=True
    )
    valor_avaliado = models.DecimalField(
        decimal_places=6, max_digits=20, default=0.00, blank=True
    )
    vida_util = models.SmallIntegerField(null=True, blank=True)
    depreciacao = models.DecimalField(
        decimal_places=6, max_digits=20, default=0.00, blank=True
    )
    residual = models.DecimalField(
        decimal_places=6, max_digits=20, default=0.00, blank=True
    )
    quantidade_dias = models.SmallIntegerField(default=0, blank=True)
    taxa_pro_rata = models.DecimalField(
        decimal_places=6, max_digits=20, default=0.00, blank=True
    )
    conservacao = models.SmallIntegerField(
        choices=Choice.get_choices_for("patrimonio", "CONSERVATION"),
        db_index=True,
        blank=True,
    )
    discarded = models.BooleanField(default=False, blank=True)
    discarded_justify = models.TextField(null=True, blank=True)
    discarded_at = models.DateTimeField(null=True, blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    discarded_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = (("avaliacao", "patrimonio"),)

        permissions = (("can_discard_review", "Pode descartar avaliação."),)

    def _undo_validate(self):
        if self.avaliacao.executor is None:
            raise Exception("Não posso desfazer uma avaliação que não foi executada.")

        if not get_current_user() or not get_current_user().has_perm(
            "patrimonio.can_discard_review"
        ):
            raise Exception("Você não tem permissão para realizar esta operação")

        query = (
            self.patrimonio.avaliacoes.exclude(discarded=True)
            .exclude(avaliacao=self.avaliacao)
            .exclude(avaliacao__data_execucao__lt=self.avaliacao.data_execucao)
            .filter(
                models.Q(
                    models.Q(avaliacao__ano__gt=self.avaliacao.ano)
                    | models.Q(
                        models.Q(avaliacao__ano=self.avaliacao.ano)
                        & models.Q(avaliacao__mes__gte=self.avaliacao.mes)
                    )
                )
            )
        )

        if query.exists():
            pendentes = [
                "%04d/%d" % (ia.avaliacao.numero, ia.avaliacao.ano)
                for ia in query.order_by("-pk")
            ]
            raise Exception(
                "Existem outras avaliações posteriores, verifique: %s."
                % ", ".join(pendentes)
            )

    def undo(self, justify):
        self._undo_validate()
        log.debug([self.valor_atual, self.valor_avaliado])

        with transaction.atomic():
            self.patrimonio.valor_atual = self.valor_atual
            if self.avaliacao.tipo == 3:
                self.patrimonio.valor_base = self.valor_atual
            self.patrimonio.save()

            self.discarded = True
            self.discarded_justify = justify
            self.discarded_by = get_current_user()
            self.discarded_at = datetime.now()
            self.save()

    @property
    def icons(self):
        return [
            self.patrimonio.icon_tipo_patirmonio(),
            self.patrimonio.icon_principal(),
            self.patrimonio.icon_conservacao(),
        ]

    def save(self, *args, **kargs):
        if self.pk is None:
            self.valor_atual = self.patrimonio.valor_atual
            self.conservacao = self.patrimonio.conservacao
            # self.vida_util = self.patrimonio.vida_util

        super(AvaliacaoItem, self).save(*args, **kargs)

    def analize(self):
        log.info(
            "Analizando %s para o patrimonio %s tipo %s"
            % (
                self.avaliacao.get_tipo_display(),
                self.patrimonio.plaqueta,
                self.patrimonio.item_entrada.nota.conta,
            )
        )
        log.info("begin")
        if (
            self.avaliacao.tipo in (1, 2)
            and not self.patrimonio.baixas.filter(nota__state__in=(1, 2)).exists()
        ):
            try:
                periodo = NewDateRange.from_month(
                    self.avaliacao.ano, self.avaliacao.mes
                )
                entrada = self.patrimonio.item_entrada
                item_tabela = self.avaliacao.tabela.itens.get(especie=entrada.especie)

                self.taxa_pro_rata = (
                    float(item_tabela.depreciacao or 0) / 100.0
                ) / 360.0
                if periodo.in_range(self.patrimonio.data_tombo.date()) is True:
                    log.info("Adquirido no mes da depreciação")
                    self.quantidade_dias = (30 - self.patrimonio.data_tombo.day) + 1

                    self.quantidade_dias = (
                        self.quantidade_dias if self.quantidade_dias > 0 else 1
                    )
                else:
                    log.info("Adquirido em periodo anterior")
                    self.quantidade_dias = 30

                residual = float(self.patrimonio.valor_base or 0) * (
                    float(item_tabela.residual or 0) / 100.00
                )
                depreciado = (
                    (
                        (float(self.patrimonio.valor_base or 0) - residual)
                        * self.taxa_pro_rata
                    )
                ) * self.quantidade_dias

                if (
                    self.patrimonio.conservacao == 1
                    and self.patrimonio.data_tombo.date()
                    < (periodo.last - relativedelta(years=1))
                ):
                    self.conservacao = 2

                self.valor_atual = roundf(self.patrimonio.valor_atual)
                self.valor_avaliado = roundf(float(self.valor_atual or 0) - depreciado)
                self.residual = roundf(residual)
                self.valor_avaliado = roundf(
                    self.residual
                    if self.valor_avaliado < self.residual
                    else self.valor_avaliado
                )
                self.depreciacao = roundf(float(self.valor_atual) - self.valor_avaliado)

                self.save()
            except Exception as e:
                log.exception(e)
                log.error(
                    "Ocorreu um erro depreciando o item %s" % self.patrimonio.plaqueta
                )
                log.debug(vars(self))
                raise Exception(
                    "\n".join(
                        [
                            "Ocorreu um erro depreciando o item %s"
                            % self.patrimonio.plaqueta,
                            "Da conta %s" % self.patrimonio.item_entrada.nota.conta.pk,
                            "Grupo %s" % self.patrimonio.item_entrada.especie.grupo.pk,
                            "Especie %s" % self.patrimonio.item_entrada.especie.pk,
                            "",
                            str(e),
                        ]
                    )
                )
        else:
            log.warn("Só é feita analise automática para avaliação do tipo depreciação")

        log.info("end")

    def executa(self):
        self.analize()
        self.patrimonio.valor_atual = roundf(self.valor_avaliado)
        if self.avaliacao.tipo == 3:
            self.patrimonio.valor_base = roundf(self.valor_avaliado)
        self.patrimonio.valor_residual = roundf(self.residual)
        if self.vida_util:
            self.patrimonio.vida_util = date.today() + relativedelta(
                years=self.vida_util
            )
        self.patrimonio.conservacao = self.conservacao
        self.patrimonio.save()


class Suspensao(AuditableMixins, models.Model):
    nota_entrada = models.ForeignKey(
        NotaEntrada, related_name="suspensoes", on_delete=models.PROTECT
    )
    item_entrada = models.ForeignKey(
        ItemEntrada,
        related_name="suspensoes",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    data_inicio = models.DateTimeField(blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    aberto_por = models.ForeignKey(
        User, related_name="+", blank=True, on_delete=models.CASCADE
    )
    data_fim = models.DateTimeField(null=True, blank=True)
    fechado_por = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    ativo = models.BooleanField(default=True)
    justificativa = models.TextField(blank=True)

    AUDITABLE = {"fields": ["ativo"]}

    class Meta:
        ordering = ("-ativo", "-pk")

    def change_patrimonio(self):
        query = Patrimonio.objects.filter(item_entrada__nota=self.nota_entrada)

        if self.item_entrada:
            query = query.filter(item_entrada=self.item_entrada)

        for pat in query:
            pat.suspenso = self.ativo
            pat.suspenso_tipo = 1 if not self.item_entrada else 2

            if not self.ativo:
                pat.data_tombo = self.data_fim
                pat.valor_atual = pat.item_entrada.valor_unitario

            pat.save()

    def _validate(self):
        query = Suspensao.objects.filter(nota_entrada=self.nota_entrada).filter(
            ativo=True
        )

        if self.pk:
            query = query.exclude(pk=self.pk)

        if query.exists():
            log.debug([e.pk for e in query])
            raise Exception("Existe um outro pedido de suspensão ativo.")

    def save(self, *args, **kargs):
        if self.pk is None:
            self.data_inicio = datetime.now()
            self.aberto_por = get_current_user()
        elif self.old_fields.get("ativo", False) is True:
            self.data_fim = datetime.now()
            self.fechado_por = get_current_user()

        self._validate()

        try:
            with transaction.atomic():
                models.Model.save(self, *args, **kargs)
                self.change_patrimonio()
        except Exception as e:
            raise e


class Notification(AuditTimestampModel):
    """Manages notifications related to asset transfers"""

    NOTIFICATION_NOT_SENT = 1
    NOTIFICATION_RECEIVED = 2
    NOTIFICATION_NOT_RECEIVED = 3

    assets_movement = models.ForeignKey(
        Movimento,
        on_delete=models.CASCADE,
        verbose_name="Movimentação Patrimonial",
        related_name="notifications",
    )
    destination = models.ForeignKey(
        PessoaFisica,
        verbose_name="Destinatário",
        related_name="asset_movement_notifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    protocol = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    protocol_movement = models.ForeignKey(
        Movimentacao,
        on_delete=models.CASCADE,
        verbose_name="Movimentação de Protocolo",
        related_name="notifications",
        null=True,
        blank=True,
    )
    notified_by = models.ForeignKey(
        User,
        related_name="patrimony_movement_notification",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    notified_at = models.DateTimeField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("-modified_at",)

    def save(self, ignore_validation=False, *args, **kwargs):
        if not ignore_validation:
            self._validate_send()

        self._validate_movement_destination()
        self._update_destination()
        self._update_content()

        super().save(*args, **kwargs)

    def _validate_movement_destination(self):
        if self.assets_movement.responsavel_destino is None:
            raise Exception(
                f"Não foi possível concluir a operação, pois a movimentação "
                f"nº {self.assets_movement.id_number} não tem responsável de "
                f"destino especificado."
            )

    def _update_destination(self):
        """Sincroniza responsável de destino com destinatário

        Enquanto a notificação não for enviada, sincroniza o responsável
        de destino da movimentação de bens com o destinatário da
        notificação (é preciso manter a consistência, já que a informação
        está duplicada).

        """
        person = self.assets_movement.responsavel_destino.pessoa_fisica
        if not self.destination or (
            self.destination and self.destination.pk != person.pk
        ):
            self.destination = person

    def _update_content(self):
        if not len(self.content):
            self.content = self.default_content

    def create_protocol(self):
        """Este método cria um protocolo eletrônico para a notificação"""
        self.protocol = Protocolo.docketing(
            subject="Comunicar %s - Movimentação de Bens" % str(self.destination.nome),
            document_type=TipoDocumento.objects.get(nome="CIENTIFICAÇÃO"),
            interested=person_from_user(get_current_user()),
            home_court=self._get_current_user_main_workplace(),
            content=self.content,
        )

        self.save()

    def delete(self, *args, **kwargs):
        self._validate_delete()
        self._delete_protocol()
        super().delete(*args, **kwargs)

    def _validate_delete(self):
        if self.was_sent:
            raise Exception(
                "Não é possível remover uma notificação que já foi enviada. "
                f"Protocolo nº {self.protocol.codigo}."
            )

    def _delete_protocol(self):
        with transaction.atomic():
            self.protocol.movimentacoes.all().delete()
            self.protocol.delete()

    @classmethod
    def bulk_send(cls, movements_pk):
        """Cria uma notificação para cada Movimento

        Argumentos:
            movements_pk: Uma lista de chaves-primárias de Movimento

        ATENÇÃO: É recomendado chamar este método através de uma task, para que
        o tempo da requisição HTTP não seja demorado.

        """
        with transaction.atomic():
            notifications = []

            # Se a transação for concluída com êxito, envia as notificações
            transaction.on_commit(lambda: cls._on_commit_bulk_send(notifications))

            # Cria as notificações
            for movement in Movimento.objects.filter(pk__in=movements_pk):
                notification = cls(
                    assets_movement=movement, content=cls.default_content()
                )
                notification.save()
                notifications.append(notification)

    @classmethod
    def _on_commit_bulk_send(cls, notifications):
        """Envia as notificações

        Argumentos:
            notifications: Uma lista de instâncias de Notification

        """
        for notification in notifications:
            if not notification.was_sent:
                notification.send()

    def send(self):
        """Este método é responsável por enviar a notificação

        Etapas:
            - Gera Termo de Responsabilidade
            - Cria o protocolo
            - Anexa o Termo de Responsabilidade ao protocolo
            - Despacha o protocolo

        """
        from celery import chain
        from adm.patrimonio.tasks import generate_term, attach_and_dispatch

        self._validate_send()

        report = "/to/mpe/adm/patrimonio/termo_responsabilidade"
        if getattr(settings, "REPORT_DEFAULT_PATH", None):
            report = f"/{settings.REPORT_DEFAULT_PATH}{report}"

        chain(
            generate_term.s(
                report=report,
                params=self._get_report_params(),
                output_format="PDF",
            )
            | attach_and_dispatch.s(
                notification_pk=self.pk, username=get_current_user().username
            )
        )()

    def _validate_send(self):
        if self.was_sent:
            raise Exception(
                "Não é possível modificar uma notificação que já foi enviada. "
                f"Protocolo nº {self.protocol.codigo}."
            )

    @property
    def was_sent(self):
        """Esta notificação foi enviada?"""
        return (
            self.pk
            and self.protocol
            and self.protocol.movimentacoes.filter(passo__gt=0).exists()
        )

    def _get_current_user_main_workplace(self):
        """Retorna a lotação principal (rh.Lotacao) do usuário atual"""
        employee = employee_from_user(get_current_user())
        return employee.workplace_by_date()

    @classmethod
    def default_content(cls):
        """Conteúdo padrão utilizado para compor o corpo do protocolo"""
        template = loader.get_template("patrimonio/notification.html")
        return template.render({})

    @classmethod
    def generate_term(cls, report, params, output_format="PDF"):
        """Gera o Termo de Responsabilidade

        Argumentos:
            report: O caminho do relatório na árvore do Jasper Server
            params: Parâmetros para a geração do relatório
            output_format: Formato do arquivo de saída

        OBS1: É recomendado chamar este método através de uma task, para que
        o tempo da requisição HTTP não seja demorado.

        OBS2: A task start_report (app contrib) não está sendo utilizada para
        gerar o Termo de Responsabilidade devido a erros de "matching query
        does not exist" que ocorrem durante a transação atômica ao
        consultar o modelo Task.

        """
        client = Client.from_config(getattr(settings, "JASPER_CONFIG", {}))
        cache_path = getattr(settings, "CACHE", {}).get("jreport", None)

        log.info("Gerando Termo de Responsabilidade...")
        with client.auth() as session:
            log.info("Authenticated on the report server!")

            queued_id = session.report_executation(
                report, params, output_format=output_format
            )
            ready = False

            while not ready:
                status = session.report_executation_status(queued_id)
                ready = status.get("value") not in ("execution", "queued")

                if status.get("value") == "ready":
                    output_id = session.report_executation_detail_exports(
                        queued_id
                    ).get("id")

                    resp = session.report_executation_output(queued_id, output_id)
                    filename = os.path.join(
                        cache_path, "-".join([queued_id, output_id])
                    )

                    with open(filename, "wb") as fd:
                        for data in iter(partial(resp.read, 8192), b""):
                            fd.write(data)

                    log.info("Report generated!")
                    return filename
                elif status.get("value") == "failed":
                    raise Exception(
                        status.get("errorDescriptor", {}).get("message", "desconhecido")
                    )

                time.sleep(0.5)

    @classmethod
    def attach_and_dispatch(cls, filename, notification_pk):
        """Cria o protocolo, anexa o termo de responsabilidade e despacha o protocolo

        Argumentos:
            filename: Caminho do arquivo de relatório gerado no método generate_term
            notification_pk: Chave-primária do modelo Notification

        OBS: É recomendado chamar este método através de uma task, para que
        o tempo da requisição HTTP não seja demorado.

        """
        with transaction.atomic():
            notification = cls.objects.get(pk=notification_pk)

            log.info(
                f"Notificação ({notification.pk}) de Movimentação de Bens: "
                "Criando o protocolo"
            )
            notification.create_protocol()

            log.info(
                f"Notificação ({notification.pk}) de Movimentação de Bens: "
                "Anexando Termo de Responsabilidade ao protocolo"
            )
            gedfile = notification.attach_term(filename)
            transaction.on_commit(lambda: notification._gedfile_create_cache(gedfile))

            log.info(
                f"Notificação ({notification.pk}) de Movimentação de Bens: "
                "Despachando o protocolo"
            )
            notification.dispatch_protocol()

    def attach_term(self, filename):
        """Anexa o Termo de Responsabilidade ao protocolo

        Argumentos:
            filename: Caminho do arquivo de relatório

        Este método cria o arquivo Ged (copia o arquivo de relatório,
        localizado no cache de relatórios, para o storage) e o associa
        ao anexo de movimentação de protocolo.

        """
        gedfile = self._create_gedfile(filename)

        movement_zero = Movimentacao.objects.filter(
            protocolo=self.protocol, passo=0
        ).first()

        attachment = Attachment(
            moviment=movement_zero, title=gedfile.filename, attach=gedfile
        )

        attachment.save()

        return gedfile

    def _gedfile_create_cache(self, gedfile):
        if gedfile.need_cache:
            gedfile.create_cache()

    def dispatch_protocol(self):
        """Movimenta o protocolo para o responsável de destino (pessoa)"""
        movement_zero = self._get_movement_zero()
        movement_zero.do_send(
            person_destination=self.destination.pk,
            employee_origin=employee_from_user(get_current_user()),
            physical=False,
            opinion=True,
        )
        self._update_notification(movement_zero)

    def _get_report_params(self):
        return {
            "outfile": self._get_formatted_filename(),
            "report_name": "Termo de Responsabilidade",
            "movimento": self.assets_movement.pk,
        }

    def _get_formatted_filename(self):
        slug = self.assets_movement.responsavel_destino.pessoa_fisica.slug
        matricula = self.assets_movement.responsavel_destino.matricula
        return f"termo-responsabilidade-{slug}-{matricula}"

    def _create_gedfile(self, filename):
        """Cria uma cópia do relatório (Termo de Responsabilidade) no storage

        Argumentos:
            filename: Caminho do arquivo de relatório

        """
        gedfile = None
        buffer = None

        with open(filename, "rb") as fd:
            buffer = b"".join([chunk for chunk in iter(partial(fd.read, 8192), b"")])

        signature = Arquivo.hash_buffer(buffer)

        gedfile = Arquivo(
            file=signature,
            filename=self._get_formatted_filename(),
            mimetype="application/pdf",
            user=get_current_user(),
            acesso=3,
        )

        gedfile.save_file(gedfile, signature, buffer)
        gedfile.save(ignore_cache=True)

        # Nesse ponto, não precisamos mais do arquivo do relatório
        if os.path.exists(filename):
            os.unlink(filename)

        return gedfile

    def _get_movement_zero(self):
        """Retorna o movimento passo 0 do protocolo"""
        return Movimentacao.objects.filter(protocolo=self.protocol, passo=0).first()

    def _update_notification(self, movement_zero):
        """Atualiza a notificação após o despacho do protocolo

        Argumentos:
            movement_zero: Uma instância de Movimentacao (movimentação
            passo 0 do protocolo referenciado pelo campo protocol)

        """
        movement_one = movement_zero.derivative_for.get(passo=1)
        self.protocol_movement = movement_one
        self.notified_by = get_current_user()
        self.notified_at = datetime.now()
        self.save(ignore_validation=True)

    @property
    def status(self):
        """Retorna o status da notificação"""
        if not self.was_sent:
            return self.NOTIFICATION_NOT_SENT

        if self.received_by:
            return self.NOTIFICATION_RECEIVED

        return self.NOTIFICATION_NOT_RECEIVED

    @property
    def received_by(self):
        """Retorna a pessoa que recebeu a notificação"""
        if (
            self.pk
            and self.protocol_movement
            and self.protocol_movement.servidor_destino
        ):
            return self.protocol_movement.servidor_destino.pessoa_fisica

        return None

    @property
    def received_at(self):
        """Retorna a data de recebimento da notificação"""
        if self.pk and self.protocol_movement:
            return self.protocol_movement.data_recebimento

        return None

    @property
    def icons(self):
        translate = {
            self.NOTIFICATION_NOT_RECEIVED: {
                "iconCls": "icon-patrimonio icon-pat-nota-finalizada",
                "title": "Notificação enviada, mas não recebida",
            },
            self.NOTIFICATION_RECEIVED: {
                "iconCls": "icon-patrimonio icon-pat-nota-aberta",
                "title": "Notificação foi recebida",
            },
            self.NOTIFICATION_NOT_SENT: {
                "iconCls": "icon-patrimonio icon-pat-notification-edit-mode",
                "title": "Notificação ainda não enviada",
            },
        }

        return [
            translate.get(
                int(self.status or 0),
                {
                    "iconCls": "icon-patrimonio icon-pat-empty",
                    "title": "Status desconhecido",
                },
            )
        ]
