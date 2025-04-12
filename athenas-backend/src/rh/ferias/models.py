# -*- coding: utf-8 -*-


from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes import fields as generic
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_managers
from django.db import models, transaction
from django.db.models import Q


from contrib.daterange import NewDateRange
from contrib.decorator import ilru_cache, to_search, deprecated
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, employee_from_user, getLogger
from engine.notification.models import Message, Notification
from rh.afastamento.models import ACTIVE, BaseLicencaAfastamento, FeriasAfastamento
from rh.const import CANCELED
from rh.ferias.exceptions import (
    ConflictFeriasError,
    DataReferenciaNotFoundError,
    FeriasError,
    InvalidStateFeriasError,
    ValidateFeriasError,
)
from rh.models import (
    AnotacaoFerias,
    MovimentacaoPosse,
    MovimentacaoRequisicao,
    Publicacao,
    RequestMove,
    Servidor,
    ServidorLotacao,
)
from common.usefulday.models import ParseNonWorkingDay
from rh.utils import send_mail_and_notify
from standard.models import AuditTimestampModel, Choice
from django.conf import settings

import codecs

import datetime


log = getLogger("Ferias:Model")

TIPO_SERVIDOR = {
    "S": "Servidor",
    "M": "Membro",
}

MODO = (
    ("CONTINUO", "Contínuo"),
    ("ANUAL", "Anual"),
)

PERIODOS_LABEL_CHOICES = {1: "Único", 2: "Semestre", 3: "Quadrimestre", 4: "Trimestre"}

MESES = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO",
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO",
}

TIPO_ANOTACAO_FERIAS = {
    "HOMOLOGACAO": "Homologação",
    "MARCACAO": "Marcação",
    "ALTERACAO": "Alteração",
    "SUSPENSAO": "Suspensão",
    "INTERRUPCAO": "Interrupção",
    "INDEFINIDO": "Indefinido",
}

CONFIG_RH_FERIAS = {
    "AUTORIZACAO_CHEFIA_MEDIATA": False,
    "HOMOLOGACAO_SEM_AUTORIZACAO": True,
    "TIPO_DOC_HOMOLOGACAO_SERVIDOR": "Ato",
    "TIPO_DOC_HOMOLOGACAO_MEMBRO": "Portaria",
}

PAS_ALIBERACAO = 1
PAS_EMANDAMENTO = 2
PAS_FRUIDA = 4
PAS_INDENIZADA = 8

PASU_NOVO = 1
PASU_AUTORIZADO_CI = 2
PASU_HOMOLOGADO = 4
PASU_EMALTERACAO = 8
PASU_ALTERADO = 16
PASU_INTERROMPIDO = 32
PASU_SUSPENSO = 64
PASU_FRUINDO = 128
PASU_FRUIDO = 256
PASU_NAOAUTORIZADO = 512
PASU_SUBSTITUTO = 1024


ESTADO_PAS = {
    PAS_ALIBERACAO: "Aguardando Liberação p/ Marcação",
    PAS_EMANDAMENTO: "Em Andamento",
    PAS_FRUIDA: "Concluída",
    PAS_INDENIZADA: "Indenizado Total ou Parcialmente",
}

ESTADO_PASU = {
    PASU_NOVO: "Inclusão solicitada",
    PASU_AUTORIZADO_CI: "Autorizado",
    PASU_HOMOLOGADO: "Homologado",  # CRIAR AFASTAMENTO
    PASU_ALTERADO: "Alterado",  # APAGAR AFASTAMENTO
    PASU_EMALTERACAO: "Alteração solicitada",
    PASU_INTERROMPIDO: "Interrompido",  # ALTERAR AFASTAMENTO
    PASU_SUSPENSO: "Suspenso",  # APAGAR AFASTAMENTO
    PASU_FRUINDO: "Em fruição",
    PASU_FRUIDO: "Usufruído",
    PASU_NAOAUTORIZADO: "Não autorizado",
    PASU_SUBSTITUTO: "Substituto",
}

"""
    Máquina de estados responsável por validar as ações e estados válidos durante a marcação de férias
"""
PAS_SM = {
    PAS_ALIBERACAO: {"liberar": PAS_EMANDAMENTO},
    PAS_EMANDAMENTO: {
        "marcar": PAS_EMANDAMENTO,
        "desmarcar": PAS_EMANDAMENTO,
        "autorizar": PAS_EMANDAMENTO,
        "desautorizar": PAS_EMANDAMENTO,
        "suspender": PAS_EMANDAMENTO,
        "interromper": PAS_EMANDAMENTO,
        "homologar": PAS_EMANDAMENTO,
        "finalizar": PAS_FRUIDA,
        "indenizar": PAS_INDENIZADA,
    },
    PAS_FRUIDA: {},
    PAS_INDENIZADA: {},
}


PASU_SM = {
    PASU_NOVO: {
        "autorizar": PASU_AUTORIZADO_CI,
        "desmarcar": PASU_NOVO,
        "desautorizar": PASU_NAOAUTORIZADO,
        "homologar": PASU_HOMOLOGADO,
    },
    PASU_SUBSTITUTO: {
        "autorizar": PASU_AUTORIZADO_CI,
        "desautorizar": PASU_NAOAUTORIZADO,
    },
    PASU_AUTORIZADO_CI: {"homologar": PASU_HOMOLOGADO},
    PASU_HOMOLOGADO: {
        "suspender": PASU_SUSPENSO,
        "fruir": PASU_FRUINDO,
        "alterar": PASU_EMALTERACAO,
        "finalizar": PASU_FRUIDO,
    },
    PASU_EMALTERACAO: {"alterar": PASU_ALTERADO, "desautorizar": PASU_HOMOLOGADO},
    PASU_ALTERADO: {},
    PASU_INTERROMPIDO: {},
    PASU_SUSPENSO: {},
    PASU_FRUINDO: {
        "finalizar": PASU_FRUIDO,
        "interromper": PASU_INTERROMPIDO,
        "suspender": PASU_SUSPENSO,
    },
    PASU_FRUIDO: {"suspender": PASU_SUSPENSO, "interromper": PASU_INTERROMPIDO},
    PASU_NAOAUTORIZADO: {},
}

FRS_ICONS_THEME = {
    "indefinido": "/%s/static/rh/images/indefinido.png" % getattr(settings, "CONTEXT"),
    "operacoes": "/%s/static/rh/images/menu.png" % getattr(settings, "CONTEXT"),
    "notificar": "/%s/static/rh/images/notificado.png" % getattr(settings, "CONTEXT"),
    "aguardando": "/%s/static/rh/images/aguardando.png" % getattr(settings, "CONTEXT"),
    "adicionar": "/%s/static/rh/images/add.png" % getattr(settings, "CONTEXT"),
    "remover": "/%s/static/rh/images/remove.png" % getattr(settings, "CONTEXT"),
    "alterar": "/%s/static/rh/images/edit.png" % getattr(settings, "CONTEXT"),
    "liberado": "/%s/static/rh/images/" % getattr(settings, "CONTEXT"),
    "pago": "/%s/static/rh/images/ferias_paga.png" % getattr(settings, "CONTEXT"),
    "homologado": "/%s/static/rh/images/pasu_homologado.png"
    % getattr(settings, "CONTEXT"),
    "bloqueado": "/%s/static/rh/images/bloqueado.png" % getattr(settings, "CONTEXT"),
    "pas_gerenciar": "/%s/static/rh/images/pas_gerenciar.png"
    % getattr(settings, "CONTEXT"),
    "pasu_marcar": "/%s/static/rh/images/add_ferias.png" % getattr(settings, "CONTEXT"),
    "pasu_novo": "/%s/static/rh/images/pasu_novo.png" % getattr(settings, "CONTEXT"),
    "pasu_desmarcar": "/%s/static/rh/images/remove_ferias.png"
    % getattr(settings, "CONTEXT"),
    "pasu_suspenso": "/%s/static/rh/images/pasu_suspenso.png"
    % getattr(settings, "CONTEXT"),
    "pasu_interrompido": "/%s/static/rh/images/pasu_interrompido.png"
    % getattr(settings, "CONTEXT"),
    "pasu_conflito": "/%s/static/rh/images/ferias_conflito.png"
    % getattr(settings, "CONTEXT"),
    "pasu_autorizado": "/%s/static/rh/images/pasu_autorizado.png"
    % getattr(settings, "CONTEXT"),
    "pasu_naoautorizado": "/%s/static/rh/images/pasu_nao_autorizado.png"
    % getattr(settings, "CONTEXT"),
    "pasu_fruindo": "/%s/static/rh/images/fruindo.png" % getattr(settings, "CONTEXT"),
    "pasu_fruido": "/%s/static/rh/images/pas_fruido.png" % getattr(settings, "CONTEXT"),
    "pasu_alterado": "/%s/static/rh/images/pasu_alterado.png"
    % getattr(settings, "CONTEXT"),
    "pasu_emalteracao": "/%s/static/rh/images/pasu_emalteracao.png"
    % getattr(settings, "CONTEXT"),
    "conflito": "/%s/static/rh/images/conflito.png" % getattr(settings, "CONTEXT"),
    "help": "/%s/static/rh/images/help.png" % getattr(settings, "CONTEXT"),
    "blank": "/%s/static/rh/images/blank_icon.png" % getattr(settings, "CONTEXT"),
    "pas_indenizada": "/%s/static/rh/images/ferias_indenizada.png"
    % getattr(settings, "CONTEXT"),
    "pas_andamento": "/%s/static/rh/images/andamento.png"
    % getattr(settings, "CONTEXT"),
}

# ------------------------------------------------------------------------------------------------

# PAS_NOVO, PAS_LIBERADA, PAS_AUTORIZADA, PAS_USUFRUINDO, PAS_USUFRUIDA

# ------------------------------------------------------------------------------------------------


def notify(
    msg_or_mid, target, sender=None, types=["SYS"], notification_cfg="", **kargs
):
    """
    This method is responsible to identify wihch notification type will be send.
    This method based in standard.models.Configuration and configurations for 'ferias'.
    """

    try:
        with transaction.atomic():
            types = define_types(types, target)
            Notification.notify(msg_or_mid, target, sender=sender, types=types, **kargs)
    except Exception as err:
        log.exception(err)
        send_mail_and_notify(source="Err", message=str(err), err=err)


def define_types(types, target):
    """
    This method analises target param returns types with its new define.
    """
    try:
        raise Exception("testes")
        # cfg = Configuration.objects.get(application='ferias')
        # tipo_servidor = 'servidor' if not target.membro else 'membro'
        # deferimento = cfg.items.filter(key='%s_tipo_deferimento' % tipo_servidor, value='1').exists()
        # indeferimento = cfg.items.filter(key='%s_tipo_indeferimento' % tipo_servidor, value='1').exists()
        # notificacao_destaque = cfg.items.filter(key='%s_notificacao_destaque' % tipo_servidor, value='1').exists()
        # notificacao_email_institucional = cfg.items.filter(key='%s_notificacao_email_institucional' % tipo_servidor, value='1').exists()
        # tipo_deferimento = '%s_tipo_deferimento' % tipo_servidor
        # tipo_indeferimento = '%s_tipo_indeferimento' % tipo_servidor
        # if ((tipo_deferimento.find(notification_cfg) > -1 and deferimento) or
        #         (tipo_indeferimento.find(notification_cfg) > -1 and deferimento)):
        #     if notificacao_destaque:
        #         types.append('ONTOP')
        #     if notificacao_email_institucional:
        #         types.append('EMAIL')
    except Exception:
        pass
    return types


def dias_uteis_nacionais(date_range=None):
    """
    Este método calcula a quantidade de dias úteis de um NewDateRange descontando os feriados e fins de semana no
    período.
    """
    if date_range is None:
        raise Exception("NewDateRange não informado.")
    feriados = len(ParseNonWorkingDay.national_holidays(date_range=date_range))
    dias_uteis = 0
    for data in date_range.iter():
        if not NewDateRange.day_weekend(data):
            dias_uteis += 1
    dias_uteis = dias_uteis - feriados
    return dias_uteis if dias_uteis > 0 else 0


def check_limit(count, limit):
    return limit and count >= limit


class Configuracao(AuditTimestampModel):

    class Meta:
        ordering = ("nome",)
        db_table = "frs_configuracao"

    nome = models.CharField(
        help_text="Identificação da configuração",
        unique=1,
        verbose_name="Nome",
        max_length=100,
    )
    dias_por_periodo = models.SmallIntegerField(
        default="30",
        help_text="Quantidade de dias máxima que pode ser usufruído em um período.",
        verbose_name="Dias por período",
    )
    quantidade_periodos = models.SmallIntegerField(
        default=1,
        help_text="Quantidade de períodos em um ano (12 meses).Ex.: Servidor = 1 periodo por ano (12 meses), Membro= 2 períodos por ano",
        verbose_name="Períodos",
        choices=list(PERIODOS_LABEL_CHOICES.items()),
    )
    tipo_servidor = models.CharField(
        default="SERVIDOR",
        help_text="Para qual tipo de servidor será aplicada essa configuração de férias.",
        verbose_name="Tipo de servidor",
        choices=list(TIPO_SERVIDOR.items()),
        max_length=30,
    )
    max_divisoes = models.SmallIntegerField(
        default=2,
        help_text="Quantidade máxima de divisões que um período de férias pode ser usufruído.",
        verbose_name="Máximo de divisões",
    )
    min_dias_por_divisao = models.SmallIntegerField(
        default="10",
        help_text="Quantidade mínima de dias que pode ser dividida o período de usufruto.",
        verbose_name="Quantidade mínimo de dias por divisão",
    )
    modo = models.CharField(
        default="CONTINUO",
        help_text="""Modo de avaliação do período aquisitivo. ANUAL: perído por ano.
            CONTINUO: período de acordo com a data de exercício do servidor.""",
        verbose_name="Modo de aquisição",
        choices=MODO,
        max_length=30,
    )
    meses_max_fruicao = models.SmallIntegerField(
        default=12,
        help_text="Tempo máximo (em meses) para o gozo dos dias de férias. OBS.: XX meses - 1 dia",
        verbose_name="Máximo fruição (meses)",
    )
    meses_prescricao = models.SmallIntegerField(
        default=24,
        help_text="Tempo máximo (em meses) para o gozo dos dias de férias, antes de prescreverem.",
        verbose_name="Prescrição (meses)",
    )
    meses_exercicio = models.SmallIntegerField(
        default=12,
        help_text="Tempo de exercício, em meses, para adquirir direito a fruição de um periodo de férias",
        verbose_name="Tempo de exercício (meses)",
        blank=True,
    )
    # meses_aquisicao = models.SmallIntegerField(
    #     default=12,
    #     help_text="Tempo de exercício, em meses, para adquirir direito de um periodo de férias",
    #     verbose_name="Tempo de aquisição (meses)",
    #     blank=True
    # )
    dias_antecedencia_fruicao = models.SmallIntegerField(
        default=15,
        help_text="Dias de antecedência entre a marcação/alteração e a fruição",
        verbose_name="Antecedência fruição (dias)",
        blank=True,
    )
    bloquear_conflitos = models.BooleanField(
        default=False,
        help_text="Bloquear para marcações conflitantes com todos os substitutos",
        verbose_name="Bloquer conflitos",
    )
    exigir_autorizacao_chefia_mediata = models.BooleanField(
        default=False,
        help_text="Se é necessário que a chefia mediata autorize após a chefia imediata",
        verbose_name="Autorizacao chefia mediata",
    )

    def __str__(self):
        return self.nome


@to_search(
    [
        {"name": "ano_aquisicao", "type": "number"},
    ]
)
class PeriodoAquisitivo(AuditTimestampModel):

    class Meta:
        ordering = ("-ano_aquisicao", "-periodo")
        unique_together = (("ano_aquisicao", "configuracao", "periodo"),)
        db_table = "frs_periodoaquisitivo"

    ano_aquisicao = models.SmallIntegerField(
        help_text="Ano de aquisição do período",
        verbose_name="Ano de aquisição",
    )
    periodo = models.SmallIntegerField(
        default=1,
        help_text="""Período (único/semestre/quadrimestre) do ano que gerou esse período aquisitivo quando as férias são anuais.
            Ex.: 2 -> para férias anuais com período aquisitivo no segundo semestre do ano.""",
        verbose_name="Período",
    )
    data_publicacao = models.DateTimeField(
        help_text="Data em que o período aquisitivo foi publicado.",
        verbose_name="Data de Publicação",
        null=True,
        blank=True,
    )
    configuracao = models.ForeignKey(
        "Configuracao",
        on_delete=models.PROTECT,
        help_text="A configuração de férias utilizado para esse período aquisitivo.",
        verbose_name="Configuração de férias",
    )
    data_inicio_prev = models.DateField(
        help_text="Data para início das marcações de férias.",
        verbose_name="Início de Previsão",
    )
    data_fim_prev = models.DateField(
        help_text="Data para finalização das marcações de férias.",
        verbose_name="Final de Previsão",
        null=True,
        blank=True,
    )
    data_homologacao_prev = models.DateField(
        help_text="Data prevista para homologação do período aquisitivo.",
        verbose_name="Data de Homologação",
        null=True,
        blank=True,
    )
    bloqueado = models.BooleanField(
        default=False,
        help_text="Os servidores não poderão utilizar esse período. Ex.: Criação de período anteriores.",
        verbose_name="Bloqueado",
    )
    periodo_anterior = models.BooleanField(
        default=False,
        help_text="Informa se o período é anterior à data atual. Deve ser usado para períodos anteriores à utilização do sistema",
        verbose_name="Antigo",
    )
    mes_fruicao = models.SmallIntegerField(
        help_text="Mês para fruição coletiva, caso haja",
        verbose_name="Mês de fruição",
        default=14,
        choices=Choice.get_choices_for("ferias", "MONTHS"),
    )
    homologation_publication = models.ForeignKey(
        "rh.Publicacao",
        verbose_name="Publicação de homologação",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    def _get_data_limite_aquisicao(self):
        """
        Retorna a data limite para que o servidor/membro possa usufruir do período aquisitivo.
        Caso o PA possua "mes_fruicao", que indica PA coletivo, retorna o dia anterior ao mes_fruicao,
        caso nao possua "mes_fruicao" retorna a menor data para aquisicao do período
        """
        if self.mes_fruicao != 14:
            import calendar

            last_day = calendar.monthrange(self.ano_aquisicao, self.mes_fruicao)[1]
            return datetime.date(
                day=last_day, month=self.mes_fruicao, year=self.ano_aquisicao
            )
        mes = int((12 / self.configuracao.quantidade_periodos) * self.periodo)
        dia = 30 if mes == 6 else 31
        ano = (
            (self.ano_aquisicao - 1)
            if self.configuracao.modo == "CONTINUO"
            else self.ano_aquisicao
        )
        return datetime.date(day=dia, month=mes, year=ano)

    data_limite_aquisicao = property(_get_data_limite_aquisicao)

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, update=True):
        try:
            self.periodo_anterior = self.isanterior
            super(PeriodoAquisitivo, self).save(force_insert, force_update)
            if update:
                self.criar_periodo_aquisitivo_servidor()
        except Exception as err:
            log.exception(err)

    def periodo_display(self):
        if self.configuracao.modo == "CONTINUO":
            return ""
        else:
            return "%dº %s" % (
                self.periodo,
                PERIODOS_LABEL_CHOICES[self.configuracao.quantidade_periodos],
            )

    def __str__(self):
        if self.configuracao.modo == "CONTINUO":
            return "%d / %d" % (self.ano_aquisicao - 1, self.ano_aquisicao)
        else:
            ano_aquisicao = self.ano_aquisicao
            periodo = self.periodo_display()
            if self.mes_fruicao != 14:
                periodo = self.get_mes_fruicao_display()
            return "%s - %s" % (ano_aquisicao, periodo)

    def create_or_update_paservidor(self, servidor):
        data_limite = self.data_limite_aquisicao
        if servidor.tipo != self.configuracao.tipo_servidor:
            raise FeriasError(
                "Tipo de servidor(%s) diferente do tipo da configuração do período(%s)"
                % (servidor, self)
            )
        if not servidor.data_referencia_ferias:
            raise DataReferenciaNotFoundError(servidor)
        if servidor.data_referencia_ferias <= data_limite:
            p = self.paservidores.filter(servidor=servidor).first()
            if not p:
                pas = PeriodoAquisitivoFactory().create(servidor.indicativo)
                pas.servidor = servidor
                pas.periodo_aquisitivo = self
                if self.isanterior:
                    pas.bloqueado = True
            else:
                pas = p.pas

            pas.atualizar_data_referencia_ferias(force=True)
            pas.atualizar_dias_ferias()
            pas.atualiza_estado()
            if (
                pas.estado == PAS_ALIBERACAO
                and pas.periodo_aquisitivo.data_inicio_prev
                <= datetime.datetime.now().date()
            ):
                pas._liberar()
            return pas
        return None

    # OPTIMIZE
    # Criação do período aquisitivo para cada servidor que pode usufruir daquele período
    # NOTIFICATION Notificar caso haja algum problema na criação de um PeriodoAquisitivoServidor -> Responsável pelas férias
    def criar_periodo_aquisitivo_servidor(self):
        # Buscar por todos os servidores para criar o periodo aquisitivo para cada um
        for serv in Servidor.objects.filter(
            Q(ativo=True) & Q(tipo=self.configuracao.tipo_servidor)
        ):
            # Apenas para os servidores ativos e que são do mesmo tipo da configuração em questão.
            # Ex.: configuração= membro e servidor=membro
            try:
                self.create_or_update_paservidor(serv)
            except (
                DataReferenciaNotFoundError
            ):  # O servidor não possui data de referencia de férias
                log.warning(
                    "Deve ser notificado que esse servidor (%s) não possui data_referecia_ferias"
                    % serv
                )
            except FeriasError as err:
                log.warning(err)
            except Exception:
                log.exception(
                    "Erro ao criar periodo aquisitivo para o servidor: %s" % (serv)
                )

    def _get_isanterior(self):
        return self.data_limite_aquisicao <= datetime.datetime.now().date()

    isanterior = property(_get_isanterior)

    def _get_publicado(self):
        return self.data_publicacao is not None

    publicado = property(_get_publicado)

    def homologar(self, publication, force=False):
        """
        Homologar todos os PAS e PASUs criado pela escala de férias e
        gera uma anotação para cada PAS homologado
        """
        from engine.mq.models import Task
        from rh.ferias.tasks import homologate

        Task.start(
            homologate,
            pa=self.pk,
            force=force,
            publication=publication,
            user=get_current_user().pk,
            success="""<p>
                FÉRIAS - Homologação de férias finalizada. Verifique resultado no arquivo
                <a href="/athenas/FRSAcquisitionPeriod/file/?uuid=%(uuid)s">link</a>.
                </p>
                <p>
                Este arquivo está disponível para download até dia
                <span style="font-weight:bold">%(deadline)s</span>
                </p>""",
        )

    def homologate(self, publication, force=False, task=None):
        """
        Homologar todos os PAS e PASUs criado pela escala de férias e
        gera uma anotação para cada PAS homologado
        """

        # pas = []
        # if not self.data_publicacao or force:
        #     for p in self.paservidores.all():
        #         p.pas.homologar()
        # self.data_publicacao = datetime.datetime.now()
        def feedback(progress_message, progress, **kwargs):
            task.progress_message = progress_message % kwargs
            task.progress = progress
            task.save()

        def write_file(text, mode="w"):
            """
            Método responsável por escrever em file_write.
            """
            try:
                file_write = codecs.open(
                    "%s/homologacao-%s.csv" % (settings.CACHE_PATH, task.uuid),
                    mode,
                    "utf-8",
                )
                file_write.write(text)
                file_write.close()
            except Exception as err:
                log.exception(err)

        log.info("PA2: %s" % self)
        homologados = []
        result = self.paservidores.filter(Q(estado__in=[PAS_EMANDAMENTO]))
        total = result.count()
        count = 0
        feedback(
            "%(message_progress)s",
            ((100.0 * float(count)) / float(total)),
            message_progress="%s -> %s" % (count, total),
        )
        write_file("Arquivo com apenas erros.\n", mode="a")
        for pas in result:
            try:
                pas.homologar({"publicacao": publication})
                log.info("HOMOLOGADO: %s" % pas)
                task.info(msg=f"HOMOLOGADO: {pas}", type_of=1)
                homologados.append(pas.pk)
                notify("FRS_HOMOLOGACAO", pas.servidor, pas=self)
                count += 1
                feedback(
                    "%(message_progress)s",
                    ((100.0 * float(count)) / float(total)),
                    message_progress="%s -> %s" % (count, total),
                )
            except Exception as err:
                log.exception(err)
                message = "%s|%s|%s\n" % (pas.servidor, pas.periodo_aquisitivo, err)
                task.info(msg=f"{message}", type_of=3)
                write_file(message, mode="a")
        publication_obj = Publicacao.objects.get(pk=publication)
        self.homologation_publication = publication_obj
        self.data_publicacao = datetime.datetime.now()
        self.save(update=False)
        return len(homologados)


# ------------------------------------------------------------------------------------------------


@to_search(
    [
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "servidor__matricula", "type": "text"},
        {"name": "periodo_aquisitivo__ano_aquisicao", "type": "number"},
        {"name": "estado", "type": "choices"},
    ]
)
class PeriodoAquisitivoServidor(AuditTimestampModel):

    class Meta:
        ordering = ("servidor", "periodo_aquisitivo")
        unique_together = (("servidor", "periodo_aquisitivo"),)
        db_table = "frs_paservidor"

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)

    pas = generic.GenericForeignKey(fk_field="id")

    servidor = models.ForeignKey(
        "rh.Servidor",
        on_delete=models.CASCADE,
        help_text="O servidor que pode marcar férias para o período aquisitivo solicitado.",
        verbose_name="Servidor",
        related_name="periodos_aquisitivos",
    )
    periodo_aquisitivo = models.ForeignKey(
        "PeriodoAquisitivo",
        on_delete=models.PROTECT,
        help_text="O período aquisitivo refente a que o servidor tem direito.",
        verbose_name="Período aquisitivo",
        related_name="paservidores",
    )
    data_referencia = models.DateField(
        help_text="Data de referencia para o calculo do período aquisitivo .",
        verbose_name="Data de referência",
        blank=True,
    )
    data_inicio_aquisicao = models.DateField(
        help_text="", verbose_name="Início aquisição", blank=True
    )
    data_fim_aquisicao = models.DateField(
        help_text="Data de referencia para o calculo do período aquisitivo .",
        verbose_name="Fim aquisição",
        blank=True,
    )
    data_inicio_usufruto = models.DateField(
        help_text="Data mínima para que se possa usufruir esse período.",
        verbose_name="Início usufruto",
        blank=True,
    )
    data_fim_usufruto = models.DateField(
        help_text="Data máxima para que se possa usufruir esse período.",
        verbose_name="Fim usufruto",
        blank=True,
        null=True,
    )
    quantidade_dias = models.SmallIntegerField(
        default=30,
        help_text="Quantidade de dias a que o servidor tem direito para o período em questão.",
        verbose_name="Quantidade de dias",
    )
    estado = models.SmallIntegerField(
        help_text="Situação atual desse período aquisitivo",
        verbose_name="Situação",
        choices=list(ESTADO_PAS.items()),
        default=PAS_ALIBERACAO,
    )
    folha_evento_terco_constitucional = models.ForeignKey(
        "gfp.FolhaEvento",
        help_text="Referência à folha e evento que gerou o pagamento do terço constitucional para o período aquisitivo.",
        verbose_name="Folha Evento",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    pago_sem_folha = models.BooleanField(
        default=False,
        help_text="Informa se o PAS foi pago antes da entrada em vigencia do sistema e a folha não pode ser indicada com precisão.",
        verbose_name="Pago sem folha",
    )
    bloqueado = models.BooleanField(
        default=False,
        help_text="Informa se o PAS pode ser manipulado por alguém, normalmente é bloqueado quando se cria um período anterior.",
        verbose_name="Bloqueado",
    )
    paid_days = models.PositiveIntegerField(default=0, verbose_name="Dias indenizados")
    homologation_publication = models.ForeignKey(
        "rh.Publicacao",
        verbose_name="Publicação de homologação",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    notificacoes = generic.GenericRelation(
        Notification, content_type_field="sender_ct", object_id_field="sender_id"
    )

    def save(self, force_insert=False, force_update=False):
        # Adicionar o tipo da classe filha
        if not self.pk:
            self.content_type = ContentType.objects.get_for_model(self)
        if self.servidor and self.periodo_aquisitivo:
            super(PeriodoAquisitivoServidor, self).save(force_insert, force_update)

    def __str__(self):
        return "%s ( %s )" % (self.servidor, self.periodo_aquisitivo)

    def _conflicting_where_substitute_pasus_found(
        self, pasu_analysis, registry_exclude=[], limit=None
    ):
        pasus_conflicting = []
        return pasus_conflicting

    def validar_acao(self, acao):
        if (self.estado in PAS_SM) and (acao in PAS_SM[self.estado]):
            return PAS_SM[self.estado][acao]
        else:
            raise InvalidStateFeriasError(
                "Ação inválida: (%s) para (%s) não existe!"
                % (ESTADO_PAS[self.estado], acao)
            )

    # TODO Retirar a necessidade de transicação no PAS
    def transicao(self, acao, estado_dest, force=False):
        if not force:
            estados = self.validar_acao(acao)
        else:
            estados = True
        if force | (estados & estado_dest):
            self.estado = estado_dest
            self.save()
        else:
            raise InvalidStateFeriasError(
                "Transição inválida: [ESTADO: %s -> AÇÃO: %s -> ESTADO: %s]!"
                % (ESTADO_PAS[self.estado], acao, ESTADO_PAS[estado_dest])
            )

    def _liberar(self):
        self.transicao("liberar", PAS_EMANDAMENTO)
        self.atualiza_estado()
        if not self.bloqueado:
            notify(
                "FRS_LIBERACAO",
                self.servidor,
                self,
                pas=self.periodo_aquisitivo,
                data_inicio_usufruto=self.data_inicio_usufruto.strftime("%d/%m/%Y"),
            )

    #   TODO Retirar o force dos métodos suspender e interromper, pois sempre serão via administrativa.
    def _suspender(self, pasu, force=False, params={}, anotar=True):
        employee = employee_from_user(get_current_user())
        pasu.suspenso_em = datetime.datetime.now()
        pasu.suspenso_por = employee
        pasu.transicao("suspender", PASU_SUSPENSO, True)
        self.data_fim_usufruto = None
        self.transicao("suspender", PAS_EMANDAMENTO, True)
        self.atualiza_estado()
        pasus_id = []
        for alt_out in pasu.alteracao_out.filter():
            pasus_id += [new_pasu.pk for new_pasu in alt_out.novos_pasus.filter()]
        self.autorizar_usufruto(
            pasus_id,
            employee.pk,
            autorizar=False,
            publicacao_id=0,
            admin=force,
            anotar=False,
        )
        if pasu.suspenso and anotar:
            try:
                msg = Message.objects.get(mid="FRS_ANOTACAO_SUSPENSAO")
                publicacao = Publicacao.objects.get(id=params["publicacao"])
            except Exception as e:
                log.debug("SUSPENDER: %s" % e)
            else:
                params["texto"] = msg.formated(
                    {
                        "pa": "%s" % self.periodo_aquisitivo,
                        "doc": "%s %s/%s"
                        % (
                            publicacao.get_tipo_display(),
                            publicacao.numero,
                            publicacao.ano,
                        ),
                        "data_doc": publicacao.data_expedicao.strftime("%d/%m/%Y"),
                        "data_inicio": pasu.data_inicio.strftime("%d/%m/%Y"),
                        "data_fim": pasu.data_fim.strftime("%d/%m/%Y"),
                        "dias": pasu.dias,
                    }
                )
                params["tipo_documento"] = ""
                params["resumo"] = "Suspensão de Férias %s" % (self.periodo_aquisitivo)
                params["periodo"] = "%s" % (self.periodo_aquisitivo)
                params["tipo"] = "SUSPENSAO"
                params["identificador"] = "%s" % pasu.id
                if publicacao:
                    params["publicacao"] = publicacao.id
                self.anotar_ferias(params)

    def _interromper(self, pasu, data, force=False, params={}, anotar=True):
        data_inicio, data_fim = pasu.data_inicio, pasu.data_fim
        pasu._interromper(data, True)
        self.data_fim_usufruto = None
        self.transicao("interromper", PAS_EMANDAMENTO, True)
        self.atualiza_estado()
        if pasu.interrompido and anotar:
            try:
                msg = Message.objects.get(mid="FRS_ANOTACAO_INTERROMPER")
                publicacao = Publicacao.objects.get(id=params["publicacao"])
            except Exception as err:
                log.debug("INTERRUPCAO: %s" % err)
            else:
                params["texto"] = msg.formated(
                    {
                        "pa": "%s" % self.periodo_aquisitivo,
                        "doc": "%s %s/%s"
                        % (
                            publicacao.get_tipo_display(),
                            publicacao.numero,
                            publicacao.ano,
                        ),
                        "data_doc": publicacao.data_expedicao.strftime("%d/%m/%Y"),
                        "data_inicio": "%s" % data_inicio.strftime("%d/%m/%Y"),
                        "data_fim": "%s" % data_fim.strftime("%d/%m/%Y"),
                        "dias": (data_fim - data_inicio).days + 1 - pasu.dias,
                        "data": data.strftime("%d/%m/%Y"),
                    }
                )
                params["tipo_documento"] = ""
                params["resumo"] = "Interrupção de Férias %s" % (
                    self.periodo_aquisitivo
                )
                params["periodo"] = "%s" % (self.periodo_aquisitivo)
                params["tipo"] = "INTERRUPCAO"
                params["identificador"] = "%s" % pasu.id
                if publicacao:
                    params["publicacao"] = publicacao.id
                self.anotar_ferias(params)

    @deprecated
    def _homologar(self):
        for pasu in self.usufrutos.filter(estado__in=[PASU_AUTORIZADO_CI, PASU_NOVO]):
            pasu.homologado = True
        self.transicao("homologar", PAS_AFRUICAO)

    def _marcar(self, parcelas):
        count_new_pasus = len(parcelas)
        dias_marcados = self.dias_marcados
        count_pasus_changing = 0
        for parcela in parcelas:
            pasu = self.adicionar_usufruto(
                parcela["data_inicio"],
                parcela["data_fim"],
                count_new_pasus=count_new_pasus,
                dias_marcados=dias_marcados,
                count_pasus_changing=count_pasus_changing,
            )
            dias_marcados += pasu.dias
            count_pasus_changing += 1
        self.transicao("marcar", PAS_EMANDAMENTO)

    @transaction.atomic
    def _indenizar(self, data=None):
        data = datetime.datetime.now().date() if not data else data
        log.debug(">>>>>> IDENIZANDO PAS %s" % self)
        # Apagando usufrutos marcados e não autorizados
        for pasu in self.usufrutos.filter(
            estado__in=[
                PASU_NOVO,
            ]
        ):
            log.debug("DELETANDO PASU %s" % pasu)
            pasu.delete()
        # Revertendo alterações solicitadas e não autorizadas
        for alt in AlteracaoPASU.objects.filter(pas=self, autorizado_em=None):
            log.debug("DELETANDO ALTERACAO %s" % alt)
            alt.delete()
        # Suspendendo usufrutos pendentes de fruição
        for pasu in self.usufrutos.filter(estado__in=[PASU_HOMOLOGADO, PASU_FRUINDO]):
            log.debug("SUSPENDENDO PASU %s" % pasu)
            self._suspender(pasu)

        dias_indenizados = self.quantidade_dias - self.dias_usufruidos

        # Gerando anotação de indenização
        try:
            msg = Message.objects.get(mid="FRS_INDENIZACAO_PAS")
        except Exception as e:
            log.debug("INDENIZAÇÃO: %s" % e)
        else:
            params = {}
            params["texto"] = msg.formated(
                {
                    "pa": "%s" % self.periodo_aquisitivo,
                    "dias": dias_indenizados,
                    "info": "",
                }
            )
            params["tipo_documento"] = ""
            params["resumo"] = "Indenização de Férias %s" % (self.periodo_aquisitivo)
            params["periodo"] = "%s" % (self.periodo_aquisitivo)
            params["tipo"] = "INDENIZACAO"
            params["identificador"] = "%s" % self.id
            # if publicacao:
            #     params['publicacao'] = publicacao.id
            self.anotar_ferias(params)

        self.transicao("indenizar", PAS_INDENIZADA, True)
        log.debug("<<<<<< PAS INDENIZADO")
        return dias_indenizados

    def homologar(self, params={}):
        if self.dias_marcados == self.quantidade_dias and self.estado in [
            PAS_EMANDAMENTO
        ]:  # As férias foram completamente marcadas
            estados = (
                [PASU_AUTORIZADO_CI, PASU_NOVO]
                if CONFIG_RH_FERIAS["HOMOLOGACAO_SEM_AUTORIZACAO"]
                else [
                    PASU_AUTORIZADO_CI,
                ]
            )
            for pasu in self.usufrutos.filter(estado__in=estados):
                pasu.homologado = True
            self.transicao("homologar", PAS_EMANDAMENTO)
            self.create_annotation(params=params)

    def create_annotation(self, params={}, pasus_id=[]):
        try:
            msg = Message.objects.get(mid="FRS_ANOTACAO_HOMOLOGA")
        except Exception as err:
            log.debug("HOMOLOGAR: %s" % err)
        else:
            parcelas = ""
            publicacao = Publicacao.objects.get(id=params["publicacao"])
            parcelas = ""
            idx = 1
            pos = ""
            params = {}
            usufrutos = self.usufrutos.filter()
            if pasus_id:
                usufrutos = usufrutos.filter(pk__in=pasus_id)
            for pasu in usufrutos.order_by("data_inicio"):
                if usufrutos.exists():
                    pos = "%sª" % idx
                    idx += 1
                parcelas += "<br />%s parcela: %s a %s (%s dias)" % (
                    pos,
                    pasu.data_inicio.strftime("%d/%m/%Y"),
                    pasu.data_fim.strftime("%d/%m/%Y"),
                    pasu.dias,
                )
            params["texto"] = msg.formated(
                {
                    "parcelas": parcelas,
                    "pa": self.periodo_aquisitivo,
                    "data_homologacao": "%s"
                    % publicacao.data_expedicao.strftime("%d/%m/%Y"),
                    "publicacao": "%s" % publicacao,
                }
            )
            params["tipo_documento"] = 1  # ATO
            params["resumo"] = self.scale_summary_annotation()
            params["periodo"] = "%s" % (self.periodo_aquisitivo)
            params["tipo"] = "HOMOLOGACAO"
            params["identificador"] = "%s" % self.id
            params["publicacao"] = publicacao.id
            return self.anotar_ferias(params)

    def scale_summary_annotation(self):
        return "Escala de Férias %s" % (self.periodo_aquisitivo)

    def anotar_ferias(self, params):
        af = AnotacaoFerias()
        if "tipo" in params:
            af.tipo = params["tipo"]
        if "identificador" in params:
            af.identificador = params["identificador"]
        af.servidor = self.servidor
        af.publicacao_id = params["publicacao"] if "publicacao" in params else None
        af.tipo_documento = (
            params["tipo_documento"] if "tipo_documento" in params else 100
        )  # 100->Documento Digital
        if not af.publicacao:
            af.numero_documento = (
                params["numero_documento"] if "numero_documento" in params else None
            )
            af.data_documento = (
                params["data_documento"] if "data_documento" in params else None
            )
        af.resumo = params["resumo"] if "resumo" in params else ""
        af.texto = params["texto"] if "texto" in params else ""
        af.periodo = params["periodo"] if "periodo" in params else "---"
        af.save()
        return af

    def _fruir(self):
        self.atualiza_PASUs()
        if self.dias_usufruidos == self.quantidade_dias:
            self.transicao("finalizar", PAS_FRUIDA)

    def _finalizar(self):
        self.atualiza_PASUs()
        if self.dias_usufruidos == self.quantidade_dias:
            self.transicao("finalizar", PAS_FRUIDA)

    def atualiza_estado(self, atualiza_pasus=True):
        if atualiza_pasus:
            self.atualiza_PASUs()
        if self.dias_usufruidos == self.quantidade_dias:
            self.estado = PAS_FRUIDA
        else:
            self.estado = PAS_EMANDAMENTO
        self.save()

    def atualiza_PASUs(self, force=False):
        for pasu in self.usufrutos.filter(
            estado__in=[PASU_NOVO, PASU_AUTORIZADO_CI, PASU_HOMOLOGADO]
        ):
            if pasu.data_fim < datetime.datetime.now().date():
                pasu.estado = PASU_FRUIDO
                log.debug("FRUINDO: %s" % pasu.data_fim.strftime("%d/%m/%Y"))
            elif pasu.data_inicio < datetime.datetime.now().date():
                pasu.estado = PASU_FRUINDO
                log.debug("FRUIDA: %s" % pasu.data_inicio.strftime("%d/%m/%Y"))
            elif force:
                pasu.estado = PASU_HOMOLOGADO
                log.debug("HOMOLOGADO: %s" % pasu.data_inicio.strftime("%d/%m/%Y"))
            pasu.save()

    def validate_pasu_retroativo(self, pasu, force=False):
        if not force and pasu.data_inicio <= datetime.datetime.now().date():
            raise ValidateFeriasError(
                "Sua parcela não pode ser anterior à data de hoje. Para marcação retroativa solicite ao GESTÃO DE PESSOAS."
            )
        return pasu

    def validate_pasu_menor_dias_adquiridos(self, pasu, exclude_pasus=[]):
        dias_pasus_exclude = 0
        for p in exclude_pasus:
            dias_pasus_exclude += PeriodoAquisitivoServidorUsufruto.objects.get(
                pk=p
            ).dias
        # VALIDATE Verifica se a quantidade de dias solicitada não está maior que a quantidade adquirida
        if (
            self.dias_marcados + pasu.dias - dias_pasus_exclude
            > self.quantidade_dias - self.paid_days
        ):
            raise ValidateFeriasError(
                "Quantidade de dias marcados (%s) está superior a quantidade de dias adquiridos (%s)"
                % (
                    self.dias_marcados
                    + pasu.dias
                    - self.dias_usufruidos
                    - dias_pasus_exclude,
                    self.quantidade_dias - self.dias_usufruidos - self.paid_days,
                )
            )
        return pasu

    def validate_dias_aprovisionados(self):
        """
        Este método verifica se a quantidade de dias marcados é maior que a quantidade máxima.
        """
        if self.dias_aprovisionados > self.quantidade_dias:
            raise ValidateFeriasError(
                "Quantidade de dias marcados (%s) está superior a quantidade de dias adquiridos (%s)"
                % (self.dias_aprovisionados, self.quantidade_dias)
            )
        return True

    def validate_conflito_interno(self, pasu, exclude_pasus=[]):
        conflitos = [
            conflito
            for conflito in self.conflitos_usufruto_servidor(pasu, exclude_pasus)
        ]
        if len(conflitos) > 0:
            message = ""
            for con in conflitos:
                message = "%s\n%s" % (message, con)
            raise ValidateFeriasError(
                "A parcela que está tentando marcar conflita com outra já marcada %s"
                % message
            )
        return pasu

    def validate_candidate(self, candidates=[]):
        """
        This method validates the PeriodoAquisitivoServidorUsufruto candidates to.
        """
        conflict = []
        for candidate in candidates:
            for cand in candidates:
                if (
                    candidate != cand
                    and NewDateRange(candidate.data_inicio, candidate.data_fim)
                    .intersect(NewDateRange(cand.data_inicio, cand.data_fim))
                    .days
                    > 0
                ):
                    conflict.append(candidate)
        return conflict

    def validate_conflito_externo(self, pasu, force=False):
        if not force:
            conflitos = self.conflito(pasu)
            if conflitos is not False:
                mensagem = """Sua parcela não pode ser marcada para esta data, pois está em conflito com todos os seus
                    substitutos. Infringindo, contudo, o Art. 3° do Ato 220/2005."""
                for conflito in conflitos:
                    mensagem += "%s - %s" % (
                        conflito.periodo_aquisitivo_servidor.servidor,
                        conflito,
                    )
                raise ValidateFeriasError(mensagem)
        return pasu

    def validate_antecedencia_fruicao(self, pasu, force=False):
        antecedencia_valida = True
        dias_antecedencia_fruicao = (
            self.periodo_aquisitivo.configuracao.dias_antecedencia_fruicao
        )
        data_marcacao = datetime.datetime.now().date()
        data_fruicao = pasu.data_inicio
        mensagem = "Sua parcela deve ser marcada com, no mínimo, quinze (15) dias de antecedência do início da fruição."
        dias_uteis = (
            dias_uteis_nacionais(date_range=NewDateRange(data_marcacao, data_fruicao))
            if data_marcacao <= data_fruicao
            else 0
        )
        if self.servidor.tipo == "M" and (
            pasu.data_inicio - datetime.timedelta(dias_antecedencia_fruicao)
            <= data_marcacao
        ):
            antecedencia_valida = False
        elif self.servidor.tipo == "S" and dias_antecedencia_fruicao > dias_uteis:
            antecedencia_valida = False
            mensagem = (
                "Sua parcela deve ser marcada com, no mínimo, quinze (%s) dias úteis de antecedência do início da fruição."
                % dias_antecedencia_fruicao
            )
        if not force and not antecedencia_valida:
            log.debug(
                "I: %s | M: %s | A: %s(%s)"
                % (
                    pasu.data_inicio,
                    data_marcacao,
                    pasu.data_inicio - datetime.timedelta(dias_antecedencia_fruicao),
                    datetime.timedelta(dias_antecedencia_fruicao),
                )
            )
            raise ValidateFeriasError(mensagem)

    def validar_usufruto(
        self,
        pasu,
        force=False,
        exclude_pasus=[],
        count_new_pasus=0,
        dias_marcados=0,
        count_pasus_changing=0,
    ):
        dias_pasus_exclude = 0
        for p in exclude_pasus:
            dias_pasus_exclude += PeriodoAquisitivoServidorUsufruto.objects.get(
                pk=p
            ).dias
        # if self.servidor.tipo == 'M':
        #     self.validate_antecedencia_fruicao(pasu, force)
        self.validate_antecedencia_fruicao(pasu, force)
        self.validate_pasu_retroativo(pasu, force)
        self.validate_pasu_menor_dias_adquiridos(pasu, exclude_pasus)
        self.validate_dias_aprovisionados()

        # VALIDATE Verifica se ainda possui uma parcela disponível ou se esse periodo aquisitivo servidor ja teve alguma
        # parcela interrompida, pois caso haja, a parcela a ser marcada deve COMPLETAR a quantidade de dias restantes
        # qtd_dias_restante = self.quantidade_dias - self.dias_marcados + dias_pasus_exclude - self.paid_days
        qtd_dias_restante = (
            self.quantidade_dias - dias_marcados + dias_pasus_exclude - self.paid_days
        )
        if not force:
            qtd_pasu_valido = self.usufrutos.filter(
                estado__in=[
                    PASU_NOVO,
                    PASU_AUTORIZADO_CI,
                    PASU_HOMOLOGADO,
                    PASU_EMALTERACAO,
                    PASU_FRUINDO,
                    PASU_FRUIDO,
                    PASU_INTERROMPIDO,
                ]
            ).count()
            qtd_pasu_disponivel = (
                self.periodo_aquisitivo.configuracao.max_divisoes
                - (qtd_pasu_valido - len(exclude_pasus))
                - count_pasus_changing
            )
            if qtd_pasu_disponivel == 0 or qtd_pasu_disponivel == 1:
                if pasu.dias != qtd_dias_restante:
                    raise ValidateFeriasError(
                        "Você deve marcar todos os %s dias restantes nessa parcela."
                        % (qtd_dias_restante)
                    )

            ultima_parcela = count_new_pasus == 1 and (qtd_pasu_disponivel in (0, 1))
            min_dias_por_divisao = (
                self.periodo_aquisitivo.configuracao.min_dias_por_divisao
            )
            diff = self.quantidade_dias - min_dias_por_divisao
            if abs(dias_pasus_exclude - self.dias_nao_marcados) != pasu.dias or (
                abs(dias_pasus_exclude - self.dias_nao_marcados) == pasu.dias
                and (qtd_dias_restante - pasu.dias) > 0
            ):
                # VALIDATE Verifica se a quantidade de dias é a quantidade de dias adquiridos ou se é maior que a quantidade mínima permitida
                if (
                    not (
                        pasu.dias == self.quantidade_dias
                        or (min_dias_por_divisao <= pasu.dias <= diff)
                    )
                ) and not ultima_parcela:
                    raise ValidateFeriasError(
                        "Você deve marcar uma parcela de %d dias ou entre %d e %d"
                        % (self.quantidade_dias, min_dias_por_divisao, diff)
                    )
        # VALIDATE: Quantidade de dias < do q os dias adquiridos para o período
        if not self.periodo_aquisitivo.periodo_anterior:
            if self.data_fim_usufruto:
                log.debug(self.data_fim_usufruto)
                if not (
                    self.data_inicio_usufruto
                    <= pasu.data_inicio
                    <= pasu.data_fim
                    <= self.data_fim_usufruto
                ):
                    raise ValidateFeriasError(
                        "Suas férias só podem ser usufruídas entre %s e %s"
                        % (
                            self.data_inicio_usufruto.strftime("%d/%m/%Y"),
                            self.data_fim_usufruto.strftime("%d/%m/%Y"),
                        )
                    )
            else:
                if not (self.data_inicio_usufruto <= pasu.data_inicio):
                    raise ValidateFeriasError(
                        "Suas férias só podem ser usufruídas após %s"
                        % (self.data_inicio_usufruto.strftime("%d/%m/%Y"))
                    )
        self.validate_conflito_interno(pasu, exclude_pasus)
        self.validate_conflito_externo(pasu, force)
        return pasu

    def validate_installment_amount(self, pasu_new=[], exclude_pasus=[]):
        qtd_dias_alterados = 0
        for excl in self.usufrutos.filter(pk__in=exclude_pasus):
            qtd_dias_alterados += excl.dias

        qtd_dias_restante = (
            self.quantidade_dias
            - (self.dias_marcados - qtd_dias_alterados)
            - self.paid_days
        )
        qtd_pasu_valido = self.usufrutos.filter(
            estado__in=[
                PASU_NOVO,
                PASU_AUTORIZADO_CI,
                PASU_HOMOLOGADO,
                PASU_EMALTERACAO,
                PASU_FRUINDO,
                PASU_FRUIDO,
                PASU_INTERROMPIDO,
            ]
        ).count() - len(exclude_pasus)
        total_pasu_new = len(pasu_new)
        total_pasu_new += self.usufrutos.filter(estado=PASU_NOVO).count()
        qtd_pasu_disponivel = (
            self.periodo_aquisitivo.configuracao.max_divisoes - qtd_pasu_valido
        )
        ultima_parcela = (
            len(pasu_new) == 1
            and qtd_dias_restante
            == NewDateRange(
                pasu_new[0].get("data_inicio"), pasu_new[0].get("data_fim")
            ).days
        )
        if qtd_pasu_disponivel < total_pasu_new:
            if not ultima_parcela and len(pasu_new) == 1:
                raise FeriasError(
                    "Você deve marcar todos os %s dias restantes nessa parcela."
                    % (qtd_dias_restante)
                )
            elif len(pasu_new) > 1:
                raise FeriasError(
                    f"O número máximo de parcelas restantes é {qtd_pasu_disponivel}. Tente um número de parcelas menor que {total_pasu_new}."
                )
        elif (
            qtd_pasu_valido >= self.periodo_aquisitivo.configuracao.max_divisoes
            and self.interrompido
            and len(pasu_new) > 1
        ):
            raise FeriasError(
                "Após interrupção é necessário marcar o restante numa parecela."
                % self.periodo_aquisitivo.configuracao.max_divisoes
            )

    def adicionar_usufrutos(self, data=[], admin=False):
        self.validate_installment_amount(pasu_new=data)
        pasus = []
        count_new_pasus = len(data)
        dias_marcados = self.dias_marcados
        count_pasus_changing = 0
        for parcela in data:
            pasu = self.adicionar_usufruto(
                parcela["data_inicio"],
                parcela["data_fim"],
                admin=admin,
                count_new_pasus=count_new_pasus,
                dias_marcados=dias_marcados,
                count_pasus_changing=count_pasus_changing,
            )
            pasus.append(pasu.pk)
            dias_marcados += pasu.dias
            count_pasus_changing += 1
        return pasus

    def adicionar_usufruto(
        self,
        dataini,
        datafim,
        admin=False,
        exclude_pasus=[],
        notificar=True,
        count_new_pasus=0,
        dias_marcados=0,
        count_pasus_changing=0,
    ):
        pasu = PeriodoAquisitivoServidorUsufruto()
        pasu.data_inicio = dataini
        pasu.data_fim = datafim
        pasu.periodo_aquisitivo_servidor = self
        pasu.validar_pasu()
        self.validar_usufruto(
            pasu,
            admin,
            exclude_pasus,
            count_new_pasus=count_new_pasus,
            dias_marcados=dias_marcados,
            count_pasus_changing=count_pasus_changing,
        )

        self.validar_usufrutos_afastamento(
            pasu, exclude_pasus=exclude_pasus, force=admin
        )

        self.usufrutos.add(pasu, bulk=False)

        if not admin and notificar and self.servidor.chefe_imediato:
            notify(
                "FRS_SOLICITACAO_AUTORIZACAO",
                self.servidor.chefe_imediato,
                self,
                servidor=self.servidor,
            )
        return pasu

    def deletar_usufruto(self, pasu_id, force=False):
        pasu = self.usufrutos.get(pk=pasu_id)
        if force:
            pasu.delete()
        else:
            pasu.desmarcar()
        return pasu

    def autorizar_usufruto(
        self,
        pasus_id,
        responsavel_id,
        autorizar=False,
        publicacao_id=0,
        admin=False,
        anotar=True,
    ):
        acao = "autorizar" if autorizar else "desautorizar"
        estado_dest = PASU_AUTORIZADO_CI if autorizar else PASU_NAOAUTORIZADO
        responsavel = Servidor.objects.get(pk=responsavel_id)

        autorizar and self.validar_usufrutos_autorizacao(pasus_id, force=admin)
        pasu = None
        for pasu_id in pasus_id:
            pasu = self.usufrutos.get(pk=pasu_id)
            pasu.transicao(acao, estado_dest)
            log.info(
                "AUTORIZAR USUFRUTO: %s/%s (%s) - %s"
                % (acao, estado_dest, responsavel, pasus_id)
            )
            pasu.autorizado_em = datetime.datetime.now().date()
            pasu.autorizado_por_id = responsavel.id
            if not (admin or pasu.pas.servidor.is_subordinado(responsavel)):
                raise ValidateFeriasError(
                    """Você não tem permissão para autorizar essas parcelas.<br /> Procure o RH e verifique se sua
                    lotação está correta e/ou se você está como chefe imediato ou mediato de quem você está tentando
                    autorizar.<br />Servidor a ser autorizado: %s"""
                    % pasu.pas.servidor
                )
            pasu.save()
        if self.homologado and autorizar:
            self.homologar_usufruto(pasus_id, anotar, publicacao_id)
        return pasu

    def homologar_usufruto(self, pasus_id, anotar=False, publicacao_id=0):
        """
        Homologar uma parcela após ter sido autorizada (pela chefia imediata e/ou chefia mediata)
        Uma anotação de férias deve ser criada sempre que homologar uma parcela (exceto na homologação da escala
        que a anotação é feita no próprio PeriodoAquisitivoServidor - PAS)
        """
        for pasu_id in pasus_id:
            pasu = self.usufrutos.get(pk=pasu_id)
            pasu.homologado = True
        if anotar:
            self.anotar_homologacao_pasu(pasus_id, publicacao_id)

    def anotar_homologacao_pasu(self, pasus_id, publicacao_id=0):
        publicacao = Publicacao.objects.get(id=publicacao_id) if publicacao_id else None
        parcelas = ""
        idx = 1
        pos = ""
        params = {}
        for pasu in self.usufrutos.filter(pk__in=pasus_id).order_by("data_inicio"):
            if len(pasus_id) > 1:
                pos = "%sª" % idx
                idx += 1
            parcelas += "<br />%s parcela: %s a %s (%s dias)" % (
                pos,
                pasu.data_inicio.strftime("%d/%m/%Y"),
                pasu.data_fim.strftime("%d/%m/%Y"),
                pasu.dias,
            )
        msg = Message.objects.get(mid="FRS_ANOTACAO_PASU")
        params["publicacao"] = publicacao.id if publicacao_id else None
        params["tipo_documento"] = (
            publicacao.tipo if publicacao else 100
        )  # DOCUMENTO DIGITAL
        params["texto"] = msg.formated(
            {
                "parcelas": parcelas,
                "pa": self.periodo_aquisitivo,
                "data_homologacao": datetime.datetime.now().strftime("%d/%m/%Y"),
                "publicacao": (
                    ""
                    if not publicacao
                    else "<br />Conforme %s n° %s/%s de %s"
                    % (
                        publicacao.get_tipo_display(),
                        publicacao.numero,
                        publicacao.ano,
                        publicacao.data_vigencia.strftime("%d/%m/%Y"),
                    )
                ),
            }
        )
        params["resumo"] = self.mark_summary_annotation()
        params["periodo"] = "%s" % (self.pas.periodo_aquisitivo)
        params["tipo"] = "MARCACAO"
        params["identificador"] = "%s" % self.id
        self.anotar_ferias(params)

    def mark_summary_annotation(self):
        return "Marcação de Férias %s" % self.pas.periodo_aquisitivo

    def autorizar_alteracao(
        self,
        alteracao_id,
        responsavel_id,
        autorizar=False,
        publicacao_id=0,
        admin=False,
        anotar=True,
    ):
        alteracao = AlteracaoPASU.objects.get(pk=alteracao_id)
        parcelas = "%s" % alteracao
        responsavel = Servidor.objects.get(pk=responsavel_id)

        autorizar and self.validar_usufrutos_autorizacao(
            [pasu.pk for pasu in alteracao.novos_pasus.all()],
            exclude_pasus=[pasu.pk for pasu in alteracao.antigos_pasus.all()],
            force=admin,
        )

        if self.id == alteracao.pas.id:
            if not (admin or alteracao.pas.servidor.is_subordinado(responsavel)):
                raise ValidateFeriasError(
                    """Você não tem permissão para autorizar essas parcelas.<br />
                    Procure o RH e verifique se sua lotação está correta e/ou se você está como chefe imediato ou
                    mediato de quem você está tentando autorizar.<br />Servidor a
                    ser autorizado: %s"""
                    % alteracao.pas.servidor
                )
            alteracao.deferir(autorizar, responsavel_id, publicacao_id, anotar)
            alteracao.save()
            # Notificação
            # if not admin:
            # MODIFICADO PARA EMITIR NOTIFICAÇÃO EM TODOS OS CASOS DE INDEFERIMENTO
            notify(
                "FRS_AUTORIZACAO_ALTERACAO",
                alteracao.pas.servidor,
                self,
                notification_cfg="deferimento" if autorizar else "indeferimento",
                parcelas=parcelas,
                deferido="deferido" if autorizar else "indeferido",
            )
        return alteracao

    def solicitar_alteracao(
        self,
        antigos,
        novos,
        justificativa,
        responsavel_id=0,
        publicacao_id=0,
        anotar=True,
    ):
        """
        @antigos: array contendo os ids dos PASUs a serem alterados
        @novos: array contendo as datas inicio e fim, como dicionario, de cada PASU. Ex.:
            [{data_inicio: 25/12/2010, data_fim: 09/01/2011},{data_inicio: 01/03/2011, data_fim: 15/03/2011}]
        @justificativa: justificativa da alteração
        @responsavel_id: reponsavel pela alteração, deve ser informado apenas qndo a alteração for realizada pelo
            GestorFerias
        """
        self.validate_installment_amount(pasu_new=novos, exclude_pasus=antigos)
        # if len(novos) > self.periodo_aquisitivo.configuracao.max_divisoes:
        #     raise FeriasError('O número máximo de parcelas é %d.' % self.periodo_aquisitivo.configuracao.max_divisoes)

        action = "alterar"
        estados_validos = [
            PASU_HOMOLOGADO,
        ]
        if responsavel_id:
            estados_validos = [
                PASU_HOMOLOGADO,
                PASU_INTERROMPIDO,
                PASU_SUSPENSO,
                PASU_FRUINDO,
                PASU_FRUIDO,
            ]
        alteracao = AlteracaoPASU()
        alteracao.pas = self
        alteracao.justificativa = justificativa
        alteracao.save()
        for pasu in self.usufrutos.filter(id__in=antigos):
            if pasu.estado not in estados_validos:
                raise ValidateFeriasError("A parcela (%s) não pode ser alterada" % pasu)
            else:
                pasu.transicao(action, PASU_EMALTERACAO, (responsavel_id > 0))
                alteracao.antigos_pasus.add(pasu)
        pasus_add = []
        count_new_pasus = len(novos)
        dias_marcados = self.dias_marcados
        count_pasus_changing = 0
        log.debug("from here")
        for parcela in novos:
            pasu = self.pas.adicionar_usufruto(
                parcela["data_inicio"],
                parcela["data_fim"],
                (responsavel_id and True),
                antigos,
                notificar=False,
                count_new_pasus=count_new_pasus,
                dias_marcados=dias_marcados,
                count_pasus_changing=count_pasus_changing,
            )
            pasu.estado = PASU_SUBSTITUTO

            pasus_add.append(pasu)
            conflitos = self.validate_candidate(pasus_add)
            if len(conflitos) > 0:
                mensagem = ""
                for conflito in conflitos:
                    mensagem += "%s " % conflito
                raise ValidateFeriasError(
                    "As novas parcelas conflitam entre si: %s" % mensagem
                )

            pasu.save()
            alteracao.novos_pasus.add(pasu)

            dias_marcados += pasu.dias
            count_pasus_changing += 1
        if (
            alteracao.pas.dias_marcados
            + alteracao.dias_marcados
            - alteracao.dias_alterados
        ) > (alteracao.pas.quantidade_dias - alteracao.pas.paid_days):
            raise ValidateFeriasError(
                "Quantidade de dias marcados (%s) está superior a quantidade de dias adquiridos (%s)"
                % (
                    alteracao.pas.dias_marcados
                    + alteracao.dias_marcados
                    - alteracao.dias_alterados,
                    alteracao.pas.quantidade_dias - alteracao.pas.paid_days,
                )
            )
        if responsavel_id:
            self.autorizar_alteracao(
                alteracao.id, responsavel_id, True, publicacao_id, True, anotar
            )
        else:
            if self.servidor.chefe_imediato:
                notify(
                    "FRS_SOLICITACAO_AUTORIZACAO",
                    self.servidor.chefe_imediato,
                    self,
                    servidor=self.servidor,
                )
            else:
                log.info("O servidor %s não possui chefe imediato!" % self.servidor)
                notify(
                    "RH_SERVIDOR_CHEFE_IMEDIATO",
                    self.servidor,
                    self,
                    servidor=self.servidor,
                )
        return alteracao

    def validar_usufrutos_autorizacao(self, pasus_novos, exclude_pasus=[], force=False):
        """
        Este método verificará se os pasus informados não possuem impedimento para autorização.
        """
        try:
            for pasu_novo in pasus_novos:
                self.validar_usufrutos_afastamento(
                    PeriodoAquisitivoServidorUsufruto.objects.get(pk=int(pasu_novo)),
                    exclude_pasus=exclude_pasus,
                )
        except Exception as err:
            raise FeriasError("Não é possível Autorizar. %s" % err.value)
        return True

    def validar_usufrutos_afastamento(self, pasu_novo, exclude_pasus=[], force=False):
        """
        Este método verifica se o pasu novo não possui impedimento para criação.
        """
        try:
            dr_pasu_novo = NewDateRange(pasu_novo.data_inicio, pasu_novo.data_fim)
            departure_exclude = []
            for exclude in exclude_pasus:
                pasu_exclude = PeriodoAquisitivoServidorUsufruto.objects.get(
                    pk=int(exclude)
                )
                dr_exclude = NewDateRange(
                    pasu_exclude.data_inicio, pasu_exclude.data_fim
                )
                if dr_pasu_novo.intersect(dr_exclude).days > 0:
                    log.info(
                        "PASU NOVO: %s - INTERCEDEU: %s dias - COM PASU EXCLUÍDO DA VALIDAÇÃO: %s"
                        % (
                            pasu_novo,
                            dr_pasu_novo.intersect(dr_exclude).days,
                            pasu_exclude,
                        )
                    )
                    for pk in FeriasAfastamento.objects.filter(
                        data_inicio=pasu_exclude.data_inicio,
                        data_fim=pasu_exclude.data_fim,
                    ).values("pk"):
                        departure_exclude.append(pk.get("pk"))
                    # return True
            conflict = FeriasAfastamento.verifica_sobreposicao_periodo(
                servidor=pasu_novo.periodo_aquisitivo_servidor.servidor,
                data_inicio=pasu_novo.data_inicio,
                data_fim=pasu_novo.data_fim,
                cancelado=False,
                exclude=departure_exclude,
            )
            if conflict:
                raise Exception("Existe conflito com algum afastamento.")
        except Exception as err:
            departament = (
                "RH 3216-7565." if not self.servidor.membro else "Expediente 3216-7538."
            )
            raise FeriasError(
                "%s. Entre em contato com %s" % (err.args[0], departament)
            )
        return True

    # Retorna os usufrutos que serão analisados para verificar se há conflito com uma parcela específica
    # O retorno já está filtrado pelo tipo do servidor
    @ilru_cache()
    def _get_filter_conflitos(self):
        # usufrutos = PeriodoAquisitivoServidorUsufruto.objects.exclude(
        #     estado__in=[PASU_ALTERADO, PASU_SUSPENSO, PASU_NAOAUTORIZADO, PASU_SUBSTITUTO, ]).filter(
        #     periodo_aquisitivo_servidor__servidor__tipo=self.servidor.tipo)
        employees = []
        employee = self.servidor
        work_locations = employee.work_locations
        if not work_locations.exists():
            work_locations = employee._raw_locations().first()
            work_locations = [work_locations.lotacao] if work_locations else []
        usufrutos = PeriodoAquisitivoServidorUsufruto.objects.exclude(
            estado__in=[
                PASU_ALTERADO,
                PASU_SUSPENSO,
                PASU_NAOAUTORIZADO,
                PASU_SUBSTITUTO,
            ]
        )
        exercises = (
            ServidorLotacao.work_assignment_exercise(
                workplace=[wl.pk for wl in work_locations]
            )
            .exclude(servidor=employee)
            .exclude(
                lotacao__pk__in=employee.work_assignment.filter(
                    lotacao__in=work_locations
                )
                .filter(commission=True)
                .values("lotacao__pk")
            )
        )
        for sl in exercises:
            employees.append(sl.servidor.id)
        usufrutos = usufrutos.filter(
            periodo_aquisitivo_servidor__servidor__in=employees
        )

        return usufrutos

    def conflitos(self, pasu, exclude=False, limit=None):
        """
        :py:function:: conflitos(self, pasu, exclude=False)

        This method returns a list of PeriodoAquisitivoServidorUsufruto that conflicts with substitutes.
        Employee is given by PeriodoAquisitivoServidor(self).

        Employee's way.

        :param PeriodoAquisitivoServidorUsufruto pasu:
        :return: list of PeriodoAquisitivoServidorUsufruto
        :rtype: list
        """
        log.debug("conflitos")
        return self.conflicts(pasu, exclude=exclude, limit=limit)

    def check_all_conflict(self, pasu, exclude=False, registry_exclude=[], limit=None):
        """
        :py:function:: check_all_conflict(self, pasu, exclude=False)

        This method checks if a given PeriodoAquisitivoServidorUsufruto conflicts with substitutes and where substitute.

        :param PeriodoAquisitivoServidorUsufruto pasu:
        :param boolean exclude:
        :param list registry_exclude: list of registry to exclude of the analysis
        :return: boolean
        :rtype: boolean
        """
        from rh.models import Replacement

        check = False
        try:
            conflicts = pasu.pas.conflitos(pasu, exclude=exclude, limit=limit)
        except Replacement.PublicationNotFoundError as err:
            log.exception(err)
            conflicts = check = err
        if len(conflicts):
            check = True
        return check

    def conflicts(self, pasu, exclude=False, limit=None):
        """
        :py:function:: conflicts(self, pasu, exclude=False)

        This method returns a list of PeriodoAquisitivoServidorUsufruto that conflicts with substitutes.
        Employee is given by PeriodoAquisitivoServidor(self).

        Employee's way.

        :param PeriodoAquisitivoServidorUsufruto pasu:
        :return: list of PeriodoAquisitivoServidorUsufruto
        :rtype: list
        """
        usufrutos = self._get_filter_conflitos().exclude(
            periodo_aquisitivo_servidor__servidor=self.servidor
        )
        dr_pasu = NewDateRange(pasu.data_inicio, pasu.data_fim)

        identify = {}
        count = 1
        for usu in usufrutos:
            dr_usufruto = NewDateRange(usu.data_inicio, usu.data_fim)
            if dr_usufruto.intersect(dr_pasu).days > 0:
                registry = usu.periodo_aquisitivo_servidor.servidor.matricula
                identify.update(
                    {
                        count: {
                            "registry": registry,
                            "pasu": usu,
                            "order": "0",
                            "workplace": "----",
                        }
                    }
                )
                count += 1
        return identify

    def conflitos_contratos_old(self, pasu):
        conflitos = []
        try:
            from planejamento.contrato.models import Gestor, Contrato

            gestor = Gestor.objects.filter(user__servidor=pasu.pas.servidor)
            if gestor.exists():
                gestor = gestor.last()
                contratos = Contrato.objects.exclude(
                    Q(data_inicio__gt=pasu.data_fim)
                    | Q(data_vencimento__lt=pasu.data_inicio)
                ).filter(Q(gestor=gestor) | Q(responsaveis=gestor))
                contratos = contratos.exclude(
                    responsaveis__user__servidor=None
                ).distinct()
                dr_pasu = NewDateRange(pasu.data_inicio, pasu.data_fim)
                for contrato in contratos.order_by("data_vencimento_flag"):
                    if (
                        NewDateRange(contrato.data_inicio, contrato.data_vencimento)
                        .intersect(dr_pasu)
                        .days
                        > 0
                    ):
                        employeers = (
                            Servidor.objects.filter(
                                Q(pk=contrato.gestor.user.servidor.pk)
                                | Q(
                                    pk__in=contrato.responsaveis.values(
                                        "user__servidor"
                                    )
                                )
                            )
                            .exclude(matricula=gestor.user.servidor.matricula)
                            .distinct()
                        )
                        for emp in employeers:
                            usufrutos = (
                                PeriodoAquisitivoServidorUsufruto.objects.exclude(
                                    estado__in=[
                                        PASU_ALTERADO,
                                        PASU_SUSPENSO,
                                        PASU_NAOAUTORIZADO,
                                        PASU_SUBSTITUTO,
                                    ]
                                ).filter(periodo_aquisitivo_servidor__servidor=emp)
                            )
                            for usu in usufrutos:
                                if (
                                    NewDateRange(usu.data_inicio, usu.data_fim)
                                    .intersect(dr_pasu)
                                    .days
                                    > 0
                                ):
                                    conflitos.append({"contrato": contrato, "usu": usu})
        except Exception as err:
            log.exception(err)
        return conflitos

    def conflitos_contratos(self, pasu):
        conflitos = {}
        try:
            from planejamento.contrato.models import Supervisor

            dr_pasu = NewDateRange(pasu.data_inicio, pasu.data_fim)
            subs = Supervisor.get_employee_substitutes(
                pasu.pas.servidor.matricula, pasu.data_inicio, pasu.data_fim
            )
            for sub in subs:
                for emp in Servidor.objects.filter(
                    matricula__in=sub.get("registry", [])
                ):
                    usufrutos = PeriodoAquisitivoServidorUsufruto.objects.filter(
                        periodo_aquisitivo_servidor__servidor=emp
                    ).exclude(
                        estado__in=[
                            PASU_ALTERADO,
                            PASU_SUSPENSO,
                            PASU_NAOAUTORIZADO,
                            PASU_SUBSTITUTO,
                        ]
                    )
                    for usu in usufrutos:
                        if (
                            NewDateRange(usu.data_inicio, usu.data_fim)
                            .intersect(dr_pasu)
                            .days
                            > 0
                        ):
                            value = {
                                "number": sub.get("number"),
                                "usu": usu,
                                "kind": sub.get("kind"),
                            }
                            a = conflitos.get(emp.matricula, [])
                            a.append(value)
                            conflitos.update({emp.matricula: a})
                if len(conflitos) > 0:
                    break
        except Exception as err:
            log.exception(err)
            conflitos = {
                self.servidor.matricula: [{"number": err, "usu": None, "kind": None}]
            }
        return conflitos

    def conflitos_afastamento(self, pasu):
        """Retorna os conflitos com outros membros/servidores de acordo com a lei vigente"""
        old_pasus = []
        if pasu.alteracao_in.exists():
            change = pasu.alteracao_in.filter().latest("pk")
            old_pasus = change.antigos_pasus.all()

        departures = (
            BaseLicencaAfastamento.objects.filter(servidor=self.servidor)
            .exclude(estado__in=(CANCELED,))
            .exclude(data_fim__lt=pasu.data_inicio)
            .exclude(data_inicio__gt=pasu.data_fim)
        )
        departures = FeriasAfastamento.excluir_conflitos(
            servidor=self.servidor,
            query=departures,
            data_inicio=pasu.data_inicio,
            data_fim=pasu.data_fim,
            pk=None,
            cancelado=False,
        )
        if departures.exists():
            for old in old_pasus:
                departures = departures.exclude(
                    data_inicio=old.data_inicio, data_fim=old.data_fim
                )
        return BaseLicencaAfastamento.verifica_interseccao_periodo(
            self.servidor, pasu.data_inicio, pasu.data_fim, departures=departures
        )

    def conflitos_substituicao(self, pasu):
        return BaseLicencaAfastamento.substitutions_conflicts(
            None, pasu.pas.servidor, pasu.data_inicio, pasu.data_fim
        )

    def conflito(self, pasu):
        return False

    def conflitos_usufruto_servidor(self, pasu, exclude_pasus=[]):
        """Retorna os conflitos entre parcelas de um mesmo servidor"""
        log.debug("Conflito interno: %s" % pasu)
        if not pasu:
            return []
        if pasu.id:
            exclude_pasus.append(pasu.id)
        query_usufrutos = (
            PeriodoAquisitivoServidorUsufruto.objects.filter(
                periodo_aquisitivo_servidor__servidor=self.servidor
            )
            .exclude(
                estado__in=[
                    PASU_ALTERADO,
                    PASU_SUSPENSO,
                    PASU_NAOAUTORIZADO,
                    PASU_SUBSTITUTO,
                ]
            )
            .exclude(data_fim_cache__lt=pasu.data_inicio)
            .exclude(data_prevista_fim__lt=pasu.data_inicio)
            .exclude(data_inicio__gt=pasu.data_fim)
        )
        log.debug("Qtd Conflito: %s" % query_usufrutos.count())
        usufrutos = []
        for usu in query_usufrutos.exclude(pk__in=exclude_pasus):
            log.debug("PASU: %s - %s" % (usu, usu.get_estado_display()))
            if (
                usu.data_inicio <= pasu.data_inicio and usu.data_fim >= pasu.data_inicio
            ) or (usu.data_inicio <= pasu.data_fim and usu.data_fim >= pasu.data_fim):
                log.debug("_________CONFLITO___________")
                usufrutos.append(usu)
        return usufrutos

    @property
    def pago(self):
        """Retorna se esse PA foi pago ou não, verificando se existe uma folha referenciada pelo campo 'folha_terco_constitucional'"""
        return self.pago_sem_folha or self.folha_evento_terco_constitucional is not None

    def _get_desabilitado(self):
        """
        Retorna se esse PA pode ser manipulado pelo usuário - para marcação de férias
        """
        return self.bloqueado or self.estado in [
            PAS_ALIBERACAO,
            PAS_FRUIDA,
            PAS_INDENIZADA,
        ]

    desabilitado = property(_get_desabilitado)

    def _get_interrompido(self):
        """Retorna se alguma parcela para esse periodo foi interrompido"""
        return self.usufrutos.exclude(suspenso_em=None).count() > 0

    interrompido = property(_get_interrompido)

    # Retorna se alguma parcela para esse periodo foi suspenso
    def _get_suspenso(self):
        return self.usufrutos.exclude(suspenso_em=None).count() > 0

    suspenso = property(_get_suspenso)

    def _get_fruido(self):
        return self.estado == PAS_FRUIDA

    fruido = property(_get_fruido)

    def _get_fruindo(self):
        return self.usufrutos.filter(estado=PASU_FRUINDO).count() > 0

    fruindo = property(_get_fruindo)

    def _get_homologado(self):
        return (
            self.periodo_aquisitivo.publicado
            or self.periodo_aquisitivo.periodo_anterior
        )

    homologado = property(_get_homologado)

    # O próximo dia ao final da aquisição
    def _get_data_inicio_usufruto(self):
        return self.data_fim_aquisicao + datetime.timedelta(days=1)

    # TODO Verificar se o tempo de prescrição é em meses comerciais ou não - OK
    def _get_data_fim_usufruto(self):
        if (
            self.periodo_aquisitivo.periodo_anterior
            or self.suspenso
            or self.interrompido
        ):
            return None
        dt = self.data_fim_aquisicao
        return dt + relativedelta(
            years=self.periodo_aquisitivo.configuracao.meses_max_fruicao / 12,
            months=self.periodo_aquisitivo.configuracao.meses_max_fruicao % 12,
        )

    # TODO Verificar todas as possibilidades que podem reduzir os dias de férias de um servidor
    # OPTIMIZE
    def atualizar_dias_ferias(self):
        termination_date = self.servidor.data_desligamento
        if (
            self.servidor.type_by_possession in ("REQ", "RFC", "RCM", "REX")
            and termination_date
            and termination_date >= datetime.datetime.now().date()
        ):
            termination_date = None
        last_date = (
            (termination_date - relativedelta(days=1)) if termination_date else None
        )
        if self.servidor.is_acordo_cooperacao:
            range_bond = NewDateRange()
            for req in RequestMove.objects.filter(servidor=self.servidor):
                range_bond += NewDateRange(req.data_exercicio, req.data_desligamento)
        else:
            range_bond = NewDateRange(self.servidor.data_exercicio, last_date)
        range_acquisition = NewDateRange(
            self.data_inicio_aquisicao, self.data_fim_aquisicao
        )
        range_pas = range_acquisition.intersect(range_bond)

        if range_pas != range_acquisition and termination_date:
            self.quantidade_dias = 0
        else:
            self.quantidade_dias = 30
        return self.quantidade_dias

    def atualizar_datas_ferias(self):
        self.data_inicio_aquisicao = self._get_data_inicio_aquisicao()
        self.data_fim_aquisicao = self._get_data_fim_aquisicao()
        if self.data_inicio_aquisicao > self.data_fim_aquisicao:
            self.data_inicio_aquisicao = self.data_fim_aquisicao
        self.data_inicio_usufruto = self.data_fim_aquisicao + datetime.timedelta(days=1)
        self.data_fim_usufruto = (
            None
            if self.periodo_aquisitivo.isanterior
            else self._get_data_fim_usufruto()
        )
        self.save()

    # TODO Verificar a forma de obter a data de referencia para o periodo aquisitivo em questao
    # Um campo com essa data esta em rh.Servidor, porém deve ser analisado se existem outras
    # situações que essa data pode ser acrescida.
    # OBS.: Essa informação será pesistida aqui pois o servidor pode ter datas de referencia de ferias
    # diferentes em periodos diferentes
    def atualizar_data_referencia_ferias(self, force=False, save=False):
        if self.periodo_aquisitivo.configuracao.modo == "ANUAL":
            # OPTIMIZE Rotina para calcular a data correta de referencia, quando o tipo de ferias for ANUAL
            # pois neste tipo a data de referencia é 01/01/XXXX ou, se for semestral, 01/01/XXXX e 01/07/XXXX
            # Lembrar que aqui o que muda é apenas o mês da referencia
            d_inicio_ano = datetime.date(self.periodo_aquisitivo.ano_aquisicao, 1, 1)
            mes = (12 / self.periodo_aquisitivo.configuracao.quantidade_periodos) * (
                self.periodo_aquisitivo.periodo - 1
            ) + 1
            self.data_referencia = d_inicio_ano.replace(month=int(mes))
        else:
            # NOTIFICATION Notificar que o servidor não possui data de referencia de férias
            if not self.servidor.data_referencia_ferias:
                raise DataReferenciaNotFoundError(self.servidor)
            self.data_referencia = self.servidor.data_referencia_ferias
        if force:
            self.data_inicio_aquisicao = self._get_data_inicio_aquisicao()
            self.data_fim_aquisicao = self._get_data_fim_aquisicao()
            if self.data_inicio_aquisicao > self.data_fim_aquisicao:
                self.data_inicio_aquisicao = self.data_fim_aquisicao
            self.data_inicio_usufruto = self.data_fim_aquisicao + datetime.timedelta(
                days=1
            )
            self.data_fim_usufruto = (
                None
                if self.periodo_aquisitivo.isanterior
                else self._get_data_fim_usufruto()
            )
        if save:
            self.save()
        return self.data_referencia

    def _get_data_ini_aquisicao(self):
        return self._get_data_inicio_aquisicao()

    # O data_inicio_aquisicao é igual ao dia posterior ao da data_referencia_ferias com o mesmo ano
    # do periodo_aquisitivo.ano_aquisicao caso o modo seja CONTINUO
    # Sendo o modo ANUAL, a data de inicio de aquisicao  é o primeiro dia do período (ANO, SEMESTRE, QUADRIMESTRE, etc)
    #  e quem identifica
    # TODO verificar possibilidade de erro com data
    def _get_data_inicio_aquisicao(self):
        d_aquisicao = self.data_referencia
        # Para os servidores em geral - deve ser sobrescrito para PAS especializado, se necessário
        # O ano de início da aquisição é o ano anterior ao ano do período aquisitivo, ou seja,
        # periodo aquisitivo: 2011, inicio do periodo: 2010
        return d_aquisicao + relativedelta(
            years=self.periodo_aquisitivo.ano_aquisicao - d_aquisicao.year - 1
        )

    # OPTIMIZE O código desse método pode ser otimizado pois esse código pode ser usado em mais locais que operam com datas
    def _get_data_fim_aquisicao(self):
        df = self.data_inicio_aquisicao
        conf = self.periodo_aquisitivo.configuracao
        return df + relativedelta(
            years=int(conf.meses_exercicio / 12),
            months=int(conf.meses_exercicio % 12),
            days=-1,
        )

    # TODO
    def _get_dias_marcados(self):
        dm = self.usufrutos.filter(
            estado__in=[
                PASU_NOVO,
                PASU_AUTORIZADO_CI,
                PASU_HOMOLOGADO,
                PASU_EMALTERACAO,
                PASU_INTERROMPIDO,
                PASU_FRUINDO,
                PASU_FRUIDO,
            ]
        ).aggregate(dias_marcados=models.Sum("dias"))
        return dm["dias_marcados"] or 0

    dias_marcados = property(_get_dias_marcados)  # PROPERTY

    @property
    def dias_aprovisionados(self):
        dm = self.usufrutos.filter(
            estado__in=[
                PASU_NOVO,
                PASU_AUTORIZADO_CI,
                PASU_HOMOLOGADO,
                PASU_SUBSTITUTO,
                PASU_INTERROMPIDO,
                PASU_FRUINDO,
                PASU_FRUIDO,
            ]
        ).aggregate(dias_marcados=models.Sum("dias"))
        return (dm["dias_marcados"] or 0) - self.paid_days

    # TODO
    def _get_dias_agendados(self):
        return self.dias_marcados - self.dias_usufruidos

    dias_agendados = property(_get_dias_agendados)  # PROPERTY

    # TODO
    def _get_dias_usufruidos(self):
        dm = self.usufrutos.filter(
            estado__in=[PASU_INTERROMPIDO, PASU_FRUIDO]
        ).aggregate(dias_marcados=models.Sum("dias"))
        return dm["dias_marcados"] or 0

    dias_usufruidos = property(_get_dias_usufruidos)  # PROPERTY

    # TODO
    def _get_dias_nao_marcados(self):
        return self.quantidade_dias - self.dias_marcados - self.paid_days

    dias_nao_marcados = property(_get_dias_nao_marcados)  # PROPERTY

    def _get_dias_autorizados(self):
        dm = self.usufrutos.exclude(
            estado__in=[PASU_NOVO, PASU_ALTERADO, PASU_SUSPENSO]
        ).aggregate(dias_marcados=models.Sum("dias"))
        return dm["dias_marcados"] or 0

    dias_autorizados = property(_get_dias_autorizados)  # PROPERTY

    def _get_situacao(self):
        return ESTADO_PAS[self.estado] if self.estado in ESTADO_PAS else "Indefinido"

    situacao = property(_get_situacao)

    def _get_folha(self):
        text = None
        if self.pago:
            text = "PAGO (sem informação da folha)"
            if self.folha_evento_terco_constitucional:
                text = "%s (%s)" % (
                    self.folha_evento_terco_constitucional.folha,
                    self.folha_evento_terco_constitucional.evento,
                )
        return text

    folha = property(_get_folha)

    @property
    def dias_ausufruir(self):
        return self.quantidade_dias - self.dias_usufruidos - self.paid_days

    @property
    def days_not_enjoyed(self):
        return self.quantidade_dias - self.dias_usufruidos - self.paid_days

    @classmethod
    def create_automatic_book_vacation(cls, pa):
        from engine.mq.models import Task
        from rh.ferias.tasks import create_automatic_book_vacation

        Task.start(
            create_automatic_book_vacation,
            pa=pa,
            type_employee="S",
            user=get_current_user().pk,
            success="""<p>
                FÉRIAS - Marcação de férias finalizada. Verifique resultado no arquivo
                <a href="/athenas/FRSEmployeeAcquisitionPeriod/file/?uuid=%(uuid)s">link</a>.
                </p>
                <p>
                Este arquivo está disponível para download até dia
                <span style="font-weight:bold">%(deadline)s</span>
                </p>""",
        )

    @classmethod
    def _create_automatic_book_vacation(cls, pa, type_employee, user=None, task=None):
        from engine.mq.models import Task

        task = Task.objects.get(pk=task)

        def write_file(text, mode="w"):
            """
            Método responsável por escrever em file_write.
            """
            try:
                file_write = codecs.open(
                    "%s/marcacao-%s.csv" % (settings.CACHE_PATH, task.uuid),
                    mode,
                    "utf-8",
                )
                file_write.write(text)
                file_write.close()
            except Exception as err:
                log.exception(err)

        periods = PeriodoAquisitivoServidor.objects.filter(
            periodo_aquisitivo__pk=pa,
            servidor__tipo=type_employee,
            servidor__ativo=True,
        )
        for pas in periods:
            if not pas.homologado and pas.dias_agendados == 0:
                date_start_usufruct = pas.data_inicio_usufruto
                date_end_usufruct = pas.data_inicio_usufruto + relativedelta(days=29)
                message = "%s|%s|%s|%s|%s" % (
                    pas.servidor.matricula,
                    pas.servidor.pessoa_fisica,
                    pas.periodo_aquisitivo,
                    DateUtils.date_to_str(date_start_usufruct),
                    DateUtils.date_to_str(date_end_usufruct),
                )
                departures = (
                    pas.servidor.departures()
                    .filter(
                        ~Q(licenca__licencaafastamentoconjuge=None)
                        | ~Q(licenca__licencainteresseparticular=None)
                        | Q(afastamento__afastamentooutroorgao__onus=2)
                    )
                    .filter(estado=ACTIVE)
                )
                if not departures.exists():
                    try:
                        pas.adicionar_usufrutos(
                            data=[
                                {
                                    "data_inicio": date_start_usufruct,
                                    "data_fim": date_end_usufruct,
                                }
                            ],
                            admin=True,
                        )
                        message += "|%s\n" % "MARCADO"
                    except Exception as err:
                        log.exception(err)
                        message += "|%s|%s\n" % ("NÃO MARCADO", err)
                else:
                    message += "|%s|%s\n" % ("NÃO MARCADO", departures.last())
                write_file(message, mode="a")

    @property
    def status(self):
        status = []
        if self.fruido:
            status.append(
                {
                    "icon": FRS_ICONS_THEME["pasu_fruido"],
                    "title": "Período aquisitivo fruído",
                    "alt": "Fruido",
                }
            )
        elif self.fruindo:
            status.append(
                {
                    "icon": FRS_ICONS_THEME["pasu_fruindo"],
                    "title": "Parcela em fruição",
                    "alt": "Fruindo",
                }
            )
        elif self.estado == PAS_EMANDAMENTO:
            status.append(
                {
                    "icon": FRS_ICONS_THEME["pas_andamento"],
                    "title": "Em andamento",
                    "alt": "Andamento",
                }
            )
        elif self.estado == PAS_INDENIZADA:
            status.append(
                {
                    "icon": FRS_ICONS_THEME["pas_indenizada"],
                    "title": "Período Indenizado",
                    "alt": "Indenizado",
                }
            )
        elif self.estado == PAS_ALIBERACAO:
            status.append(
                {
                    "icon": FRS_ICONS_THEME["aguardando"],
                    "title": "Aguardando liberação",
                    "alt": "Liberacao",
                }
            )
        else:
            status.append({"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"})
        if self.pago:
            status.append(
                {
                    "icon": FRS_ICONS_THEME["pago"],
                    "title": "Período aquisitivo pago (%s)" % self.folha,
                    "alt": "Pago",
                }
            )
        else:
            status.append({"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"})
        if self.bloqueado:
            status.append(
                {
                    "icon": FRS_ICONS_THEME["bloqueado"],
                    "title": "Período bloqueado",
                    "alt": "Bloqueado",
                }
            )
        else:
            status.append({"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"})
        return status


class PeriodoAquisitivoServidorMembro(PeriodoAquisitivoServidor):
    class Meta:
        db_table = "frs_paservidormembro"

    @ilru_cache()
    def _matricula_substitutos(self):
        return self.substitutos()

    @ilru_cache()
    def _get_filter_conflitos(self):
        matriculas_substitutos = self._matricula_substitutos()
        if len(matriculas_substitutos) > 0:
            usufrutos = (
                PeriodoAquisitivoServidorUsufruto.objects.filter(
                    periodo_aquisitivo_servidor__servidor__matricula__in=matriculas_substitutos
                )
                .exclude(
                    estado__in=[
                        PASU_ALTERADO,
                        PASU_SUSPENSO,
                        PASU_NAOAUTORIZADO,
                        PASU_SUBSTITUTO,
                    ]
                )
                .filter(periodo_aquisitivo_servidor__servidor__tipo=self.servidor.tipo)
            )
        else:
            usufrutos = PeriodoAquisitivoServidorUsufruto.objects.exclude(
                estado__in=[
                    PASU_ALTERADO,
                    PASU_SUSPENSO,
                    PASU_NAOAUTORIZADO,
                    PASU_SUBSTITUTO,
                ]
            ).filter(periodo_aquisitivo_servidor__servidor__tipo=self.servidor.tipo)
        return usufrutos

    """
    Soma 5 dias a cada mês trabalhado, sendo que 1 dia trabalhado no mês ja considera o mês inteiro
    """

    def atualizar_dias_ferias(self):
        ini_aquisicao = self.data_inicio_aquisicao
        fim_aquisicao = self.data_fim_aquisicao
        exercicio = self.servidor.data_exercicio
        if not exercicio:
            self.quantidade_dias = (
                0  # Retorna ZERO (0) caso o membro não tenha data de exercício
            )
        elif exercicio > fim_aquisicao:
            self.quantidade_dias = (
                0  # O membro entrou em exercicio depois do final do periodo aquisitivo
            )
        elif exercicio < ini_aquisicao:
            self.quantidade_dias = (
                self.periodo_aquisitivo.configuracao.dias_por_periodo
            )  # O membro entrou antes do período aquisitivo
        else:
            meses = (
                (fim_aquisicao.year * 12 + fim_aquisicao.month)
                - (exercicio.year * 12 + exercicio.month)
                + 1
            )
            self.quantidade_dias = meses * 5
        return (
            self.quantidade_dias
        )  # Quantidade de meses multiplicado por 5 dias, 5 dias -> por mes trabalhado

    def _get_data_inicio_aquisicao(self):
        return self.data_referencia

    def substitutos(self):
        """
        Este método retorna os substitutos existentes na tabela de substituição automática.
        """
        return set(
            self.pas.servidor.my_replacement_substitute_vacation().values_list(
                "substitute__servidores_lotacao__servidor__matricula", flat=True
            )
        )

    def conflitos(self, pasu, exclude=False, limit=None):
        """
        :py:function:: conflitos(self, pasu, exclude=False)

        This method returns a list of PeriodoAquisitivoServidorUsufruto that conflicts with substitutes.
        Employee is given by PeriodoAquisitivoServidor(self).

        Member's way.

        :param PeriodoAquisitivoServidorUsufruto pasu:
        :return: list of PeriodoAquisitivoServidorUsufruto
        :rtype: list
        """
        log.debug("conflitos")
        from rh.models import Replacement

        identify = {}
        registry_exclude = []
        identify_count = []

        try:
            identify = self.conflicts(pasu, exclude=exclude, limit=limit)

            for key in identify.keys():
                registry = identify[key].get("registry", None)
                if registry and registry not in registry_exclude:
                    registry_exclude.append(registry)
                identify_count.append(registry if registry else 0)

            log.debug(f"@ identify {identify}")
            if check_limit(len(identify), limit):
                return identify

            conflicts_pasu = pasu.pas._conflicting_where_substitute_pasus_found(
                pasu, registry_exclude=registry_exclude, limit=limit
            )

            if len(conflicts_pasu):
                count = (
                    identify_count[len(identify_count) - 1]
                    if len(identify_count)
                    else 0
                )
                for key in conflicts_pasu:
                    count += 1
                    identify.update({count: conflicts_pasu[key]})
                    if check_limit(len(identify), limit):
                        return identify
        except Replacement.PublicationNotFoundError as err:
            log.exception(err)
            identify = {0: {"error": "%s" % err}}
        log.debug(f"# identify {identify}")
        return identify

    def conflicts(self, pasu, exclude=False, limit=None):
        """
        :py:function:: conflicts(self, pasu, exclude=False)

        This method returns a list of PeriodoAquisitivoServidorUsufruto that conflicts with substitutes.
        Employee is given by PeriodoAquisitivoServidor(self).

        Member's way.

        :param PeriodoAquisitivoServidorUsufruto pasu:
        :return: list of PeriodoAquisitivoServidorUsufruto
        :rtype: list
        """
        log.debug("conflicts")
        identify = {}
        count = 0
        usufrutos = self._get_filter_conflitos().exclude(
            periodo_aquisitivo_servidor__servidor=self.servidor
        )
        usufrutos = usufrutos.exclude(data_prevista_fim__lt=pasu.data_inicio)
        usufrutos = usufrutos.exclude(data_fim_cache__lt=pasu.data_inicio)
        usufrutos = usufrutos.exclude(data_inicio__gt=pasu.data_fim)
        dr_pasu = NewDateRange(pasu.data_inicio, pasu.data_fim)

        my_replacement_substitute_vacation = (
            self.servidor.my_replacement_substitute_vacation()
        )
        my_replacement_employee_workplace_vacation = (
            self.servidor.my_replacement_employee_workplace_vacation().filter(
                servidor__tipo="M"
            )
        )

        for usu in usufrutos:
            dr_usufruto = NewDateRange(usu.data_inicio, usu.data_fim)
            if dr_usufruto.intersect(dr_pasu).days > 0:
                registry = usu.periodo_aquisitivo_servidor.servidor.matricula
                for (
                    employee_workplace
                ) in my_replacement_employee_workplace_vacation.filter(
                    servidor__matricula=registry
                ):
                    for rpl in my_replacement_substitute_vacation.filter(
                        substitute__servidores_lotacao__lotacao=employee_workplace.lotacao,
                        substitute__servidores_lotacao__servidor=employee_workplace.servidor,
                    ).distinct():
                        new = {
                            "registry": registry,
                            "pasu": usu,
                            "order": rpl.order,
                            "workplace": rpl.replaced,
                        }
                        if not PeriodoAquisitivoServidorMembro.check_duplicity_substitute(
                            identify, new
                        ):
                            identify.update({count: new})
                            count += 1
                        if check_limit(count, limit):
                            break
                    if check_limit(count, limit):
                        break
            if check_limit(count, limit):
                break
        return identify

    def check_all_conflict(self, pasu, exclude=False, registry_exclude=[], limit=None):
        """
        :py:function:: check_all_conflict(self, pasu, exclude=False)

        This method checks if a given PeriodoAquisitivoServidorUsufruto conflicts with substitutes and where substitute.

        :param PeriodoAquisitivoServidorUsufruto pasu:
        :param boolean exclude:
        :param list registry_exclude: list of registry to exclude of the analysis
        :return: boolean
        :rtype: boolean
        """
        from rh.models import Replacement

        check = False
        try:
            conflicts = pasu.pas.conflitos(pasu, exclude=exclude, limit=limit)
            if not len(conflicts):
                if not registry_exclude:
                    registry_exclude = [
                        conflicts[key].get("registry", None)
                        for key in list(conflicts.keys())
                        if conflicts[key].get("registry", None)
                    ]
                if len(
                    pasu.pas._conflicting_where_substitute_pasus_found(
                        pasu, registry_exclude=registry_exclude, limit=limit
                    )
                ):
                    check = True
            else:
                check = True
        except Replacement.PublicationNotFoundError as err:
            log.exception(err)
            check = err
        return check

    def chek_conflicts_where_substitute(
        self, pasu, registry_where_substitute=[], exclude=False
    ):
        """
        :py:function:: chek_conflicts_where_substitute(self, pasu, registry_where_substitute=[], exclude=False)

        This method checks conflicts where employee is substitute.
         of PASU(PeriodoAquisitivoServidorUsufruto) against a provided list of registry.

        :param PeriodoAquisitivoServidorUsufruto pasu_analysis: pasu_analysis
        :param list registry_where_substitute: registry_where_substitute

        :return: list of PeriodoAquisitivoServidorUsufruto
        :rtype: list of PeriodoAquisitivoServidorUsufruto
        """
        conflitos = []
        _check_conflitct = self._check_conflict_for_pasu_and_registry(
            pasu, registry=registry_where_substitute
        )
        registry_conflicted = []
        for _check in _check_conflitct:
            if _check.pas.servidor.matricula not in registry_conflicted:
                registry_conflicted.append(_check.pas.servidor.matricula)

        """condição para gerar conflitos: todos os substitutos terem férias agendadas"""
        if len(registry_conflicted) >= len(registry_where_substitute):
            conflitos += _check_conflitct

        return conflitos

    def _check_conflict_for_pasu_and_registry(self, pasu_analysis, registry=[]):
        """
        :py:function:: _check_conflict_for_pasu_and_registry(self, pasu_analysis, registry=[])

        This method checks conflicts of PASU(PeriodoAquisitivoServidorUsufruto) against a provided list of registry.

        :param PeriodoAquisitivoServidorUsufruto pasu_analysis: pasu_analysis
        :param list registry: registry

        :return: list of PeriodoAquisitivoServidorUsufruto
        :rtype: list of PeriodoAquisitivoServidorUsufruto
        """
        usufrutos = (
            PeriodoAquisitivoServidorUsufruto.objects.filter(
                periodo_aquisitivo_servidor__servidor__matricula__in=registry,
                periodo_aquisitivo_servidor__servidor__tipo=self.servidor.tipo,
            )
            .exclude(
                estado__in=[
                    PASU_ALTERADO,
                    PASU_SUSPENSO,
                    PASU_NAOAUTORIZADO,
                    PASU_SUBSTITUTO,
                ]
            )
            .exclude(periodo_aquisitivo_servidor__servidor=self.servidor)
        )
        conflitos = []
        dr_pasu = NewDateRange(pasu_analysis.data_inicio, pasu_analysis.data_fim)
        usufrutos = usufrutos.exclude(data_prevista_fim__lt=pasu_analysis.data_inicio)
        usufrutos = usufrutos.exclude(data_fim_cache__lt=pasu_analysis.data_inicio)
        usufrutos = usufrutos.exclude(data_inicio__gt=pasu_analysis.data_fim)
        for usu in usufrutos:
            dr_usufruto = NewDateRange(usu.data_inicio, usu.data_fim)
            if dr_usufruto.intersect(dr_pasu).days > 0:
                conflitos.append(usu)
        return conflitos

    def conflicting_where_substitute(
        self, pasu_analysis, registry_exclude=[], limit=None
    ):
        """
        :py:function:: conflicting_where_substitute(self, pasu_analysis, registry_exclude=[])

        This method returns substitutes that conflicting by given specific period(pasu_analysis).
        Este método retorna os substitutos que conflitam com o período.

        :param PeriodoAquisitivoServidorUsufruto pasu_analysis: PeriodoAquisitivoServidorUsufruto to conflict analysis
        :param list registry_exclude: list of registry to exclude of the analysis
        :return: dict {
            count: {
                'registry': '',
                'pasu': 'PeriodoAquisitivoServidorUsufruto',
                'order': 'order of substitution',
                'workplace': 'unicode of replaced'
            }
        }
        :rtype: dict
        """
        identify = {}
        count = 0
        registry_where_substituted = self._registry_where_substitute()
        where_substitute_employee_workplace_vacation = []
        if len(registry_where_substituted):
            where_substitute_employee_workplace_vacation = (
                self.servidor.where_substitute_employee_workplace_vacation().filter(
                    servidor__tipo="M"
                )
            )
        for reg in registry_where_substituted:
            if reg not in registry_exclude:
                pasus = self.chek_conflicts_where_substitute(
                    pasu_analysis, registry_where_substitute=[reg]
                )
                q1 = where_substitute_employee_workplace_vacation.filter(
                    servidor__matricula=reg
                )
                for pasu in pasus:
                    for employee_workplace in q1:
                        for rpl in self.servidor.where_replacement_substitute_vacation(
                            workplace=employee_workplace.lotacao,
                            employee=employee_workplace.servidor,
                        ):
                            new = {
                                "registry": reg,
                                "pasu": pasu,
                                "order": rpl.order,
                                "workplace": rpl.replaced,
                            }
                            if not PeriodoAquisitivoServidorMembro.check_duplicity_substitute(
                                identify, new
                            ):
                                identify.update({count: new})
                                count += 1

                            if check_limit(count, limit):
                                break
                        if check_limit(count, limit):
                            break
            if check_limit(count, limit):
                break
        return identify

    @classmethod
    def check_duplicity_substitute(cls, lines, new):
        exists = False
        for key in lines:
            if (
                lines.get(key).get("registry") == new.get("registry")
                and lines.get(key).get("workplace") == new.get("workplace")
                # lines.get(key).get('order') == new.get('order') and
            ):
                exists = True
                break
        return exists

    def _registry_where_substitute(self):
        """
        :py:function:: _registry_where_substitute(self)

        This method returns registry of the employee where substitute.

        :return: list
        :rtype: list
        """
        registry_where_substitute = [
            employee.matricula
            for employee in self.servidor.where_substitute_employee_vacation()
        ]
        return registry_where_substitute

    def _conflicting_where_substitute_pasus_found(
        self, pasu_analysis, registry_exclude=[], limit=None
    ):
        """
        :py:function:: _conflicting_where_substitute_pasus_found(self, pasu_analysis, registry_exclude=[])

        This method returns substitutes that conflicting by given specific period(pasu_analysis).

        :param PeriodoAquisitivoServidorUsufruto pasu_analysis: PeriodoAquisitivoServidorUsufruto to conflict analysis
        :param list registry_exclude: list of registry to exclude of the analysis
        :return: list
        :rtype: list
        """
        log.debug("_conflicting_where_substitute_pasus_found")
        return pasu_analysis.pas.conflicting_where_substitute(
            pasu_analysis, registry_exclude=registry_exclude, limit=limit
        )

    def conflito(self, pasu):
        """
        Retorna True caso @pasu esta em conflito com TODOS os servidores substitutos e o
        atributo @bloquear_conflito seja True em Configuracao
        """
        log.debug(self.periodo_aquisitivo.configuracao.bloquear_conflitos)
        if self.periodo_aquisitivo.configuracao.bloquear_conflitos:
            return False

        conflito_bloqueante = False

        registry_substitutes = self._matricula_substitutos()
        if registry_substitutes:
            self.validate_conflitos(pasu, substitutos=registry_substitutes)
        elif not self.avoid_conflict_member():
            raise ConflictFeriasError("Não possui substituto.")

        return conflito_bloqueante

    def conflitantes(self, pasu_analysis):
        """
        :py:function:: conflitantes(self, pasu_analysis)

        This method returns a dict of employee:pasu that conflicts with the given pasu_analysis.

        Este método retorna os substitutos que conflitam com o período.

        :param PeriodoAquisitivoServidorUsufruto pasu_analysis:
        :return: dict
        :rtype: dict
        """
        conflitantes = {}
        conflicts = self.conflitos(pasu_analysis)
        pasus = [conflicts[key].get("pasu") for key in conflicts]
        for pasu in pasus:
            if pasu.pas.servidor.matricula not in conflitantes:
                conflitantes[pasu.pas.servidor.matricula] = []
            conflitantes.update({pasu.pas.servidor.matricula: pasu})
        return conflitantes

    def validate_conflitos(self, pasu, substitutos=[]):
        """
        :py:function:: validate_conflitos(self, pasu, substitutos=[])

        This method validates if a conflict is block mandatory.
        At least one substitute can't conflicts against substituted.

        Este método verifica se existe algum conflito bloqueante. Pelo menos um dos substitutos não pode conflitar
        com o substituído.

        :param PeriodoAquisitivoServidorUsufruto pasu:
        :param list substitutos: list of registry to substitutos
        :return: bool
        :rtype: bool
        :raises Exception:
        """
        log.debug("__________validate_conflitos______________")
        conflito_bloqueante = False
        mensagem = "<br>Conflito(s):"
        conflitantes = self.conflitantes(pasu)
        if len(substitutos) <= len(conflitantes):
            conflito_bloqueante = True
        for conflitante in list(conflitantes.keys()):
            mensagem += "<br>%s:  %s" % (
                conflitantes.get(conflitante).pas.servidor,
                conflitantes.get(conflitante),
            )

        if (
            self.periodo_aquisitivo.configuracao.bloquear_conflitos
            and self.avoid_conflict_member()
        ):
            conflito_bloqueante = False

        if conflito_bloqueante:
            raise ConflictFeriasError(mensagem)
        return conflito_bloqueante

    def avoid_conflict_member(self):
        avoid = False
        if (
            not self.servidor.member_substitute
            and BaseLicencaAfastamento.objects.filter(
                servidor=self.servidor, estado=ACTIVE
            )
            .filter(
                Q(desempenhofuncao__isnull=False)
                | Q(atuacaogrupotrabalho__isnull=False)
            )
            .exists()
        ):
            avoid = not self.servidor.owner_of_job_position_effective()
        return avoid

    def validate_installment_amount(self, pasu_new=[], exclude_pasus=[]):
        # CHECAGEM BÁSICA ANTEIOR FOI COMENTADA EM FAVOR DA NOVA IMPLEMENTAÇÃO
        # if len(novos) > self.periodo_aquisitivo.configuracao.max_divisoes:
        #     raise FeriasError('O número máximo de parcelas é %d.' % self.periodo_aquisitivo.configuracao.max_divisoes)
        super(PeriodoAquisitivoServidorMembro, self).validate_installment_amount(
            pasu_new=pasu_new, exclude_pasus=exclude_pasus
        )

    def conflitos_substituicao(self, pasu):
        return BaseLicencaAfastamento.substitutions_conflicts(
            None, pasu.pas.servidor, pasu.data_inicio, pasu.data_fim
        )


class PeriodoAquisitivoServidorAdmin(PeriodoAquisitivoServidor):
    class Meta:
        db_table = "frs_paservidoradmin"

    @ilru_cache()
    def _get_filter_conflitos(self):
        usufrutos = super(PeriodoAquisitivoServidorAdmin, self)._get_filter_conflitos()
        return usufrutos


# ------------------------------------------------------------------------------------------------


"""
Classe para a criação de PeriodoAquisitivoServidor de acordo com o servidor.
Ex.: Membro -> PeriodoAquisitivoServidorMembro
     Administrativo(Servidor) -> PeriodoAquisitivoServidorAdmin
"""


class PeriodoAquisitivoFactory:
    class Meta:
        abstract = True

    """
    Cria o periodo aquisitivo para o tipo de servidor requisitado
    """

    def create(self, tipo_servidor="S", bloqueado=False):
        if tipo_servidor == "M":  # Membros
            self.pas = PeriodoAquisitivoServidorMembro()
        else:  # Servidores Administrativos (tipo_servidor=='S'):
            self.pas = PeriodoAquisitivoServidorAdmin()
        return self.pas


# ------------------------------------------------------------------------------------------------


@to_search(
    [
        {
            "name": "periodo_aquisitivo_servidor__servidor__pessoa_fisica__nome",
            "type": "text",
        },
        {"name": "periodo_aquisitivo_servidor__servidor__matricula", "type": "text"},
        {
            "name": "periodo_aquisitivo_servidor__periodo_aquisitivo__ano_aquisicao",
            "type": "number",
        },
        {"name": "autorizado_por__pessoa_fisica__nome", "type": "text"},
        {"name": "estado", "type": "choices"},
    ]
)
class PeriodoAquisitivoServidorUsufruto(AuditTimestampModel):
    """
    Classe para controlar os usufrutos de cada servidor
    """

    class Meta:
        db_table = "frs_paservidorusufruto"

    periodo_aquisitivo_servidor = models.ForeignKey(
        "PeriodoAquisitivoServidor",
        on_delete=models.CASCADE,
        help_text="O período aquisitivo refente a que o servidor tem direito.",
        verbose_name="Período aquisitivo",
        related_name="usufrutos",
    )
    data_inicio = models.DateField(
        help_text="Início da fruição desse período de férias.", verbose_name="Início"
    )
    data_prevista_fim = models.DateField(
        null=True,
        blank=True,
        help_text="Data prevista de fim da fruição desse período de férias.",
        verbose_name="Prevista de Fim",
    )
    data_fim_cache = models.DateField(
        null=True,
        blank=True,
        help_text="Data fim da fruição desse período de férias.",
        verbose_name="Data Fim Cache",
    )
    dias = models.SmallIntegerField(
        help_text="Quantidade de dias marcados", verbose_name="Dias marcados", default=0
    )
    interrompido = models.BooleanField(
        help_text="Se a parcela foi interrompida.",
        verbose_name="Interrompido",
        default=False,
    )
    estado = models.SmallIntegerField(
        help_text="Situação atual",
        verbose_name="Situação",
        default=PASU_NOVO,
        choices=list(ESTADO_PASU.items()),
    )
    autorizado_em = models.DateField(
        help_text="Data em que essa parcela foi autorizada pela chefia.",
        verbose_name="Autorizado em",
        blank=True,
        null=True,
    )
    autorizado_por = models.ForeignKey(
        "rh.Servidor",
        on_delete=models.PROTECT,
        help_text="O servidor (Chefe) que autorizou essa parcela",
        verbose_name="Autorizado por",
        related_name="ferias_autorizadas",
        blank=True,
        null=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True, blank=True)
    suspenso_em = models.DateTimeField(blank=True, null=True)
    suspenso_por = models.ForeignKey(
        "rh.Servidor",
        on_delete=models.PROTECT,
        help_text="O servidor que suspenendeu essa parcela",
        verbose_name="Suspenso por",
        related_name="ferias_suspensas",
        blank=True,
        null=True,
    )
    notificacoes = generic.GenericRelation(
        Notification, content_type_field="sender_ct", object_id_field="sender_id"
    )

    def save(self, force_insert=False, force_update=False):
        try:
            if self.validar_pasu():
                if self.data_prevista_fim is None:
                    self.data_prevista_fim = self.data_fim
                self.data_fim_cache = self.data_fim
                super(PeriodoAquisitivoServidorUsufruto, self).save(
                    force_insert, force_update
                )
        except FeriasError as err:
            log.exception(err)
            raise err
        except Exception as err:
            log.exception(err)
            raise FeriasError("Erro ao salvar a parcela de usufruto.")

    def __str__(self):
        return (
            "%s - %s a %s"
            % (
                self.periodo_aquisitivo_servidor.periodo_aquisitivo,
                DateUtils.date_to_str(self.data_inicio),
                DateUtils.date_to_str(self.data_fim) if self.data_fim else "",
            )
            if self.periodo_aquisitivo_servidor_id
            else "PASU Vazio"
        )

    def _get_data_fim(self):
        return (
            self.data_inicio + datetime.timedelta(days=self.dias - 1)
            if (self.dias and self.data_inicio)
            else self.data_inicio
        )

    def _set_data_fim(self, date):
        if self.data_inicio:
            self.dias = (date - self.data_inicio).days + 1
        return self.dias

    data_fim = property(_get_data_fim, _set_data_fim)

    # Retorna a situação (texto descritivo do estado) de uma parcela
    def _get_situacao(self):
        return ESTADO_PASU[self.estado] if self.estado in ESTADO_PASU else "Indefinido"

    situacao = property(_get_situacao)

    def _get_autorizado(self):
        """Retrona se a parcela foi autorizada"""
        # self.estado in [PASU_HOMOLOGADO, PASU_ALTERADO, PASU_INTERROMPIDO, PASU_SUSPENSO, PASU_FRUINDO, PASU_FRUIDO]
        return (
            self.autorizado_em
            and self.estado
            not in [
                PASU_NAOAUTORIZADO,
            ]
            or False
        )

    # TODO Voltar para o estado anterior caso não seja autorizado
    def _set_autorizado(self, value):
        acao = "autorizar" if value is True else "desautorizar"
        estado_dest = PASU_AUTORIZADO_CI if value is True else PASU_NAOAUTORIZADO
        self.transicao(acao, estado_dest)
        self.autorizado_em = datetime.datetime.now().date()
        return self.save()

    autorizado = property(_get_autorizado, _set_autorizado)

    def _get_notificado(self):
        return self.notificacoes.all().count() > 0

    notificado = property(_get_notificado)

    # Retorna se a parcela foi homologada
    # TODO Verificar se está com um valor válido
    @property
    def homologado(self):
        return self.estado in [
            PASU_HOMOLOGADO,
            PASU_EMALTERACAO,
            PASU_ALTERADO,
            PASU_INTERROMPIDO,
            PASU_SUSPENSO,
            PASU_FRUINDO,
            PASU_FRUIDO,
        ]

    @homologado.setter
    def homologado(self, value):
        if value is True:
            self.transicao("homologar", PASU_HOMOLOGADO)
        return self.save()

    def _interromper(self, data, force=False):
        if data:
            # A data final da parcela fica sendo o dia anterior à interrupção
            self.data_fim = data - datetime.timedelta(days=1)
            self.suspenso_em = datetime.datetime.now()
            self.suspenso_por = employee_from_user(get_current_user())
            self.transicao(
                "interromper", PASU_INTERROMPIDO, True
            )  # A interrupção sempre é via administrativa, logo, pode ser retroativo.
            self.interrompido = True
            self.save()
        return self

    # Retorna se a parcela foi interrompida
    def _get_interrompido(self):
        return self.estado == PASU_INTERROMPIDO

    def _set_interrompido(self, data):
        return self._interromper(data)

    interromper = property(_get_interrompido, _set_interrompido)

    # Retorna se a parcela para foi suspensa
    def _get_suspenso(self):
        return self.estado == PASU_SUSPENSO

    def _set_suspenso(self, value):
        if value:
            self.transicao("suspender", PASU_SUSPENSO)
            self.suspenso_em = datetime.now()
            self.suspenso_por = employee_from_user(get_current_user())

    suspenso = property(_get_suspenso, _set_suspenso)

    # Retorna se a parcela foi alterada, por processo formal, após a homologação
    def _get_alterado(self):
        return self.estado == PASU_ALTERADO

    def _set_alterado(self, value):
        if value is True:
            self.transicao("alterar", PASU_ALTERADO)

    alterado = property(_get_alterado, _set_alterado)

    # Retorna se a parcela foi alterada, por processo formal, após a homologação
    def _get_emalteracao(self):
        return self.estado == PASU_EMALTERACAO

    def _set_emalteracao(self, value):
        if value is True:
            self.transicao("alterar", PASU_EMALTERACAO)

    emalteracao = property(_get_emalteracao, _set_emalteracao)

    # Retorna se a parcela foi alterada, por processo formal, após a homologação
    def _get_pasu_alteracao(self):
        return PASUAlteracao.objects.filter(
            periodoaquisitivoservidorusufruto_ptr=self
        ).exists()

    pasu_alteracao = property(_get_pasu_alteracao)

    # Retorna se a parcela foi alterada, por processo formal, após a homologação
    def _get_alteracao(self):
        return (
            self.alteracao_out.get(Q(autorizado=True) | Q(autorizado_por=None))
            if self.emalteracao or self.alterado
            else None
        )

    alteracao = property(_get_alteracao)

    # Retorna se a parcela foi fruida
    def _get_fruido(self):
        return self.estado == PASU_FRUIDO

    def _set_fruido(self, value):
        if value is True:
            self.transicao("finalizar", PASU_FRUIDO)

    fruido = property(_get_fruido)

    # Retorna se a parcela esta em fruicao
    def _get_fruindo(self):
        return self.estado == PASU_FRUINDO

    def _set_fruindo(self, value):
        if value is True:
            self.transicao("fruir", PASU_FRUINDO)

    fruindo = property(_get_fruindo)

    # Retorna o PAS específico (PASAdmin ou PASMembro)
    def _get_pas(self):
        return self.periodo_aquisitivo_servidor.pas

    pas = property(_get_pas)

    def validar_acao(self, acao):
        if (self.estado in PASU_SM) and (acao in PASU_SM[self.estado]):
            return PASU_SM[self.estado][acao]
        else:
            raise InvalidStateFeriasError(
                "Ação inválida: (%s) para (%s) não existe!"
                % (ESTADO_PASU[self.estado], acao)
            )

    def transicao(self, acao, estado_dest, force=False):
        if not force:
            estados = self.validar_acao(acao)
        else:
            estados = True
        # Verifica se é uma transição forçada (feita por um administrativo) ou senão for verifica se o estado destino está
        # dentro dos estados possíveis
        if force | (estados & estado_dest):
            self.estado = estado_dest
            self.save()
        else:
            raise InvalidStateFeriasError(
                "Transição inválida: [ESTADO: %s -> AÇÃO: %s -> ESTADO: %s]!"
                % (ESTADO_PAS[self.estado], acao, ESTADO_PAS[estado_dest])
            )

    def validar_pasu(self):
        if not self.periodo_aquisitivo_servidor_id:
            raise ValidateFeriasError("O período de aquisição dever ser indicado")
        if not (self.data_inicio and self.data_fim):
            raise ValidateFeriasError("Data inicial e data final devem ser preenchidas")
        if self.data_inicio > self.data_fim:
            raise ValidateFeriasError("Data final deve ser posterior à data inicial")
        return True

    def conflitos(self):
        """
        :py:function:: conflitos(self, pasu, exclude=False)

        This method returns a list of PeriodoAquisitivoServidorUsufruto that conflicts
        with its own PeriodoAquisitivoServidorUsufruto.
        Employee is given by PeriodoAquisitivoServidorUsufruto(self).periodo_aquisitivo_servidor.

        :param PeriodoAquisitivoServidorUsufruto pasu:
        :return: list of PeriodoAquisitivoServidorUsufruto
        :rtype: list
        """
        serv = self.periodo_aquisitivo_servidor.servidor
        return [
            usu
            for usu in PeriodoAquisitivoServidor.objects.filter(
                periodo_aquisitivo_servidor__servidor=serv
            )
            if not (self.data_fim < usu.data_inicio or self.data_inicio > usu.data_fim)
        ]

    # -------- Ações --------------------------------------------------------------------
    def alterar(self):
        self.validar_acao("alterar")

    def desmarcar(self):
        self.transicao("desmarcar", PASU_NOVO)
        self.delete()

    def _reenviar(self):
        substitutions = self.pas.conflitos_substituicao(self)
        if not substitutions.exists():
            self.save()
        else:
            raise FeriasError(
                "Por favor verifique os conflitos, pois ainda existem substituições pendentes %s"
                % substitutions.first()
            )

    @classmethod
    def get_conflitos(cls, pasus=[], limit=None):
        obj = {
            "result": [],
        }
        for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(
            pk__in=pasus
        ).exclude(
            estado__in=[
                PASU_ALTERADO,
                PASU_NAOAUTORIZADO,
                PASU_SUSPENSO,
                PASU_FRUIDO,
                PASU_INTERROMPIDO,
            ]
        ):
            pas = pasu.pas
            dr_pasu = NewDateRange(pasu.data_inicio, pasu.data_fim)
            conflicts_pasu = pas.conflitos(pasu)
            log.debug(f"conflicts_pasu {conflicts_pasu}")
            for key in conflicts_pasu:
                usu = conflicts_pasu[key].get("pasu", None)
                obj["result"].append(
                    {
                        "pk": usu.pk if usu else "",
                        "periodo_aquisitivo": (
                            "%s" % usu.periodo_aquisitivo_servidor.periodo_aquisitivo
                            if usu
                            else ""
                        ),
                        "servidor": (
                            "%s" % usu.periodo_aquisitivo_servidor.servidor
                            if usu
                            else conflicts_pasu[key].get("error")
                        ),
                        "periodo": (
                            "%s - %s"
                            % (
                                DateUtils.date_to_str(usu.data_inicio),
                                DateUtils.date_to_str(usu.data_fim),
                            )
                            if usu
                            else ""
                        ),
                        "marcado_em": (
                            DateUtils.date_to_str(usu.criado_em) if usu else ""
                        ),
                        "qtd": (
                            NewDateRange(usu.data_inicio, usu.data_fim)
                            .intersect(dr_pasu)
                            .days
                            if usu
                            else ""
                        ),
                        "order": conflicts_pasu[key].get("order", 0),
                        "workplace": str(conflicts_pasu[key].get("workplace")),
                    }
                )

            conflitos_afastamento = pas.conflitos_afastamento(pasu)
            log.debug(f"conflitos_afastamento {conflitos_afastamento}")
            for afastamento in conflitos_afastamento:
                if (
                    pasu.data_inicio != afastamento.data_inicio
                    and pasu.data_fim != afastamento.data_fim
                ):
                    obj["result"].append(
                        {
                            "pk": afastamento.pk,
                            "periodo_aquisitivo": "--------------------------",
                            "servidor": "%s" % afastamento,
                            "periodo": "%s - %s"
                            % (
                                DateUtils.date_to_str(afastamento.data_inicio),
                                (
                                    DateUtils.date_to_str(afastamento.data_fim)
                                    if afastamento.data_fim
                                    else ""
                                ),
                            ),
                            "marcado_em": DateUtils.date_to_str(afastamento.created_at),
                            "qtd": NewDateRange(
                                afastamento.data_inicio, afastamento.data_fim
                            )
                            .intersect(dr_pasu)
                            .days,
                            "order": "",
                            "workplace": "",
                        }
                    )

            conflitos_substituicao = pas.conflitos_substituicao(pasu)
            log.debug(f"conflitos_substituicao {conflitos_substituicao}")
            for substituicao in conflitos_substituicao:
                message_conflict = "Substituindo %s" % substituicao
                if substituicao.designation_substituted:
                    message_conflict = "Substituindo: %s" % (
                        substituicao.designation_substituted.lotacao
                    )
                obj["result"].append(
                    {
                        "pk": substituicao.pk,
                        "periodo_aquisitivo": "--------------------------",
                        "servidor": message_conflict,
                        "periodo": "%s - %s"
                        % (
                            DateUtils.date_to_str(substituicao.data_inicio),
                            (
                                DateUtils.date_to_str(substituicao.data_fim)
                                if substituicao.data_fim
                                else ""
                            ),
                        ),
                        "marcado_em": DateUtils.date_to_str(substituicao.created_at),
                        "qtd": NewDateRange(
                            substituicao.data_inicio, substituicao.data_fim
                        )
                        .intersect(dr_pasu)
                        .days,
                        "order": "",
                        "workplace": "",
                    }
                )

            conflicts = pas.conflitos_contratos(pasu)
            log.debug(f"conflicts {conflicts}")
            for key in list(conflicts.keys()):
                for conflict in conflicts.get(key):
                    pasu = conflict.get("usu")
                    message_conflict = ""
                    if pasu:
                        message_conflict = "Fiscal %s: %s - %s" % (
                            conflict.get("kind"),
                            conflict.get("number"),
                            pas.servidor,
                        )
                    obj["result"].append(
                        {
                            "pk": "",
                            "periodo_aquisitivo": (
                                "%s"
                                % usu.periodo_aquisitivo_servidor.periodo_aquisitivo
                                if pasu
                                else ""
                            ),
                            "servidor": message_conflict,
                            "periodo": (
                                str(
                                    "%s - %s"
                                    % (
                                        DateUtils.date_to_str(pasu.data_inicio),
                                        DateUtils.date_to_str(pasu.data_fim),
                                    )
                                )
                                if pasu
                                else ""
                            ),
                            "marcado_em": (
                                DateUtils.date_to_str(pasu.criado_em) if pasu else ""
                            ),
                            "qtd": (
                                NewDateRange(pasu.data_inicio, pasu.data_fim)
                                .intersect(dr_pasu)
                                .days
                                if pasu
                                else ""
                            ),
                            "order": "",
                            "workplace": "",
                        }
                    )
        return obj


# ---------------------------------------------------------------------------------------------
class PASUAlteracao(PeriodoAquisitivoServidorUsufruto):
    """
    Classe para controlar os usufrutos que alteraram outro usufruto
    """

    class Meta:
        db_table = "frs_pasualterado"

    pasu_alterado = models.ForeignKey(
        "PeriodoAquisitivoServidorUsufruto",
        on_delete=models.CASCADE,
        help_text="O usufruto que foi alterado por esse.",
        verbose_name="Usufruto alterado",
        related_name="pasu_alteracao",
    )
    justificativa = models.TextField(
        help_text="Justificativa para a alteração da parcela de ususfruto.",
        verbose_name="Justificativa",
    )


# ---------------------------------------------------------------------------------------------


class AlteracaoPASU(AuditTimestampModel):
    """
    Classe para controlar os usufrutos que alteraram outro usufruto
    """

    class Meta:
        db_table = "frs_alteracao"

    pas = models.ForeignKey(
        "PeriodoAquisitivoServidor",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Alteração de parcelas de um servidor em um determinado período aquisitivo.",
        verbose_name="Alteração",
        related_name="alteracoes",
    )
    novos_pasus = models.ManyToManyField(
        "PeriodoAquisitivoServidorUsufruto",
        blank=True,
        verbose_name="Novos",
        related_name="alteracao_in",
    )
    antigos_pasus = models.ManyToManyField(
        "PeriodoAquisitivoServidorUsufruto",
        blank=True,
        verbose_name="Antigos",
        related_name="alteracao_out",
    )
    anotacao = models.ForeignKey(
        "rh.AnotacaoFerias",
        on_delete=models.PROTECT,
        help_text="Anotação de Alteração.",
        verbose_name="Anotação",
        blank=True,
        null=True,
        related_name="alteracoes_ferias",
    )
    autorizado = models.BooleanField(
        help_text="Se a autorizacao foi deferida ou indeferida.",
        verbose_name="Autorizado",
        blank=True,
        default=False,
    )
    autorizado_em = models.DateField(
        help_text="Data em que essa parcela foi autorizada pela chefia.",
        verbose_name="Autorizado em",
        blank=True,
        null=True,
    )
    autorizado_por = models.ForeignKey(
        "rh.Servidor",
        on_delete=models.PROTECT,
        help_text="O servidor (Chefe) que autorizaou essa parcela",
        verbose_name="Autorizado por",
        related_name="autorizacoes_ferias",
        blank=True,
        null=True,
    )
    criado_em = models.DateTimeField(auto_now=True, blank=True)
    justificativa = models.TextField(
        help_text="Justificativa para a alteração da parcela de ususfruto.",
        verbose_name="Justificativa",
    )

    def __str__(self):
        if self.novos_pasus and self.antigos_pasus:
            novos = []
            antigos = []
            for pasu in self.novos_pasus.all():
                novos.append(
                    "%s à %s (%s dias)"
                    % (
                        pasu.data_inicio.strftime("%d/%m/%Y"),
                        pasu.data_fim.strftime("%d/%m/%Y"),
                        pasu.dias,
                    )
                )
            for pasu in self.antigos_pasus.all():
                antigos.append(
                    "%s à %s (%s dias)"
                    % (
                        pasu.data_inicio.strftime("%d/%m/%Y"),
                        pasu.data_fim.strftime("%d/%m/%Y"),
                        pasu.dias,
                    )
                )
            return "De: %s para: %s" % (
                ", ".join(antigos) or "Época oportuna",
                ", ".join(novos) or "Época oportuna",
            )
        return "Indefinido"

    def validate_pas_for_pasus(self, antigos):
        """
        Valida se os PASUs a serem alterados são do mesmo pas do pedido de alteração
        @antigos: array contendo os ids dos PASUs a serem alterados
        Um exceção é disparada caso algum dos PASUs não seja do mesmo PAS da alteração
        RETURN: True se validou corretamente
        """
        if not isinstance(antigos, list):
            raise FeriasError("[E0001]: Erro ao executar operação.")
        for id in antigos:
            if not self.pas.usufrutos.filter(id=id):
                raise ValidateFeriasError(
                    "As parcelas a serem alteradas devem ser do mesmo período."
                )
        return True

    def _get_dias_alterados(self):
        dm = self.antigos_pasus.aggregate(dias=models.Sum("dias"))
        return dm["dias"] or 0

    dias_alterados = property(_get_dias_alterados)

    def _get_dias_marcados(self):
        dm = self.novos_pasus.aggregate(dias=models.Sum("dias"))
        return dm["dias"] or 0

    dias_marcados = property(_get_dias_marcados)

    def _get_epoca_oportuna(self):
        _epoca_oportuna = self.dias_alterados - self.dias_marcados
        if _epoca_oportuna < 0:
            _epoca_oportuna = 0
        return _epoca_oportuna

    epoca_oportuna = property(_get_epoca_oportuna)

    def _get_deferido(self):
        return self.autorizado

    deferido = property(_get_deferido)

    def _get_indeferido(self):
        """
        Retorna True quando uma Alteracao tem @autorizacao como False e uma data em @autorizado_em setada.
        Pois por default @autorizado é False e por isso apenas a informação de @autorizado como False
        não pode caracterizar como indeferido, mas se for False e tiver a data de autorizacao em @autorizado_em
        ai sim pode ser considerado indeferido
        """
        return not self.autorizado and self.autorizado_em

    indeferido = property(_get_indeferido)

    def deferir(self, autorizar, responsavel_id, publicacao_id=0, anotar=True):
        for pasu in self.antigos_pasus.all():
            if autorizar:
                pasu.alterado = True
            else:  # Se foi indeferido o PASU volta para o estado de HOMOLOGADO
                pasu.estado = PASU_HOMOLOGADO
                pasu.save()
        for pasu in self.novos_pasus.all():
            pasu.autorizado_por_id = responsavel_id
            pasu.autorizado = autorizar
        self.autorizado = autorizar
        self.autorizado_por_id = responsavel_id
        self.autorizado_em = datetime.datetime.now()
        if autorizar:
            if self.pas.homologado:
                self.pas.homologar_usufruto(
                    [p.id for p in self.novos_pasus.all()], False, publicacao_id
                )
            # TODO anotar autorizacao
            if anotar:
                self.criar_anotacao(publicacao_id)
        else:
            self.delete()

    def criar_anotacao(self, publicacao_id=0):
        params = {}
        publicacao = Publicacao.objects.get(id=publicacao_id) if publicacao_id else None
        params["texto"] = self.get_texto(publicacao_id)
        params["publicacao"] = publicacao.id if publicacao else None
        params["tipo_documento"] = (
            publicacao.tipo if publicacao else 100
        )  # DOCUMENTO DIGITAL
        params["resumo"] = "Alteração de Férias %s" % self.pas.periodo_aquisitivo
        params["periodo"] = "%s" % self.pas.periodo_aquisitivo
        params["tipo"] = "ALTERACAO"
        params["identificador"] = "%s" % self.id
        self.pas.anotar_ferias(params)
        return True

    def get_texto(self, publicacao_id):
        publicacao = Publicacao.objects.get(id=publicacao_id) if publicacao_id else None
        modo = (
            "%s n° %s/%s de %s"
            % (
                publicacao.get_tipo_display(),
                publicacao.numero,
                publicacao.ano,
                publicacao.data_vigencia.strftime("%d/%m/%Y"),
            )
            if publicacao
            else "solicitação online (via sistema Athenas) n° %s de %s"
            % (self.id, self.criado_em.strftime("%d/%m/%Y"))
        )
        parcelas = ""
        for pasu in self.antigos_pasus.all():
            if parcelas:
                parcelas += ", "
            parcelas += "%s a %s (%s dias)" % (
                pasu.data_inicio.strftime("%d/%m/%Y"),
                pasu.data_fim.strftime("%d/%m/%Y"),
                pasu.dias,
            )
        usufrutos = ""
        for pasu in self.novos_pasus.all():
            if usufrutos:
                usufrutos += ", "
            usufrutos += "%s a %s (%s dias)" % (
                pasu.data_inicio.strftime("%d/%m/%Y"),
                pasu.data_fim.strftime("%d/%m/%Y"),
                pasu.dias,
            )
        msg = Message.objects.get(mid="FRS_ANOTACAO_ALTERACAO")
        if self.epoca_oportuna > 0:
            if usufrutos:
                usufrutos += " e "
            usufrutos += "%s dias para época oportuna" % self.epoca_oportuna
            msg = Message.objects.get(mid="FRS_ANOTACAO_ALTERACAO_ATHENAS")
            modo = ("%s conforme " % self.justificativa) + modo
        return msg.formated(
            {
                "pa": "%s" % self.pas.periodo_aquisitivo,
                "modo": modo,
                "usufrutos": usufrutos,
                "parcelas": parcelas,
            }
        )

    def indeferir(self, responsavel_id, publicacao_id=0):
        pass

    def delete(self, *args, **kargs):
        log.debug("DELETING %s ======================" % self)

        pasus = [pasu.pk for pasu in self.antigos_pasus.all()]
        log.debug("PASUS: %s" % pasus)

        for pasu in self.novos_pasus.all():
            pasu.delete()

        for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(pk__in=pasus):
            log.debug("PASU: %s(%s)" % (pasu, pasu.get_estado_display()))

        PeriodoAquisitivoServidorUsufruto.objects.filter(pk__in=pasus).update(
            estado=PASU_HOMOLOGADO
        )

        for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(pk__in=pasus):
            log.debug("PASU: %s(%s)" % (pasu, pasu.get_estado_display()))

        if self.anotacao:
            self.anotacao.delete()

        super(AlteracaoPASU, self).delete(*args, **kargs)
        log.debug("FIM DELETING <<<<<<<<<<<<<<<<<<<<<<")

    @classmethod
    def alteracao_ferias_epoca_oportuna(
        cls, user, instance, servidor, data_inicio, data_fim, justificativa, publicacao
    ):
        """
        Este método altera para época oportuna todos os períodos marcados que intercedam com o período informado.
        """
        mail_mensagens = []
        alteracaoPasu = None
        try:
            with transaction.atomic():
                for pas in PeriodoAquisitivoServidor.objects.filter(
                    servidor=servidor,
                    usufrutos__data_inicio__gte=data_inicio,
                    usufrutos__data_inicio__lte=data_fim,
                    usufrutos__estado__in=(PASU_HOMOLOGADO, PASU_FRUINDO, PASU_FRUIDO),
                ).distinct():
                    try:
                        with transaction.atomic():
                            pasus_antigos = pas.usufrutos.filter(
                                data_inicio__gte=data_inicio,
                                data_inicio__lte=data_fim,
                                estado__in=(PASU_HOMOLOGADO, PASU_FRUINDO, PASU_FRUIDO),
                            )
                            parcelas = ""
                            for pasu in pasus_antigos:
                                if len(parcelas) > 0:
                                    parcelas += ", "
                                parcelas += "%s a %s (%s dias)" % (
                                    pasu.data_inicio.strftime("%d/%m/%Y"),
                                    pasu.data_fim.strftime("%d/%m/%Y"),
                                    pasu.dias,
                                )
                            mensagem = (
                                "O(A) %s gerou alteração dos períodos aquisitivos: %s."
                                % (instance, parcelas)
                            )
                            alteracaoPasu = pas.solicitar_alteracao(
                                antigos=pasus_antigos,
                                novos=[],
                                responsavel_id=user.servidor.pk,
                                justificativa="Alteração gerada por %s" % justificativa,
                                publicacao_id=(
                                    publicacao.pk if publicacao is not None else None
                                ),
                            )
                            pas.atualiza_estado()
                            texto = alteracaoPasu.get_texto(
                                publicacao.pk if publicacao is not None else None
                            )
                            Notification.notify(
                                "FRS_NOTIFICACAO_ATHENAS",
                                servidor,
                                instance,
                                mensagem=texto,
                            )
                            Notification.notify(
                                "FRS_NOTIFICACAO_ATHENAS",
                                user.servidor,
                                instance,
                                mensagem=mensagem,
                            )
                    except Exception as err:
                        texto = (
                            "Problema na solicitação de alteração do PAS: %s para época futura."
                            % pas
                        )
                        log.info(texto)
                        log.exception(err)
                        with transaction.atomic():
                            try:
                                if alteracaoPasu is not None:
                                    alteracaoPasu.delete()
                            except Exception as err:
                                log.exception(err)
                        mail_mensagens.append(texto)
        except Exception as err:
            texto = "Problema na alteração das férias para época futura."
            log.info(texto)
            log.exception(err)
            mail_mensagens.append(texto)
        finally:
            try:
                for mensagem in mail_mensagens:
                    mail_managers(
                        "ERRO EM %s" % cls.__name__, mensagem, fail_silently=True
                    )
            except Exception as err:
                log.exception(err)
        return True

    @classmethod
    def change_vacation_by_fire(
        cls, user, fired, employee, date_start, justification, publication
    ):
        """
        Este método altera para época oportuna todos os períodos marcados que intercedam com o período informado.
        """
        alteracaoPasu = None
        try:
            possessions = MovimentacaoPosse.objects.filter(
                Q(servidor=employee)
                & (
                    Q(data_desligamento__gt=fired.data_desligamento)
                    | Q(data_desligamento=None)
                )
            ).exclude(pk=fired.movimentacao_posse.pk)
            if not possessions.exists():
                with transaction.atomic():
                    for pas in PeriodoAquisitivoServidor.objects.filter(
                        servidor=employee,
                        usufrutos__data_inicio__gte=date_start,
                        usufrutos__estado__in=(
                            PASU_HOMOLOGADO,
                            PASU_FRUINDO,
                            PASU_FRUIDO,
                        ),
                    ).distinct():
                        try:
                            with transaction.atomic():
                                pasus_antigos = pas.usufrutos.filter(
                                    data_inicio__gte=date_start,
                                    estado__in=(
                                        PASU_HOMOLOGADO,
                                        PASU_FRUINDO,
                                        PASU_FRUIDO,
                                    ),
                                )
                                parcelas = ""
                                for pasu in pasus_antigos:
                                    if len(parcelas) > 0:
                                        parcelas += ", "
                                    parcelas += "%s a %s (%s dias)" % (
                                        pasu.data_inicio.strftime("%d/%m/%Y"),
                                        pasu.data_fim.strftime("%d/%m/%Y"),
                                        pasu.dias,
                                    )
                                mensagem = (
                                    "O(A) %s gerou alteração dos períodos aquisitivos: %s."
                                    % (fired, parcelas)
                                )
                                alteracaoPasu = pas.solicitar_alteracao(
                                    antigos=pasus_antigos,
                                    novos=[],
                                    responsavel_id=user.servidor.pk,
                                    justificativa="Alteração gerada por %s"
                                    % justification,
                                    publicacao_id=(
                                        publication.pk if publication else None
                                    ),
                                )
                                pas.atualiza_estado()
                                texto = alteracaoPasu.get_texto(
                                    publication.pk if publication else None
                                )
                                Notification.notify(
                                    "FRS_NOTIFICACAO_ATHENAS",
                                    employee,
                                    fired,
                                    mensagem=texto,
                                )
                                Notification.notify(
                                    "FRS_NOTIFICACAO_ATHENAS",
                                    user.servidor,
                                    fired,
                                    mensagem=mensagem,
                                )
                        except Exception as err:
                            log.exception(err)
                            print(err)
                            texto = (
                                "Problema na solicitação de alteração do PAS: %s para época futura."
                                % pas
                            )
                            log.info(texto)
                            print(texto)
                            with transaction.atomic():
                                try:
                                    if alteracaoPasu is not None:
                                        alteracaoPasu.delete()
                                except Exception as err:
                                    log.exception(err)
                                    print(err)
        except Exception as err:
            log.exception(err)
            print(err)
            texto = "Problema na alteração das férias para época futura."
            log.info(texto)
            print(texto)
        return True


class VacationConflict:

    def __init__(self, **kargs):
        self.verbose = kargs.get("verbose", True)

    def _print(self, text, verbose=False):
        if verbose or self.verbose:
            print(text)

    def conflicts(
        self,
        verbose=None,
        pas=[],
        pas_estado=[
            PAS_EMANDAMENTO,
        ],
        pasu_estado=[PASU_HOMOLOGADO, PASU_NOVO, PASU_AUTORIZADO_CI],
        count_conflict_accept=2,
    ):
        """
        :py:function:: conflicts(
            self, verbose=None, pas=[], pas_estado=[PAS_EMANDAMENTO, ], pasu_estado=[PASU_HOMOLOGADO, PASU_NOVO, PASU_AUTORIZADO_CI]):

        This method show conflicts found.
        conflitos com substitutos

        :param boolean verbose: Verbose None(use class definition)
        :param list pas: pas list of the pk PeriodoAquisitivo
        :param list pas_estado: pas_estado list of the estado PeriodoAquisitivoServidor
        :param list pasu_estado: pas_estado list of the estado PeriodoAquisitivoServidorUsufruto
        :param int conflicts: amount of conflicts to show

        """
        self._print("""\nVerificando se existem conflitos em férias.""")
        verbose_old = self.verbose
        if verbose in [True, False]:
            self.verbose = verbose
        periodos = PeriodoAquisitivoServidorMembro.objects.filter(estado__in=pas_estado)
        if pas:
            periodos = PeriodoAquisitivoServidorMembro.objects.filter(
                periodo_aquisitivo__pk__in=pas
            )
        periodos = periodos.exclude(
            servidor__matricula__in=MovimentacaoPosse.objects.filter(
                quadro__cargo__nome__icontains="substituto", ativo=True
            ).values("servidor__matricula")
        )
        periodos = periodos.distinct()
        count = 0
        self._print("\n")
        for pas in periodos:
            servidor = pas.servidor
            usufrutos = pas.usufrutos.filter()
            if len(pasu_estado) > 0:
                usufrutos = usufrutos.filter(estado__in=pasu_estado)
            for pasu in usufrutos:
                if not servidor.my_replacement().exists():
                    self._print(
                        "\nSERVIDOR: %s - %s"
                        % (servidor, servidor.get_owner_location_workplace().last())
                    )
                    print("NAO EXISTE TABELA DE SUBSTITUTOS")
                    break
                try:
                    conflitantes = pas.conflitantes(pasu)
                    total_conflicts = len(conflitantes)
                    if total_conflicts > 0 and total_conflicts >= count_conflict_accept:
                        count += 1
                        self._print(
                            "\nSERVIDOR: %s - %s - PASU: %s - ESTADO: %s"
                            % (
                                servidor,
                                servidor.get_owner_location_workplace().last(),
                                pasu,
                                pasu.get_estado_display(),
                            )
                        )
                        # substitutos = servidor.my_substitute()
                        # for subs in substitutos:
                        #     if len(subs.get('substitutos')):
                        #         self._print('CARGO: (%s) %s' % (
                        #             subs.get('cargo'),
                        #             subs.get('cargo_nome'),
                        #         ))
                        #         # self._print('\nCARGO: (%s) %s POSSUI_SUBSTITUTO: %s - EXERCICIO_PLENO: %s - AFASTADO %s' % (
                        #         #     subs.get('cargo'),
                        #         #     subs.get('cargo_nome'),
                        #         #     subs.get('possui_substituto'),
                        #         #     subs.get('exercicio_pleno'),
                        #         #     subs.get('afastado'),
                        #         # ))
                        #         self._print('SUBSTITUTOS:')
                        #         for s in subs.get('substitutos'):
                        #             self._print('%s - %s' % (s.get('cargo_subs_nome'), s.get('servidor')))
                        self._print("CONFLITANTES (%s):" % total_conflicts)
                        dr_pasu = NewDateRange(pasu.data_inicio, pasu.data_fim)
                        for c in conflitantes:
                            pasu_conflito = conflitantes.get(c)
                            dr_conflito = NewDateRange(
                                pasu_conflito.data_inicio, pasu_conflito.data_fim
                            )
                            self._print(
                                "%s - %s - %s - Dias em conflito: (%s)"
                                % (
                                    pasu_conflito.pas.servidor.posses_ativas.first(),
                                    pasu_conflito,
                                    pasu_conflito.get_estado_display(),
                                    dr_pasu.intersect(dr_conflito).days,
                                )
                            )
                        self._print(
                            "\n-----------------------------------------------------"
                        )
                except Exception as err:
                    self._print(err)
        self._print(count)
        self.verbose = verbose_old

    def chek_conflicts_where_substitute(
        self,
        employee=None,
        verbose=None,
        pas=[],
        pas_estado=[
            PAS_EMANDAMENTO,
        ],
        pasu_estado=[PASU_HOMOLOGADO, PASU_NOVO, PASU_AUTORIZADO_CI],
    ):
        """
        :py:function:: chek_conflicts_where_substitute(
            self,
            employee=None,
            verbose=None,
            pas=[],
            pas_estado=[PAS_EMANDAMENTO, ],
            pasu_estado=[PASU_HOMOLOGADO, PASU_NOVO, PASU_AUTORIZADO_CI]
        ):

        This method show conflicts where the employee is substitute.

        :param Servidor employee: Verbose None(use class definition)
        :param boolean verbose: Verbose None(use class definition)
        :param list pas: pas list of the pk PeriodoAquisitivo
        :param list pas_estado: pas_estado list of the estado PeriodoAquisitivoServidor
        :param list pasu_estado: pas_estado list of the estado PeriodoAquisitivoServidorUsufruto

        """
        self._print("""\nVerificando se existem conflitos em férias.""")
        verbose_old = self.verbose
        if verbose in [True, False]:
            self.verbose = verbose
        periodos = PeriodoAquisitivoServidorMembro.objects.filter(
            estado__in=pas_estado,
        )
        if pas:
            periodos = PeriodoAquisitivoServidorMembro.objects.filter(
                periodo_aquisitivo__pk__in=pas
            )
        if employee:
            periodos = periodos.filter(servidor=employee)
        periodos = periodos.distinct()
        count = 0
        self._print("\n")
        for pas in periodos.order_by("servidor"):
            servidor = pas.servidor
            usufrutos = pas.usufrutos.filter()
            if len(pasu_estado) > 0:
                usufrutos = usufrutos.filter(estado__in=pasu_estado)
            for pasu in usufrutos:
                try:
                    identify = pas.conflicting_where_substitute(pasu)
                    if len(identify):
                        self._print(
                            "\nSERVIDOR: %s - %s"
                            % (servidor, servidor.get_owner_location_workplace().last())
                        )
                        self._print(
                            "PASU: %s - ESTADO: %s" % (pasu, pasu.get_estado_display())
                        )
                    for key in identify:
                        pasu_conflicting = identify[key].get("pasu")
                        if pasu_conflicting:
                            dr_pasu = NewDateRange(pasu.data_inicio, pasu.data_fim)
                            empl = Servidor.objects.get(
                                matricula=identify[key].get("registry")
                            )
                            self._print(
                                "   ->  %s - %s - %s"
                                % (
                                    empl,
                                    identify[key].get("order"),
                                    identify[key].get("workplace"),
                                )
                            )
                            count += 1
                            pasu_conflito = pasu_conflicting
                            dr_conflito = NewDateRange(
                                pasu_conflito.data_inicio, pasu_conflito.data_fim
                            )
                            self._print(
                                "          #  %s - %s - Dias em conflito: (%s)"
                                % (
                                    pasu_conflito,
                                    pasu_conflito.get_estado_display(),
                                    dr_pasu.intersect(dr_conflito).days,
                                )
                            )
                    if len(identify):
                        self._print(
                            "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                        )
                except Exception as err:
                    self._print(err)
        self._print(count)
        self.verbose = verbose_old

    def employees(
        self,
        verbose=None,
        pas=[],
        pas_estado=[
            PAS_EMANDAMENTO,
        ],
        pasu_estado=[PASU_HOMOLOGADO, PASU_NOVO, PASU_AUTORIZADO_CI],
        count_conflict_accept=2,
    ):
        """
        :py:function:: conflicts(
            self, verbose=None, pas=[], pas_estado=[PAS_EMANDAMENTO, ], pasu_estado=[PASU_HOMOLOGADO, PASU_NOVO, PASU_AUTORIZADO_CI]):

        This method show conflicts found.

        :param boolean verbose: Verbose None(use class definition)
        :param list pas: pas list of the pk PeriodoAquisitivo
        :param list pas_estado: pas_estado list of the estado PeriodoAquisitivoServidor
        :param list pasu_estado: pas_estado list of the estado PeriodoAquisitivoServidorUsufruto
        :param int conflicts: amount of conflicts to show

        """
        employees = []
        periodos = PeriodoAquisitivoServidorMembro.objects.filter(
            estado__in=pas_estado
        ).distinct()
        if pas:
            periodos = PeriodoAquisitivoServidorMembro.objects.filter(
                periodo_aquisitivo__pk__in=pas
            )
        for pas in periodos:
            usufrutos = pas.usufrutos.filter()
            if len(pasu_estado) > 0:
                usufrutos = usufrutos.filter(estado__in=pasu_estado)
            for pasu in usufrutos:
                try:
                    conflitantes = pas.conflitantes(pasu)
                    total_conflicts = len(conflitantes)
                    if total_conflicts > 0 and total_conflicts >= count_conflict_accept:
                        employees.append(pas.servidor.matricula)
                except Exception as err:
                    log.exception(err)
                    # self._print(unicode(err))
        # with codecs.open('%s/employees.txt' % settings.CACHE.get('dir'), 'w', 'utf-8') as fd:
        #     fd.write(unicode(employees))
        return Servidor.objects.filter(matricula__in=employees)

    def conflicts_informations(
        self,
        employee_registry=None,
        pas=[],
        pas_estado=[
            PAS_EMANDAMENTO,
        ],
        pasu_estado=[PASU_HOMOLOGADO, PASU_NOVO, PASU_AUTORIZADO_CI],
        count_conflict_accept=2,
        exclude_registry=[],
    ):
        """
        :py:function:: conflicts_informations(self, employee_registry):

        This method show conflicts found.

        :param boolean verbose: Verbose None(use class definition)
        :param list pas: pas list of the pk PeriodoAquisitivo
        :param list pas_estado: pas_estado list of the estado PeriodoAquisitivoServidor
        :param list pasu_estado: pas_estado list of the estado PeriodoAquisitivoServidorUsufruto
        :param int conflicts: amount of conflicts to show

        """
        periodos = PeriodoAquisitivoServidorMembro.objects.filter(
            estado__in=pas_estado, servidor__matricula=employee_registry
        )
        if pas:
            periodos = PeriodoAquisitivoServidorMembro.objects.filter(
                periodo_aquisitivo__pk__in=pas
            )
        periodos = periodos.distinct()
        count = 0
        infos = {}
        for pas in periodos:
            # servidor = pas.servidor
            usufrutos = pas.usufrutos.filter()
            if len(pasu_estado) > 0:
                usufrutos = usufrutos.filter(estado__in=pasu_estado)
            for pasu in usufrutos:
                try:
                    conflitantes = pas.conflitantes(pasu)
                    total_conflicts = len(conflitantes)
                    if (
                        total_conflicts > 0
                    ):  # and total_conflicts >= count_conflict_accept:
                        count += 1
                        dr_pasu = NewDateRange(pasu.data_inicio, pasu.data_fim)
                        for c in conflitantes:
                            pasu_conflito = conflitantes.get(c)
                            if (
                                pasu_conflito.pas.servidor.matricula
                                not in exclude_registry
                            ):
                                dr_conflito = NewDateRange(
                                    pasu_conflito.data_inicio, pasu_conflito.data_fim
                                )
                                detail = {
                                    "employee_registry": pasu_conflito.pas.servidor.matricula,
                                    "employee": pasu_conflito.pas.servidor,
                                    "pasu": pasu,
                                    "pasu_situation": pasu.get_estado_display(),
                                    "pasu_conflict": pasu_conflito,
                                    "pasu_conflict_situation": pasu_conflito.get_estado_display(),
                                    "days": dr_pasu.intersect(dr_conflito).days,
                                }
                                infos.update({pasu_conflito.pk: detail})
                except Exception as err:
                    log.exception(err)
        return infos
