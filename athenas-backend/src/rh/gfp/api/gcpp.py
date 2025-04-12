import json
from datetime import datetime
from django.db.models import Count, Q

from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger
from contrib.decorator import login_required

from engine.mq.models import Task
from standard.models import Choice, Item
from rh.models import ControlePagamentoPessoal
from rh.gfp.models import Folha

from rh.gfp.api.payroll import GFPPayroll
from rh.gfp.gcpp_utils import (
    calcular_e_salvar_gcpp,
    confirmar_e_salvar_gcpp,
    declinar_e_salvar_gcpp,
    aplicar_e_salvar_gcpp,
    valida_tipo_folha,
)
from rh.gfp.tasks_gcpp import (
    calcular_gcpps_task,
    confirmar_gcpps_task,
    declinar_gcpps_task,
    aplicar_pgto_task,
)


json_engine = get_json_engine()
log = getLogger(__name__)


class GfpGCPPRestful(RestfulDRY):

    _model = ControlePagamentoPessoal

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
        "evento__numero__icontains",
        "evento__titulo__icontains",
    )

    def get_query(self):
        query = super(GfpGCPPRestful, self).get_query()
        return query.exclude(servidor__type_by_possession__in=["EST", "RES"])

    def json(self, args=[]):
        eventos = (
            ControlePagamentoPessoal.objects.values(
                "evento__numero", "evento__titulo", "evento__tipo"
            )
            .annotate(total=Count("evento"))
            .order_by("evento")
        ).exclude(
            evento__numero__in=[
                "15600",
                "15602",
                "15700",
                "15702",
                "15800",
                "15802",
                "15900",
                "15902",
            ]
        )
        verbas = {
            "verbas": [
                {
                    "numero": e["evento__numero"],
                    "titulo": f"{e['evento__numero']} | {e['evento__titulo']}",
                    "tipo": e["evento__tipo"],
                }
                for e in eventos
            ]
        }
        self.response["content-type"] = "text/javascript"
        self.response.write(f"Ext._create('rh.gfp.gcpp.Manage', {verbas})")

    def model_to_dict(self, instance):
        params = super(GfpGCPPRestful, self).model_to_dict(instance)

        valor_calc = (
            "" if instance.valor_calculado is None else str(instance.valor_calculado)
        )
        valor_pgto = "" if instance.valor_pgto is None else str(instance.valor_pgto)

        if instance.faltas.exists():
            mes = (
                Choice.objects.filter(
                    name="MONTHS",
                    app_label="rh",
                    value=instance.faltas.first().data.month,
                )
                .first()
                .label
            )
            ref_falta = f"{instance.faltas.first().data.year} - {mes.title()}"
        else:
            ref_falta = "-"

        params.update(
            {
                "icons": self.get_icons(instance),
                "verba": f"{instance.evento.numero} | {instance.evento.titulo}",
                "valor_calculado": valor_calc,
                "valor_pgto": valor_pgto,
                "periodo": self.get_periodo(instance),
                "conferido_em": instance.conferido_em.strftime("%d/%m/%Y"),
                "conferido_por": f"{instance.conferido_por}",
                "ref_falta": ref_falta,
            }
        )

        return params

    def get_icons(self, instance):
        obj = []
        if instance.status == "analise":
            title = "Em Análise"
            icon = "icon-status-away"
        elif instance.status == "calculado":
            title = "Calculado"
            icon = "icon-status-offline"
        elif instance.status == "apto":
            title = "Apto para Pgto"
            icon = "icon-status"
        elif instance.status == "inapto":
            title = "Inapto para Pgto"
            icon = "icon-status-busy"
        elif instance.status == "pago":
            title = "Pago"
            icon = "icon-cash"

        if instance.evento.tipo == "D":
            icone_tipo = "icon-core icon-core-minus"
            titulo_tipo = "Desconto"
        else:
            icone_tipo = "icon-core icon-core-add"
            titulo_tipo = "Provento"

        icone_status = {
            "iconCls": f"icon-fopag {icon}",
            "title": title,
            "alt": title,
        }

        icone_tipo_verba = {
            "iconCls": icone_tipo,
            "title": titulo_tipo,
            "alt": titulo_tipo,
        }

        obj.append(icone_status)
        obj.append(icone_tipo_verba)

        return obj

    def get_periodo(self, instance):
        mes = (
            Choice.objects.filter(
                name="MONTHS", app_label="rh", value=instance.periodo_mes
            )
            .first()
            .label
        )

        return f"{instance.periodo_ano} - {mes.title()}"

    def query_todos(self, **kwargs):
        q = ControlePagamentoPessoal.objects.filter()

        if kwargs.get("filtro_ano") != "TODOS":
            q = q.filter(periodo_ano=kwargs.get("filtro_ano"))

        if kwargs.get("filtro_mes") != "0":
            q = q.filter(periodo_mes=kwargs.get("filtro_mes"))

        if kwargs.get("somente_calculado", False) is True:
            q = q.filter(valor_calculado__isnull=False)

        if kwargs.get("somente_confirmado", False) is True:
            q = q.filter(valor_pgto__isnull=False)

        if kwargs.get("filtro_txt", False) not in ["", None]:
            q = q.filter(
                Q(servidor__matricula__icontains=kwargs.get("filtro_txt"))
                | Q(servidor__pessoa_fisica__nome__icontains=kwargs.get("filtro_txt"))
                | Q(evento__numero__icontains=kwargs.get("filtro_txt"))
            )

        filtro_status = kwargs.get("filtro_status")
        if "" not in filtro_status:
            q = q.filter(status__in=filtro_status)

        filtro_verba = kwargs.get("filtro_verba")
        if "" not in filtro_verba:
            q = q.filter(evento__numero__in=filtro_verba)

        if self.__class__.__name__ == "GfpGCPPEstResRestful":
            q = q.filter(servidor__type_by_possession__in=["EST", "RES"])
        else:
            q = q.exclude(servidor__type_by_possession__in=["EST", "RES"])

        return q

    def calcular_gcpp(self, *args):
        success = True
        message = ""

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = (
                "Você não tem permissão para alterar %s." % self.Model._meta.object_name
            )
        else:
            gcpp_ids = self.request.POST.getlist("gcpp_ids")

            filtro_ano = self.request.POST.get("filtro_ano")
            filtro_mes = self.request.POST.get("filtro_mes")
            filtro_txt = self.request.POST.get("filtro_txt")
            filtro_status = self.request.POST.getlist("filtro_status")
            filtro_verba = self.request.POST.getlist("filtro_verba")

            folha = Folha.objects.filter(
                tipo_folha__titulo="NORMAL",
                periodo__ano=filtro_ano,
                periodo__mes=filtro_mes,
            )

            if folha.exists() is False:
                success = False
                message = "Não é possível realizar o cálculo. Não existe Folha do tipo 'NORMAL' no período selecionado."
            else:
                gcpps = []
                if gcpp_ids[0] == "todos":
                    q_gcpps = self.query_todos(
                        filtro_ano=filtro_ano,
                        filtro_mes=filtro_mes,
                        filtro_txt=filtro_txt,
                        filtro_status=filtro_status,
                        filtro_verba=filtro_verba,
                    )
                else:
                    q_gcpps = ControlePagamentoPessoal.objects.filter(pk__in=gcpp_ids)

                for gcpp in q_gcpps:
                    if gcpp.status == "pago":
                        if q_gcpps.count() == 1:
                            success = False
                        message = "O registro escolhido já está pago."
                    elif gcpp.status == "inapto":
                        if q_gcpps.count() == 1:
                            success = False
                        message = "O registro escolhido está inapto para pagamento."
                    else:
                        gcpps.append(gcpp)

                if len(gcpps) > 0:
                    if len(gcpps) == 1:
                        calcular_e_salvar_gcpp(gcpps[0])
                    else:
                        try:
                            Task.start(
                                calcular_gcpps_task,
                                description="Calculando registros de Pagamento de Pessoal.",
                                user=self.request.user.id,
                                gcpp_ids=[gcpp.pk for gcpp in gcpps],
                            )

                            message = "Iniciando cálculo de Pagamento de Pessoal."
                        except:
                            success = False
                            message = "ERRO ao calcular Pagamento de Pessoal."

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))

    def confirmar_gcpp(self, *args):
        success = True
        message = ""

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = (
                "Você não tem permissão para alterar %s." % self.Model._meta.object_name
            )
        else:

            gcpp_ids = self.request.POST.getlist("gcpp_ids")

            gcpps = []
            if gcpp_ids[0] == "todos":
                q_gcpps = self.query_todos(
                    filtro_ano=self.request.POST.get("filtro_ano"),
                    filtro_mes=self.request.POST.get("filtro_mes"),
                    filtro_txt=self.request.POST.get("filtro_txt"),
                    filtro_status=self.request.POST.getlist("filtro_status"),
                    filtro_verba=self.request.POST.getlist("filtro_verba"),
                    somente_calculado=True,
                )
            else:
                q_gcpps = ControlePagamentoPessoal.objects.filter(pk__in=gcpp_ids)

            for gcpp in q_gcpps:
                if gcpp.status == "pago":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido já está pago.
                    """
                elif gcpp.status == "inapto":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido está inapto para pagamento.
                    """
                elif gcpp.status == "apto":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido já está apto (confirmado) para pagamento.
                    """
                elif gcpp.status != "calculado":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido ainda não foi calculado.
                    """
                else:
                    gcpps.append(gcpp)

            if gcpps:
                if len(gcpps) == 1:
                    confirmar_e_salvar_gcpp(gcpps[0])
                else:
                    try:
                        Task.start(
                            confirmar_gcpps_task,
                            description=f"Confirmando registros de Pagamento de Pessoal.",
                            user=self.request.user.id,
                            gcpp_ids=[gcpp.pk for gcpp in gcpps],
                        )

                        message = f"Iniciando confirmação de Pagamento de Pessoal."
                    except:
                        success = False
                        message = f"ERRO ao confirmar Pagamento de Pessoal."

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))

    def declinar_gcpp(self, *args):
        success = True
        message = ""

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = (
                "Você não tem permissão para alterar %s." % self.Model._meta.object_name
            )
        else:

            gcpp_ids = self.request.POST.getlist("gcpp_ids")

            gcpps = []
            if gcpp_ids[0] == "todos":
                q_gcpps = self.query_todos(
                    filtro_ano=self.request.POST.get("filtro_ano"),
                    filtro_mes=self.request.POST.get("filtro_mes"),
                    filtro_txt=self.request.POST.get("filtro_txt"),
                    filtro_status=self.request.POST.getlist("filtro_status"),
                    filtro_verba=self.request.POST.getlist("filtro_verba"),
                )
            else:
                q_gcpps = ControlePagamentoPessoal.objects.filter(pk__in=gcpp_ids)

            for gcpp in q_gcpps:
                if gcpp.status == "pago":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido já está pago.
                    """
                elif gcpp.status == "inapto":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido já está inapto para pagamento.
                    """
                else:
                    gcpps.append(gcpp)

            if gcpps:
                if len(gcpps) == 1:
                    declinar_e_salvar_gcpp(gcpp)
                else:
                    try:
                        Task.start(
                            declinar_gcpps_task,
                            description=f"Declinando registros de Pagamento de Pessoal.",
                            user=self.request.user.id,
                            gcpp_ids=[gcpp.pk for gcpp in gcpps],
                        )

                        message = f"Iniciando declinação de Pagamento de Pessoal."
                    except:
                        success = False
                        message = f"ERRO ao declinar Pagamento de Pessoal."

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))

    def aplicar_pgto_gcpp(self, *args):
        success = True
        message = ""

        gcpp_ids = self.request.POST.getlist("gcpp_ids")
        gcpps = []

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = (
                "Você não tem permissão para alterar %s." % self.Model._meta.object_name
            )
        else:

            if gcpp_ids[0] == "todos":
                q_gcpps = self.query_todos(
                    filtro_ano=self.request.POST.get("filtro_ano"),
                    filtro_mes=self.request.POST.get("filtro_mes"),
                    filtro_txt=self.request.POST.get("filtro_txt"),
                    filtro_status=self.request.POST.getlist("filtro_status"),
                    filtro_verba=self.request.POST.getlist("filtro_verba"),
                    somente_confirmado=True,
                )
            else:
                q_gcpps = ControlePagamentoPessoal.objects.filter(pk__in=gcpp_ids)

            for gcpp in q_gcpps:
                if gcpp.status == "pago":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido já está pago.
                    """
                elif gcpp.status == "inapto":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido está inapto para pagamento.
                    """
                elif gcpp.status != "apto" and gcpp.status != "calculado":
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido ainda não foi calculado.
                    É necessário primeiro realizar o cálculo e confirmar, para depois poder aplicar o pagamento.
                    """
                elif gcpp.status != "apto" and gcpp.valor_pgto in [None, 0]:
                    if q_gcpps.count() == 1:
                        success = False
                    message = f"""
                    O registro escolhido está calculado mas ainda não foi confirmado.
                    É necessário realizar a confirmação, para depois poder aplicar o pagamento.
                    """
                else:
                    gcpps.append(gcpp)

        rst = {
            "success": success,
            "message": message,
            "aplicar_gcpp_ids": [gcpp.pk for gcpp in gcpps] if gcpps else "",
        }
        self.response.write(json_engine.encode(rst))

    def export(self, args=[]):
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = []
        for record in query:
            rst.append(
                {
                    "matricula": record.servidor.matricula,
                    "servidor": record.servidor.pessoa_fisica.social_name,
                    "verba": f"{record.evento.numero} {record.evento.titulo}",
                    "qtd_dias_confirmado": record.qtd_dias_confirmado or "",
                    "qtd_dias_calculado": record.qtd_dias_calculado or "",
                    "valor_calculado": record.valor_calculado or "",
                    "qtd_dia_ptgo": record.qtd_dias_pgto or "",
                    "valor_ptgo": record.valor_pgto or "",
                    "porcentagem_deferida": round((record.pct or 0.00), 2),
                    "periodo_ref": f"{record.periodo_ano} - {record.get_periodo_mes_display()}",
                    "dt_conferencia": record.conferido_em.strftime("%d/%m/%Y"),
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class GfpGCPPPayrollRestfull(GFPPayroll):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.gcpp.payroll.Manage")')

    def get_query(self):
        query = super(GfpGCPPPayrollRestfull, self).get_query()
        return query.filter(status__in=[1, 2])

    def do_put(self, pk=None):
        success = True
        message = ""

        aplicar_gcpp_ids = self.request.PUT.getlist("aplicar_gcpp_ids")
        folha_id = self.request.PUT.get("folha")

        if len(aplicar_gcpp_ids) > 0:
            query = ControlePagamentoPessoal.objects.filter(id__in=aplicar_gcpp_ids)
            folha = Folha.objects.get(pk=folha_id)

            if len(aplicar_gcpp_ids) == 1:
                gcpp = query.first()
                if valida_tipo_folha(gcpp, folha):
                    raise Exception(
                        f"Não é permitido aplicar o Registro: {gcpp.servidor} - {gcpp.servidor.type_by_possession} para a Folha: {folha.tipo_folha}!"
                    )

                res_aplicar_gcpp = aplicar_e_salvar_gcpp(aplicar_gcpp_ids[0], folha_id)
                success = res_aplicar_gcpp["success"]
                message = res_aplicar_gcpp["message"]
            else:
                for gcpp_id in aplicar_gcpp_ids:
                    gcpp = ControlePagamentoPessoal.objects.get(id=gcpp_id)
                    if not valida_tipo_folha(gcpp, folha):
                        Task.start(
                            aplicar_pgto_task,
                            description=f"Aplicando em folha registro de Controle de Pagamento.",
                            user=self.request.user.id,
                            gcpp_id=gcpp_id,
                            folha_id=folha_id,
                        )
                        message = "Iniciando aplicação em folha de registro de Controle de Pagamento."

        rst = {
            "success": success,
            "message": message,
        }
        return rst


class GfpGCPPEstResRestful(GfpGCPPRestful):
    """
    Tela com estrutura do GCPP para moderação de Desconto de Faltas de estagiários e residentes ['EST', 'RES']
    """

    _model = ControlePagamentoPessoal

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
        "evento__numero__icontains",
        "evento__titulo__icontains",
    )

    def get_query(self):
        query = super(GfpGCPPRestful, self).get_query()
        return query.filter(servidor__type_by_possession__in=["EST", "RES"])

    def json(self, args=[]):
        eventos = (
            ControlePagamentoPessoal.objects.filter(
                servidor__type_by_possession__in=["EST", "RES"]
            )
            .values("evento__numero", "evento__titulo")
            .annotate(total=Count("evento"))
            .order_by("evento")
        )
        verbas = {
            "verbas": [
                {
                    "numero": e["evento__numero"],
                    "titulo": f"{e['evento__numero']} | {e['evento__titulo']}",
                }
                for e in eventos
            ]
        }
        self.response["content-type"] = "text/javascript"
        self.response.write(f"Ext._create('rh.gfp.gcpp_est_res.Manage', {verbas})")

    def calcular_gcpp(self, *args):
        success = True
        message = ""

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = (
                "Você não tem permissão para alterar %s." % self.Model._meta.object_name
            )
        else:
            gcpp_ids = self.request.POST.getlist("gcpp_ids")

            filtro_ano = self.request.POST.get("filtro_ano")
            filtro_mes = self.request.POST.get("filtro_mes")
            filtro_txt = self.request.POST.get("filtro_txt")
            filtro_status = self.request.POST.getlist("filtro_status")
            filtro_verba = self.request.POST.getlist("filtro_verba")

            gcpps = []
            if gcpp_ids[0] == "todos":
                q_gcpps = self.query_todos(
                    filtro_ano=filtro_ano,
                    filtro_mes=filtro_mes,
                    filtro_txt=filtro_txt,
                    filtro_status=filtro_status,
                    filtro_verba=filtro_verba,
                )
            else:
                q_gcpps = ControlePagamentoPessoal.objects.filter(pk__in=gcpp_ids)

            folha_est = Folha.objects.filter(
                tipo_folha__titulo="ESTAGIÁRIOS",
                periodo__ano=filtro_ano,
                periodo__mes=filtro_mes,
            )
            folha_res = Folha.objects.filter(
                tipo_folha__titulo="RESIDENTES",
                periodo__ano=filtro_ano,
                periodo__mes=filtro_mes,
            )
            if (
                q_gcpps.filter(servidor__type_by_possession="EST").exists()
                and folha_est.exists() is False
            ) or (
                q_gcpps.filter(servidor__type_by_possession="RES").exists()
                and folha_res.exists() is False
            ):
                success = False
                message = "Não é possível realizar o cálculo. Não existe Folha do tipo 'ESTAGIÁRIOS' ou 'RESIDENTES' no período selecionado."
            else:
                for gcpp in q_gcpps:
                    if gcpp.status == "pago":
                        if q_gcpps.count() == 1:
                            success = False
                        message = "O registro escolhido já está pago."
                    elif gcpp.status == "inapto":
                        if q_gcpps.count() == 1:
                            success = False
                        message = "O registro escolhido está inapto para pagamento."
                    else:
                        gcpps.append(gcpp)

                if len(gcpps) > 0:
                    if len(gcpps) == 1:
                        calcular_e_salvar_gcpp(
                            gcpps[0],
                            titulo_folha=(
                                "ESTAGIÁRIOS"
                                if gcpps[0].servidor.type_by_possession == "EST"
                                else "RESIDENTES"
                            ),
                        )
                    else:
                        try:
                            Task.start(
                                calcular_gcpps_task,
                                description="Calculando registros de Pagamento de Pessoal.",
                                user=self.request.user.id,
                                gcpp_ids=[gcpp.pk for gcpp in gcpps],
                            )

                            message = "Iniciando cálculo de Pagamento de Pessoal."
                        except:
                            success = False
                            message = "ERRO ao calcular Pagamento de Pessoal."

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))
