# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime, timedelta

import math
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes import fields as generic
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver


from contrib.daterange import NewDateRange
from contrib.decorator import auditable, to_search
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, getLogger
from engine.models import ControllerPermission, Group
from engine.notification.models import Notification
from rh import const as rh_const
from rh.afastamento.models import (
    AfastamentoCursoConcurso,
    AfastamentoMandatoEletivo,
    AfastamentoPrisao,
    LicencaAfastamentoConjuge,
    LicencaAtividadePolitica,
    LicencaDoencaPessoaFamilia,
    LicencaMandatoClassista,
    LicencaSaude3Dias,
    LicencaSaudeJuntaMedica,
    LicencaServicoMilitar,
)
from rh.models import MovimentacaoEstabilizacao, Publicacao, Servidor
from rh.ponto.models import Falta
from standard.models import AuditTimestampModel
from standard.questionario.models import Elemento, Questionario, QuestionarioResposta

SEP = "##"
DIVSEP = "$$"
log = getLogger(__name__)

ESTADOS_AVALIACAO = {1: "NOVO", 2: "AVALIADO", 3: "MANIFESTADO", 4: "FINALIZADO"}

DADO_LEGADO = {
    1: "NOVO",
    2: "LEGADO",
}

TIPO_PARTICIPANTE = {
    "1": "PRESIDENTE",
    "2": "SECRETÁRIO",
    "3": "INTEGRANTE",
    "4": "SUPLENTE",
}

DECISAO_COMISSAO = {
    1: "RECOMENDA",
    2: "NÃO RECOMENDA",
}

DECISAO_CHEFE_ORGAO = {
    1: "HOMOLOGA",
    2: "NÃO HOMOLOGA",
}


class ComissaoAvaliadora(models.Model):
    class Meta:
        ordering = ("-id",)
        db_table = "gep_comissao_avaliadora"

    comissao_anterior = models.ForeignKey(
        "ComissaoAvaliadora",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    publicacao = models.ForeignKey(
        "rh.Publicacao", related_name="+", on_delete=models.CASCADE
    )
    data_inicio = models.DateField(blank=True)
    data_fim = models.DateField(null=True, blank=True)
    integrantes = models.ManyToManyField("rh.Servidor", through="IntegrantesComissao")
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Comissão: %s à %s - %s " % (
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "",
            self.publicacao,
        )

    def save(self, *args, **kwargs):
        if self.comissao_anterior:
            ComissaoAvaliadora.objects.filter(pk=self.comissao_anterior.pk).update(
                data_fim=self.data_inicio - timedelta(1)
            )
        super(ComissaoAvaliadora, self).save(*args, **kwargs)


class IntegrantesComissao(AuditTimestampModel):
    class Meta:
        ordering = ("ordem",)
        db_table = "gep_integrantes_comissao"

    comissao_id = models.ForeignKey(
        "ComissaoAvaliadora", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    servidor_id = models.ForeignKey(
        "rh.Servidor", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    tipo_participante = models.CharField(
        max_length=1, choices=list(TIPO_PARTICIPANTE.items()), default=4
    )
    ordem = models.PositiveSmallIntegerField(null=True, blank=True)
    impedimento = models.BooleanField(
        verbose_name="Impedido de participar do processo temporariamente", default=False
    )

    def __str__(self):
        return "%s - %s - %s" % (self.servidor_id, self.comissao_id, self.get_display())

    def next_position(self):
        return (
            int(
                IntegrantesComissao.objects.filter(comissao_id=self.comissao_id)
                .aggregate(ultima_posicao=models.Max("ordem"))
                .get("ultima_posicao")
                or 0
            )
            + 1
        )

    def get_display(self):
        if int(self.tipo_participante) == 1:
            return "PRESIDENTE"
        elif int(self.tipo_participante) == 2:
            return "SECRETÁRIO"
        elif int(self.tipo_participante) == 3:
            return "INTEGRANTE"
        elif int(self.tipo_participante) == 4:
            return "SUPLENTE"

    def get_impedimento(self):
        if self.impedimento:
            return "SIM"
        else:
            return "NÃO"

    def move_up(self):
        if self.ordem == 1:
            return False
        else:
            try:
                q = IntegrantesComissao.objects.get(
                    comissao_id=self.comissao_id, ordem=(self.ordem - 1)
                )
            except Exception:
                q = None
            finally:
                if q is not None:
                    q.ordem = self.ordem
                    q.save()
                self.ordem -= 1
                self.save()
                return True

    def move_down(self):
        try:
            q = IntegrantesComissao.objects.get(
                comissao_id=self.comissao_id, ordem=(self.ordem + 1)
            )
        except Exception as e:
            q = None
            log.exception(e)
        finally:
            if q is not None:
                q.ordem = self.ordem
                q.save()
                self.ordem += 1
                self.save()
                return True
            else:
                return False

    def reorder(self):
        posicao = 1
        for ic in IntegrantesComissao.objects.filter(
            comissao_id=self.comissao_id
        ).order_by("ordem"):
            if ic.ordem != posicao:
                ic.ordem = posicao
                ic.save()
            posicao += 1

    def save(self, *args, **kwargs):
        comissao_permission, created = ControllerPermission.objects.get_or_create(
            name="estagio-comissao"
        )
        comissao_permission.users.add(self.servidor_id.user)
        group = Group.objects.get(name="estagio-comissao")
        self.servidor_id.user.groups.add(group)
        if not self.pk:
            self.ordem = self.next_position()

        super(IntegrantesComissao, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        comissao_permission = ControllerPermission.objects.get(name="estagio-comissao")
        comissao_permission.users.remove(self.servidor_id.user)
        group = Group.objects.get(name="estagio-comissao")
        self.servidor_id.user.groups.remove(group)

        super(IntegrantesComissao, self).delete(*args, **kwargs)
        self.reorder()


@to_search(
    [
        {
            "name": "estagio_prob_servidor__posse_servidor__servidor__matricula",
            "type": "text",
        },
        {
            "name": "estagio_prob_servidor__posse_servidor__servidor__pessoafisica__nome",
            "type": "",
        },
    ]
)
class EstagioComissaoServidor(AuditTimestampModel):
    class Meta:
        ordering = ("estagio_prob_servidor__fim_estagio",)
        db_table = "gep_estagio_comissao_servidor"
        permissions = (
            ("estagio_comissao", "Comissão de Estágio"),
            ("estagio_decisao", "Decisão de Estágio"),
        )

    estagio_prob_servidor = models.ForeignKey(
        "EstagioProbatorioServidor",
        related_name="comissao_estagio",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    integrante_comissao_avaliadora = models.ManyToManyField(
        "IntegrantesComissao", related_name="comissao_estagio"
    )

    def __str__(self):
        return "Servidor: %s" % (self.estagio_prob_servidor)

    def save(self, *args, **kwargs):
        try:
            Notification.notify_all(
                "gep-comissao",
                [
                    user.servidor_id
                    for user in self.integrante_comissao_avaliadora.all()
                    if self.integrante_comissao_avaliadora.filter().count()
                ],
                types=("SYS",),
                **{
                    "from": self.estagio_prob_servidor.posse_servidor.servidor,
                },
            )
        except Exception as e:
            log.info(e)
        super(EstagioComissaoServidor, self).save(*args, **kwargs)

    def is_liberado_para_decisao(self):
        return (
            True
            if int(self.get_qtd_recomendacoes_realizadas) == self.qtd_max_recomendacao
            else False
        )

    def is_julgado(self):
        return self.decisao_chefe_orgao.exists()

    def get_decisao_chefe_orgao_text(self):
        return self.decisao_chefe_orgao.filter()[0].get_decisao()

    def get_decisao_estagio(self):
        if self.decisao_chefe_orgao.exists():
            decisao_chefe_orgao = self.decisao_chefe_orgao.filter()[0]
            return True if int(decisao_chefe_orgao.decisao) == 1 else False
        else:
            return False

    def get_internship_decision(self):
        if self.decisao_chefe_orgao.exists():
            decisao_chefe_orgao = self.decisao_chefe_orgao.filter().first()
            if not decisao_chefe_orgao.decisao:
                raise Exception("Decisão ainda não foi tomada.")
            elif int(decisao_chefe_orgao.decisao) == 1:
                return True
        return False

    def get_integrantes_comissao(self):
        integrantes = ""
        for it in self.integrante_comissao_avaliadora.all():
            integrantes += "".join(" - ")
            integrantes += "".join(it.servidor_id.pessoa_fisica.nome)

        return integrantes

    def get_texto_qtd_julgamentos(self):
        restando = int(
            self.qtd_max_recomendacao - self.apreciacao_comissao.filter().count()
        )
        qtd = int(self.apreciacao_comissao.filter().count())
        if restando == 0:
            return "Todos já realizaram a recomendação"
        else:
            return "%d integrante(s) já recomendaram. Resta(m) %d recomendar" % (
                qtd,
                restando,
            )

    def get_texto_realizaram_recomendacao(self):
        # pks_j = []
        integrantes = ""
        for jc in self.apreciacao_comissao.all():
            if self.integrante_comissao_avaliadora.filter(
                pk=jc.integrante_avaliador.pk
            ).exists():
                integrantes += "".join(" - ")
                integrantes += "".join(
                    jc.integrante_avaliador.servidor_id.pessoa_fisica.nome
                )

        return "Já realizaram a recomendação: %s " % integrantes

    def get_texto_aguardando_recomendar(self):
        pks = []
        integrantes = ""
        for jc in self.apreciacao_comissao.all():
            pks.append(jc.integrante_avaliador.id)

        for ec in self.integrante_comissao_avaliadora.all():
            if ec.id not in pks:
                integrantes += "".join(" - ")
                integrantes += "".join(ec.servidor_id.pessoa_fisica.nome)
        return "Falta(m) recomendar o(s) integrante(s) %s " % integrantes

    def get_status(self):
        """
        Retorna icones de status.
        """
        status = []
        pks = []
        user = Servidor.objects.get(user=get_current_user())
        status.append(
            {
                "iconCls": "icon-gep-group",
                "title": "Integrantes da comissão: %s"
                % self.get_integrantes_comissao(),
            }
        )
        if self.apreciacao_comissao.filter().exists():
            status.append(
                {
                    "iconCls": "icon-gep-recomendacao-realizada",
                    "title": "%s" % self.get_texto_realizaram_recomendacao(),
                }
            )
        if self.apreciacao_comissao.filter().count() < 3:
            status.append(
                {
                    "iconCls": "icon-gep-recomendacao-nao-realizada",
                    "title": "%s" % self.get_texto_aguardando_recomendar(),
                }
            )

        for aux in self.apreciacao_comissao.all():
            pks.append(aux.integrante_avaliador.servidor_id.id)
        if user.id in pks:
            status.append(
                {
                    "iconCls": "icon-gep-ok",
                    "title": "Sua recomendação foi realizada para este servidor",
                }
            )
        else:
            status.append(
                {
                    "iconCls": "icon-gep-warning",
                    "title": "Aguardando sua recomendação para este servidor",
                }
            )

        return status

    def get_decisao(self):
        return (
            True
            if ApreciacaoComissao.objects.filter(
                comissao_servidor=self, decisao=1
            ).count()
            > ApreciacaoComissao.objects.filter(
                comissao_servidor=self, decisao=2
            ).count()
            else False
        )

    def get_status_gestor_orgao(self):
        """
        Retorna icones de status para o gestor de orgão.
        """
        status = []
        status.append(
            {
                "iconCls": "icon-gep-group",
                "title": "Integrantes da comissão: %s"
                % self.get_integrantes_comissao(),
            }
        )

        if not self.is_liberado_para_decisao():
            status.append(
                {
                    "iconCls": "icon-gep-warning",
                    "title": "Aguardando recomendação de todos os integrantes da comissão de estágio...",
                }
            )
        elif not self.decisao_chefe_orgao.filter().exists():
            if self.get_decisao():
                status.append(
                    {
                        "iconCls": "icon-gep-recomendou",
                        "title": "A Comissão recomenda a confirmação do servidor no cargo",
                    }
                )
            else:
                status.append(
                    {
                        "iconCls": "icon-gep-nao-recomendou",
                        "title": "A Comissão não recomenda a confirmação do servidor no cargo",
                    }
                )
            status.append(
                {"iconCls": "icon-gep-warning", "title": "Aguardando decisão..."}
            )
        else:
            status.append({"iconCls": "icon-gep-ok", "title": "Decisão proferida"})

        return status

    @property
    def get_qtd_recomendacoes_realizadas(self):
        return int(self.apreciacao_comissao.filter().count())

    @property
    def qtd_max_recomendacao(self):
        return 3


class ApreciacaoComissao(AuditTimestampModel):
    class Meta:
        db_table = "gep_apreciacao_comissao"
        ordering = ("comissao_servidor__estagio_prob_servidor__fim_estagio",)

    comissao_servidor = models.ForeignKey(
        "EstagioComissaoServidor",
        related_name="apreciacao_comissao",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    integrante_avaliador = models.ForeignKey(
        "IntegrantesComissao", related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    decisao = models.CharField(
        max_length=1, choices=list(DECISAO_COMISSAO.items()), null=True, blank=True
    )

    def __str__(self):
        return "%s - Avaliador %s - %s" % (
            self.comissao_servidor,
            self.integrante_avaliador.servidor_id.pessoa_fisica.nome,
            self.get_decisao(),
        )

    class ApreciacaoExists(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Você já realizou o julgamento do estágio probatório para este servidor.",
            )

    def get_decisao(self):
        if int(self.decisao) == 1:
            return "Recomenda a confirmação no cargo."
        elif int(self.decisao) == 2:
            return "Não recomenda a confirmação no cargo."

    def save(self, *args, **kwargs):
        if ApreciacaoComissao.objects.filter(
            comissao_servidor=self.comissao_servidor,
            integrante_avaliador=self.integrante_avaliador,
        ).exists():
            raise Exception(str(ApreciacaoComissao.ApreciacaoExists()))
        super(ApreciacaoComissao, self).save(*args, **kwargs)


class DecisaoChefeOrgao(AuditTimestampModel):

    class Meta:
        db_table = "gep_decisao_chefe_orgao"
        ordering = ("estagio_comissao_servidor__estagio_prob_servidor__fim_estagio",)
        permissions = (("can_valid_stage_prob", "Validar permissões para julgamento"),)

    # Parametro "on_delete" adicionado. (Django 2)
    estagio_comissao_servidor = models.ForeignKey(
        "EstagioComissaoServidor",
        related_name="decisao_chefe_orgao",
        on_delete=models.CASCADE,
    )
    decisao = models.CharField(
        max_length=1, choices=list(DECISAO_CHEFE_ORGAO.items()), null=True, blank=True
    )
    fundamentacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return "%s - %s " % (self.estagio_comissao_servidor, self.get_decisao_display())

    class DecisaoExists(Exception):
        def __init__(self):
            Exception.__init__(
                self, "Você já realizou a decisão do estágio probatório deste servidor."
            )

    def get_decisao(self):
        return (
            "Homologa a recomendação da Comissão, de acordo com sua fundamentação."
            if int(self.decisao) == 1
            else "Não Homologa a recomendação da Comissão, de acordo com a fundamentação."
        )

    def save(self, *args, **kwargs):
        if DecisaoChefeOrgao.objects.filter(
            estagio_comissao_servidor=self.estagio_comissao_servidor
        ).exists():
            raise Exception(str(DecisaoChefeOrgao.DecisaoExists()))
        try:
            gestor_orgao = Servidor.objects.get(user=get_current_user)
            Notification.notify(
                "gep-decisao-realizada",
                self.estagio_comissao_servidor.estagio_prob_servidor.posse_servidor.servidor,
                types=("SYS",),
                **{
                    "from": str(gestor_orgao),
                    "date": DateUtils.date_to_str(datetime.now().date()),
                    "decision": self.get_decisao(),
                    # 'fundamentation': self.fundamentacao
                },
            )
            gestor_permission = ControllerPermission.objects.get(name="estagio-gestor")
            Notification.notify_all(
                "gep-decisao-realizada-rh",
                [
                    user.servidor
                    for user in gestor_permission.users.all()
                    if user.servidor
                ],
                types=("SYS",),
                **{
                    "from": str(gestor_orgao),
                    "to": str(
                        self.estagio_comissao_servidor.estagio_prob_servidor.posse_servidor.servidor
                    ),
                    "decision": self.get_decisao(),
                    # 'fundamentation': self.fundamentacao
                },
            )
        except Exception as e:
            log.info(e)
        super(DecisaoChefeOrgao, self).save(*args, **kwargs)


class Conceito(models.Model):

    class Meta:
        # ordering= ('descricao',)
        db_table = "gep_conceito"

    valor_inicial = models.DecimalField(max_digits=5, decimal_places=2)
    valor_final = models.DecimalField(max_digits=5, decimal_places=2)
    descricao = models.CharField(max_length=100, null=True, blank=True, default="")

    def __str__(self):
        return self.descricao


class Configuracao(models.Model):

    class Meta:
        # ordering= ('data_inicio',)
        db_table = "gep_configuracao"

    configuracao_anterior = models.ForeignKey(
        "Configuracao",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    questionario = models.ForeignKey(
        Questionario, related_name="estagio_configuracao", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    questionario_manifestacao_servidor = models.ForeignKey(
        Questionario,
        related_name="manifestacao_servidor",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    publicacao = models.ForeignKey(
        "rh.Publicacao", related_name="estagio_configuracao", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    data_inicio = models.DateField(blank=True)
    data_fim = models.DateField(null=True, blank=True)
    qtde_avaliacoes = models.SmallIntegerField(
        verbose_name="Quantidade de Avaliações", default="3"
    )
    qtde_meses_entre_avaliacao = models.SmallIntegerField(
        verbose_name="Quantidade de meses entre avaliações", default="10"
    )
    porc_aprovacao = models.DecimalField(
        verbose_name="Porcentagem de Aprovação", max_digits=5, decimal_places=2
    )
    conceitos = models.ManyToManyField(Conceito, related_name="configuracao")
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - %s" % (self.questionario, self.publicacao)

    def save(self, *args, **kwargs):
        if self.configuracao_anterior:
            Configuracao.objects.filter(pk=self.configuracao_anterior.pk).update(
                data_fim=self.data_inicio - timedelta(1)
            )
        super(Configuracao, self).save(*args, **kwargs)


@to_search(
    [
        {"name": "posse_servidor__servidor__matricula", "type": "text"},
        {"name": "posse_servidor__servidor__pessoafisica__nome", "type": ""},
    ]
)
class EstagioProbatorioServidor(models.Model):
    # mp = MovimentacaoPosse.objects.filter(quadro__cargo__tipo_lei_cargo='EF',ativo=True,servidor__tipo='S')
    class Meta:
        ordering = ("proxima_avaliacao",)
        db_table = "gep_estagio_prob_servidor"
        permissions = (
            ("estagio_admin", "Administrador de estágio"),
            ("estagio_avaliador", "Avaliador de servidor em estágio probatório"),
            ("estagio_avaliado", "Avaliado em estágio probatório"),
        )

    posse_servidor = models.OneToOneField(
        "rh.MovimentacaoPosse",
        related_name="estagio_probatorio",
        on_delete=models.CASCADE,
    )
    ultima_avaliacao = models.DateField(
        verbose_name="Data Ultima Avaliacao", null=True, blank=True
    )
    proxima_avaliacao = models.DateField(
        verbose_name="Data Proxima Avaliacao", null=True, blank=True
    )
    configuracao = models.ForeignKey(
        Configuracao, verbose_name="Configuracao", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    bloqueada = models.BooleanField(verbose_name="Bloqueada", default=False)
    avaliacoes_realizadas = models.SmallIntegerField(default=0)
    media = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    status = models.CharField(
        max_length=1, choices=list(rh_const.STATUS_ESTAGIO.items()), default=1
    )
    fim_estagio = models.DateField(
        verbose_name="Data Fim Estágio", null=True, blank=True
    )
    dias_falta = models.DecimalField(
        null=True, blank=True, default=0, max_digits=5, decimal_places=2
    )
    estado_avaliacao = models.CharField(
        max_length=1, choices=list(ESTADOS_AVALIACAO.items()), default=1, blank=True
    )
    ciencia_decisao_estagio = models.DateField(
        verbose_name="Data da Ciência da Decisão do estágio", null=True, blank=True
    )
    dado_legado = models.CharField(
        max_length=1, choices=list(DADO_LEGADO.items()), default=1, blank=True
    )
    publicacao_homologacao = models.ForeignKey(
        "rh.Publicacao",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    LICENCA_DOENCA = 120
    LICENCA_DOENCA_PESSOA_FAMILIA = 90
    LICENCA_MATERNIDADE = 180
    LICENCA_ATIVIDADE_POLITICA = 90

    def __str__(self):
        return "%s - %s" % (self.posse_servidor, self.ultima_avaliacao)

    def validate(self, qr, qtype):
        evaluation = False
        manifestation = False
        if self.avaliacoes.exists():
            evaluation = (
                self.avaliacoes.first().questionario_resposta
                and qr == self.avaliacoes.first().questionario_resposta
            )
        if self.manifestacao_servidor.exists():
            manifestation = (
                self.manifestacao_servidor.first().questionario_resposta
                and qr == self.manifestacao_servidor.first().questionario_resposta
            )
        if qtype == "manifestation":
            log.debug(f"RETORNEI mani: {manifestation}")
            return manifestation
        if qtype == "evaluation":
            log.debug(f"RETORNEI evalu: {evaluation}")
            return evaluation

        return evaluation or manifestation

    class AvalicaoBloqueada(Exception):
        def __init__(self):
            Exception.__init__(
                self, "A Avaliação referente a esta etapa não pode mais ser alterada."
            )

    class FinalizacaoEmDisputa(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Esta etapa ainda está pendente no processo Avaliação ou Manifestação.",
            )

    class ManifestacaoBloqueada(Exception):
        def __init__(self):
            Exception.__init__(self, "Não é possivel alterar esta manifestação.")

    def get_deadline(self):
        now = self.getNow()
        if not self.proxima_avaliacao:
            # bloqueada
            pass
        elif now < (self.proxima_avaliacao - relativedelta(days=15)):
            # Aguardando
            return 0
        elif (
            (self.proxima_avaliacao - relativedelta(days=15))
            <= now
            <= self.proxima_avaliacao
        ):
            # Liberada
            return 1
        else:
            # Atrasada
            return 2

    def _liberada(self):
        """
        Verifica se falta 10 dias para a realização da avaliação de uma etapa.
        """
        return (
            True
            if self.proxima_avaliacao is not None
            and self.getNow() == (self.proxima_avaliacao - relativedelta(days=15))
            else False
        )

    def _liberada_dia(self):
        """
        Verifica se falta 10 dias para a realização da avaliação de uma etapa.
        """
        return (
            True
            if self.proxima_avaliacao is not None
            and self.getNow() == (self.proxima_avaliacao - relativedelta(days=2))
            else False
        )

    def _atrasada(self):
        """
        Verifica se a etapa de avaliação já ultrapassou mais de um mês sem a realização da avaliação pelo chefe.
        """
        rs = []
        for avaliacoes in self.avaliacoes.all():
            rs.append(avaliacoes.periodo_avaliado)
        return (
            True
            if self.proxima_avaliacao is not None
            and self.current_stage not in rs
            and self.getNow() > self.proxima_avaliacao + relativedelta(days=+1)
            else False
        )

    def _manifestacao_atrasada(self):
        """
        Verifica se a etapa de avaliação já ultrapassou mais de um mês sem a realização da avaliação pelo chefe.
        """
        if self.avaliacoes.filter(periodo_avaliado=self.current_stage).exists():
            rs = []
            for manifestacao in self.manifestacao_servidor.all():
                rs.append(manifestacao.estagio_avaliacao.periodo_avaliado)
            return (
                True
                if self.proxima_avaliacao is not None
                and self.current_stage not in rs
                and self.getNow() > self.proxima_avaliacao + relativedelta(days=+3)
                else False
            )

    def _acao_estado_avalicao(self, acao=None):
        """
        Verifica se é possivel realizar uma ação de alteração de Avaliação ou Manifestacao bem como uma
        Finalização de etapa, bloqueando caso o estado da avaliacao não permita
        @ACAO = O que esta querendo realizar (1 = AlterarAvaliacao/Avaliar, 2 = AlterarManifestacao/Manifestar, 3 = Finalizar)
        @ESTADO = Estado da avalicao (1 = NOVO, 2 = AVALIADO, 3 = MANIFESTADO, 4 = FINALIZADO)
        """
        log.info(acao)
        log.info(self.estado_avaliacao)
        if acao is None:
            return False
        elif acao == 1:
            return True if int(self.estado_avaliacao) != 4 else False
        elif acao == 2:
            return (
                True
                if int(self.estado_avaliacao) == 2 or int(self.estado_avaliacao) == 3
                else False
            )
        elif acao == 3:
            return True if int(self.estado_avaliacao) == 3 else False

    def _ciencia_decisao(self):
        if self.ciencia_decisao_estagio is not None:
            raise Exception(
                "Ciência já realizada em %s ."
                % DateUtils.date_to_str(self.ciencia_decisao_estagio)
            )
        elif self.valida_ciencia_decisao_estagio():
            self.ciencia_decisao_estagio = self.getNow()
            self.save()

            decisao_chefe_orgao = self.comissao_estagio.filter()[
                0
            ].decisao_chefe_orgao.filter()[0]
            chefe_orgao = Servidor.objects.get(user=decisao_chefe_orgao.created_by)
            gestor_permission = ControllerPermission.objects.get(name="estagio-gestor")
            Notification.notify_all(
                "gep-ciencia-servidor",
                [
                    user.servidor
                    for user in gestor_permission.users.all()
                    if user.servidor
                ],
                types=("SYS",),
                **{
                    "from": str(self.posse_servidor.servidor),
                    "chefe_orgao": str(chefe_orgao),
                },
            )
        else:
            raise Exception(
                "Ação indisponível. Aguardando decisão do estágio probatório."
            )

    @property
    def _servidor_estagio(self):
        return self.posse_servidor.servidor

    @property
    def _servidor_estagio_nome(self):
        return self.posse_servidor.servidor.pessoa_fisica.nome

    @property
    def _servidor_estagio_matricula(self):
        return self.posse_servidor.servidor.matricula

    @property
    def _dias_interrompidos(self):
        dias_interrompidos = 0
        for aval in self.avaliacoes.all():
            dias_interrompidos += aval.dias_interrompidos
        return dias_interrompidos

    @property
    def _dias_afastamento(self):
        return (self.fim_estagio - self._fim_estagio_original).days

    @property
    def _fim_estagio_original(self):
        return self._inicio_estagio + relativedelta(
            months=self._meses_estabilizacao, days=-1
        )

    def atualiza_etapas(self):
        """
        Atualiza os dados de uma etapa de avaliação, recalculando os dados para a proxima etapa ou caso seja a ultima,
        finaliza e muda o status para estágio finalizado.
        @status = 1 -> Em estágio probatório.
        @status = 2 -> Todas as etapas do estágio foram finalizadas.
        @status = 3 -> Em processo de avaliação pela comissão de estágio probatório.
        """
        log.info("atualizando etapas ---->>>>>>>>>>>> %s" % self)

        for avaliacoes in self.avaliacoes.all():
            etapa = self.current_stage
            if self.current_stage == avaliacoes.periodo_avaliado:
                if self.current_stage == self._qtd_avaliacoes:
                    # ULTIMA ETAPA DE AVALIACAO
                    log.info("Finalizando etapa %d de %s " % (self.current_stage, self))
                    self.dias_falta = self.get_faltas_injustificas()
                    self.status = (
                        3  # AGUARDANDO FORMAÇÃO DA COMISSÃO DE AVALIAÇÃO DO ESTÁGIO
                    )
                    # self.status = 2
                    self.bloqueada = True
                    self.ultima_avaliacao = self.proxima_avaliacao
                    self.proxima_avaliacao = None
                    self.media = self._media_conceito_final[0]
                    self.avaliacoes_realizadas = self.current_stage
                    self.fim_estagio = self.get_fim_estagio(self._dias_interrompidos)
                    self.estado_avaliacao = 4
                    self.save()
                    self.notifica_liberacao_para_comissao()
                else:
                    log.info("Atualizando etapa %d de %s " % (self.current_stage, self))
                    self.dias_falta = self.get_faltas_injustificas()
                    self.ultima_avaliacao = self.proxima_avaliacao
                    self.proxima_avaliacao = self.next_evaluation(
                        self.proxima_avaliacao
                    )
                    self.media = self._media_conceito_final[0]
                    self.avaliacoes_realizadas = self.current_stage
                    self.fim_estagio = self.get_fim_estagio(self._dias_interrompidos)
                    self.estado_avaliacao = 1
                    self.save()
                Notification.notify(
                    "gep-avaliacao-finalizada",
                    self.posse_servidor.servidor,
                    types=("SYS",),
                    **{"period": str(etapa)},
                )

    def bloqueia_etapa(self):
        """
        Bloqueia uma etapa de avaliação do estágio probatório.
        """
        self.bloqueada = True
        self.save()

    def calcula_suspensao_save_afastamentos(self):
        """
        Após criar uma licença, caso a licença/afastamento estejada dentro da etapa do estágio probatório do servidor modifica
        a data fim da etapa adicionando os dias que compreendem o periodo das licença/afastamento.
        Notifica o servidor que a etapa será prorrogada ao ser criado uma licença/afastamento que impacte no estágio probatório.
        Calcula sobre licenças/afastamentos que impactam no estágio probatório.
        """
        base = NewDateRange(self.init_evaluation(), self.proxima_avaliacao)
        range_licenca_total = (
            NewDateRange()
        )  # Guarda os dias caso o estagio interrompa imediatamente
        range_licenca_total2 = (
            NewDateRange()
        )  # Guarda os dias segundo o artigo 88 da lei 1818
        range_licenca_total3 = (
            NewDateRange()
        )  # Guarda os dias dos afastamentos que nao estao no artigo 88
        ESTADOS = [
            1,
            4,
        ]

        # ===============================Licensa3Dias===================================================
        licenca_3dias = (
            LicencaSaude3Dias.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in licenca_3dias:
            range_licenca3dias = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_3dias = NewDateRange()
            range_3dias += base.intersect(range_licenca3dias)
            range_licenca_total2 += range_3dias

            # if range_3dias.days > self.LICENCA_DOENCA:
            #     range_licenca_total+=range_3dias

        # ===============================LicencaSaudeJuntaMedica===================================================
        licenca_junta_medica = (
            LicencaSaudeJuntaMedica.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in licenca_junta_medica:
            range_licencajm = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_junta_medica = NewDateRange()
            range_junta_medica += base.intersect(range_licencajm)
            range_licenca_total2 += range_junta_medica

            if range_junta_medica.days > self.LICENCA_DOENCA:
                range_licenca_total += range_junta_medica

        # ===============================LicencaDoencaPessoaFamilia===================================================
        licenca_doenca_familia = (
            LicencaDoencaPessoaFamilia.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in licenca_doenca_familia:
            range_familia = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_f = NewDateRange()
            range_licenca_f += base.intersect(range_familia)
            range_licenca_total2 += range_licenca_f

            if range_licenca_f.days > self.LICENCA_DOENCA_PESSOA_FAMILIA:
                range_licenca_total += range_licenca_f

        # ================================LicencaAfastamentoConjuge==========================================================
        afastamento_conjuge = (
            LicencaAfastamentoConjuge.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )

        for licenca in afastamento_conjuge:
            range_conjuge = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_conjuge
            range_licenca_total2 += range_conjuge

        # =================================LicencaServicoMilitar=================================================
        servico_militar = (
            LicencaServicoMilitar.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in servico_militar:
            range_militar = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_militar
            range_licenca_total2 += range_militar

        # # =================================LicencaAdocao=================================================
        # adocao = LicencaAdocao.objects.filter(
        #     servidor__matricula=self.posse_servidor.servidor.matricula
        # ).exclude(Q(data_inicio__gt=base.last) | Q(data_fim__isnull=False, data_fim__lt=base.first)).exclude(estado__in = ESTADOS)
        # for licenca in adocao:
        #     range_adocao = NewDateRange(licenca.data_inicio, licenca.data_fim)
        #     range_licenca_total2 += range_adocao

        # ==================================LicencaMandatoClassista================================================
        afastamento_classista = (
            LicencaMandatoClassista.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_classista:
            range_classista = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total2 += range_classista

        # # ==================================AfastamentoOutroOrgao================================================
        # licenca_outro_orgao = AfastamentoOutroOrgao.objects.filter(
        #     servidor__matricula=self.posse_servidor.servidor.matricula
        # ).exclude(Q(data_inicio__gt=base.last) | Q(data_fim__isnull=False, data_fim__lt=base.first)).exclude(estado__in = ESTADOS)
        # for licenca in licenca_outro_orgao:
        #     range_outro_orgao = NewDateRange(licenca.data_inicio, licenca.data_fim)
        #     range_licenca_total += range_outro_orgao
        #     range_licenca_total3 += range_outro_orgao

        # ===================================AtividadePolitica===============================================
        licenca_politica = (
            LicencaAtividadePolitica.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in licenca_politica:
            range_politica = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_p = NewDateRange()
            range_licenca_p += base.intersect(range_politica)
            range_licenca_total2 += range_politica

            if range_licenca_p.days > self.LICENCA_ATIVIDADE_POLITICA:
                range_licenca_total += range_licenca_p

        # ==================================AfastamentoMandatoEletivo================================================
        afastamento_eletivo = (
            AfastamentoMandatoEletivo.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_eletivo:
            range_eletivo = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_eletivo
            range_licenca_total3 += range_eletivo

        # ===================================AfastamentoCursoConcurso===============================================
        afastamento_curso_concurso = (
            AfastamentoCursoConcurso.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_curso_concurso:
            range_curso_concurso = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_curso_concurso
            range_licenca_total3 += range_curso_concurso

        # ==================================AfastamentoPrisao================================================
        afastamento_prisao = (
            AfastamentoPrisao.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_prisao:
            range_prisao = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_prisao

        if (
            range_licenca_total2.days > 120
        ):  # se as somas das licencas previstas no artigo 88 da lei 1818 forem superiores a 120 dias
            if math.isinf(range_licenca_total2.days):
                self.bloqueia_etapa()
                self.notifica_afastamento_sem_fim()
                log.info(
                    " Bloqueado etapa. Afastamento do servidor %s não possui data fim."
                    % self
                )
            else:
                soma_licencas = range_licenca_total2.days + range_licenca_total3.days
                self.next_date_licenca(soma_licencas)
                self.notifica_afastamento(soma_licencas)
                if range_licenca_total2.days > 0:
                    log.info(
                        "Art 88, 1818 - Atualizando estagio de %s acrescentado %d dias."
                        % (self, soma_licencas)
                    )
                    log.info(
                        "PROXIMA AVALIACAO: de %s para %s"
                        % (
                            self.next_evaluation(),
                            base.first
                            + relativedelta(
                                months=self.configuracao.qtde_meses_entre_avaliacao,
                                days=soma_licencas,
                            ),
                        )
                    )
        else:
            if math.isinf(range_licenca_total.days):
                self.bloqueia_etapa()
                self.notifica_afastamento_sem_fim()
                log.info(
                    " Bloqueado etapa. Afastamento do servidor %s não possui data fim."
                    % self
                )
            else:
                self.next_date_licenca(range_licenca_total.days)
                self.notifica_afastamento(range_licenca_total.days)
                if range_licenca_total.days > 0:
                    log.info(
                        "Atualizando estagio de %s acrescentado %d dias."
                        % (self, range_licenca_total.days)
                    )
                    log.info(
                        "PROXIMA AVALIACAO: de %s para %s"
                        % (
                            self.next_evaluation(),
                            base.first
                            + relativedelta(
                                months=self.configuracao.qtde_meses_entre_avaliacao,
                                days=range_licenca_total.days,
                            ),
                        )
                    )

    def calcula_suspensao_afastamentos_cron(self):
        """
        Modifica a data final de uma etapa do estágio probatório, adicionando os dias referentes as licenças/afastamentos
        que estejam dentro do periodo da etapa do estágio.
        Calcula sobre licenças/afastamentos que impactam no estágio probatório.
        """
        base = NewDateRange(self.init_evaluation(), self.proxima_avaliacao)
        range_licenca_total = (
            NewDateRange()
        )  # Guarda os dias caso o estagio interrompa imediatamente
        range_licenca_total2 = (
            NewDateRange()
        )  # Guarda os dias segundo o artigo 88 da lei 1818, somando os dias
        range_licenca_total3 = (
            NewDateRange()
        )  # Guarda os dias dos afastamentos contemplados no artigo 20
        ESTADOS = [
            1,
            4,
        ]

        # ===============================Licensa3Dias===================================================
        licenca_3dias = (
            LicencaSaude3Dias.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in licenca_3dias:
            range_licenca3dias = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_3dias = NewDateRange()
            range_3dias += base.intersect(range_licenca3dias)
            range_licenca_total2 += range_3dias

            # if range_3dias.days > self.LICENCA_DOENCA:
            #     range_licenca_total+=range_3dias

        #  ===============================LicencaSaudeJuntaMedica===================================================
        licenca_junta_medica = (
            LicencaSaudeJuntaMedica.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in licenca_junta_medica:
            range_licencajm = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_junta_medica = NewDateRange()
            range_junta_medica += base.intersect(range_licencajm)
            range_licenca_total2 += range_junta_medica

            if range_junta_medica.days > self.LICENCA_DOENCA:
                range_licenca_total += range_junta_medica

        # ===============================LicencaDoencaPessoaFamilia===================================================
        licenca_doenca_familia = (
            LicencaDoencaPessoaFamilia.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in licenca_doenca_familia:
            range_familia = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_f = NewDateRange()
            range_licenca_f += base.intersect(range_familia)
            range_licenca_total2 += range_licenca_f

            if range_licenca_f.days > self.LICENCA_DOENCA_PESSOA_FAMILIA:
                range_licenca_total += range_licenca_f

        # ================================LicencaAfastamentoConjuge==========================================================
        afastamento_conjuge = (
            LicencaAfastamentoConjuge.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )

        for licenca in afastamento_conjuge:
            range_conjuge = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_conjuge
            range_licenca_total2 += range_conjuge

        # =================================LicencaServicoMilitar=================================================
        servico_militar = (
            LicencaServicoMilitar.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in servico_militar:
            range_militar = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_militar
            range_licenca_total2 += range_militar

        # # =================================LicencaAdocao=================================================
        # adocao = LicencaAdocao.objects.filter(
        #     servidor__matricula=self.posse_servidor.servidor.matricula
        # ).exclude(Q(data_inicio__gt=base.last) | Q(data_fim__isnull=False, data_fim__lt=base.first)).exclude(estado__in = ESTADOS)
        # for licenca in adocao:
        #     range_adocao = NewDateRange(licenca.data_inicio, licenca.data_fim)
        #     range_licenca_total2 += range_adocao

        # ==================================LicencaMandatoClassista================================================
        afastamento_classista = (
            LicencaMandatoClassista.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_classista:
            range_classista = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total2 += range_classista

        # # ==================================AfastamentoOutroOrgao================================================
        # licenca_outro_orgao = AfastamentoOutroOrgao.objects.filter(
        #     servidor__matricula=self.posse_servidor.servidor.matricula
        # ).exclude(Q(data_inicio__gt=base.last) | Q(data_fim__isnull=False, data_fim__lt=base.first)).exclude(estado__in = ESTADOS)
        # for licenca in licenca_outro_orgao:
        #     range_outro_orgao = NewDateRange(licenca.data_inicio, licenca.data_fim)
        #     range_licenca_total += range_outro_orgao
        #     range_licenca_total3 += range_outro_orgao

        # ===================================AtividadePolitica===============================================
        licenca_politica = (
            LicencaAtividadePolitica.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in licenca_politica:
            range_politica = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_p = NewDateRange()
            range_licenca_p += base.intersect(range_politica)
            range_licenca_total2 += range_politica

            if range_licenca_p.days > self.LICENCA_ATIVIDADE_POLITICA:
                range_licenca_total += range_licenca_p

        # ==================================AfastamentoMandatoEletivo================================================
        afastamento_eletivo = (
            AfastamentoMandatoEletivo.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_eletivo:
            range_eletivo = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_eletivo
            range_licenca_total3 += range_eletivo

        # ===================================AfastamentoCursoConcurso===============================================
        afastamento_curso_concurso = (
            AfastamentoCursoConcurso.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_curso_concurso:
            range_curso_concurso = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_curso_concurso
            range_licenca_total3 += range_curso_concurso

        # ==================================AfastamentoPrisao================================================
        afastamento_prisao = (
            AfastamentoPrisao.objects.filter(
                servidor__matricula=self.posse_servidor.servidor.matricula
            )
            .exclude(
                Q(data_inicio__gt=base.last)
                | Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_prisao:
            range_prisao = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_prisao

        if (
            range_licenca_total2.days > 120
        ):  # se as somas das licencas previstas no artigo 88 da lei 1818 forem superiores a 120 dias
            if math.isinf(range_licenca_total2.days):
                self.bloqueia_etapa()
                print(
                    " Bloqueado etapa de %s. Afastamento/Licença não possui data fim."
                    % self
                )
                log.info(
                    " Bloqueado etapa. Afastamento do servidor %s não possui data fim."
                    % self
                )
            else:
                soma_licencas = range_licenca_total2.days + range_licenca_total3.days
                self.next_date_licenca(soma_licencas)
                if range_licenca_total2.days > 0:
                    log.info(
                        "Art 88, 1818 - Atualizando estagio de %s acrescentado %d dias."
                        % (self, soma_licencas)
                    )
                    log.info(
                        "PROXIMA AVALIACAO: de %s para %s"
                        % (
                            self.next_evaluation(),
                            base.first
                            + relativedelta(
                                months=self.configuracao.qtde_meses_entre_avaliacao,
                                days=soma_licencas,
                            ),
                        )
                    )
        else:
            if math.isinf(range_licenca_total.days):
                self.bloqueia_etapa()
                print(
                    " Bloqueado etapa de %s. Afastamento/Licença não possui data fim."
                    % self
                )
                log.info(
                    " Bloqueado etapa. Afastamento do servidor %s não possui data fim."
                    % self
                )
            else:
                self.next_date_licenca(range_licenca_total.days)
                if range_licenca_total.days > 0:
                    print("Recalculando estagio de: %s." % self)
                    log.info(
                        "Atualizando estagio de %s acrescentado %d dias."
                        % (self, range_licenca_total.days)
                    )
                    log.info(
                        "PROXIMA AVALIACAO: de %s para %s"
                        % (
                            self.next_evaluation(),
                            base.first
                            + relativedelta(
                                months=self.configuracao.qtde_meses_entre_avaliacao,
                                days=range_licenca_total.days,
                            ),
                        )
                    )

    def desbloqueia_etapa(self):
        """
        Desbloqueia uma etapa de avaliação do estágio probatório
        """
        self.bloqueada = False
        self.save()

    @property
    def _meses_estabilizacao(self):
        return 36

    @property
    def dias(self):
        """
        Retorna a quantidade de dias que faltam até a avaliação de uma etapa.
        """
        return (
            (self.proxima_avaliacao - datetime.now().date()).days
            if self.proxima_avaliacao
            else "0"
        )

    @property
    def current_stage(self):
        """
        Retorna etapa atual do estágio probatório.
        """
        # retorna a etapa atual do servidor
        return (
            3
            if self.avaliacoes_realizadas == self._qtd_avaliacoes
            else self.avaliacoes_realizadas + 1
        )

    @property
    def _qtd_avaliacoes(self):
        """
        Retorna a quantidade de etapas de avaliação da configuração.
        """
        return self.configuracao.qtde_avaliacoes

    @property
    def _media_conceito_final(self):
        """
        Retorna a média e o conceito das avaliações das etapas.
        """
        media = 0
        conceito = None
        for avaliacoes in self.avaliacoes.all():
            media += avaliacoes.get_media_etapa()
        media_final = (media / int(self.avaliacoes.count())) if media > 0 else 0

        conceito = Conceito.objects.get(
            valor_inicial__lte=round(media_final, 2),
            valor_final__gte=round(media_final, 2),
        ).descricao

        return [media_final, conceito]

    @property
    def _media_conceito_max(self):
        media_geral = media_final = flag_count = 0
        for fator in self.configuracao.fator_avaliacao.all():
            soma = 0
            # conceito = None
            for quesito in fator.quesito_avaliacao.all():
                for elem in quesito.elemento.all():
                    valor = (
                        elem.elemento.alternativas.aggregate(
                            max_peso=models.Max("valor")
                        )["max_peso"]
                        or 0
                    )
                    soma += float(valor)
                media = float(soma) / float(quesito.count_elementos)
                media_geral += media
                flag_count += 1
        if media_geral != 0:
            media_final = media_geral / flag_count

        return round(media_final, 2)

    @property
    def _pct_conceito_final(self):
        return (
            (100 * self._media_conceito_final[0] / self._media_conceito_max)
            if self._media_conceito_max
            else 0
        )

    @property
    def _qtd_meses_estagio(self):
        return self.configuracao.qtde_meses_entre_avaliacao * self._qtd_avaliacoes

    @property
    def get_end_phase(self):
        """
        Retorna a data do fim do estágio
        """
        return self._inicio_estagio + relativedelta(months=+self._qtd_meses_estagio)

    @property
    def is_released(self):
        """
        Verifica se a etapa já esta liberada para avaliacao
        """
        now = self.getNow()
        if not self.proxima_avaliacao:
            return False
        elif now < (self.proxima_avaliacao - relativedelta(days=15)):
            #  elif now < (self.proxima_avaliacao - relativedelta(months= 1)):
            return False
        else:
            return True

    @property
    def is_finalized(self):
        """
        Verifica se foram finalizadas todas as etapas do estágio probatório
        """
        return (
            True
            if int(self.status) == 4
            and int(self.avaliacoes_realizadas) == self._qtd_avaliacoes
            else False
        )

    def init_evaluation(self):
        """
        Retorna o início de uma etapa do estágio probatório.
        """
        return self.ultima_avaliacao if self.ultima_avaliacao else self._inicio_estagio

    @property
    def julgamento_estagio_integrantes(self):
        for ce in self.comissao_estagio.all():
            return ce.apreciacao_comissao.filter().count()

    def get_situacao(self):
        """
        Retorna a situação do estágio probatório.
        """
        if int(self.status) == 1 and self.bloqueada:
            return "Bloqueada"
        if int(self.status) == 1 and not self.bloqueada:
            return "Em Andamento"
        elif int(self.status) == 2 and self.bloqueada:
            return "Aguardando Homologação"
        elif int(self.status) == 3 and self.bloqueada:
            return "Comissão Avaliadora"
        elif int(self.status) == 4 and self.bloqueada:
            return "Homologada"

    def _etapa_bloqueada(self):
        return True if self.bloqueada is True and int(self.status) == 1 else False

    def icons_gestor(self):
        """
        Icones do gestor de estágio
        """
        status = []
        now = self.getNow()
        if not self.proxima_avaliacao:
            if self.status == 2:
                status.append(
                    {
                        "iconCls": "icon-progressoes icon-progressoes-status-blocked",
                        "title": "Bloqueada/Finalizada",
                    }
                )
        elif now < (self.proxima_avaliacao - relativedelta(days=15)):
            status.append(
                {
                    "iconCls": "icon-progressoes icon-progressoes-status-offline",
                    "title": "Aguardando.",
                }
            )
        elif (
            (self.proxima_avaliacao - relativedelta(days=15))
            <= now
            <= self.proxima_avaliacao
        ):
            status.append(
                {
                    "iconCls": "icon-progressoes icon-progressoes-status",
                    "title": "Liberada",
                }
            )
        else:
            status.append(
                {
                    "iconCls": "icon-progressoes icon-progressoes-status-busy",
                    "title": "Atrasada",
                }
            )

        for aval in self.avaliacoes.all():
            if aval.avaliacao_realizada():
                status.append(
                    {
                        "iconCls": "icon-gep-chefe",
                        "title": "Avaliação já realizada pelo(a) chefe.",
                    }
                )
            if aval.avaliacao_realizada():
                qs = aval.manifestacao_servidor.all()
                if qs.exists():
                    status.append(
                        {
                            "iconCls": "icon-gep-servidor",
                            "title": "Manifestação já realizada pelo(a) servidor(a).",
                        }
                    )
                    status.append(
                        {
                            "iconCls": "icon-gep-warning",
                            "title": "Aguardando Finalização da etapa.",
                        }
                    )
            if aval.notificacao_existente():
                status.append(
                    {
                        "iconCls": "icon-gep-notificacao",
                        "title": "Notificação do chefe realizada.",
                    }
                )

        if self._etapa_bloqueada():
            status.append({"iconCls": "icon-gep-bloqueado", "title": "Etapa Bloqueada"})
        if int(self.status) == 2:
            status.append(
                {
                    "iconCls": "icon-estagio icon-checked",
                    "title": "Finalizada todas as etapas. Aguardando Homologação...",
                }
            )
        if int(self.status) == 4:
            status.append(
                {"iconCls": "icon-estagio icon-archive-impress", "title": "Homologado"}
            )

        return status

    def get_state_icons_comissao(self):
        """
        Icones da etapa de formação/avaliçao da comissão
        """
        status = self.icons_gestor()
        if self.liberado_para_formar_comissao():
            if (
                not self.comissao_estagio.filter().count()
                and self.liberado_para_formar_comissao()
            ):
                status.append(
                    {
                        "iconCls": "icon-gep-warning",
                        "title": "Aguardando formação da comissão.",
                    }
                )
            if (
                self.comissao_estagio.filter().count()
                and int(self.julgamento_estagio_integrantes) == 3
            ):
                status.append(
                    {
                        "iconCls": "icon-gep-group",
                        "title": "Integrantes da comissão: %s"
                        % self.comissao_estagio.filter()[0].get_integrantes_comissao(),
                    }
                )
                status.append(
                    {
                        "iconCls": "icon-gep-ok",
                        "title": "Todas as recomendações da comissão foram realizados.",
                    }
                )
                if self.comissao_estagio.filter()[0].decisao_chefe_orgao.exists():
                    status.append(
                        {
                            "iconCls": "icon-gep-decisao",
                            "title": "Decisão do Estágio Probatório realizada.",
                        }
                    )
                    if self.ciencia_decisao_estagio is None:
                        status.append(
                            {
                                "iconCls": "icon-gep-warning",
                                "title": "Aguardando ciênca da decisão do Estágio Probatório pelo servidor.",
                            }
                        )
                    else:
                        status.append(
                            {
                                "iconCls": "icon-gep-recomendou",
                                "title": "Ciênca da decisão do Estágio Probatório realizada pelo servidor.",
                            }
                        )
                else:
                    status.append(
                        {
                            "iconCls": "icon-gep-aguardando-decisao",
                            "title": "Aguardando decisão do Estágio Probatório.",
                        }
                    )

            elif (
                self.comissao_estagio.filter().count()
                and int(self.julgamento_estagio_integrantes) < 3
            ):
                status.append(
                    {
                        "iconCls": "icon-gep-group",
                        "title": "Integrantes da comissão: %s"
                        % self.comissao_estagio.filter()[0].get_integrantes_comissao(),
                    }
                )
                status.append(
                    {
                        "iconCls": "icon-gep-suspenso",
                        "title": "Aguardando recomendação dos integrantes da comissão.",
                    }
                )
                status.append(
                    {
                        "iconCls": "icon-gep-recomendacao-nao-realizada",
                        "title": "%s"
                        % self.comissao_estagio.filter()[
                            0
                        ].get_texto_aguardando_recomendar(),
                    }
                )

        return status

    def get_state_icons(self):
        """
        Retorna os icons.
        """
        status = self.get_state_icons_comissao()

        return status

    def getNow(self):
        """
        Retorna a data atual.
        """
        return datetime.now().date()

    def get_periodo_estagio(self):
        return "%s a %s " % (
            DateUtils.date_to_str(self._inicio_estagio),
            DateUtils.date_to_str(self.get_fim_estagio()),
        )

    @property
    def _inicio_estagio(self):
        return self.posse_servidor.data_exercicio

    def get_fim_estagio(self, dias=0):
        """
        Retorna a data fim do estágio probatório.
        """
        if self.fim_estagio:
            # return self.fim_estagio + relativedelta(days=dias)
            dt = self._inicio_estagio + relativedelta(
                months=self._meses_estabilizacao, days=dias
            )
            return dt - relativedelta(days=1)
        else:
            return (
                self._inicio_estagio
                + relativedelta(months=+self._meses_estabilizacao, days=-1)
                if dias == 0
                else self.get_fim_estagio() + relativedelta(days=dias)
            )

    def get_dias_ate_interrupcao(self, date):
        """
        Retorna a quantidade de dias entre a data de inicio de uma etapa com uma data passada como parametro.
        """
        if self.ultima_avaliacao:
            diferenca = (
                NewDateRange(self.ultima_avaliacao, date)
                if date >= self.ultima_avaliacao
                else timedelta(0)
            )
            return diferenca.days
        else:
            diferenca = (
                NewDateRange(self._inicio_estagio, date)
                if date >= self._inicio_estagio
                else timedelta(0)
            )
            return diferenca.days

    def get_faltas_injustificas(self):
        """
        Retorna a quantidade de dias de falta em uma etapa de avaliação.
        """
        horas_40 = 0
        horas_30 = 0
        horas_20 = 0
        dias_40 = 0
        dias_30 = 0
        dias_20 = 0
        dias = 0
        for falta in Falta.objects.filter(
            servidor__matricula=self.posse_servidor.servidor.matricula,
            data__range=(self.init_evaluation(), self.next_evaluation()),
        ):
            if falta.carga_horaria.quantidade == 40:
                horas_40 += falta.get_hours_float()
                dias_40 = horas_40 / 8
            elif falta.carga_horaria.quantidade == 30:
                horas_30 += falta.get_hours_float()
                dias_30 = horas_30 / 6
            elif falta.carga_horaria.quantidade == 20:
                horas_20 += falta.get_hours_float()
                dias_20 = horas_20 / 4
        dias = dias_40 + dias_30 + dias_20

        return "%.2f" % dias

    def get_wait_finish(self):
        """
        Verifica se está aguardando finalização de uma etapa pelo Departamento de RH.
        """
        rs = []
        for manif in self.manifestacao_servidor.all():
            rs.append(manif.estagio_avaliacao.periodo_avaliado)
        return True if self.current_stage in rs and self.bloqueada is False else False

    def get_integrantes_comissao(self):
        for ce in self.comissao_estagio.all():
            return ce.get_integrantes_comissao()

    def gera_chave(self):
        """
        Gera uma chave para ser usada ao responder um questionário.
        """
        chave = hashlib.sha224(
            bytes(self.posse_servidor.servidor.matricula)
        ).hexdigest()
        return chave

    def next_evaluation(self, data=None):
        """
        Retorna a proxima data para avaliacao de uma etapa
        """
        if not data:
            data = self.ultima_avaliacao or self._inicio_estagio
        qtd_mes = self.configuracao.qtde_meses_entre_avaliacao
        data_prox_avaliacao = data + relativedelta(months=+qtd_mes)
        return data_prox_avaliacao

    def next_date_licenca(self, days=0):
        """
        Retorna a proxima data de uma etapa a partir da quantidade de dias passados como parametro.
        """
        base = NewDateRange(
            self.ultima_avaliacao if self.ultima_avaliacao else self._inicio_estagio,
            self.proxima_avaliacao,
        )
        if self.proxima_avaliacao:
            nova_data_avaliacao = base.first + relativedelta(
                months=self.configuracao.qtde_meses_entre_avaliacao, days=days
            )
            self.proxima_avaliacao = nova_data_avaliacao
            self.fim_estagio = self.get_fim_estagio(days)
            self.bloqueada = False
            self.save()

    def notifica_avaliacao_liberada(self, chefe=None):
        """
        Notifica o chefe de um servidor que a avaliação de uma etapa do estágio foi liberada para avaliação.
        """
        if chefe:
            Notification.notify(
                "gep-avaliacao-liberada",
                chefe,
                types=("SYS",),
                **{
                    "from": str(self.posse_servidor.servidor),
                    "period": str(self.current_stage),
                },
            )

    def notifica_avaliacao_atrasada(self, chefe=None):
        """
        Notifica o chefe de deterimando servidor a avaliação de uma etapa está atradada.
        """
        if chefe:
            Notification.notify(
                "gep-avaliacao-atrasada",
                chefe,
                types=("SYS",),
                **{
                    "from": str(self.posse_servidor.servidor),
                    "period": str(self.current_stage),
                },
            )

    def notifica_manifestacao_atrasada(self):
        """
        Notifica o servidor que a manifestação do estágio está atrasada.
        """
        Notification.notify(
            "gep-manifestacao-atrasada",
            self.posse_servidor.servidor,
            types=("SYS",),
            **{
                # 'from': self.posse_servidor.servidor,
                "period": str(self.current_stage)
            },
        )

    def notifica_afastamento(self, dias=0):
        """
        Notifica o servidor que a etapa foi prorrogada em virtude de licença/afastamento
        """
        if dias > 0:
            Notification.notify(
                "gep-etapa-prorrogada",
                self.posse_servidor.servidor,
                types=("SYS",),
                **{
                    "period": str(self.current_stage),
                    "days": str(dias),
                },
            )

    def notifica_afastamento_sem_fim(self):
        """
        Notifica o servidor que a etapa foi bloqueada em virtude de licença/afastamento sem data de fim.
        """
        Notification.notify(
            "gep-licenca-sem-fim",
            self.posse_servidor.servidor,
            types=("SYS",),
            **{
                "period": str(self.current_stage),
            },
        )

    def notifica_liberacao_para_comissao(self):
        gestor_permission = ControllerPermission.objects.get(name="estagio-gestor")
        Notification.notify_all(
            "gep-aguardando-comissao",
            [user.servidor for user in gestor_permission.users.all() if user.servidor],
            types=("SYS",),
            **{
                "from": str(self._servidor_estagio),
            },
        )

    def liberado_para_formar_comissao(self):
        return (
            True
            if int(self.avaliacoes_realizadas) == self._qtd_avaliacoes
            and int(self.status) == 3
            else False
        )

    def valida_ciencia_decisao_estagio(self):
        return (
            True
            if self.liberado_para_formar_comissao()
            and self.comissao_estagio.exists()
            and self.comissao_estagio.filter()[0].is_julgado()
            else False
        )

    def valida_homologacao(self):
        return True if int(self.status) == 2 else False

    def approved(self):
        try:
            ecs = EstagioComissaoServidor.objects.get(estagio_prob_servidor=self)
            return ecs.get_internship_decision()
        except EstagioComissaoServidor.DoesNotExist:
            raise Exception("Comissão não encontrada!")
        except Exception as err:
            raise err
        return False

    def is_aprovado(self):
        try:
            ecs = EstagioComissaoServidor.objects.get(estagio_prob_servidor=self)
            return ecs.get_decisao_estagio()
        except EstagioComissaoServidor.DoesNotExist:
            return None

    def estabilizar(self, pub_estabilizacao):
        if self.approved():
            log.info(
                ">>> Anotando Estabilização do Servidor: %s" % self._servidor_estagio
            )
            est = MovimentacaoEstabilizacao()
            est.posse = self.posse_servidor
            est.data_vigencia = self.fim_estagio + relativedelta(days=1)
            est.publicacao_movimentacao = pub_estabilizacao
            est.save()

    def criar_apd(self):
        log.info(">>>> CRIANDO APD DO SERVIDOR :%s" % self.posse_servidor.servidor)
        from rh.apd.models import (
            Configuration as ConfApd,
            Commission as CommissionApd,
            PeriodicEvaluationPerformance,
        )

        conf = ConfApd.objects.latest("id")
        commission = CommissionApd.objects.latest("id")
        data_final_estagio = self.fim_estagio + relativedelta(days=1)
        PeriodicEvaluationPerformance(
            configuration=conf,
            commission=commission,
            employee=self.posse_servidor,
            start_date=data_final_estagio,
            end_date=(data_final_estagio + relativedelta(months=12)),
        ).save()

    def save(self, *args, **kargs):

        super(EstagioProbatorioServidor, self).save(*args, **kargs)

    @classmethod
    def homologate(klass, stage, publication=None):
        with transaction.atomic():
            estagios = EstagioProbatorioServidor.objects.filter(pk__in=stage)
            publicacao = Publicacao.objects.get(pk=int(publication))
            for estagio_servidor in estagios:
                log.info(estagio_servidor)
                if estagio_servidor.valida_homologacao():
                    estagio_servidor.publicacao_homologacao = publicacao
                    estagio_servidor.status = 4
                    estagio_servidor.save()
                    estagio_servidor.estabilizar(publicacao)
                    estagio_servidor.criar_apd()
                else:
                    raise Exception(
                        "%s não encontra-se apto a receber a homologação!"
                        % estagio_servidor.posse_servidor.servidor
                    )


@auditable("criado_em", "avaliador")
class EstagioAvaliacao(models.Model):

    class Meta:
        db_table = "gep_estagio_avaliacao"

    questionario_resposta = models.ForeignKey(
        QuestionarioResposta, related_name="estagio_avaliacao", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    avaliado = models.ForeignKey(
        EstagioProbatorioServidor, related_name="avaliacoes", on_delete=models.PROTECT
    )
    avaliador = models.ForeignKey(
        "rh.Servidor", related_name="avaliacao_estagio", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    periodo_avaliado = models.SmallIntegerField(default=0)
    status = models.BooleanField(null=False, default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    data_inicio_etapa = models.DateField(null=False)
    dias_interrompidos = models.SmallIntegerField(default=0)
    data_fim_etapa = models.DateField(null=False)
    cargo_avaliador = models.ForeignKey(
        "rh.Cargo", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    lotacao_avaliador = models.ForeignKey(
        "rh.Lotacao", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    cargo_avaliado = models.ForeignKey(
        "rh.Cargo", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    lotacao_avaliado = models.ForeignKey(
        "rh.Lotacao", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    finalizado_por = models.ForeignKey(
        "rh.Servidor", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    finalizado_em = models.DateTimeField(auto_now=True)
    media_comissao = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    observacao_comissao = models.TextField(blank=True, null=True)
    notificacoes = generic.GenericRelation(
        Notification, content_type_field="sender_ct", object_id_field="sender_id"
    )
    avaliador_externo = models.TextField(
        null=True, blank=True, verbose_name="Avaliador de Órgão Externo"
    )
    matricula_externo = models.TextField(
        null=True, blank=True, verbose_name="Matricula do Avaliador de Órgão Externo"
    )
    cargo_externo = models.TextField(
        null=True, blank=True, verbose_name="Cargo do Avaliador de Órgão Externo"
    )
    lotacao_externo = models.TextField(
        null=True, blank=True, verbose_name="Lotação do Avaliador de Órgão Externo"
    )
    data_avaliacao_externa = models.DateField(null=True, blank=True)

    def __str__(self):
        return "Avaliado: %s - Avaliador: %s - Periodo Avaliado: %d" % (
            self.avaliado.posse_servidor.servidor.pessoa_fisica.nome,
            self.avaliador,
            self.periodo_avaliado,
        )

    class EstagioFinalizado(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Esse servidor já foi avaliado em todos os períodos do estágio probatório.",
            )

    class AvaliacaoBloqueada(Exception):
        def __init__(self):
            Exception.__init__(self, "Avaliação bloqueada.")

    class AvaliacaoNaoLiberada(Exception):
        def __init__(self):
            Exception.__init__(self, "Esta avaliação ainda não está liberada.")

    class AvaliacaoRealizada(Exception):
        def __init__(self):
            Exception.__init__(self, "Avaliação para este período já foi realizada.")

    @property
    def get_periodo_avaliado(self):
        return self.periodo_avaliado

    @property
    def proximo_periodo(self):
        return self.periodo_avaliado + 1 if self.periodo_avaliado else 1

    def avaliacao_realizada(self):
        return (
            True
            if int(self.avaliado.current_stage) == int(self.periodo_avaliado)
            and self.avaliado.bloqueada is False
            else False
        )

    def get_situacao(self):
        return "Em andamento" if self.status else "Finalizada"

    def etapa_finalizada_por(self):
        """
        Grava quem finalizou a etapa de avaliação.
        """
        user = Servidor.objects.get(user=get_current_user())
        self.finalizado_por = user
        self.status = False
        self.save()

    def avisa_sobre_decisao(self):
        return (
            True
            if self.avaliado.comissao_estagio.exists()
            and self.avaliado.comissao_estagio.filter()[0].is_julgado()
            and self.avaliado.ciencia_decisao_estagio is None
            else False
        )

    def get_status(self):
        """
        Retorna icones de status.
        """
        status = []

        if (
            int(self.periodo_avaliado) == int(self.avaliado.current_stage)
            and self.status is True
        ):
            status.append(
                {
                    "iconCls": "icon-gep-chefe",
                    "title": "Avaliação já realizada pelo chefe.",
                }
            )
        if (
            int(self.periodo_avaliado) == int(self.avaliado.current_stage)
            and self.status is True
        ):
            qs = self.manifestacao_servidor.all()
            if qs.exists():
                status.append(
                    {
                        "iconCls": "icon-gep-servidor",
                        "title": "Manifestação já realizada pelo(a) servidor(a).",
                    }
                )
                status.append(
                    {
                        "iconCls": "icon-gep-warning",
                        "title": "Aguardando Finalização da etapa...",
                    }
                )
        if self.status is False:
            status.append(
                {"iconCls": "icon-gep-etapa-finalizada", "title": "Etapa concluída."}
            )

        if self.avisa_sobre_decisao():
            status.append(
                {
                    "iconCls": "icon-gep-warning",
                    "title": "Decisão do seu estágio probatório foi realizada. <br> Dê ciência do recebimento da informação.<br> Decisão proferida: %s "
                    % self.avaliado.comissao_estagio.filter()[
                        0
                    ].get_decisao_chefe_orgao_text(),
                }
            )
        elif self.avaliado.ciencia_decisao_estagio is not None:
            status.append(
                {
                    "iconCls": "icon-gep-recomendou",
                    "title": "Ciência da decisão realizada em %s."
                    % DateUtils.date_to_str(self.avaliado.ciencia_decisao_estagio),
                }
            )
        return status

    def get_media_etapa(self):
        if self.media_comissao:
            return round(self.media_comissao, 2)
        else:
            media_geral = 0
            media_final = 0
            flag_count = 0
            for fator in self.avaliado.configuracao.fator_avaliacao.all():
                soma = 0
                # conceito = None
                for quesito in fator.quesito_avaliacao.all():
                    for elem in quesito.elemento.all():
                        for resp in self.questionario_resposta.resposta_set.all():
                            if elem.elemento.id == resp.questao_id:
                                soma += resp.peso
                    media = float(soma) / float(quesito.count_elementos)
                    media_geral += media
                    flag_count += 1
            if media_geral != 0:
                media_final = media_geral / flag_count

            return round(media_final, 2)

    def get_max_media_etapa(self):
        if self.media_comissao:
            return round(self.media_comissao, 2)
        else:
            media_geral = media_final = flag_count = 0
            for fator in self.avaliado.configuracao.fator_avaliacao.all():
                soma = 0
                # conceito = None
                for quesito in fator.quesito_avaliacao.all():
                    log.debug("QUESITO: %s" % quesito)
                    for elem in quesito.elemento.all():
                        log.debug("ELEM: %s" % elem)
                        valor = (
                            self.questionario_resposta.resposta_set.aggregate(
                                max_peso=models.Max("peso")
                            )["max_peso"]
                            or 0
                        )
                        soma += valor
                    media = float(soma) / float(quesito.count_elementos)
                    media_geral += media
                    flag_count += 1
            if media_geral != 0:
                media_final = media_geral / flag_count

            return round(media_final, 2)

    def notifica_chefe_nao_concordancia(self, instance=None, mensagem=None):
        try:
            chefe = instance.posse_servidor.servidor.chefe_imediato
            Notification.notify(
                "gep-notifica-discordancia",
                chefe,
                sender=self,
                types=("SYS",),
                **{
                    "msg": str(mensagem),
                },
            )
            log.info("Notificando %s" % chefe)
        except Exception as e:
            log.info(e)
        # EstagioAvaliacao.objects.get(avaliado__posse_servidor__servidor__matricula=115612, periodo_avaliado=self.avaliado.current_stage)
        # Notification.notify('BEM_VINDO', self.avaliado._servidor_estagio, sender=self)

    def notificacao_existente(self):
        return (
            True
            if self.notificacoes.count()
            and self.periodo_avaliado == self.avaliado.current_stage
            else False
        )

    def save(self, *args, **kargs):
        self.avaliado.estado_avaliacao = 2
        self.avaliado.save()

        # LOTACAO E CARGO DO AVALIADO(SERVIDOR SUBORDINADO)
        self.cargo_avaliado = self.avaliado.posse_servidor.quadro.cargo
        self.lotacao_avaliado = (
            self.avaliado.posse_servidor.servidor.workplace_by_date()
        )

        # LOTACAO DO CHEFE AVALIADOR
        if self.avaliador:
            cargo_avaliador = (
                self.avaliador.posses_ativas.all()[0]
                if self.avaliador.posses_ativas
                else None
            )

            self.cargo_avaliador = (
                cargo_avaliador.quadro.cargo if cargo_avaliador else None
            )
            self.lotacao_avaliador = (
                self.avaliador.workplace_by_date()
                if self.avaliador.workplace_by_date()
                else None
            )
        else:
            try:
                self.avaliador = Servidor.objects.get(user__username="athenas")
            except Exception:
                self.avaliador = Servidor.objects.get(user=get_current_user)

        super(EstagioAvaliacao, self).save(*args, **kargs)


class FatorAvaliacao(models.Model):

    class Meta:
        ordering = ["descricao"]
        db_table = "gep_fator_avaliacao"

    descricao = models.CharField(max_length=300, null=False, default="")
    configuracao = models.ForeignKey(
        Configuracao, related_name="fator_avaliacao", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - %s " % (self.descricao, self.configuracao)


class QuesitoAvaliacao(models.Model):

    class Meta:
        db_table = "gep_quesito_avaliacao"

    fator_avaliacao = models.ForeignKey(
        FatorAvaliacao, related_name="quesito_avaliacao", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    elemento = models.ManyToManyField(Elemento, related_name="quesito_avaliacao")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s " % (self.fator_avaliacao, self.elemento)

    @property
    def count_elementos(self):
        return self.elemento.all().count()


@auditable("criado_em", "estagio_avaliacao")
class ManifestacaoEstagio(models.Model):
    class Meta:
        db_table = "gep_manifestacao_estagio"

    servidor = models.ForeignKey(
        EstagioProbatorioServidor,
        related_name="manifestacao_servidor",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    estagio_avaliacao = models.ForeignKey(
        EstagioAvaliacao, related_name="manifestacao_servidor", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    questionario_resposta = models.ForeignKey(
        QuestionarioResposta,
        related_name="manifestacao_servidor",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % (self.servidor)

    class ManifestacaoRealizada(Exception):
        def __init__(self):
            Exception.__init__(self, "Manifestação para este período já foi realizada.")

    def save(self, *args, **kargs):
        self.estagio_avaliacao.avaliado.estado_avaliacao = 3
        self.estagio_avaliacao.avaliado.save()
        super(ManifestacaoEstagio, self).save(*args, **kargs)


@receiver(post_save, sender=ApreciacaoComissao)
def signals_save_apreciacao_comissao(sender, instance=None, **kargs):
    try:
        # log.info(instance.comissao_servidor.is_liberado_para_decisao())
        if instance.comissao_servidor.is_liberado_para_decisao():
            try:
                # Notificar o gestor do orgão sobre estagio liberado para decisao
                gestor_permission = ControllerPermission.objects.get(
                    name="estagio-decisao-gestor"
                )
                Notification.notify_all(
                    "gep-decisao-liberada",
                    [
                        user.servidor
                        for user in gestor_permission.users.all()
                        if user.servidor
                    ],
                    types=("SYS",),
                    **{
                        "from": str(
                            instance.comissao_servidor.estagio_prob_servidor.posse_servidor.servidor
                        ),
                    },
                )
            except Exception as e:
                log.info(e)
    except Exception as e:
        log.debug(e)
