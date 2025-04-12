# -.- coding: utf-8 -.-

from django.conf import settings

from rh.afastamento.models import (
    FeriasAfastamento,
    FolgaAniversario,
    FolgaCompensacao,
    FolgaEleitoral,
    Plantao,
    Recesso,
    AwardLicense,
)
from rh.models import (
    AnotacaoFerias,
    AnotacaoFolgaAniversario,
    AnotacaoFolgaCompensacao,
    AnotacaoFolgaEleitoral,
    AnotacaoPlantao,
    AnotacaoRecesso,
)

PERIODS_YEAR_UNIQUE = 1
PERIODS_YEAR_SEMESTER = 2
PERIODS_YEAR_TRIMESTER = 3
PERIODS_YEAR_FOURMONTH = 4

PERIODS_YEAR_CHOICE = {
    PERIODS_YEAR_UNIQUE: "Único",
    PERIODS_YEAR_SEMESTER: "Semestre",
    PERIODS_YEAR_TRIMESTER: "Trimeste",
    PERIODS_YEAR_FOURMONTH: "Quadrimeste",
}

CONF_VACATION = 1
CONF_RECESS = 2
CONF_BIRTHDAY_BREAK = 3
CONF_ELECTORAL_SLACK = 4
CONF_DUTTY = 5
CONF_COMPENSATION = 6
CONF_AWARD = 7

ACQP_CREATION_CREATED = 1
ACQP_CREATION_UPDATED = 2
ACQP_CREATION_REMOVED = 3
ACQP_CREATION_WITHOUT = 4
ACQP_CREATION_ERROR = 9

CONFIGURATION_CHOICE = {
    CONF_VACATION: "Férias",
    CONF_RECESS: "Recesso",
    CONF_BIRTHDAY_BREAK: "Folga de Aniversário",
    CONF_ELECTORAL_SLACK: "Folga Eleitoral",
    CONF_DUTTY: "Folga de Plantão",
    CONF_COMPENSATION: "Folga por Compensação",
    CONF_AWARD: "Licença Prêmio",
}

CONFIGURATION_TO_ANNOTATION_CLASS = {
    CONF_VACATION: AnotacaoFerias,
    CONF_RECESS: AnotacaoRecesso,
    CONF_BIRTHDAY_BREAK: AnotacaoFolgaAniversario,
    CONF_ELECTORAL_SLACK: AnotacaoFolgaEleitoral,
    CONF_DUTTY: AnotacaoPlantao,
    CONF_COMPENSATION: AnotacaoFolgaCompensacao,
}

CONFIGURATION_TO_DEPARTURE_CLASS = {
    CONF_VACATION: FeriasAfastamento,
    CONF_RECESS: Recesso,
    CONF_BIRTHDAY_BREAK: FolgaAniversario,
    CONF_ELECTORAL_SLACK: FolgaEleitoral,
    CONF_DUTTY: Plantao,
    CONF_COMPENSATION: FolgaCompensacao,
    CONF_AWARD: AwardLicense,
}

ACQP_WAIT = 1
ACQP_PROGRESS = 2
ACQP_FINISHED = 4
ACQP_INDEMNIFIED = 8
# ACQP_PENDENCY = 10
ACQP_PRESCRIBED = 12

ACQUISITION_PERIOD_STATUS_CHOICE = {
    ACQP_WAIT: "Aguardando Liberação p/ Marcação",
    ACQP_PROGRESS: "Em Andamento",
    ACQP_FINISHED: "Concluído",
    ACQP_INDEMNIFIED: "Indenizado Total ou Parcialmente",
    # ACQP_PENDENCY: 'Pendência',
    ACQP_PRESCRIBED: "Prescrito",
}

USU_NEW = 1
USU_AUTORIZED_CI = 2
USU_HOMOLOGATED = 4
USU_CHANGING = 8
USU_CHANGED = 16
USU_INTERRUPTED = 32
USU_SUSPENDED = 64
USU_ENJOYING = 128
USU_ENJOYED = 256
USU_NOT_AUTHORIZED = 512
USU_SUBSTITUTE = 1024
USU_CANCELED = 2048
USU_SOLD = 4096

USUFRUCT_STATUS_CHOICE = {
    USU_NEW: "Inclusão solicitada",
    USU_AUTORIZED_CI: "Autorizado",
    USU_HOMOLOGATED: "Homologado",  # CRIAR AFASTAMENTO
    USU_CHANGED: "Retificado",  # APAGAR AFASTAMENTO #Mudar label Alterado para Retificado MPMT
    USU_CHANGING: "Retificação Solicitada",  # Mudar label Alteração solicitada para Retificação Solicitada MPMT
    USU_INTERRUPTED: "Interrompido",  # ALTERAR AFASTAMENTO
    USU_SUSPENDED: "Suspenso",  # APAGAR AFASTAMENTO
    USU_ENJOYING: "Homologado",  # Mudar label Em fruição para Homologado MPMT
    USU_ENJOYED: "Homologado",  # Mudar label Usufruído para Homologado MPMT
    USU_NOT_AUTHORIZED: "Não autorizado",
    USU_SUBSTITUTE: "Substituto",
    USU_SOLD: "Vendido",
    USU_CANCELED: "Cancelado",
}

ACT_BOOK = 1
ACT_CHANGE = 2
ACT_SUSPEND = 3
ACT_INTERRUPT = 4
ACT_INDEMNIFY = 5
ACT_SELL = 7
ACT_RECTIFY = 8
ACT_CANCEL = 9
ACT_REMAINING = 10
ACT_BOOK_SELL = 11
ACT_CORRECT = 12

ACTIVITY_TYPE_CHOICE = {
    ACT_BOOK: "MARCAÇÃO",  # usuario validar quando não estiver autorizado
    ACT_CHANGE: "ALTERAÇÃO",  # usuario validar quando não estiver autorizado
    ACT_SUSPEND: "SUSPENSÃO",
    ACT_INTERRUPT: "INTERRUPÇÃO",
    ACT_INDEMNIFY: "INDENIZAÇÃO",  # ação do admin/athenas
    ACT_SELL: "VENDA",  # pedido do usuário, solicitação de venda # usuario validar quando não estiver autorizado
    ACT_BOOK_SELL: "MARCAÇÃO/VENDA",
    ACT_CANCEL: "CANCELAR",
    ACT_RECTIFY: "RETIFICAÇÃO",
    ACT_REMAINING: "MARCAR REMANESCENTE",
    ACT_CORRECT: "CORRECÃO",
}

USUFRUCT_STATUS_MODIFIED = {
    ACT_BOOK: USU_HOMOLOGATED,
    ACT_CHANGE: USU_CHANGED,
    ACT_RECTIFY: USU_CHANGED,
    ACT_SUSPEND: USU_SUSPENDED,
    ACT_BOOK_SELL: USU_HOMOLOGATED,
    ACT_CANCEL: USU_CANCELED,
}

ACTIVITY_TO_METHOD_NAME = {
    ACT_BOOK: "book",  # usuario validar quando não estiver autorizado
    ACT_CHANGE: "change",  # usuario validar quando não estiver autorizado
    ACT_SUSPEND: "suspend",
    ACT_INTERRUPT: "interrupt",
    ACT_INDEMNIFY: "indemnify",  # ação do admin/athenas
    ACT_SELL: "sell",  # pedido do usuário, solicitação de venda # usuario validar quando não estiver autorizado
    ACT_BOOK_SELL: "book_sell",
    ACT_CANCEL: "cancel",
}

ACT_ST_CREATED = 1
ACT_ST_AUTHORIZED = 2
ACT_ST_AUTHORIZED_M = 6
ACT_ST_NOT_AUTHORIZED = 3
ACT_ST_HOMOLOGATED = 4
ACT_ST_CANCELED = 5
ACT_ST_SOLD = 7

ACTIVITY_STATUS_CHOICE = {
    ACT_ST_CREATED: "CRIADO",
    ACT_ST_AUTHORIZED: "AUTORIZADO",
    ACT_ST_AUTHORIZED_M: "AUTORIZADO CHEFE MEDIATO",
    ACT_ST_NOT_AUTHORIZED: "NÃO AUTORIZADO",
    ACT_ST_HOMOLOGATED: "HOMOLOGADO",
    ACT_ST_CANCELED: "CANCELADO",
    ACT_ST_SOLD: "VENDIDO",
}

"""
    Máquina de estados responsável por validar as ações e estados válidos durante a marcação de férias
"""

ACQP_ACT_BOOK = 1
ACQP_ACT_CHANGE = 2
ACQP_ACT_SUSPEND = 3
ACQP_ACT_INTERRUPT = 4
ACQP_ACT_INDEMNIFY = 5
ACQP_ACT_AUTHORIZE = 6
ACQP_ACT_HOMOLOGATE = 8
ACQP_ACT_SELL = 7
ACQP_ACT_CANCEL = 9
ACQP_ACT_BOOK_SELL = 11


ACQP_ACTIONS = {
    ACQP_ACT_BOOK: "MARCAR",
    ACQP_ACT_CHANGE: "ALTERAR",
    ACQP_ACT_SUSPEND: "SUSPENDER",
    ACQP_ACT_INTERRUPT: "INTERROMPER",
    ACQP_ACT_INDEMNIFY: "INDENIZAR",
    ACQP_ACT_AUTHORIZE: "AUTORIZAR",
    ACQP_ACT_HOMOLOGATE: "HOMOLOGAR",
    ACQP_ACT_SELL: "VENDER",
    ACQP_ACT_CANCEL: "CANCELAR",
    ACQP_ACT_BOOK_SELL: "MARCAR/VENDER",
}
ACQP_ACTIONS_DISPLAY = {
    ACQP_ACT_BOOK: "MARCAÇÃO",
    ACQP_ACT_CHANGE: "ALTERAÇÃO",
    ACQP_ACT_SUSPEND: "SUSPENSÃO",
    ACQP_ACT_INTERRUPT: "INTERRUPÇÃO",
    ACQP_ACT_INDEMNIFY: "INDENIZAÇÃO",
    ACQP_ACT_AUTHORIZE: "AUTORIZAÇÃO",
    ACQP_ACT_HOMOLOGATE: "HOMOLOGAÇÃO",
    ACQP_ACT_SELL: "VENDA",
    ACQP_ACT_CANCEL: "CANCELA",
    ACQP_ACT_BOOK_SELL: "MARCAR/VENDER",
}

ACTIVITY_SM = {
    ACT_ST_CREATED: {
        "autorizar": ACT_ST_AUTHORIZED,
        "desautorizar": ACT_ST_NOT_AUTHORIZED,
        "homologar": ACT_ST_HOMOLOGATED,
        "cancelar": ACT_ST_CANCELED,
        "vender": ACT_ST_SOLD,
        "corrigir": ACT_ST_HOMOLOGATED,
    },
    ACT_ST_AUTHORIZED: {
        "autorizar": ACT_ST_AUTHORIZED_M,
        "homologar": ACT_ST_HOMOLOGATED,
        "cancelar": ACT_ST_CANCELED,
    },
    ACT_ST_AUTHORIZED_M: {
        "homologar": ACT_ST_HOMOLOGATED,
        "cancelar": ACT_ST_CANCELED,
    },
    ACT_ST_NOT_AUTHORIZED: {
        "cancelar": ACT_ST_CANCELED,
    },
    ACT_ST_HOMOLOGATED: {"cancelar": ACT_ST_CANCELED, "corrigir": ACT_ST_HOMOLOGATED},
    ACT_ST_CANCELED: {},
    ACT_ST_SOLD: {
        "autorizar": (ACT_ST_AUTHORIZED, ACT_ST_AUTHORIZED_M),
        "desautorizar": ACT_ST_NOT_AUTHORIZED,
        "homologar": ACT_ST_HOMOLOGATED,
        "cancelar": ACT_ST_CANCELED,
    },
}

AP_SM = {
    ACQP_WAIT: {
        "liberar": ACQP_PROGRESS,
        "marcar": (ACQP_WAIT, ("dayoff.dayoffadmin",)),
        "alterar": (ACQP_WAIT, ("dayoff.dayoffadmin",)),
        "autorizar": (ACQP_WAIT, ("dayoff.dayoffadmin",)),
        "vender": (ACQP_WAIT, ("dayoff.dayoffadmin",)),
        "cancelar": (ACQP_WAIT, ("dayoff.dayoffadmin",)),
        "homologar": (ACQP_WAIT, ("dayoff.dayoffadmin",)),
        # 'investigar': (ACQP_PENDENCY, ('dayoff.dayoffadmin',)),
        "prescrever": (ACQP_PRESCRIBED, ("dayoff.dayoffadmin",)),
        "finalizar": ACQP_FINISHED,
    },
    ACQP_PROGRESS: {
        "alterar": ACQP_PROGRESS,
        "marcar": ACQP_PROGRESS,
        "desmarcar": ACQP_PROGRESS,
        "autorizar": ACQP_PROGRESS,
        "desautorizar": ACQP_PROGRESS,
        "suspender": ACQP_PROGRESS,
        "interromper": ((ACQP_PROGRESS, ACQP_FINISHED),),
        "homologar": ACQP_PROGRESS,
        "finalizar": ACQP_FINISHED,
        "cancelar": ACQP_PROGRESS,
        "indenizar": ACQP_INDEMNIFIED,
        "vender": ACQP_PROGRESS,
        "corrigir": ACQP_PROGRESS,
        # 'investigar': ACQP_PENDENCY,
        "prescrever": ACQP_PRESCRIBED,
    },
    ACQP_FINISHED: {
        "cancelar": ACQP_PROGRESS,
        # 'investigar': ACQP_PENDENCY,
        "prescrever": ACQP_PRESCRIBED,
        "autorizar": (ACQP_PROGRESS, ("dayoff.dayoffadmin",)),
        "homologar": (ACQP_PROGRESS, ("dayoff.dayoffadmin",)),
        "suspender": (ACQP_PROGRESS, ("dayoff.dayoffadmin",)),
        "interromper": ((ACQP_PROGRESS, ACQP_FINISHED), ("dayoff.dayoffadmin",)),
        "liberar": ((ACQP_PROGRESS), ("dayoff.dayoffadmin",)),
        "alterar": (ACQP_PROGRESS, ("dayoff.dayoffadmin",)),  #
    },
    ACQP_INDEMNIFIED: {
        # 'investigar': ACQP_PENDENCY,
        "prescrever": ACQP_PRESCRIBED
    },
}

USU_SM = {
    USU_NEW: {
        "autorizar": USU_AUTORIZED_CI,
        "desmarcar": USU_NEW,
        "desautorizar": USU_NOT_AUTHORIZED,
        "homologar": USU_HOMOLOGATED,
        "alterar": USU_SUBSTITUTE,
        "cancelar": USU_CANCELED,
    },
    USU_SUBSTITUTE: {
        "autorizar": USU_AUTORIZED_CI,
        "desautorizar": USU_NOT_AUTHORIZED,
        "cancelar": USU_CANCELED,
    },
    USU_AUTORIZED_CI: {
        "homologar": USU_HOMOLOGATED,
        "cancelar": (USU_CANCELED, ("dayoff.dayoffadmin",)),
    },
    USU_HOMOLOGATED: {
        "suspender": USU_SUSPENDED,
        "fruir": USU_ENJOYING,
        "alterar": USU_CHANGING,
        "finalizar": USU_ENJOYED,
        "interromper": USU_INTERRUPTED,
        "cancelar": (USU_CANCELED, ("dayoff.dayoffadmin",)),
        "pagar": (USU_SOLD, ("dayoff.dayoffpayment",)),
    },
    USU_CHANGING: {
        "alterar": USU_CHANGED,
        "desautorizar": USU_HOMOLOGATED,
        "cancelar": USU_CANCELED,
    },
    USU_CHANGED: {},
    USU_INTERRUPTED: {"cancelar": (USU_CANCELED, ("dayoff.dayoffadmin",))},
    USU_SUSPENDED: {"cancelar": (USU_CANCELED, ("dayoff.dayoffadmin",))},
    USU_ENJOYING: {
        "finalizar": USU_ENJOYED,
        "interromper": USU_INTERRUPTED,
        "suspender": USU_SUSPENDED,
        "alterar": USU_CHANGED,  #
        "cancelar": (USU_CANCELED, ("dayoff.dayoffadmin",)),
    },
    USU_ENJOYED: {
        "suspender": USU_SUSPENDED,
        "interromper": USU_INTERRUPTED,
        "alterar": USU_CHANGED,  #
        "cancelar": (USU_CANCELED, ("dayoff.dayoffadmin",)),
    },
    USU_NOT_AUTHORIZED: {},
    USU_SOLD: {},
}

AUTO_HOMOLOGATION_NOT = 1
AUTO_HOMOLOGATION_AFTER_SCALE = 2
AUTO_HOMOLOGATION = 3

AUTO_HOMOLOGATION_CHOICE = {
    AUTO_HOMOLOGATION_NOT: "NÃO AUTO HOMOLOGAR",
    AUTO_HOMOLOGATION_AFTER_SCALE: "AUTO HOMOLOGAR APÓS ESCALA",
    AUTO_HOMOLOGATION: "AUTO HOMOLOGAR",
}

PORTAL = 1
MANUAL = 2

ORIGIN_REQUEST = {PORTAL: "Vida Funcional", MANUAL: "Manual"}

DAYOFF_ICONS_THEME = {
    "indefinido": "/%s/static/rh/images/indefinido.png" % getattr(settings, "CONTEXT"),
    "operacoes": "/%s/static/rh/images/menu.png" % getattr(settings, "CONTEXT"),
    "notificar": "/%s/static/rh/images/notificado.png" % getattr(settings, "CONTEXT"),
    "waiting": "/%s/static/rh/images/aguardando.png" % getattr(settings, "CONTEXT"),
    "adicionar": "/%s/static/rh/images/add.png" % getattr(settings, "CONTEXT"),
    "remover": "/%s/static/rh/images/remove.png" % getattr(settings, "CONTEXT"),
    "denied": "/%s/static/images/denied.png" % getattr(settings, "CONTEXT"),
    "alterar": "/%s/static/rh/images/edit.png" % getattr(settings, "CONTEXT"),
    "liberado": "/%s/static/rh/images/" % getattr(settings, "CONTEXT"),
    "paid": "/%s/static/rh/images/ferias_paga.png" % getattr(settings, "CONTEXT"),
    "homologated": "/%s/static/rh/images/pasu_homologado.png"
    % getattr(settings, "CONTEXT"),
    "blocked": "/%s/static/rh/images/bloqueado.png" % getattr(settings, "CONTEXT"),
    "ap_manager": "/%s/static/rh/images/pas_gerenciar.png"
    % getattr(settings, "CONTEXT"),
    "usu_book": "/%s/static/rh/images/add_ferias.png" % getattr(settings, "CONTEXT"),
    "usu_new": "/%s/static/rh/images/pasu_novo.png" % getattr(settings, "CONTEXT"),
    "usu_cancel": "/%s/static/rh/images/remove_ferias.png"
    % getattr(settings, "CONTEXT"),
    "usu_suspended": "/%s/static/rh/images/pasu_suspenso.png"
    % getattr(settings, "CONTEXT"),
    "usu_interrupted": "/%s/static/rh/images/pasu_interrompido.png"
    % getattr(settings, "CONTEXT"),
    "usu_conflict": "/%s/static/rh/images/ferias_conflito.png"
    % getattr(settings, "CONTEXT"),
    "usu_authorized": "/%s/static/rh/images/pasu_autorizado.png"
    % getattr(settings, "CONTEXT"),
    "usu_not_authorized": "/%s/static/rh/images/pasu_nao_autorizado.png"
    % getattr(settings, "CONTEXT"),
    "usu_enjoying": "/%s/static/rh/images/fruindo.png" % getattr(settings, "CONTEXT"),
    "usu_enjoyed": "/%s/static/rh/images/pas_fruido.png" % getattr(settings, "CONTEXT"),
    "usu_changed": "/%s/static/rh/images/pasu_alterado.png"
    % getattr(settings, "CONTEXT"),
    "usu_changing": "/%s/static/rh/images/pasu_emalteracao.png"
    % getattr(settings, "CONTEXT"),
    "conflito": "/%s/static/rh/images/conflito.png" % getattr(settings, "CONTEXT"),
    "help": "/%s/static/rh/images/help.png" % getattr(settings, "CONTEXT"),
    "blank": "/%s/static/rh/images/blank_icon.png" % getattr(settings, "CONTEXT"),
    "ap_indemnified": "/%s/static/rh/images/ferias_indenizada.png"
    % getattr(settings, "CONTEXT"),
    "ap_progress": "/%s/static/rh/images/andamento.png" % getattr(settings, "CONTEXT"),
    "pendency": "/%s/static/rh/images/athenas-0683.png" % getattr(settings, "CONTEXT"),
    "prescribed": "/%s/static/rh/images/athenas-0371.png"
    % getattr(settings, "CONTEXT"),
}


# Constantes relacionadas ao sub_type_of_usufruct
REGULAR_VACATIONS = 9000
INDIVIDUAL_VACATION = 9001
FORENSIC_RECESS = 9002
BIRTHDAY_BREAK = 9003
ELECTORAL_SLACK = 9004
ONCALL_BONUS_SERVERS = 9005
COMP_CLERARANCE_SERVERS = 9006
COMP_CLEARANCE_MEMBERS = 9007
COMP_VACATION_MEMBERS = 9008
PREMIUM_LICENSE = 9009
INTERNS_RECESS = 9010
SUBSTITUTE_PROMOTER_CONTEST = 9011
INTERNSHIP_COMPETITION = 9012
BLOOD_DONATION_USUFRUCT = 9013
RESIDENT_RECESS = 9014

# Constantes relacionadas ao Controle de Pagamentos de Usufrutos RH (UsufructPaymentControl)
PAYMENT_PENDING = 1
PAYMENT_DECLINED = 2
PAYMENT_CHECKED = 3

# Constantes relacionadas ao Controle de Pagamentos de Usufrutos GFP (UsufructPaymentControl)
PAYMENT_WAITING = 1
PAYMENT_DENNIED = 2
PAYMENT_APPROVED = 3
PAYMENT_FINALIZED = 4
