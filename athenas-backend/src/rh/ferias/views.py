# -*- coding: utf-8 -*-

from datetime import datetime

from django import forms
from django.conf import settings
from django.db import transaction
from django.db.models import Q

from auditoria.models import LineLog
from contrib import decorator, extjs
from contrib.daterange import NewDateRange
from contrib.decorator import add_methods
from contrib.newrest import Restful
from contrib.utils import DateUtils, get_json_engine, getLogger

# from rh.gfp.views import GFPFolhaEvento
from engine.notification.models import Message, Notification
from rh.ferias.exceptions import FeriasError

# from rh.ferias.exceptions import PASU_NOVO
from rh.ferias.models import (
    ESTADO_PAS,
    ESTADO_PASU,
    PAS_ALIBERACAO,
    PAS_EMANDAMENTO,
    PAS_INDENIZADA,
    PASU_ALTERADO,
    PASU_AUTORIZADO_CI,
    PASU_EMALTERACAO,
    PASU_FRUIDO,
    PASU_FRUINDO,
    PASU_HOMOLOGADO,
    PASU_INTERROMPIDO,
    PASU_NAOAUTORIZADO,
    PASU_NOVO,
    PASU_SUBSTITUTO,
    PASU_SUSPENSO,
    AlteracaoPASU,
    Configuracao,
    PeriodoAquisitivo,
    PeriodoAquisitivoServidor,
    PeriodoAquisitivoServidorUsufruto,
    notify,
)
from rh.gfp.models import FolhaEvento
from rh.models import Publicacao, Servidor
from rh.views import RHServidor
from standard.models import Configuration
from standard.views import AutoCompleteField

json = get_json_engine()

log = getLogger("Ferias:View")


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


class FRSConfiguracao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Configuracao
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    def get_columns_grid(self, args=[]):

        obj = [
            {
                "header": "Nome",
                "sortable": True,
                "dataIndex": "nome",
                "key": "id",
                "width": 200,
            },
            {
                "header": "Dias por período",
                "sortable": False,
                "dataIndex": "dias_por_periodo",
                "key": "dias_por_periodo",
                "width": 100,
            },
            {
                "header": "Periodos por ano",
                "sortable": False,
                "dataIndex": "quantidade_periodos",
                "key": "quantidade_periodos",
                "width": 100,
            },
            {
                "header": "Tipo de servidor",
                "sortable": False,
                "dataIndex": "tipo_servidor",
                "key": "tipo_servidor",
                "width": 100,
            },
            {
                "header": "Máx. de divisões",
                "sortable": False,
                "dataIndex": "max_divisoes",
                "key": "max_divisoes",
                "width": 100,
            },
            {
                "header": "Dias por divisão",
                "sortable": False,
                "dataIndex": "min_dias_por_divisao",
                "key": "min_dias_por_divisao",
                "width": 100,
            },
            {
                "header": "Modo de aquisição",
                "sortable": False,
                "dataIndex": "modo",
                "key": "modo",
                "width": 100,
            },
            {
                "header": "Prescrição (meses)",
                "sortable": False,
                "dataIndex": "meses_prescricao",
                "key": "meses_prescricao",
                "width": 100,
            },
            {
                "header": "Tempo de exercício (meses)",
                "sortable": False,
                "dataIndex": "meses_exercicio",
                "key": "meses_exercicio",
                "width": 100,
            },
        ]

        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Férias - Configurações",
        "LIST": "Configurações",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filter",
    }


class FRSPeriodoAquisitivo(extjs.ExtCrud):

    class Form(forms.ModelForm):

        class Meta:
            model = PeriodoAquisitivo
            exclude = [
                "publicado",
                "bloqueado",
                "periodo_anterior",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Período Aquisitivo",
                "sortable": True,
                "dataIndex": "__description__",
                "width": 100,
                "status": True,
            },
            {
                "header": "Publicado",
                "sortable": False,
                "dataIndex": "publicado",
                "width": 60,
            },
            {
                "header": "Data de publicação",
                "sortable": False,
                "dataIndex": "data_publicacao",
                "width": 110,
            },
            {
                "header": "Configuração",
                "sortable": False,
                "dataIndex": "configuracao",
                "width": 150,
            },
            {
                "header": "Inicío previsão",
                "sortable": False,
                "dataIndex": "data_inicio_prev",
                "width": 100,
            },
            {
                "header": "Fim previsão",
                "sortable": False,
                "dataIndex": "data_fim_prev",
                "width": 100,
            },
            {
                "header": "Iniciar bloqueado",
                "sortable": False,
                "dataIndex": "bloqueado",
                "width": 100,
            },
        ]

        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Férias - Período de Aquisição",
        "LIST": "Períodos de Aquisição",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filter",
    }


class FRSPeriodoAquisitivoServidor(extjs.ExtEditorCrud):

    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        periodo_aquisitivo = AutoCompleteField(
            model=PeriodoAquisitivo,
            controller=FRSPeriodoAquisitivo,
            label="Período Aquisitivo",
        )
        folha_evento_terco_constitucional = AutoCompleteField(
            model=FolhaEvento,
            # controller = GFPFolhaEvento,
            label="Adicional de Férias",
            required=False,
        )
        homologation_publication = AutoCompleteField(
            model=Publicacao, label="Publicação de Homologação", required=False
        )

        class Meta:
            model = PeriodoAquisitivoServidor
            exclude = [
                "content_type",
                "pas",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    def get_columns_grid(self, args=[]):

        obj = [
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "width": 250,
            },
            {
                "header": "Periodo aquisitivo",
                "sortable": True,
                "dataIndex": "periodo_aquisitivo",
                "width": 120,
            },
            {
                "header": "Data referência",
                "sortable": False,
                "dataIndex": "data_referencia",
                "width": 80,
            },
            {
                "header": "Dias",
                "sortable": True,
                "dataIndex": "quantidade_dias",
                "width": 50,
            },
            {"header": "Estado", "sortable": True, "dataIndex": "estado", "width": 200},
            {
                "header": "Folha-1/3 constitucional",
                "sortable": False,
                "dataIndex": "folha_evento_terco_constitucional",
                "width": 200,
            },
            {
                "header": "Bloqueado",
                "sortable": False,
                "dataIndex": "bloqueado",
                "width": 60,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Férias - Períodos Aquisitivos Servidores",
        "LIST": "Períodos Aquisitivos Servidores",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filter",
    }


class FRSPeriodoAquisitivoServidorUsufruto(extjs.ExtCrud):
    class Form(forms.ModelForm):
        data_fim = forms.DateField(label="Final")

        class Meta:
            model = PeriodoAquisitivoServidorUsufruto
            exclude = [
                "interrompido",
                "dias",
                "estado",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    def get_fields(self):
        fields = super(FRSPeriodoAquisitivoServidorUsufruto, self).get_fields()
        fields.update({"data_fim": self.Form.Meta.model.data_fim})
        return fields

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Período aquisitivo",
                "sortable": True,
                "dataIndex": "periodo_aquisitivo_servidor",
                "width": 300,
            },
            {
                "header": "Início",
                "sortable": False,
                "dataIndex": "data_inicio",
                "width": 100,
            },
            {"header": "Fim", "sortable": False, "dataIndex": "data_fim", "width": 100},
            {"header": "Dias", "sortable": False, "dataIndex": "dias", "width": 100},
            {
                "header": "Situação",
                "sortable": False,
                "dataIndex": "estado",
                "width": 100,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Férias - Marcação e alteração",
        "LIST": "Períodos de Férias Marcados",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filter",
    }

    def get_query(self):
        try:
            query = self.Form.Meta.model.objects.all()
            filter = True
            if self.request.POST.get("pas", False):
                query = query.filter(
                    periodo_aquisitivo_servidor=self.request.POST.get("pas")
                )
                filter = False
            if self.request.POST.get("servidor", False):
                query = query.filter(
                    periodo_aquisitivo_servidor__servidor=self.request.POST.get(
                        "servidor"
                    )
                )
                filter = False
            if "admin" not in self.request.POST:
                estados = [
                    PASU_NOVO,
                    PASU_AUTORIZADO_CI,
                    PASU_HOMOLOGADO,
                    PASU_EMALTERACAO,
                    PASU_FRUINDO,
                    PASU_INTERROMPIDO,
                    PASU_FRUIDO,
                    PASU_SUBSTITUTO,
                    PASU_NAOAUTORIZADO,
                ]
                if self.request.POST.get("todos", False) == "true":
                    estados.append(PASU_ALTERADO)
                    estados.append(PASU_SUSPENSO)
                query = query.filter(estado__in=estados)
            else:
                filter = False
            if filter:
                query = query.filter(
                    pk=-1
                )  # Usado para bloquear tentativa de ver todos os PASUs
        except (
            Exception
        ) as err:  # TODO NOTIFICATION notificar que esse usuário não estar ligado a um servidor
            self.log.exception(err)
            query = query.filter(pk=-1)
        return query

    @decorator.login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}

        sort = self.request.POST.get("sort", "criado_em")
        dir = "-" if self.request.POST.get("dir", "") == "DESC" else ""

        query = self.get_query().order_by("%s%s" % (dir, sort))
        obj["totalRows"] = query.count()

        if "keyword" in self.request.POST:
            query = self.apply_filter(query)

        start = int(self.request.POST["start"]) if "start" in self.request.POST else 0
        limit = int(self.request.POST["limit"]) if "limit" in self.request.POST else 50

        for pasu in query[start : (start + limit)]:
            status = []
            if pasu.estado == PASU_NOVO:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_novo"],
                        "title": "Parcela marcada e aguardando autorização",
                        "alt": "Nova",
                    }
                )
            elif pasu.autorizado and not pasu.estado == PASU_NAOAUTORIZADO:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_autorizado"],
                        "title": "Parcela autorizada pela chefia",
                        "alt": "Autorizado",
                    }
                )
            elif pasu.estado == PASU_NAOAUTORIZADO:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_naoautorizado"],
                        "title": "Parcela indeferida pela chefia",
                        "alt": "Não autorizado",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )

            if pasu.homologado:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["homologado"],
                        "title": "Parcela homologada pelo RH",
                        "alt": "Homologado",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )

            if pasu.fruido or pasu.interrompido:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_fruido"],
                        "title": "Parcela fruída",
                        "alt": "Fruída",
                    }
                )
            elif pasu.fruindo:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_fruindo"],
                        "title": "Parcela em fruíção",
                        "alt": "Fruíndo",
                    }
                )

            conflict = False
            log.debug("checking conflict")
            if pasu.estado in (
                PASU_HOMOLOGADO,
                PASU_FRUINDO,
                PASU_AUTORIZADO_CI,
                PASU_EMALTERACAO,
                PASU_NOVO,
                PASU_SUBSTITUTO,
            ):
                conflict = pasu.pas.check_all_conflict(pasu, limit=1)
                log.debug(f"conflict: {conflict}")
                if not conflict:
                    conflict = pasu.pas.conflitos_substituicao(pasu).exists()
            if conflict:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_conflito"],
                        "title": "Parcela conflita com a de outro membro/servidor. Verifique detalhamento",
                        "alt": "Conflito",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )

            if pasu.suspenso:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_suspenso"],
                        "title": "Parcela suspensa pela administração",
                        "alt": "Suspensa",
                    }
                )
            elif pasu.interrompido:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_interrompido"],
                        "title": "Parcela interrompida pela administração",
                        "alt": "Interrompida",
                    }
                )
            elif pasu.alterado:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_alterado"],
                        "title": "Parcela alterada",
                        "alt": "Alterada",
                    }
                )
            elif pasu.emalteracao:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_emalteracao"],
                        "title": "Aguardando autorização de alteração...",
                        "alt": "Em alteração",
                    }
                )

            try:
                if pasu.notificado:
                    texto = ""
                    for notificao in pasu.notificacoes.all():
                        texto += " " + notificao.formatMsg()
                    status.append(
                        {
                            "icon": FRS_ICONS_THEME["notificar"],
                            "title": texto,
                            "alt": "Notificada",
                        }
                    )
            except Exception as e:
                self.log.exception(e)
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            obj["result"].append(
                {
                    "status": status,
                    "pk": pasu.pk,
                    "servidor": "%s" % pasu.pas.servidor,
                    "periodo_aquisitivo": "%s" % pasu.pas.periodo_aquisitivo,
                    "data_inicio": DateUtils.date_to_str(pasu.data_inicio),
                    "data_fim": DateUtils.date_to_str(pasu.data_fim),
                    "dias": pasu.dias,
                    "situacao": "%s" % pasu.situacao,
                    "criado_em": DateUtils.datetime_to_str(pasu.criado_em),
                    "criado_por": str(pasu.created_by),
                    "modificado_por": str(pasu.modified_by),
                    "modificado_em": DateUtils.datetime_to_str(pasu.modified_at),
                    "autorizado_em": (
                        DateUtils.date_to_str(pasu.autorizado_em)
                        if pasu.autorizado_em
                        else ""
                    ),
                    "autorizado_por": (
                        str(pasu.autorizado_por.user) if pasu.autorizado_por else ""
                    ),
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@decorator.help_for()
class FRSMarcacaoFerias(extjs.ExtWidget):

    class Form(forms.ModelForm):
        class Meta:
            model = PeriodoAquisitivoServidor
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    def get_help_items(self, tag):
        help_items = [
            {
                "id": "passo-1",
                "html": """<h1>Regras e considerações para marcação e alteração de férias</h1>
            <ol>
                <li class="number">
                    <b>Período aquisitivo (PA)</b> - é o período em exercício que um servidor deve ter para adquirir o direito de usufruir um período de férias.
                    <ul>
                        <li class="topic">&nbsp;&nbsp;Exemplo de acordo com a legislação atual:</li>
                        <li class="topic">&nbsp;&nbsp;&nbsp;&nbsp;Membros:</li>
                        <li>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2010 - 1° Semestre: Efetivo exercício de 01/01/2010 a 30/06/2010 podendo usufruir 30 dias (ou proporcional) a partir de 01/07/2010</li>
                        <li class="topic">&nbsp;&nbsp;&nbsp;&nbsp;Administrativo:</li>
                        <li>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2010/2011(para um servidor com data de posse/exercício em <strong>01/09</strong>/2008): Efetivo exercício entre <strong>01/09</strong>/2010 e 31/08/2011 podendo usufruir 30 dias a partir de <strong>01/09</strong>/2011</li>
                    </ul>
                </li>

                <li class="number"><b>Usufruto</b> - são os dias adquiridos para fruição após um período aquisitivo (normalmente 30)</li>
                <li class="number">
                    <b>Parcela de Usufruto</b> - quantidade de dias do usufruto marcado para ser usufruído, atualmente o usufruto pode ser dividido em até duas parcelas.
                    <ul>
                        <li class="topic">&nbsp;&nbsp;Exemplo de acordo com a legislação atual:</li>
                        <li class="topic">&nbsp;&nbsp;&nbsp;&nbsp;Membros: Podem dividir em até duas parcelas de 15 dias</li>
                        <li>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Usufruto de 30 dias: 1(uma) parcela de 30 dias ou 2(duas) de 15 dias</li>
                        <li>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Usufruto com menos de 30 dias(Usufruto proporcional): 1(uma) única parcela com a quantidade de dias do usufruto</li>
                        <li class="topic">&nbsp;&nbsp;&nbsp;&nbsp;Administrativos: Podem dividir em até duas parcelas entre 10 e 20 dias</li>
                        <li>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Usufruto de 30 dias: 1(uma) parcela de 30 dias ou 2(duas) parcelas (10 e 20, 12 e 18, 15 e 15, etc )</li>
                    </ul>
                </li>
            </ol>""",
            },
            {
                "id": "passo-2",
                "html": '<h1>Informações Úteis (PA)</h1><br /> <img width="531" height="403" src="/%s/static/rh/images/help/ferias/sf_001.png" />'
                % getattr(settings, "CONTEXT"),
            },
            {
                "id": "passo-3",
                "html": '<h1>Passo 1 - Marcando nova(s) parcela(s)</h1><img width="561" height="380" src="/%s/static/rh/images/help/ferias/sf_002.png" />'
                % getattr(settings, "CONTEXT"),
            },
            {
                "id": "passo-4",
                "html": '<h1>Passo 2 - Marcando nova(s) parcela(s)</h1><img width="411" height="387" src="/%s/static/rh/images/help/ferias/sf_003.png" />'
                % getattr(settings, "CONTEXT"),
            },
            {
                "id": "passo-5",
                "html": '<h1>Passo 1 - Alterando parcela(s) já marcada(s)</h1><img width="564" height="438" src="/%s/static/rh/images/help/ferias/sf_004.png" />'
                % getattr(settings, "CONTEXT"),
            },
            {
                "id": "passo-6",
                "html": '<h1>Passo 2 - Alterando parcela(s) já marcada(s)</h1><img width="536" height="501" src="/%s/static/rh/images/help/ferias/sf_005.png" />'
                % getattr(settings, "CONTEXT"),
            },
            {
                "id": "passo-7",
                "html": '<h1>Passo 3 - Alterando parcela(s) já marcada(s)</h1><img width="601" height="422" src="/%s/static/rh/images/help/ferias/sf_006.png" />'
                % getattr(settings, "CONTEXT"),
            },
            {
                "id": "passo-8",
                "html": "<h1>Obrigado...</h1><p>Nos ajude enviando sua dúvida,sugestão e/ou crítica para athenas@mp.to.gov.br</p>",
            },
        ]
        items = {"default": help_items[0:9]}
        return items[tag]

    def get_fields(self):
        fields = super(FRSPeriodoAquisitivoServidor, self).get_fields()
        fields.update(
            {
                "data_inicio_aquisicao": self.Form.Meta.model.data_inicio_aquisicao,
                "data_fim_aquisicao": self.Form.Meta.model.data_fim_aquisicao,
                "data_inicio_usufruto": self.Form.Meta.model.data_inicio_usufruto,
                "data_fim_usufruto": self.Form.Meta.model.data_fim_usufruto,
            }
        )
        return fields

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "width": 300,
            },
            {
                "header": "Período aquisitivo",
                "sortable": True,
                "dataIndex": "periodo_aquisitivo",
                "width": 160,
            },
            {
                "header": "Referência",
                "sortable": False,
                "dataIndex": "data_referencia",
                "width": 80,
            },
            {
                "header": "Início da aquisição",
                "sortable": False,
                "dataIndex": "data_inicio_aquisicao",
                "width": 100,
            },
            {
                "header": "Fim da aquisição",
                "sortable": False,
                "dataIndex": "data_fim_aquisicao",
                "width": 100,
            },
            {
                "header": "Dias",
                "sortable": False,
                "dataIndex": "quantidade_dias",
                "width": 50,
            },
            {
                "header": "Início usufruto",
                "sortable": False,
                "dataIndex": "data_inicio_usufruto",
                "key": "data_inicio_usufruto",
                "width": 80,
            },
            {
                "header": "Fim usufruto",
                "sortable": False,
                "dataIndex": "data_fim_usufruto",
                "width": 100,
            },
        ]

        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Férias - Período de Aquisição por Servidor",
        "LIST": "Períodos de Aquisição por Servidor",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filter",
    }

    @decorator.login_required(type="JSON")
    def usufruto(self, args=[]):
        obj = {"success": False}
        params = {}
        try:
            acao = self.request.POST["acao"]
            params["dataini"] = (
                datetime.date(
                    datetime.strptime(
                        self.request.POST["data_inicio"],
                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                    )
                )
                if "data_inicio" in self.request.POST
                else ""
            )
            params["datafim"] = (
                datetime.date(
                    datetime.strptime(
                        self.request.POST["data_fim"],
                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                    )
                )
                if "data_fim" in self.request.POST
                else ""
            )
            if "pasu" in self.request.POST:
                params["pasu"] = self.request.POST.get("pasu")
                pasu = PeriodoAquisitivoServidorUsufruto.objects.get(params["pasu"])
            if "pas" in self.request.POST:
                pas = self.Form.Meta.model.objects.get(pk=self.request.POST.get("pas"))
            else:
                pas = pasu.pas
            pas.gerenciar_usufruto(acao, params)
            obj["success"] = True
        except FeriasError as err:
            obj["error"] = err.value
            self.log.exception(err)
        except Exception as err:
            obj["error"] = (
                "Um erro inesperado ocorreu. Entre em contato com o administrador do sistema!"
            )
            self.log.exception(err)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def conflitos_usufruto(self, args=[]):
        obj = {"success": False, "conflitos": []}
        try:
            pas = self.Form.Meta.model.objects.get(pk=self.request.POST["pas"])
            conflicts_pasu = pas.pas.conflitos(self.request.POST["pasu"])
            for key in conflicts_pasu:
                usu = conflicts_pasu[key].get("pasu")
                obj["result"].append(
                    {
                        "pk": usu.pk,
                        "periodo_aquisitivo": "%s"
                        % usu.periodo_aquisitivo_servidor.periodo_aquisitivo,
                        "servidor": "%s" % usu.periodo_aquisitivo_servidor.servidor,
                        "periodo": "%s - %s"
                        % (
                            DateUtils.date_to_str(usu.data_inicio),
                            DateUtils.date_to_str(usu.data_fim),
                        ),
                        "marcado_em": DateUtils.date_to_str(usu.criado_em),
                        "qtd": NewDateRange(usu.data_inicio, usu.data_fim)
                        .intersect(dr_pasu)
                        .days,
                        "order": conflicts_pasu[key].get("order"),
                        "workplace": conflicts_pasu[key].get("workplace"),
                    }
                )
            obj["success"] = True
        except FeriasError as err:
            obj["error"] = err.value
        except Exception as err:
            obj["error"] = (
                "Um erro inesperado ocorreu. Entre em contato com o administrador do sistema!"
            )
            self.log.exception(err)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @decorator.login_required(type="JSON")
    def get_conflitos(self, args=[]):
        obj = PeriodoAquisitivoServidorUsufruto.get_conflitos(
            pasus=self.request.POST.getlist("pasus")
        )
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def deletar_usufruto(self, args=[]):
        obj = {"success": False}
        try:
            pas = self.Form.Meta.model.objects.get(pk=self.request.POST["pas"])
            pasu = self.request.POST["pasu"]
            pas.deletar_usufruto(pasu)
            obj["success"] = True
        except Exception as e:
            obj["error"] = (
                "Um erro inesperado ocorreu ao apagar a parcela. Entre em contato com o administrador do sistema!"
            )
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @decorator.login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.ferias.MarcacaoFerias()")

    def get_query(self):
        query = PeriodoAquisitivoServidor.objects.all()
        try:
            query = query.filter(servidor=self.request.user.servidor, bloqueado=False)
        except (
            Exception
        ) as err:  # TODO: NOTIFICATION notificar que esse usuário não estar ligado a um servidor
            self.log.exception(err)
            self.log.debug("Servidor nao encontrado: %s" % self.request.user.servidor)
            query = query.filter(pk=-1)
        return query

    @decorator.login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        sort = (
            self.request.POST.getlist("sort") if "sort" in self.request.POST else "pk"
        )
        query = self.get_query()
        if ("todos" in self.request.POST) & (self.request.POST["todos"] == "false"):
            query = query.filter(
                estado__in=[
                    PAS_EMANDAMENTO,
                ]
            )
        query = query.order_by(*sort)

        obj["totalRows"] = query.count()

        start = int(self.request.POST["start"]) if "start" in self.request.POST else 0
        limit = int(self.request.POST["limit"]) if "limit" in self.request.POST else 50

        for pas in query[start : (start + limit)]:
            status = []
            if pas.fruido:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_fruido"],
                        "title": "Período aquisitivo fruído",
                        "alt": "Fruido",
                    }
                )
            elif pas.fruindo:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_fruindo"],
                        "title": "Parcela em fruição",
                        "alt": "Fruindo",
                    }
                )
            elif pas.estado == PAS_EMANDAMENTO:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pas_andamento"],
                        "title": "Em andamento",
                        "alt": "Andamento",
                    }
                )
            elif pas.estado == PAS_INDENIZADA:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pas_indenizada"],
                        "title": "Período Indenizado",
                        "alt": "Indenizado",
                    }
                )
            elif pas.estado == PAS_ALIBERACAO:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["aguardando"],
                        "title": "Aguardando liberação",
                        "alt": "Liberacao",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            if pas.pago:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pago"],
                        "title": "Período aquisitivo pago (%s)" % pas.folha,
                        "alt": "Pago",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            if pas.bloqueado:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["bloqueado"],
                        "title": "Período bloqueado",
                        "alt": "Bloqueado",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            quantidade_dias = pas.quantidade_dias
            dias_usufruidos = pas.dias_usufruidos
            paid_days = pas.paid_days
            obj["result"].append(
                {
                    "pk": pas.pk,
                    "status": status,
                    "periodo_aquisitivo": "%s" % pas.periodo_aquisitivo,
                    "servidor": "%s" % pas.servidor,
                    "data_referencia": DateUtils.date_to_str(pas.data_referencia),
                    "quantidade_dias": quantidade_dias,
                    "dias_marcados": pas.dias_marcados,
                    "dias_agendados": pas.dias_agendados,
                    "dias_usufruidos": dias_usufruidos,
                    "paid_days": paid_days,
                    "dias_ausufruir": quantidade_dias - dias_usufruidos - paid_days,
                    "dias_nao_marcados": pas.dias_nao_marcados,
                    "usufruto_ini": "%s"
                    % DateUtils.date_to_str(pas.data_inicio_usufruto),
                    "usufruto_fim": (
                        "%s" % DateUtils.date_to_str(pas.data_fim_usufruto)
                        if pas.data_fim_usufruto
                        else "---"
                    ),
                    "situacao": "%s" % pas.situacao,
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @decorator.login_required(type="JSON")
    def marcacao(self, args=[]):
        obj = {"success": False, "pas": {}}
        try:
            linelog = LineLog(request=self.request, level=100, status=0)
            with transaction.atomic():
                acao = self.request.POST["acao"]
                # O atributo 'pas' retorna o PeriodoAquisitivoServidor especializado (Membro ou Admin)
                pas = self.Form.Meta.model.objects.get(pk=self.request.POST["pas"]).pas
                if acao == "marcar":
                    datas = (
                        [
                            {
                                "data_inicio": datetime.date(
                                    datetime.strptime(
                                        d.split(",")[0],
                                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                                    )
                                ),
                                "data_fim": datetime.date(
                                    datetime.strptime(
                                        d.split(",")[1],
                                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                                    )
                                ),
                            }
                            for d in self.request.POST.getlist("datas")
                        ]
                        if "datas" in self.request.POST
                        and len(self.request.POST.getlist("datas")) > 0
                        and self.request.POST.getlist("datas")[0]
                        else []
                    )
                    self._marcar(pas, datas)
                    obj["success"] = True
                    obj["retorno"] = {
                        "pk": pas.pk,
                        "dias_marcados": pas.dias_marcados,
                        "dias_agendados": pas.dias_agendados,
                        "dias_usufruidos": pas.dias_usufruidos,
                        "situacao": ESTADO_PAS[pas.estado],
                    }
                elif acao == "desmarcar":
                    pasu_id = self.request.POST.get("pasu", -1)
                    self._desmarcar(pas, pasu_id)
                    obj["success"] = True
                    obj["retorno"] = {
                        "pk": pas.pk,
                        "dias_marcados": pas.dias_marcados,
                        "dias_agendados": pas.dias_agendados,
                        "dias_usufruidos": pas.dias_usufruidos,
                        "situacao": ESTADO_PAS[pas.estado],
                    }
                elif acao == "alterar":
                    pasus_id = (
                        self.request.POST.getlist("pasus")
                        if "pasus" in self.request.POST
                        and len(self.request.POST.getlist("pasus")) > 0
                        else []
                    )
                    datas = (
                        [
                            {
                                "data_inicio": datetime.date(
                                    datetime.strptime(
                                        d.split(",")[0],
                                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                                    )
                                ),
                                "data_fim": datetime.date(
                                    datetime.strptime(
                                        d.split(",")[1],
                                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                                    )
                                ),
                            }
                            for d in self.request.POST.getlist("datas")
                        ]
                        if "datas" in self.request.POST
                        and self.request.POST["datas"]
                        and len(self.request.POST.getlist("datas")) > 0
                        else []
                    )
                    justificativa = self.request.POST.get("justificativa", "")
                    self.log.debug("PASUS: %s" % pasus_id)
                    self._alterar(pas, pasus_id, datas, justificativa)
                    obj["success"] = True
                    obj["retorno"] = {
                        "pk": pas.pk,
                        "dias_marcados": pas.dias_marcados,
                        "dias_agendados": pas.dias_agendados,
                        "dias_usufruidos": pas.dias_usufruidos,
                        "situacao": ESTADO_PAS[pas.estado],
                    }
                else:
                    self.log.debug("Acao invalida - PAS: %s| ACAO: %s" % pas, acao)
                    obj["error"] = "Ação inválida."
        except FeriasError as err:
            obj["error"] = err.value
            self.log.exception(err)
        except Exception as err:
            obj["error"] = (
                "Um erro inesperado ocorreu. Entre em contato com o administrador do sistema!"
            )
            self.log.exception(err)
        else:
            linelog.status = 1
        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _marcar(self, pas, data=[]):
        pas.adicionar_usufrutos(data)
        pas.transicao("marcar", PAS_EMANDAMENTO)
        return True

    def _desmarcar(self, pas, pasu_id):
        pasu = pas.deletar_usufruto(pasu_id)
        pas.transicao("desmarcar", PAS_EMANDAMENTO)
        return pasu

    def _alterar(self, pas, pasus_id, datas, justificativa):
        alteracao = pas.solicitar_alteracao(pasus_id, datas, justificativa)
        return alteracao


@add_methods(
    {
        "notificar": notify,
        "notificar_todos": Notification.notify_all,
    }
)
class FRSAutorizacaoFerias(extjs.ExtWidget):

    class Form(forms.ModelForm):
        class Meta:
            model = PeriodoAquisitivoServidor
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    @decorator.login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.ferias.AutorizacaoFerias()")

    def get_query(self):
        # TODO Otimizar essa query, pois estou buscando os ids de todos os PA's que possuem autorizacao a ser feita
        servidor = self.request.user.servidor
        serv_ids = servidor.subordinados_ids
        pasus_alteracoes = [
            alt.antigos_pasus.all()[0].id
            for alt in AlteracaoPASU.objects.filter(
                Q(autorizado_em=None) & Q(pas__servidor__id__in=serv_ids)
            )
            if alt.antigos_pasus.count() > 0
        ]
        query = PeriodoAquisitivoServidorUsufruto.objects.filter(
            Q(periodo_aquisitivo_servidor__servidor__id__in=serv_ids)
            & (
                Q(
                    estado__in=[
                        PASU_NOVO,
                    ]
                )
                | Q(id__in=pasus_alteracoes)
            )
        )
        return query

    @decorator.login_required(type="JSON")
    def get_info(self, args=[]):
        obj = {
            "success": False,
        }
        try:
            pasu = PeriodoAquisitivoServidorUsufruto.objects.get(
                pk=self.request.POST["pasu"]
            )
        except Exception as e:
            self.log.exception(e)
            obj["result"] = {
                "message": "Parcela de usufruto não encontrada, por favor entre em contato com o administrador do sistema"
            }
        else:
            pas = pasu.pas
            alteracao = (
                pasu.alteracao_out.all()[0] if pasu.alteracao_out.count() > 0 else None
            )
            obj["success"] = True
            obj["result"] = {
                "servidor": "%s" % pas.servidor,
                "pas": {
                    "servidor": "%s" % pas.servidor,
                    "periodo_aquisitivo": "%s" % pas.periodo_aquisitivo,
                    "quantidade_dias": pas.quantidade_dias,
                    "dias_marcados": pas.dias_marcados,
                    "dias_agendados": pas.dias_agendados,
                    "dias_usufruidos": pas.dias_usufruidos,
                    "data_ini_usufruto": (
                        DateUtils.date_to_str(pas.data_inicio_usufruto)
                        if pas.data_inicio_usufruto
                        else ""
                    ),
                },
            }
            if not (pasu.emalteracao or pasu.alterado):
                self.log.debug("EM ALTERAÇÃO")
                obj["result"]["pasu"] = {
                    "periodo": "%s" % pasu,
                    "dias": pasu.dias,
                    "estado": ESTADO_PASU[pasu.estado],
                    "emalteracao": False,
                    "justificativa": "",
                }
            else:
                # Pega a alteracao que esta alterando esse PASU
                alteracao = (
                    pasu.alteracao_out.filter(autorizado_em=None)[0]
                    if pasu.emalteracao
                    else pasu.alteracao_out.exclude(autorizado_em=None)[0]
                )
                antigos = [
                    {
                        "data_inicio": (
                            "%s" % DateUtils.date_to_str(old_pasu.data_inicio)
                            if old_pasu.data_inicio
                            else ""
                        ),
                        "data_fim": (
                            "%s" % DateUtils.date_to_str(old_pasu.data_fim)
                            if old_pasu.data_fim
                            else ""
                        ),
                        "dias": old_pasu.dias,
                    }
                    for old_pasu in alteracao.antigos_pasus.all()
                ]
                novos = [
                    {
                        "pk": new_pasu.id,
                        "data_inicio": (
                            "%s" % DateUtils.date_to_str(new_pasu.data_inicio)
                            if new_pasu.data_inicio
                            else ""
                        ),
                        "data_fim": (
                            "%s" % DateUtils.date_to_str(new_pasu.data_fim)
                            if new_pasu.data_fim
                            else ""
                        ),
                        "dias": new_pasu.dias,
                        "conflict": new_pasu.pas.check_all_conflict(pasu),
                    }
                    for new_pasu in alteracao.novos_pasus.all()
                ]
                obj["result"]["pasu"] = {
                    "novos": novos,
                    "antigos": antigos,
                    "epoca_oportuna": alteracao.epoca_oportuna,
                    "justificativa": alteracao.justificativa,
                    "emalteracao": True,
                }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @decorator.login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        sort = self.request.POST["sort"] if "sort" in self.request.POST else "pa"
        dir = (
            "-"
            if "dir" in self.request.POST and self.request.POST["dir"] == "DESC"
            else ""
        )
        sorted = "%s%s" % (dir, sort)

        query = self.get_query()
        if sort == "pa":
            query = query.order_by(
                "%speriodo_aquisitivo_servidor__periodo_aquisitivo__ano_aquisicao"
                % dir,
                "%speriodo_aquisitivo_servidor__periodo_aquisitivo__periodo" % dir,
                "periodo_aquisitivo_servidor__servidor",
            )
        else:
            query = query.order_by(sorted)
        obj["totalRows"] = query.count()

        start = int(self.request.POST["start"]) if "start" in self.request.POST else 0
        limit = int(self.request.POST["limit"]) if "limit" in self.request.POST else 50

        for pasu in query[start : (start + limit)]:
            status = []
            if pasu.notificado:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["notificar"],
                        "title": "Notificada para alteração por conflitos",
                        "alt": "Notificada",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            if pasu.emalteracao:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_emalteracao"],
                        "title": "Aguardando autorização de alteração...",
                        "alt": "Em alteração",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )

            conflict = pasu.pas.check_all_conflict(pasu)
            if conflict:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_conflito"],
                        "title": "Parcela conflita com a de outro membro/servidor %s"
                        % (conflict if not isinstance(conflict, bool) else ""),
                        "alt": "Conflito",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )

            emalteracao = pasu.alteracao_out.count() > 0
            responsavel = (
                pasu.pas.servidor.chefe_imediato
                if pasu.pas.servidor.chefe_imediato
                else "----"
            )
            workplace = pasu.pas.servidor.workplace_by_date()
            obj["result"].append(
                {
                    "status": status,
                    "pk": pasu.pk,
                    "pa": "%s" % pasu.pas.periodo_aquisitivo,
                    "servidor": "%s" % pasu.pas.servidor,
                    "data_inicio": (
                        DateUtils.date_to_str(pasu.data_inicio)
                        if not emalteracao
                        else "---"
                    ),
                    "data_fim": (
                        DateUtils.date_to_str(pasu.data_fim)
                        if not emalteracao
                        else "---"
                    ),
                    "dias": pasu.dias if not emalteracao else "---",
                    "situacao": "%s" % pasu.situacao,
                    "alteracao": emalteracao,
                    "lotacao": (
                        ("%s" % workplace) if workplace else "Não possui lotação ativa"
                    ),
                    "chefia": "%s" % responsavel,
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @decorator.login_required(type="JSON")
    def autorizacao(self, args=[]):
        obj = {"success": False}
        linelog = LineLog(request=self.request, level=101, status=0)
        try:
            with transaction.atomic():
                acao = self.request.POST["acao"]
                pasu_id = self.request.POST.get("pasu", -1)
                if acao == "autorizar":
                    self._autorizar(pasu_id)
                    obj["success"] = True
                elif acao == "desautorizar":
                    pasu_id = self.request.POST.get("pasu", -1)
                    log.debug(pasu_id)
                    self._desautorizar(pasu_id)
                    obj["success"] = True
                elif acao == "notificar":
                    pasu_id = self.request.POST.get("pasu", -1)
                    msg = self.request.POST.get("mensagem", None)
                    self._notificar(pasu_id, msg)
                    obj["success"] = True
                else:
                    self.log.debug("Acao invalida - PAS: %s| ACAO: %s" % pas, acao)
                    obj["error"] = "Ação inválida."
        except FeriasError as err:
            obj["error"] = err.value
        except Exception as err:
            obj["error"] = (
                "Um erro inesperado ocorreu. Entre em contato com o administrador do sistema!"
            )
            self.log.exception(err)
        else:
            linelog.status = 1

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _autorizar(self, pasu_id):
        pasu = PeriodoAquisitivoServidorUsufruto.objects.get(pk=pasu_id)
        alteracao = (
            pasu.alteracao_out.filter(Q(autorizado=False) & Q(autorizado_por=None))[0]
            if pasu.emalteracao
            else None
        )
        responsavel = self.request.user.servidor
        pas = pasu.pas
        if alteracao:
            alteracao = pas.autorizar_alteracao(alteracao.id, responsavel.pk, True)
        else:
            pasu = pas.autorizar_usufruto([pasu_id], responsavel.pk, True)
            self.notificar("FRS_AUTORIZACAO", pas.servidor, pas, pasu=pasu)
        pas.transicao("autorizar", PAS_EMANDAMENTO)

    def _desautorizar(self, pasu_id):
        pasu = PeriodoAquisitivoServidorUsufruto.objects.get(pk=pasu_id)
        alteracao = pasu.alteracao
        responsavel = self.request.user.servidor
        pas = pasu.pas
        if alteracao:
            alteracao = pas.autorizar_alteracao(alteracao.id, responsavel.pk, False)
        else:
            pasu = pas.autorizar_usufruto([pasu_id], responsavel.pk, False)
        pas.transicao("desautorizar", PAS_EMANDAMENTO)

    def _notificar(self, pasu_id, msg=None):
        pasu = PeriodoAquisitivoServidorUsufruto.objects.get(pk=pasu_id)
        # responsavel = self.request.user.servidor
        pas = pasu.pas
        if msg:
            m = Message()
            m.message = msg
            m.header = "Férias"
            m.save()
            res = self.notificar(m, pas.servidor, pasu, pasu=pasu)
        else:
            res = self.notificar("FRS_NOTIFICACAO", pas.servidor, pasu, pasu=pasu)
        return res


class FRSAutorizacaoFeriasChefia(FRSAutorizacaoFerias):

    class Form(forms.ModelForm):
        class Meta:
            model = PeriodoAquisitivoServidor
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    def get_tipo(self):
        return "S"

    def get_query_pasus_updates(self):
        return [
            alt.antigos_pasus.all()[0].id
            for alt in AlteracaoPASU.objects.filter(
                Q(autorizado_em=None) & Q(pas__servidor__tipo=self.get_tipo())
            )
            if alt.antigos_pasus.exists()
        ]

    def get_query(self):
        try:
            # TODO Otimizar essa query, pois estou buscando os ids de todos os PA's que possuem autorizacao a ser feita
            query = PeriodoAquisitivoServidorUsufruto.objects.filter(
                Q(periodo_aquisitivo_servidor__servidor__tipo=self.get_tipo())
                & (
                    Q(
                        estado__in=[
                            PASU_NOVO,
                        ]
                    )
                    | Q(id__in=self.get_query_pasus_updates())
                )
            ).exclude(
                Q(
                    estado__in=[
                        PASU_SUSPENSO,
                    ]
                )
            )
        except Exception as e:
            log.exception(e)
        return query

    def query_keyword(self):
        qToSearch = None
        if self.request.POST.get("keyword", False):
            keyword = self.request.POST.get("keyword", "")
            qkeyword = Q(
                periodo_aquisitivo_servidor__servidor__pessoa_fisica__nome__icontains=keyword
            ) | Q(periodo_aquisitivo_servidor__servidor__matricula__icontains=keyword)
            qToSearch = qkeyword
        return qToSearch

    @decorator.login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        sort = self.request.POST["sort"] if "sort" in self.request.POST else "pa"
        dir = (
            "-"
            if "dir" in self.request.POST and self.request.POST["dir"] == "DESC"
            else ""
        )
        sorted = "%s%s" % (dir, sort)

        query = self.get_query()
        query_keyword = self.query_keyword()
        if query_keyword:
            query = query.filter(query_keyword)
        if sort == "pa":
            query = query.order_by(
                "%speriodo_aquisitivo_servidor__periodo_aquisitivo__ano_aquisicao"
                % dir,
                "%speriodo_aquisitivo_servidor__periodo_aquisitivo__periodo" % dir,
                "periodo_aquisitivo_servidor__servidor",
            )
        elif sort == "servidor":
            query = query.order_by("%speriodo_aquisitivo_servidor__servidor" % dir)
        elif sort == "chefia":
            query = query.order_by(
                "%speriodo_aquisitivo_servidor__servidor__chefe_imediato" % dir
            )
        else:
            query = query.order_by(sorted)
        obj["totalRows"] = query.count()

        start = int(self.request.POST["start"]) if "start" in self.request.POST else 0
        limit = int(self.request.POST["limit"]) if "limit" in self.request.POST else 35

        pasus_updates = self.get_query_pasus_updates()

        for pasu in query[start : (start + limit)]:
            status = []
            conflict = False
            if pasu.notificado:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["notificar"],
                        "title": "Notificada para alteração por conflitos",
                        "alt": "Notificada",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            if pasu.emalteracao:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_emalteracao"],
                        "title": "Aguardando autorização de alteração...",
                        "alt": "Em alteração",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )

            emalteracao = pasu.alteracao_out.count() > 0

            new_pasus = []
            if pasu.pk in pasus_updates:
                alter = AlteracaoPASU.objects.get(antigos_pasus__pk=pasu.pk)
                conflict_out = False
                for novo in alter.novos_pasus.filter():
                    conflict = novo.pas.check_all_conflict(novo, limit=1)
                    if conflict:
                        conflict_out = True
                    new_pasus.append(
                        {
                            "pk": novo.pk,
                            "data_inicio": DateUtils.date_to_str(novo.data_inicio),
                            "data_fim": DateUtils.date_to_str(novo.data_fim),
                            "conflict": conflict,
                        }
                    )

                if conflict_out:
                    status.append(
                        {
                            "icon": FRS_ICONS_THEME["pasu_conflito"],
                            "title": "Parcela conflita com a de outro membro/servidor",
                            "alt": "Conflito",
                        }
                    )
                else:
                    status.append(
                        {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                    )
            else:
                conflict = pasu.pas.check_all_conflict(pasu, limit=1)
                if conflict:
                    status.append(
                        {
                            "icon": FRS_ICONS_THEME["pasu_conflito"],
                            "title": "Parcela conflita com a de outro membro/servidor",
                            "alt": "Conflito",
                        }
                    )
                else:
                    status.append(
                        {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                    )

            responsavel = (
                pasu.pas.servidor.chefe_imediato
                if pasu.pas.servidor.chefe_imediato
                else "----"
            )
            workplace = pasu.pas.servidor.workplace_by_date()

            if not emalteracao:
                data_inicio = DateUtils.date_to_str(pasu.data_inicio)
                data_fim = DateUtils.date_to_str(pasu.data_fim)
                dias = pasu.dias
                criado_em = DateUtils.datetime_to_str(pasu.criado_em)
                criado_por = str(pasu.created_by)
                modificado_por = str(pasu.modified_by)
                modificado_em = DateUtils.datetime_to_str(pasu.modified_at)
            else:
                data_inicio = "---"
                data_fim = "---"
                dias = "---"
                alter = pasu.alteracao_out.all()[0]
                criado_em = DateUtils.datetime_to_str(alter.criado_em)
                criado_por = str(alter.created_by)
                modificado_por = str(alter.modified_by)
                modificado_em = DateUtils.datetime_to_str(alter.modified_at)

            obj["result"].append(
                {
                    "status": status,
                    "pk": pasu.pk,
                    "pa": "%s" % pasu.pas.periodo_aquisitivo,
                    "servidor": "%s" % pasu.pas.servidor,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "dias": dias,
                    "situacao": "%s" % pasu.situacao,
                    "alteracao": emalteracao,
                    "lotacao": (
                        str(workplace) if workplace else "Não possui lotação ativa"
                    ),
                    "chefia": "%s" % responsavel,
                    "criado_em": criado_em,
                    "criado_por": criado_por,
                    "modificado_por": modificado_por,
                    "modificado_em": modificado_em,
                    "conflict": conflict,
                    "new_pasus": new_pasus,
                }
            )
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class FRSAutorizacaoFeriasChefiaMembros(FRSAutorizacaoFeriasChefia):

    @decorator.login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.ferias.AutorizacaoFeriasMembros()")

    def get_tipo(self):
        return "M"


class FRSAutorizacaoFeriasChefiaAdmin(FRSAutorizacaoFeriasChefia):

    @decorator.login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.ferias.AutorizacaoFeriasAdmin()")

    def get_tipo(self):
        return "S"


class FRSGestorFerias(extjs.ExtWidget):

    class Form(forms.ModelForm):
        class Meta:
            pa_model = PeriodoAquisitivo
            pas_model = PeriodoAquisitivoServidor
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    @decorator.login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.ferias.GestorFerias()")

    def apply_filter(self, query):
        qs = []

        if "keyword" in self.request.POST:
            if "servidor" in self.request.POST.getlist("toSearch"):
                qs.append(Q(servidor__matricula__iexact=self.request.POST["keyword"]))
                qs.append(
                    Q(
                        servidor__pessoa_fisica__nome__icontains=self.request.POST[
                            "keyword"
                        ]
                    )
                )
        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)

        return query.filter(q) if q else query

    def get_query(self):
        query = PeriodoAquisitivoServidor.objects.all()
        if "pa" in self.request.POST:
            pa = self.request.POST["pa"]
            query = query.filter(periodo_aquisitivo=pa)
        return query

    @decorator.login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}

        sort = self.request.POST["sort"] if "sort" in self.request.POST else ""
        dir = (
            "-"
            if "dir" in self.request.POST and self.request.POST["dir"] == "DESC"
            else ""
        )

        if sort:
            query = self.get_query().order_by("%s%s" % (dir, sort))
        else:
            query = self.get_query().order_by(
                "periodo_aquisitivo", "servidor__pessoa_fisica__nome"
            )

        obj["totalRows"] = query.count()

        if "keyword" in self.request.POST:
            query = self.apply_filter(query)

        start = int(self.request.POST["start"]) if "start" in self.request.POST else 0
        limit = int(self.request.POST["limit"]) if "limit" in self.request.POST else 50

        for pas in query[start : (start + limit)]:
            status = []
            if pas.fruido:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_fruido"],
                        "title": "Período aquisitivo fruído",
                        "alt": "Fruido",
                    }
                )
            elif pas.fruindo:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pasu_fruindo"],
                        "title": "Parcela em fruição",
                        "alt": "Fruindo",
                    }
                )
            elif pas.estado == PAS_EMANDAMENTO:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pas_andamento"],
                        "title": "Em andamento",
                        "alt": "Andamento",
                    }
                )
            elif pas.estado == PAS_INDENIZADA:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pas_indenizada"],
                        "title": "Período Indenizado",
                        "alt": "Indenizado",
                    }
                )
            elif pas.estado == PAS_ALIBERACAO:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["aguardando"],
                        "title": "Aguardando liberação",
                        "alt": "Liberacao",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            if pas.pago:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["pago"],
                        "title": "Período aquisitivo pago (%s)" % pas.folha,
                        "alt": "Pago",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            if pas.bloqueado:
                status.append(
                    {
                        "icon": FRS_ICONS_THEME["bloqueado"],
                        "title": "Período bloqueado",
                        "alt": "Bloqueado",
                    }
                )
            else:
                status.append(
                    {"icon": FRS_ICONS_THEME["blank"], "title": "", "alt": "--"}
                )
            quantidade_dias = pas.quantidade_dias
            dias_usufruidos = pas.dias_usufruidos
            paid_days = pas.paid_days
            obj["result"].append(
                {
                    "pk": pas.pk,
                    "status": status,
                    "periodo_aquisitivo": "%s" % pas.periodo_aquisitivo,
                    "periodo_aquisitivo_pk": pas.periodo_aquisitivo.pk,
                    "servidor": "%s" % pas.servidor,
                    "servidor_pk": pas.servidor.pk,
                    "quantidade_dias": quantidade_dias,
                    "dias_marcados": pas.dias_marcados,
                    "dias_agendados": pas.dias_agendados,
                    "dias_usufruidos": dias_usufruidos,
                    "dias_nao_marcados": pas.dias_nao_marcados,
                    "paid_days": paid_days,
                    "dias_ausufruir": quantidade_dias - dias_usufruidos - paid_days,
                    "bloqueado": pas.bloqueado,
                    "usufruto_ini": "%s"
                    % DateUtils.date_to_str(pas.data_inicio_usufruto),
                    "usufruto_fim": (
                        "%s" % DateUtils.date_to_str(pas.data_fim_usufruto)
                        if pas.data_fim_usufruto
                        else ""
                    ),
                    "folha_terco": "%s" % pas.folha if pas.pago else "Não pago",
                    "folha_terco_pk": (
                        pas.folha_evento_terco_constitucional.pk
                        if pas.folha_evento_terco_constitucional
                        else 0
                    ),
                    "situacao": "%s" % pas.situacao,
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @decorator.login_required(type="JSON")
    def gerenciamento(self, args=[]):
        obj = {"result": {}, "success": False, "retorno": {}}
        linelog = LineLog(request=self.request, level=99, status=0)
        try:
            with transaction.atomic():
                acao = self.request.POST["acao"]
                pa_id = self.request.POST.get("pa", 0)
                pas_id = self.request.POST.get("pas", 0)
                pasu_id = self.request.POST.get("pasu", 0)
                if acao == "marcar":
                    # O atributo 'pas' retorna o PeriodoAquisitivoServidor especializado (Membro ou Admin)
                    pas = PeriodoAquisitivoServidor.objects.get(pk=pas_id).pas
                    datas = (
                        [
                            {
                                "data_inicio": datetime.date(
                                    datetime.strptime(
                                        d.split(",")[0],
                                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                                    )
                                ),
                                "data_fim": datetime.date(
                                    datetime.strptime(
                                        d.split(",")[1],
                                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                                    )
                                ),
                            }
                            for d in self.request.POST.getlist("datas")
                        ]
                        if "datas" in self.request.POST
                        and len(self.request.POST.getlist("datas")) > 0
                        and self.request.POST.getlist("datas")[0]
                        else []
                    )
                    anotar = True if "anotacao" in self.request.POST else False
                    self._marcar(pas, datas, anotar)
                    obj["success"] = True
                    obj["retorno"] = {
                        "pk": pas.pk,
                        "dias_marcados": pas.dias_marcados,
                        "dias_agendados": pas.dias_agendados,
                        "dias_usufruidos": pas.dias_usufruidos,
                        "situacao": ESTADO_PAS[pas.estado],
                    }
                    linelog.json_description["retorno"] = obj["retorno"]
                elif acao == "desmarcar":
                    pasu_id = (
                        self.request.POST["pasu"] if "pasu" in self.request.POST else -1
                    )
                    # O atributo 'pas' retorna o PeriodoAquisitivoServidor especializado (Membro ou Admin)
                    pas = PeriodoAquisitivoServidor.objects.get(pk=pas_id).pas
                    self._desmarcar(pas, pasu_id)
                    obj["success"] = True
                    obj["retorno"] = {
                        "pk": pas.pk,
                        "dias_marcados": pas.dias_marcados,
                        "dias_agendados": pas.dias_agendados,
                        "dias_usufruidos": pas.dias_usufruidos,
                        "situacao": ESTADO_PAS[pas.estado],
                    }
                    linelog.json_description["retorno"] = obj["retorno"]
                elif acao == "alterar":
                    anotar = True if "anotacao" in self.request.POST else False
                    pasus_id = (
                        self.request.POST.getlist("pasus")
                        if "pasus" in self.request.POST
                        and len(self.request.POST.getlist("pasus")) > 0
                        else []
                    )
                    # O atributo 'pas' retorna o PeriodoAquisitivoServidor especializado (Membro ou Admin)
                    pas = PeriodoAquisitivoServidor.objects.get(pk=pas_id).pas
                    datas = (
                        [
                            {
                                "data_inicio": datetime.date(
                                    datetime.strptime(
                                        d.split(",")[0],
                                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                                    )
                                ),
                                "data_fim": datetime.date(
                                    datetime.strptime(
                                        d.split(",")[1],
                                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                                    )
                                ),
                            }
                            for d in self.request.POST.getlist("datas")
                        ]
                        if "datas" in self.request.POST
                        and len(self.request.POST.getlist("datas")) > 0
                        and self.request.POST.getlist("datas")[0]
                        else []
                    )
                    justificativa = self.request.POST.get("justificativa", "")
                    publicacao_id = self.request.POST.get("publicacao", 0)
                    self._alterar(
                        pas, pasus_id, datas, justificativa, publicacao_id, anotar
                    )
                    obj["success"] = True
                    obj["retorno"] = {
                        "pk": pas.pk,
                        "dias_marcados": pas.dias_marcados,
                        "dias_agendados": pas.dias_agendados,
                        "dias_usufruidos": pas.dias_usufruidos,
                        "situacao": ESTADO_PAS[pas.estado],
                    }
                    linelog.json_description["retorno"] = obj["retorno"]
                elif acao == "liberar":
                    pas_pks = []
                    if pas_id:
                        self._liberar(pas_id)
                        pas_pks = [
                            pas_id,
                        ]
                    elif pa_id:
                        pas_pks = self._liberar_pa(pa_id)
                    if len(pas_pks) > 0:
                        obj["result"]["message"] = (
                            "Foram liberados %d período de férias." % len(pas_pks)
                        )
                    else:
                        obj["result"][
                            "message"
                        ] = "Nenhuma período de férias foi liberado."
                    obj["success"] = True
                    linelog.json_description["pas_liberados"] = pas_pks
                elif acao == "homologar":
                    publicacao = (
                        self.request.POST["publicacao"]
                        if "publicacao" in self.request.POST
                        else -1
                    )
                    homologados = 0
                    try:
                        homologados = self._homologar_pa(pa_id, publicacao)
                        if homologados > 0:
                            obj["result"]["message"] = (
                                "Foram homologados %d período de férias." % homologados
                            )
                        else:
                            obj["result"][
                                "message"
                            ] = "Homologação iniciada, acompanhe pelo visualizador de tarefas."
                        obj["success"] = True
                    except Exception as err:
                        log.exception(err)
                        obj["result"]["message"] = "%s" % (err)
                    linelog.json_description["pas_homologados"] = homologados
                elif acao == "alterarbloqueio":
                    pas_id = (
                        self.request.POST.getlist("pas")
                        if "pas" in self.request.POST
                        else -1
                    )
                    bloqueados = self._alterar_bloqueio(pas_id)
                    obj["result"][
                        "message"
                    ] = "Bloqueio(s) do período de férias alterado com sucesso."
                    obj["success"] = True
                    linelog.json_description["bloqueios"] = bloqueados
                elif acao == "suspender":
                    anotar = True if "anotacao" in self.request.POST else False
                    pasu_id = self.request.POST.get("pasu", -1)
                    data = datetime.strptime(
                        self.request.POST.get("data", datetime.now().date()),
                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                    ).date()
                    pas = self._suspender(pasu_id, data, anotar)
                    obj["result"]["message"] = "Parcela de férias suspensa com sucesso."
                    obj["pas"] = {
                        "dias_marcados": pas.dias_marcados,
                        "dias_agendados": pas.dias_agendados,
                        "dias_usufruidos": pas.dias_usufruidos,
                        "situacao": pas.situacao,
                    }
                    obj["success"] = True
                    linelog.json_description["retorno"] = obj["pas"]
                elif acao == "atualizar":
                    if pa_id:
                        pa = PeriodoAquisitivo.objects.get(pk=pa_id)
                        qtd_pas_anterior = pa.paservidores.count()
                        pa.criar_periodo_aquisitivo_servidor()
                        qtd_pas = pa.paservidores.count()
                        obj["result"][
                            "message"
                        ] = "Período Aquisitivo atualizado com sucesso."
                        obj["pa"] = {"novos": qtd_pas - qtd_pas_anterior}
                        obj["success"] = True
                        linelog.json_description["retorno"] = obj["pa"]
                    else:
                        obj["error"] = (
                            "Período Aquisitivo não informado para atualização dos servidores."
                        )
                        linelog.json_description["retorno"] = "ACAO INVALIDA"
                elif acao == "update_paservidor":
                    servidor_id = (
                        self.request.POST["servidor"]
                        if "servidor" in self.request.POST
                        else None
                    )
                    if pa_id and servidor_id:
                        servidor = Servidor.objects.get(pk=servidor_id)
                        pa = PeriodoAquisitivo.objects.get(pk=pa_id)
                        pa.create_or_update_paservidor(servidor)
                        obj["result"][
                            "message"
                        ] = "O período aquisitivo do servidor foi criado/atualizado com sucesso."
                        obj["success"] = True
                        linelog.json_description["retorno"] = obj
                    else:
                        obj["error"] = (
                            "Período Aquisitivo ou servidor não informado para atualização."
                        )
                        linelog.json_description["retorno"] = "ACAO INVALIDA"
                elif acao == "indenizar":
                    pas_id = (
                        self.request.POST.getlist("pas")
                        if "pas" in self.request.POST
                        else -1
                    )
                    if pas_id:
                        indenizacoes = self._indenizar(pas_id)
                        obj["result"][
                            "message"
                        ] = "<p><b>Relatório de indenizações</b></p>"
                        for i in indenizacoes:
                            obj["result"][
                                "message"
                            ] += "</br>%s: %s dia(s) indenizados" % (
                                i.periodo_aquisitivo,
                                indenizacoes[i],
                            )
                        obj["success"] = True
                        linelog.json_description["retorno"] = obj
                    else:
                        obj["error"] = (
                            "Período Aquisitivo ou servidor não informado para atualização."
                        )
                        linelog.json_description["retorno"] = "ACAO INVALIDA"
                elif acao == "reenviar":
                    self._reenviar(
                        PeriodoAquisitivoServidorUsufruto.objects.get(pk=pasu_id)
                    )
                    obj["success"] = True
                else:
                    obj["error"] = "Ação inválida."
                    linelog.json_description["retorno"] = "ACAO INVALIDA"
        except FeriasError as err:
            obj["error"] = "%s" % err
            self.log.debug("FERIAS ERROR: %s" % err.value)
            linelog.json_description["error"] = obj["error"]
        except Exception as err:
            obj["error"] = (
                "Um erro inesperado ocorreu. Entre em contato com o administrador do sistema! %s"
                % err
            )
            self.log.exception(err)
            linelog.json_description["error"] = obj["error"]
        else:
            linelog.status = 1

        linelog.save()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _reenviar(self, pasu):
        pasu._reenviar()

    def _marcar(self, pas, datas=[], anotar=True):
        pasus = []
        pasu = None
        publicacao = self.request.POST.get("publicacao", 0)
        if len(datas) > pas.periodo_aquisitivo.configuracao.max_divisoes:
            raise FeriasError(
                "O número máximo de parcelas é %d."
                % pas.periodo_aquisitivo.configuracao.max_divisoes
            )
        count_new_pasus = len(datas)
        dias_marcados = pas.dias_marcados
        count_pasus_changing = 0
        for parcela in datas:
            pasu = pas.adicionar_usufruto(
                parcela["data_inicio"],
                parcela["data_fim"],
                True,
                count_new_pasus=count_new_pasus,
                dias_marcados=dias_marcados,
                count_pasus_changing=count_pasus_changing,
            )
            dias_marcados += pasu.dias
            count_pasus_changing += 1
            pasus.append(pasu.id)
            notify("FRS_AUTORIZACAO", pas.servidor, pas, pasu=pasu)
        pas.homologado and pas.autorizar_usufruto(
            pasus, self.request.user.servidor.id, True, publicacao, True, anotar
        )
        pas.atualiza_estado(True)
        if len(datas) == 0:
            raise FeriasError("Nenhum período informado.")
        return pasu

    def _desmarcar(self, pas, pasu_id):
        pasu = pas.deletar_usufruto(pasu_id, True)
        pas.atualiza_estado()
        return pasu

    def _alterar(
        self, pas, pasus_id, datas, justificativa, publicacao_id=0, anotar=True
    ):
        if len(pasus_id) == 0 or (len(pasus_id) == 1 and pasus_id[0] == ""):
            raise FeriasError("Nenhum período selecionado.")
        responsavel = self.request.user.servidor
        alteracao = pas.solicitar_alteracao(
            pasus_id, datas, justificativa, responsavel.id, publicacao_id, anotar
        )
        pas.atualiza_estado()
        return alteracao

    def _liberar_pa(self, pa_id):
        pa = PeriodoAquisitivo.objects.get(pk=pa_id)
        liberados = []
        for pas in pa.paservidores.filter(estado__in=[PAS_ALIBERACAO]):
            try:
                self._liberar(pas.pk)
            except Exception as e:
                log.exception(e)
            else:
                liberados.append(pas.pk)
        return liberados

    def _liberar(self, pas_id):
        pas = PeriodoAquisitivoServidor.objects.get(pk=pas_id)
        pas = pas.pas
        pas._liberar()

    def _homologar_pa(self, pa_id, publicacao):
        pa = PeriodoAquisitivo.objects.get(pk=pa_id)
        log.info("PA: %s" % pa)
        homologados = []
        if pa.publicado or (
            pa.data_homologacao_prev
            and pa.data_homologacao_prev > datetime.now().date()
        ):
            return pa.paservidores.filter(
                Q(usufrutos__estado__in=[PASU_HOMOLOGADO])
            ).count()
        if not pa.data_homologacao_prev:
            raise Exception(
                "Para homologar é necessário preencher a Data de Previsão de Homologação do Período"
            )
        pa.homologar(publicacao)
        # log.info("PA2: %s" % pa)
        # for pas in pa.paservidores.filter(Q(estado__in=[PAS_EMANDAMENTO])):
        #     try:
        #         pas.homologar({'publicacao': publicacao})
        #         log.info("HOMOLOGADO: %s" % pas)
        #         homologados.append(pas.pk)
        #         notify('FRS_HOMOLOGACAO', pas.servidor, pas=pa)
        #     except Exception as err:
        #         log.exception(err)
        # # pa.data_publicacao = datetime.now()
        # pa.save(update=False)
        return 0

    def _alterar_bloqueio(self, pas_id):
        # responsavel = self.request.user.servidor
        desbloqueados = {}
        for pas in PeriodoAquisitivoServidor.objects.filter(pk__in=pas_id):
            pas.bloqueado = not pas.bloqueado
            pas.save()
            desbloqueados[pas.pk] = pas.bloqueado
        return desbloqueados

    def _suspender(self, pasu_id, data, anotar=True):
        """
        Este método pode suspender ou interromper um PASU, de acordo com o estado em que ele se encontra e a
            data informada.
        Caso o estado seja PASU_FRUINDO na data informada o PASU será interrompido,
        caso contrário uma tentativa de suspender será efetuada, porém se o estado não for válido para
        suspensão uma exception será disparada
        estado          ->              acao
        PASU_FRUINDO                interromper
        PASU_HOMOLOGADO         suspender
        qualquer outro                 exception
        """
        pasu = PeriodoAquisitivoServidorUsufruto.objects.get(pk=pasu_id)
        publicacao = self.request.POST["publicacao"]
        pas = pasu.pas
        if pasu.data_inicio < data <= pasu.data_fim:
            pas._interromper(pasu, data, True, {"publicacao": publicacao}, anotar)
        elif pasu.data_inicio >= data:
            log.info("_suspender")
            pas._suspender(pasu, True, {"publicacao": publicacao}, anotar)
        return pas

    def _indenizar(self, pas_ids, anotar=True):
        """
        Este método altera o estado do PAS de um determinado servidor para o estado de 'PAS_INDENIZADA'.
        Pré-requisitos: O estado do PAS está em 'PAS_EMANDAMENTO'
        """
        indenizados = {}
        for pas_id in pas_ids:
            pas = PeriodoAquisitivoServidor.objects.get(pk=pas_id)
            if pas.dias_agendados:
                indenizados[pas] = "Erro: Possui dias agendados - 0"
            else:
                pas.paid_days = (
                    pas.quantidade_dias - pas.dias_usufruidos - pas.paid_days
                )
                try:
                    pas.save()
                except Exception:
                    break
                dias = pas._indenizar()
                indenizados[pas] = dias
        return indenizados

    @decorator.login_required(type="JSON")
    def list_folha_terco(self, args=[]):
        obj = {"result": []}
        pas = (
            PeriodoAquisitivoServidor.objects.get(pk=self.request.POST["pas"])
            if "pas" in self.request.POST
            else None
        )
        matricula_servidor = pas.servidor.matricula
        obj["result"] = [
            {
                "pk": fe.pk,
                "description": "%s (evento %s)" % (fe.folha, fe.evento.numero),
            }
            for fe in pas.servidor.entries.filter(
                Q(
                    evento__numero__in=[
                        "0147",
                        "0236",
                        "0234",
                        "0199",
                        "0226",
                        "0223",
                        "05000",
                        "05006",
                        "07700",
                        "08300",
                    ]
                )
            )
            .exclude(
                Q(
                    id__in=[
                        p.folha_evento_terco_constitucional.pk
                        for p in PeriodoAquisitivoServidor.objects.filter(
                            Q(servidor__matricula=matricula_servidor)
                            & ~Q(folha_evento_terco_constitucional=None)
                        )
                    ]
                )
            )
            .order_by("-folha__periodo__ano", "-folha__periodo__mes")
        ]
        # Adiciona a opção de PAGO (sem informação da folha) à lista de se o período for anterior e nao estiver setado como pago_sem_folha
        # if pas.periodo_aquisitivo.periodo_anterior and not pas.pago_sem_folha:
        obj["result"].insert(
            0, {"pk": -1, "description": "PAGO (sem informação da folha)"}
        )
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @decorator.login_required(type="JSON")
    def update_folha_terco(self, args=[]):
        pas = (
            PeriodoAquisitivoServidor.objects.get(pk=self.request.POST["pas"])
            if "pas" in self.request.POST
            else -1
        )
        folha_terco = (
            self.request.POST["folha_terco"] or None
            if "folha_terco" in self.request.POST
            else None
        )
        obj = {
            "result": {},
            "success": False,
        }
        obj["result"]["message"] = "Erro ao alterar folha de terço constitucional."
        if pas:
            if int(folha_terco or 0) == -1:
                pas.pago_sem_folha = True
                pas.folha_evento_terco_constitucional_id = None
            else:
                pas.folha_evento_terco_constitucional_id = folha_terco
                pas.pago_sem_folha = False
            pas.save()
            obj["result"][
                "message"
            ] = "Folha de terço constitucional alterada com sucesso."
            if pas.pago:
                obj["result"]["folha"] = {
                    "pk": (
                        pas.folha_evento_terco_constitucional.pk
                        if pas.folha_evento_terco_constitucional
                        else 0
                    ),
                    "description": "%s" % pas.folha,
                }
            else:
                obj["result"]["folha"] = {"pk": 0, "description": "Não pago"}
            obj["success"] = True

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class FRSGestorFeriasMembros(FRSGestorFerias):

    @decorator.login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.ferias.GestorFeriasMembros()")

    def get_query(self):
        # TODO Otimizar essa query, pois estou buscando os ids de todos os PA's que possuem
        query = (
            super(FRSGestorFeriasMembros, self)
            .get_query()
            .filter(periodo_aquisitivo__configuracao__tipo_servidor="M")
        )
        return query


class FRSGestorFeriasAdministrativo(FRSGestorFerias):

    @decorator.login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.ferias.GestorFeriasAdministrativo()")

    def get_query(self):
        # TODO Otimizar essa query, pois estou buscando os ids de todos os PA's que possuem
        query = (
            super(FRSGestorFeriasAdministrativo, self)
            .get_query()
            .filter(periodo_aquisitivo__configuracao__tipo_servidor="S")
        )
        return query


class FRSGestorFeriasFOPAG(FRSGestorFerias):
    @decorator.login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.ferias.GestorFeriasFolhaPagamento()")


class FRSAutorizacaoPASU(FRSPeriodoAquisitivoServidorUsufruto):
    def get_query(self):
        servidor = self.request.user.servidor
        serv_ids = servidor.subordinados_ids
        pa = self.request.POST["pa"] if "pa" in self.request.POST else -1
        try:
            query = PeriodoAquisitivoServidorUsufruto.objects.filter(
                Q(periodo_aquisitivo_servidor__servidor__in=serv_ids)
                & Q(periodo_aquisitivo_servidor__periodo_aquisitivo=pa)
                & Q(
                    periodo_aquisitivo_servidor__estado__in=[
                        PAS_EMANDAMENTO,
                    ]
                )
                & Q(estado__in=[PASU_NOVO, PASU_AUTORIZADO_CI, PASU_EMALTERACAO])
            )
        except (
            Exception
        ) as e:  # TODO NOTIFICATION notificar que esse usuário não estar ligado a um servidor
            self.log.exception(e)
            self.log.debug("Servidor nao encontrado: %s" % self.request.user.servidor)
            query = query.filter(pk=-1)

        return query


class FRSConfiguration(Restful):
    """
    **Classe** para acessar a configuração padrão de envio de emails.
    """

    _model = Configuration

    force_upper = False

    def json(self, args=[]):
        import json

        cfg = Configuration.get_or_create("ferias")
        values = {
            "pk": cfg.pk,
            "servidor_tipo_deferimento": cfg.get("servidor_tipo_deferimento"),
            "servidor_tipo_indeferimento": cfg.get("servidor_tipo_indeferimento"),
            "servidor_notificacao_destaque": cfg.get("servidor_notificacao_destaque"),
            "servidor_notificacao_email_institucional": cfg.get(
                "servidor_notificacao_email_institucional"
            ),
            "membro_tipo_deferimento": cfg.get("membro_tipo_deferimento"),
            "membro_tipo_indeferimento": cfg.get("membro_tipo_indeferimento"),
            "membro_notificacao_destaque": cfg.get("membro_notificacao_destaque"),
            "membro_notificacao_email_institucional": cfg.get(
                "membro_notificacao_email_institucional"
            ),
        }
        dicio = {"values": values}
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.ferias.configuration.message.Manager", %s)'
            % json.dumps(dicio)
        )

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            slug=instance.application,
            servidor_tipo_deferimento=instance.get("servidor_tipo_deferimento"),
            servidor_tipo_indeferimento=instance.get("servidor_tipo_indeferimento"),
            servidor_notificacao_destaque=instance.get("servidor_notificacao_destaque"),
            servidor_notificacao_email_institucional=instance.get(
                "servidor_notificacao_email_institucional"
            ),
            membro_tipo_deferimento=instance.get("membro_tipo_deferimento"),
            membro_tipo_indeferimento=instance.get("membro_tipo_indeferimento"),
            membro_notificacao_destaque=instance.get("membro_notificacao_destaque"),
            membro_notificacao_email_institucional=instance.get(
                "membro_notificacao_email_institucional"
            ),
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(FRSConfiguration, self).get_params(*args, **kargs)
        cfg = Configuration.get_or_create("ferias")
        if "servidor_tipo_deferimento" in params:
            cfg.set("servidor_tipo_deferimento", 1)
            del params["servidor_tipo_deferimento"]
        else:
            cfg.set("servidor_tipo_deferimento", 0)

        if "servidor_tipo_indeferimento" in params:
            cfg.set("servidor_tipo_indeferimento", 1)
            del params["servidor_tipo_indeferimento"]
        else:
            cfg.set("servidor_tipo_indeferimento", 0)

        if "servidor_notificacao_destaque" in params:
            cfg.set("servidor_notificacao_destaque", 1)
            del params["servidor_notificacao_destaque"]
        else:
            cfg.set("servidor_notificacao_destaque", 0)

        if "servidor_notificacao_email_institucional" in params:
            cfg.set("servidor_notificacao_email_institucional", 1)
            del params["servidor_notificacao_email_institucional"]
        else:
            cfg.set("servidor_notificacao_email_institucional", 0)
        if "membro_tipo_deferimento" in params:
            cfg.set("membro_tipo_deferimento", 1)
            del params["membro_tipo_deferimento"]
        else:
            cfg.set("membro_tipo_deferimento", 0)

        if "membro_tipo_indeferimento" in params:
            cfg.set("membro_tipo_indeferimento", 1)
            del params["membro_tipo_indeferimento"]
        else:
            cfg.set("membro_tipo_indeferimento", 0)

        if "membro_notificacao_destaque" in params:
            cfg.set("membro_notificacao_destaque", 1)
            del params["membro_notificacao_destaque"]
        else:
            cfg.set("membro_notificacao_destaque", 0)

        if "membro_notificacao_email_institucional" in params:
            cfg.set("membro_notificacao_email_institucional", 1)
            del params["membro_notificacao_email_institucional"]
        else:
            cfg.set("membro_notificacao_email_institucional", 0)

        return params
