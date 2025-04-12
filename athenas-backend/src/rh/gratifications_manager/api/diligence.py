import json
from datetime import datetime

from django.db.models import Q

from contrib.newrest import RestfulDRY
from contrib.decorator import login_required
from contrib.utils import get_json_engine, getLogger
from contrib.middleware import get_current_user
from contrib.daterange import NewDateRange

from engine.mq.models import Task
from rh.models import MovimentacaoDiligencia, GratDiligencia
from rh.gfp.models import Evento, Servidor

from rh.gratifications_manager.gm_utils import *
from rh.gfp.gcpp_utils import criar_gcpp

from rh.gratifications_manager.tasks_diligence import calcular_movs_diligs_task

json_engine = get_json_engine()
log = getLogger(__name__)


class GMDiligenceMoveRestful(RestfulDRY):

    _model = MovimentacaoDiligencia

    full_text_index = (
        "comarca__nome__icontains",
        "substituto__pessoa_fisica__nome__icontains",
        "substituto__matricula__icontains",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gratifications_manager.diligence.Manage")')

    def do_get(self, pk=None):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        if pk is not None:
            try:
                inst = self.get_query().get(pk=pk)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Processo com sucesso!",
                        "instance": self.model_to_dict(inst),
                    }
                )
        else:
            try:
                query = self.get_query()
                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                query = self.remove_projection(query)

                query = self.filtrar_registros(query)

                rst.update(count=query.count())
                query = self.do_page(query)

            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                log.exception(str(e))
                rst.update(message=str(e))
            else:
                rst.update(
                    {
                        "collection": [self.model_to_dict(record) for record in query],
                        "success": True,
                        "message": "Processado com sucesso!",
                    }
                )

        return rst

    def filtrar_registros(self, query):
        filtro = self.request.GET.get("filtro", "todos")
        if filtro != "todos":
            periodo_ano = self.request.GET.get("periodo_ano", datetime.today().year)
            periodo_mes = self.request.GET.get("periodo_mes", datetime.today().month)

            q_grat_diligencia = GratDiligencia.objects.filter(
                ano=periodo_ano,
                mes=periodo_mes,
            )

            if filtro == "avaliar":
                q_grat_diligencia = q_grat_diligencia.filter(
                    status__in=["DEFER", "INDEFER"],
                )
            elif filtro == "deferido":
                q_grat_diligencia = q_grat_diligencia.filter(
                    status__in=["AVAL", "INDEFER"],
                )
            elif filtro == "indeferido":
                q_grat_diligencia = q_grat_diligencia.filter(
                    status__in=["AVAL", "DEFER"],
                )

            excluir_diligs_ids = [
                mov_diligencia.mov_diligencia.pk for mov_diligencia in q_grat_diligencia
            ]
            query = query.exclude(pk__in=excluir_diligs_ids)

        return query

    def calcular_diligencia(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo_ano = self.request.POST.get("periodo_ano")
        periodo_mes = self.request.POST.get("periodo_mes")

        diligencia = MovimentacaoDiligencia.objects.get(
            pk=self.request.POST.get("diligencia_id")
        )
        q_grat_diligencia = self.verificar_grat_diligencia(
            diligencia, periodo_ano, periodo_mes
        )

        if q_grat_diligencia.exists():
            grat_diligencia = q_grat_diligencia.first()
            if grat_diligencia.status == "DEFER":
                obj["success"] = False
                obj["message"] = "O registro selecionado já está DEFERIDO!"
            elif grat_diligencia.status == "INDEFER":
                obj["success"] = False
                obj["message"] = "O registro selecionado está INDEFERIDO!"
        else:
            grat_diligencia = GratDiligencia(
                mov_diligencia=diligencia,
                ano=periodo_ano,
                mes=periodo_mes,
                evento=Evento.objects.get(numero="12000"),
            )

        folha = buscar_folha(grat_diligencia.ano, grat_diligencia.mes)
        if folha.exists() is False:
            obj["success"] = False
            obj["message"] = (
                "Não é possível realizar o cálculo, não há folha vigente para o período selecionado."
            )
        else:
            evento = Evento.objects.get(numero="12000")

            res_titular = calc_from_period(
                grat_diligencia.mov_diligencia.servidor, folha.first(), evento
            )
            grat_diligencia.qtd_dias_consolidado_titular = int(res_titular["qnt"])

            range_periodo = NewDateRange.range_from_month(
                int(grat_diligencia.ano), int(grat_diligencia.mes)
            )
            dt_range_periodo = NewDateRange(range_periodo[0], range_periodo[1])
            if grat_diligencia.mov_diligencia.substituto and (
                grat_diligencia.qtd_dias_consolidado_titular != dt_range_periodo.days
            ):
                res_substituto = calc_from_period(
                    grat_diligencia.mov_diligencia.substituto, folha.first(), evento
                )
                grat_diligencia.qtd_dias_consolidado_substituto = int(
                    res_substituto["qnt"]
                )

            grat_diligencia.status = "AVAL"
            grat_diligencia.data_ultimo_calculo = datetime.today()
            grat_diligencia.save()

            obj["message"] = (
                "Registro de Designação para Diligência calculado com sucesso!"
            )

        self.response.write(json_engine.encode(obj))

    def calcular_todos_diligencia(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo_ano = self.request.POST.get("periodo_ano")
        periodo_mes = self.request.POST.get("periodo_mes")

        folha = buscar_folha(periodo_ano, periodo_mes)
        if folha.exists() is False:
            obj["success"] = False
            obj["message"] = (
                "Não é possível realizar o cálculo, não há folha vigente para o período selecionado."
            )
        else:
            try:
                Task.start(
                    calcular_movs_diligs_task,
                    description=f"Processamento para calcular os registros de designação para diligência",
                    user=self.request.user.id,
                    periodo_ano=periodo_ano,
                    periodo_mes=periodo_mes,
                )

                obj[
                    "message"
                ] = """Iniciando processamento para calcular os registros de designação para diligência
                (somente os registros que não estiverem DEFERIDO ou INDEFERIDO)."""
            except:
                obj["success"] = False
                obj["message"] = "Erro no processamento para calcular os registros."

        self.response.write(json_engine.encode(obj))

    def verificar_grat_diligencia(self, diligencia, periodo_ano, periodo_mes):
        return GratDiligencia.objects.filter(
            mov_diligencia=diligencia,
            ano=periodo_ano,
            mes=periodo_mes,
            evento=Evento.objects.get(numero="12000"),
        )

    def deferir_diligencia(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo_ano = self.request.POST.get("periodo_ano")
        periodo_mes = self.request.POST.get("periodo_mes")
        diligencia = MovimentacaoDiligencia.objects.get(
            pk=self.request.POST.get("diligencia_id")
        )
        q_grat_diligencia = self.verificar_grat_diligencia(
            diligencia, periodo_ano, periodo_mes
        )

        if q_grat_diligencia.exists() is False:
            obj["success"] = False
            obj["message"] = (
                "O registro precisa ser calculado antes de ser deferido ou indeferido."
            )
        elif q_grat_diligencia.exists() and q_grat_diligencia.first().status == "DEFER":
            obj["success"] = False
            obj["message"] = "O registro selecionado já está DEFERIDO!"
        else:
            grat_diligencia = q_grat_diligencia.first()

            gcpp_titular = buscar_registro_gcpp(
                grat_diligencia.mov_diligencia.servidor,
                grat_diligencia.evento,
                grat_diligencia.ano,
                grat_diligencia.mes,
            )

            if diligencia.substituto:
                gcpp_substituto = buscar_registro_gcpp(
                    grat_diligencia.mov_diligencia.substituto,
                    grat_diligencia.evento,
                    grat_diligencia.ano,
                    grat_diligencia.mes,
                )

            if (gcpp_titular.exists() and gcpp_titular.first().status == "pago") or (
                diligencia.substituto
                and gcpp_substituto.exists()
                and gcpp_substituto.first().status == "pago"
            ):
                obj["success"] = False
                obj["message"] = (
                    "A registro de gratificação selecionado já está deferido e pago no GCPP para o titular e/ou substituto."
                )
            elif (
                gcpp_titular.exists() and gcpp_titular.first().status == "inapto"
            ) or (
                diligencia.substituto
                and gcpp_substituto.exists()
                and gcpp_substituto.first().status == "inapto"
            ):
                obj["message"] = (
                    f"O registro de gratificação selecionado já está deferido e está inapto para pagamento no GCPP para o titular e/ou substituto."
                )
            else:
                grat_diligencia.status = "DEFER"
                if grat_diligencia.qtd_dias_deferido_titular is None:
                    grat_diligencia.qtd_dias_deferido_titular = (
                        grat_diligencia.qtd_dias_consolidado_titular
                    )

                if (
                    diligencia.substituto
                    and grat_diligencia.qtd_dias_deferido_substituto is None
                ):
                    grat_diligencia.qtd_dias_deferido_substituto = (
                        grat_diligencia.qtd_dias_consolidado_substituto
                    )

                grat_diligencia.save()

                if grat_diligencia.qtd_dias_deferido_titular in [0, None]:
                    msg = f"Registro de gratificação do titular deferido. Como a quantidade de dias deferido é zero, não foi registrado no GCPP."
                else:
                    # registro gcpp está sendo criado no método save de GratAuxiliarCoordenacao
                    msg = f"Registro do titular deferido e registrado no GCPP."

                if diligencia.substituto:
                    if grat_diligencia.qtd_dias_deferido_substituto in [0, None]:
                        msg += f"Registro do substituto deferido. Como a quantidade de dias deferido é zero, não foi registrado no GCPP."
                    else:
                        # registro gcpp está sendo criado no método save de GratAuxiliarCoordenacao
                        msg += f"Registro do substituto deferido e registrado no GCPP."

                obj["message"] = msg

        self.response.write(json_engine.encode(obj))

    def indeferir_diligencia(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo_ano = self.request.POST.get("periodo_ano")
        periodo_mes = self.request.POST.get("periodo_mes")

        diligencia = MovimentacaoDiligencia.objects.get(
            pk=self.request.POST.get("diligencia_id")
        )
        q_grat_diligencia = self.verificar_grat_diligencia(
            diligencia, periodo_ano, periodo_mes
        )

        if q_grat_diligencia.exists() is False:
            obj["success"] = False
            obj["message"] = (
                "O registro precisa ser calculado antes de ser deferido ou indeferido."
            )
        elif q_grat_diligencia.exists() and q_grat_diligencia.first().status == "DEFER":
            obj["success"] = False
            obj["message"] = "O registro selecionado está DEFERIDO!"
        elif (
            q_grat_diligencia.exists() and q_grat_diligencia.first().status == "INDEFER"
        ):
            obj["success"] = False
            obj["message"] = "O registro selecionado já está INDEFERIDO!"
        else:
            grat_diligencia = q_grat_diligencia.first()
            grat_diligencia.status = "INDEFER"
            grat_diligencia.save()

            obj["message"] = "Registro selecionado indeferido com sucesso!"

        self.response.write(json_engine.encode(obj))

    def model_to_dict(self, instance):
        params = super(GMDiligenceMoveRestful, self).model_to_dict(instance)

        f = []
        if "filter" in self.request.GET:
            try:
                f = json.loads(self.request.GET.get("filter"))
            except Exception:
                f = []

        periodo_filtro = datetime.now().date()
        if f:
            periodo_filtro = datetime.strptime(f[0]["value"], "%Y-%m-%d").date()

        q_grat_diligencia = self.verificar_grat_diligencia(
            instance, periodo_filtro.year, periodo_filtro.month
        )

        icons_titular = self.get_icons_titular(instance)
        icons_substituto = self.get_icons_substituto(instance)

        status_grat_diligencia = "NAO_CALCULADO"
        qtd_dias_consolidado_titular = "-"
        qtd_dias_deferido_titular = "-"
        qtd_dias_consolidado_substituto = "-"
        qtd_dias_deferido_substituto = "-"
        if q_grat_diligencia.exists():
            grat_diligencia = q_grat_diligencia.first()

            status_grat_diligencia = grat_diligencia.status
            qtd_dias_consolidado_titular = grat_diligencia.qtd_dias_consolidado_titular
            qtd_dias_consolidado_substituto = (
                grat_diligencia.qtd_dias_consolidado_substituto
            )

            if grat_diligencia.qtd_dias_deferido_titular is not None:
                qtd_dias_deferido_titular = grat_diligencia.qtd_dias_deferido_titular

            if grat_diligencia.qtd_dias_deferido_substituto is not None:
                qtd_dias_deferido_substituto = (
                    grat_diligencia.qtd_dias_deferido_substituto
                )

        titular_ativo = False
        titular_pgto = False
        for icon in icons_titular:
            if icon["iconCls"] == "icon-fopag icon-exclamation-green":
                titular_ativo = True

            if icon["iconCls"] == "icon-fopag icon-cash":
                titular_pgto = True

        substituto_ativo = False
        substituto_pgto = False
        for icon in icons_substituto:
            if icon["iconCls"] == "icon-fopag icon-exclamation-green":
                substituto_ativo = True

            if icon["iconCls"] == "icon-fopag icon-cash":
                substituto_pgto = True

        params.update(
            {
                "icons_titular": icons_titular,
                "icons_substituto": icons_substituto,
                "titular_ativo": titular_ativo,
                "titular_pgto": titular_pgto,
                "substituto_ativo": substituto_ativo,
                "substituto_pgto": substituto_pgto,
                "qtd_dias_consolidado_titular": qtd_dias_consolidado_titular,
                "qtd_dias_deferido_titular": qtd_dias_deferido_titular,
                "qtd_dias_consolidado_substituto": qtd_dias_consolidado_substituto,
                "qtd_dias_deferido_substituto": qtd_dias_deferido_substituto,
                "icons_diligence": self.get_icons_diligencia(q_grat_diligencia),
                "status_grat_aux_coord": status_grat_diligencia,
                "periodo_ano": periodo_filtro.year,
                "periodo_mes": periodo_filtro.month,
                "grat_diligencia_id": (
                    q_grat_diligencia.first().pk if q_grat_diligencia.exists() else None
                ),
            }
        )

        return params

    def get_icons_diligencia(self, grat_diligencia):
        icons_diligencia = []

        if grat_diligencia.exists():
            if grat_diligencia.first().status == "INDEFER":
                title_status = "Indeferido"
                icon_status = "icon-status-busy"
            elif grat_diligencia.first().status == "DEFER":
                title_status = "Deferido"
                icon_status = "icon-status"
            elif grat_diligencia.first().status == "AVAL":
                title_status = "Avaliar"
                icon_status = "icon-status-away"
        else:
            title_status = "Não Calculado"
            icon_status = "icon-status-offline"

        icons_diligencia.append(
            {
                "iconCls": f"icon-fopag {icon_status}",
                "title": title_status,
                "alt": title_status,
            }
        )

        return icons_diligencia

    def get_icons_titular(self, instance):
        icon_ativo = "green" if instance.servidor.ativo else "red"
        icon = f"icon-fopag icon-exclamation-{icon_ativo}"
        status = "Titular Ativo" if instance.servidor.ativo else "Titular Inativo"
        icons_titular = [
            {
                "iconCls": icon,
                "title": status,
                "alt": status,
            }
        ]

        comarca_conferida = verifiar_comarca(instance.comarca, instance.servidor)
        if comarca_conferida is False:
            title = (
                f"O Titular não está na mesma comarca que a Designação para Diligência."
            )
            icons_titular.append(
                {
                    "iconCls": "icon-fopag icon-attention",
                    "title": title,
                    "alt": title,
                }
            )

        return icons_titular

    def get_icons_substituto(self, instance):
        if instance.substituto:
            icon_ativo = "green" if instance.substituto.ativo else "red"
            icon = f"icon-fopag icon-exclamation-{icon_ativo}"
            status = (
                "Substituto Ativo"
                if instance.substituto.ativo
                else "Substituto Inativo"
            )

            icons_substituto = [
                {
                    "iconCls": icon,
                    "title": status,
                    "alt": status,
                }
            ]
        else:
            icon = "icon-fopag icon-exclamation-black"
            status = "Não há Substituto"

            icons_substituto = [
                {
                    "iconCls": icon,
                    "title": status,
                    "alt": status,
                }
            ]

        return icons_substituto

    def export(self, args=[]):
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
            try:
                f = json.loads(self.request.GET.get("filter"))
            except Exception:
                f = []
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)

        query = self.remove_projection(query)
        query = self.filtrar_registros(query)

        rst = []
        for record in query:
            todos_meses = True
            periodo_filtro = datetime.now().date()

            if f:
                if next((item for item in f if item["stage"] == 2), None):
                    todos_meses = False
                periodo_filtro = datetime.strptime(f[0]["value"], "%Y-%m-%d").date()

            evento = Evento.objects.get(numero="12000")
            payroll = buscar_folha(periodo_filtro.year, periodo_filtro.month)

            pgto_titular = verificar_pgto_servidor(
                record.servidor, evento, periodo_filtro.year, periodo_filtro.month
            )
            pgto_substituto = verificar_pgto_servidor(
                record.substituto, evento, periodo_filtro.year, periodo_filtro.month
            )

            dias_receber_titular = calcular_dias_servidor(
                record.servidor, "titular", payroll, evento, pgto_titular, todos_meses
            )

            dias_receber_substituto = calcular_dias_servidor(
                record.substituto,
                "subs",
                payroll,
                evento,
                pgto_substituto,
                todos_meses,
                dias_receber_titular,
            )

            icons_titular = get_icons_servidor(record, "titular", pgto_titular)
            comarca_conferida = verifiar_comarca(record.comarca, record.servidor)
            if comarca_conferida is False:
                title = f"O Titular não está na mesma comarca que a Diligência."
                icons_titular.append(
                    {
                        "iconCls": "icon-fopag icon-status-away",
                        "title": title,
                        "alt": title,
                    }
                )

            icons_substituto = get_icons_servidor(record, "subs", pgto_substituto)
            if record.substituto:
                comarca_conferida = verifiar_comarca(record.comarca, record.substituto)
                if comarca_conferida is False:
                    title = f"O Substituto não está na mesma comarca que a Diligência."
                    icons_substituto.append(
                        {
                            "iconCls": "icon-fopag icon-status-away",
                            "title": title,
                            "alt": title,
                        }
                    )

            diligencia_conferida = "Não"
            icons_registro = get_icons_registro(
                record, evento, periodo_filtro.year, periodo_filtro.month
            )
            for icon_reg in icons_registro:
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Conferido":
                    diligencia_conferida = "Sim"

            titular_ativo = "Não"
            titular_pgto = "Não"
            titular_origem_pgto = "-"
            titular_conferencia_comarca = ""
            for icon_reg in icons_titular:
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Titular Ativo":
                    titular_ativo = "Sim"
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Pago":
                    titular_pgto = "Sim"
                if "alt" in icon_reg.keys() and "Origem pgto" in icon_reg["alt"]:
                    titular_origem_pgto = icon_reg["alt"]
                if (
                    "iconCls" in icon_reg.keys()
                    and "icon-status-away" in icon_reg["iconCls"]
                ):
                    titular_conferencia_comarca = icon_reg["title"]

            substituto_ativo = "Não"
            substituto_pgto = "Não"
            substituto_origem_pgto = "-"
            substituto_conferencia_comarca = ""
            for icon_reg in icons_titular:
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Substituto Ativo":
                    substituto_ativo = "Sim"
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Pago":
                    substituto_pgto = "Sim"
                if "alt" in icon_reg.keys() and "Origem pgto" in icon_reg["alt"]:
                    substituto_origem_pgto = icon_reg["alt"]
                if (
                    "iconCls" in icon_reg.keys()
                    and "icon-status-away" in icon_reg["iconCls"]
                ):
                    substituto_conferencia_comarca = icon_reg["title"]

            rst.append(
                {
                    "Diligência Conferida": diligencia_conferida,
                    "Comarca": record.comarca,
                    "Titular Matricula": record.servidor.matricula,
                    "Titular Nome": record.servidor.pessoa_fisica.nome,
                    "Titular Ativo?": titular_ativo,
                    "Titular - Conferência de Comarca": titular_conferencia_comarca,
                    "Titular - Pgto": titular_pgto,
                    "Titular - Origem Pgto": titular_origem_pgto,
                    "Titular - Dias a Receber": dias_receber_titular,
                    "Substituto Matrícula": (
                        record.substituto.matricula if record.substituto else ""
                    ),
                    "Substituto Nome": (
                        record.substituto.pessoa_fisica.nome
                        if record.substituto
                        else ""
                    ),
                    "Substituto Ativo?": substituto_ativo,
                    "Substituto - Conferência de Comarca": substituto_conferencia_comarca,
                    "Substituto - Pgto": substituto_pgto,
                    "Substituto - Origem Pgto": substituto_origem_pgto,
                    "Substituto - Dias a Receber": dias_receber_substituto,
                    "Data Início": record.data_inicio if record.data_inicio else "",
                    "Data Fim": record.data_fim if record.data_fim else "",
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class GMGratDiligencia(RestfulDRY):

    _model = GratDiligencia

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.diligence.gratificacao.Manage")'
        )

    def model_to_dict(self, instance):
        params = super(GMGratDiligencia, self).model_to_dict(instance)

        params.update({"periodo": f"{instance.ano}/{instance.mes}"})
        params.update({"titular": str(instance.mov_diligencia.servidor)})
        params.update({"substituto": str(instance.mov_diligencia.substituto)})

        return params
