import json
from datetime import datetime

from django.db.models import Q

from contrib.newrest import RestfulDRY
from contrib.decorator import login_required
from contrib.utils import get_json_engine, getLogger
from contrib.middleware import get_current_user
from contrib.daterange import NewDateRange

from engine.mq.models import Task
from standard.models import Choice
from rh.gfp.models import Evento
from rh.models import (
    ServidorLotacao,
    MovimentacaoAuxiliarCoordenacao,
    GratAuxiliarCoordenacao,
)

from rh.gratifications_manager.gm_utils import *
from rh.gfp.gcpp_utils import criar_gcpp

from rh.gratifications_manager.tasks_aux_coord import (
    calcular_movs_auxs_coords_task,
    deferir_movs_auxs_coords_task,
)

json_engine = get_json_engine()
log = getLogger(__name__)


class GMMovAuxCoordenationRestful(RestfulDRY):

    _model = MovimentacaoAuxiliarCoordenacao

    full_text_index = (
        "servidor_designacao__lotacao__nome__icontains",
        "substituto__pessoa_fisica__nome__icontains",
        "substituto__matricula__icontains",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.aux_coordenation.Manage")'
        )

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

            q_grat_aux_coord = GratAuxiliarCoordenacao.objects.filter(
                ano=periodo_ano,
                mes=periodo_mes,
            )

            if filtro == "avaliar":
                q_grat_aux_coord = q_grat_aux_coord.filter(
                    status__in=["DEFER", "INDEFER"],
                )
            elif filtro == "deferido":
                q_grat_aux_coord = q_grat_aux_coord.filter(
                    status__in=["AVAL", "INDEFER"],
                )
            elif filtro == "indeferido":
                q_grat_aux_coord = q_grat_aux_coord.filter(
                    status__in=["AVAL", "DEFER"],
                )

            excluir_auxs_coords_ids = [
                mov_aux_coord.mov_aux_coord.pk for mov_aux_coord in q_grat_aux_coord
            ]
            query = query.exclude(pk__in=excluir_auxs_coords_ids)

        return query

    def model_to_dict(self, instance):
        params = super(GMMovAuxCoordenationRestful, self).model_to_dict(instance)

        f = []
        if "filter" in self.request.GET:
            try:
                f = json.loads(self.request.GET.get("filter"))
            except Exception:
                f = []

        periodo_filtro = datetime.now().date()
        if f:
            periodo_filtro = datetime.strptime(f[0]["value"], "%Y-%m-%d").date()

        comarca_txt = "-"
        lotacao = None
        if instance.servidor_designacao and instance.servidor_designacao.lotacao:
            lotacao = instance.servidor_designacao.lotacao
            if lotacao.comarca:
                comarca_txt = lotacao.comarca.nome

        evento = self.buscar_evento_grat_coord(instance)
        q_grat_aux_coord = self.verificar_grat_aux_coord(
            instance, evento, periodo_filtro.year, periodo_filtro.month
        )

        icons_titular = self.get_icons_titular(instance, lotacao)
        icons_substituto = self.get_icons_substituto(instance, lotacao)

        status_grat_aux_coord = "NAO_CALCULADO"
        qtd_dias_consolidado_titular = "-"
        qtd_dias_deferido_titular = "-"
        qtd_dias_consolidado_substituto = "-"
        qtd_dias_deferido_substituto = "-"
        if q_grat_aux_coord.exists():
            grat_aux_coord = q_grat_aux_coord.first()

            status_grat_aux_coord = grat_aux_coord.status
            qtd_dias_consolidado_titular = grat_aux_coord.qtd_dias_consolidado_titular
            qtd_dias_consolidado_substituto = (
                grat_aux_coord.qtd_dias_consolidado_substituto
            )

            if grat_aux_coord.qtd_dias_deferido_titular is not None:
                qtd_dias_deferido_titular = grat_aux_coord.qtd_dias_deferido_titular

            if grat_aux_coord.qtd_dias_deferido_substituto is not None:
                qtd_dias_deferido_substituto = (
                    grat_aux_coord.qtd_dias_deferido_substituto
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
                "comarca": comarca_txt,
                "icons_aux_coord": self.get_icons_aux_coord(q_grat_aux_coord),
                "status_grat_aux_coord": status_grat_aux_coord,
                "periodo_ano": periodo_filtro.year,
                "periodo_mes": periodo_filtro.month,
                "grat_aux_coord_id": (
                    q_grat_aux_coord.first().pk if q_grat_aux_coord.exists() else None
                ),
            }
        )

        return params

    def verificar_grat_aux_coord(self, aux_coord, evento, periodo_ano, periodo_mes):
        return GratAuxiliarCoordenacao.objects.filter(
            mov_aux_coord=aux_coord,
            ano=periodo_ano,
            mes=periodo_mes,
            evento=evento,
        )

    def get_icons_aux_coord(self, grat_aux_coord):
        icons_aux_coord = []

        if grat_aux_coord.exists():
            if grat_aux_coord.first().status == "INDEFER":
                title_status = "Indeferido"
                icon_status = "icon-status-busy"
            elif grat_aux_coord.first().status == "DEFER":
                title_status = "Deferido"
                icon_status = "icon-status"
            elif grat_aux_coord.first().status == "AVAL":
                title_status = "Avaliar"
                icon_status = "icon-status-away"
        else:
            title_status = "Não Calculado"
            icon_status = "icon-status-offline"

        icons_aux_coord.append(
            {
                "iconCls": f"icon-fopag {icon_status}",
                "title": title_status,
                "alt": title_status,
            }
        )

        return icons_aux_coord

    def get_icons_titular(self, instance, lotacao):
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

        if lotacao is None:
            title = f"A Designação do Titular está sem Lotação."
            icons_titular.append(
                {
                    "iconCls": "icon-fopag icon-attention",
                    "title": title,
                    "alt": title,
                }
            )
        else:
            comarca_conferida = verifiar_comarca(lotacao.comarca, instance.servidor)
            if comarca_conferida is False:
                title = f"O Titular não está na mesma comarca que a Designação para Auxiliar de Coordenação."
                icons_titular.append(
                    {
                        "iconCls": "icon-fopag icon-attention",
                        "title": title,
                        "alt": title,
                    }
                )

            if (
                comarca_conferida is True
                and verifiar_lotacao(lotacao, instance.servidor) is False
            ):
                title = f"O Titular não tem Designação ativa na mesma Designação para Auxiliar de Coordenação."
                icons_titular.append(
                    {
                        "iconCls": "icon-fopag icon-attention",
                        "title": title,
                        "alt": title,
                    }
                )

        return icons_titular

    def get_icons_substituto(self, instance, lotacao):
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

        if lotacao and instance.substituto:
            comarca_conferida = verifiar_comarca(lotacao.comarca, instance.substituto)
            if comarca_conferida is False:
                title = f"O Substituto não está na mesma comarca que a Designação para Auxiliar de Coordenação."
                icons_substituto.append(
                    {
                        "iconCls": "icon-fopag icon-attention",
                        "title": title,
                        "alt": title,
                    }
                )

        return icons_substituto

    def buscar_evento_grat_coord(self, aux_coord):
        """
        Método responsável por buscar o evento verificando se a lotação é CAAD.
        """

        if "CAAD" in aux_coord.servidor_designacao.lotacao.nome:
            return Evento.objects.get(numero="12400")  # grat. função coord. 30% CAAD
        else:
            return Evento.objects.get(numero="11400")  # grat. função coord. 10%

    def calcular_aux_coord(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo_ano = self.request.POST.get("periodo_ano")
        periodo_mes = self.request.POST.get("periodo_mes")

        aux_coord = MovimentacaoAuxiliarCoordenacao.objects.get(
            pk=self.request.POST.get("aux_coord_id")
        )
        evento = self.buscar_evento_grat_coord(aux_coord)

        q_grat_aux_coord = self.verificar_grat_aux_coord(
            aux_coord, evento, periodo_ano, periodo_mes
        )
        if q_grat_aux_coord.exists():
            grat_aux_coord = q_grat_aux_coord.first()
            if grat_aux_coord.status == "DEFER":
                obj["success"] = False
                obj["message"] = "O registro selecionado já está DEFERIDO!"
            elif grat_aux_coord.status == "INDEFER":
                obj["success"] = False
                obj["message"] = "O registro selecionado está INDEFERIDO!"
        else:
            grat_aux_coord = GratAuxiliarCoordenacao(
                mov_aux_coord=aux_coord,
                ano=periodo_ano,
                mes=periodo_mes,
                evento=evento,
            )

        folha = buscar_folha(grat_aux_coord.ano, grat_aux_coord.mes)
        if folha.exists() is False:
            obj["success"] = False
            obj["message"] = (
                "Não é possível realizar o cálculo, não há folha vigente para o período selecionado."
            )
        else:
            res_titular = calc_from_period(
                grat_aux_coord.mov_aux_coord.servidor, folha.first(), evento
            )
            grat_aux_coord.qtd_dias_consolidado_titular = int(res_titular["qnt"])

            range_periodo = NewDateRange.range_from_month(
                int(grat_aux_coord.ano), int(grat_aux_coord.mes)
            )
            dt_range_periodo = NewDateRange(range_periodo[0], range_periodo[1])
            if grat_aux_coord.mov_aux_coord.substituto:
                res_substituto = calc_from_period(
                    grat_aux_coord.mov_aux_coord.substituto, folha.first(), evento
                )
                grat_aux_coord.qtd_dias_consolidado_substituto = int(
                    res_substituto["qnt"]
                )

            grat_aux_coord.status = "AVAL"
            grat_aux_coord.data_ultimo_calculo = datetime.today()
            grat_aux_coord.save()

            obj["message"] = "Registro de Auxílio Coordenação calculado com sucesso!"

        self.response.write(json_engine.encode(obj))

    def calcular_todos_aux_coord(self, *args):
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
                    calcular_movs_auxs_coords_task,
                    description=f"Processamento para calcular os registros de auxílio coordenação",
                    user=self.request.user.id,
                    periodo_ano=periodo_ano,
                    periodo_mes=periodo_mes,
                )

                obj[
                    "message"
                ] = """Iniciando processamento para calcular os registros de auxílio coordenação
                (somente os registros que não estiverem DEFERIDO ou INDEFERIDO)."""
            except:
                obj["success"] = False
                obj["message"] = "Erro no processamento para calcular os registros."

        self.response.write(json_engine.encode(obj))

    def deferir_aux_coord(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo_ano = self.request.POST.get("periodo_ano")
        periodo_mes = self.request.POST.get("periodo_mes")
        aux_coord = MovimentacaoAuxiliarCoordenacao.objects.get(
            pk=self.request.POST.get("aux_coord_id")
        )
        evento = self.buscar_evento_grat_coord(aux_coord)
        q_grat_aux_coord = self.verificar_grat_aux_coord(
            aux_coord, evento, periodo_ano, periodo_mes
        )

        if q_grat_aux_coord.exists() is False:
            obj["success"] = False
            obj["message"] = (
                "O registro precisa ser calculado antes de ser deferido ou indeferido."
            )
        elif q_grat_aux_coord.exists() and q_grat_aux_coord.first().status == "DEFER":
            obj["success"] = False
            obj["message"] = "O registro selecionado já está DEFERIDO!"
        else:
            grat_aux_coord = q_grat_aux_coord.first()

            gcpp_titular = buscar_registro_gcpp(
                grat_aux_coord.mov_aux_coord.servidor,
                grat_aux_coord.evento,
                grat_aux_coord.ano,
                grat_aux_coord.mes,
            )

            if aux_coord.substituto:
                gcpp_substituto = buscar_registro_gcpp(
                    grat_aux_coord.mov_aux_coord.substituto,
                    grat_aux_coord.evento,
                    grat_aux_coord.ano,
                    grat_aux_coord.mes,
                )

            if (gcpp_titular.exists() and gcpp_titular.first().status == "pago") or (
                aux_coord.substituto
                and gcpp_substituto.exists()
                and gcpp_substituto.first().status == "pago"
            ):
                obj["success"] = False
                obj["message"] = (
                    "O registro de gratificação selecionado já está deferido e pago no GCPP para o titular e/ou substituto."
                )
            elif (
                gcpp_titular.exists() and gcpp_titular.first().status == "inapto"
            ) or (
                aux_coord.substituto
                and gcpp_substituto.exists()
                and gcpp_substituto.first().status == "inapto"
            ):
                obj["message"] = (
                    f"O registro de gratificação selecionado já está deferido e está inapto para pagamento no GCPP para o titular e/ou substituto."
                )
            else:
                grat_aux_coord.status = "DEFER"
                if grat_aux_coord.qtd_dias_deferido_titular is None:
                    grat_aux_coord.qtd_dias_deferido_titular = (
                        grat_aux_coord.qtd_dias_consolidado_titular
                    )

                if (
                    aux_coord.substituto
                    and grat_aux_coord.qtd_dias_deferido_substituto is None
                ):
                    grat_aux_coord.qtd_dias_deferido_substituto = (
                        grat_aux_coord.qtd_dias_consolidado_substituto
                    )

                grat_aux_coord.save()

                if grat_aux_coord.qtd_dias_deferido_titular in [0, None]:
                    msg = f"Registro de gratificação do titular deferido. Como a quantidade de dias deferido é zero, não foi registrado no GCPP."
                else:
                    # registro gcpp está sendo criado no método save de GratAuxiliarCoordenacao
                    msg = f"Registro do titular deferido e registrado no GCPP."

                if aux_coord.substituto:
                    if grat_aux_coord.qtd_dias_deferido_substituto in [0, None]:
                        msg += f"Registro do substituto deferido. Como a quantidade de dias deferido é zero, não foi registrado no GCPP."
                    else:
                        # registro gcpp está sendo criado no método save de GratAuxiliarCoordenacao
                        msg += f"Registro do substituto deferido e registrado no GCPP."

                obj["message"] = msg

        self.response.write(json_engine.encode(obj))

    def deferir_todos_aux_coord(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo_ano = self.request.POST.get("periodo_ano")
        periodo_mes = self.request.POST.get("periodo_mes")

        try:
            Task.start(
                deferir_movs_auxs_coords_task,
                description=f"Processamento para deferir os registros de auxílio coordenação",
                user=self.request.user.id,
                periodo_ano=periodo_ano,
                periodo_mes=periodo_mes,
            )

            obj["message"] = (
                """Iniciando processamento para deferir os registros de auxílio coordenação"""
            )
        except:
            obj["success"] = False
            obj["message"] = "Erro no processamento para deferir os registros."

        self.response.write(json_engine.encode(obj))

    def indeferir_aux_coord(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo_ano = self.request.POST.get("periodo_ano")
        periodo_mes = self.request.POST.get("periodo_mes")

        aux_coord = MovimentacaoAuxiliarCoordenacao.objects.get(
            pk=self.request.POST.get("aux_coord_id")
        )
        evento = self.buscar_evento_grat_coord(aux_coord)
        q_grat_aux_coord = self.verificar_grat_aux_coord(
            aux_coord, evento, periodo_ano, periodo_mes
        )

        if q_grat_aux_coord.exists() is False:
            obj["success"] = False
            obj["message"] = (
                "O registro precisa ser calculado antes de ser deferido ou indeferido."
            )
        elif q_grat_aux_coord.exists() and q_grat_aux_coord.first().status == "DEFER":
            obj["success"] = False
            obj["message"] = "O registro selecionado está DEFERIDO!"
        elif q_grat_aux_coord.exists() and q_grat_aux_coord.first().status == "INDEFER":
            obj["success"] = False
            obj["message"] = "O registro selecionado já está INDEFERIDO!"
        else:
            grat_aux_coord = q_grat_aux_coord.first()
            grat_aux_coord.status = "INDEFER"
            grat_aux_coord.save()

            obj["message"] = "Registro selecionado indeferido com sucesso!"

        self.response.write(json_engine.encode(obj))

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
        # query = self.filtrar_conferencia(query)

        todos_meses = True
        periodo_filtro = datetime.now().date()

        if f:
            if next((item for item in f if item["stage"] == 2), None):
                todos_meses = False
            periodo_filtro = datetime.strptime(f[0]["value"], "%Y-%m-%d").date()

        rst = []
        for record in query:
            tag = ""
            comarca_txt = "-"
            lotacao = None
            evento = None
            if record.servidor_designacao and record.servidor_designacao.lotacao:
                lotacao = record.servidor_designacao.lotacao
                if lotacao.comarca:
                    comarca_txt = lotacao.comarca.nome
                tags = lotacao.workplace_config_tags.filter(
                    Q(tag__in=["2", "3", "4", "5", "12"]),
                    Q(start_validity__lte=periodo_filtro),
                    Q(end_validity__isnull=True) | Q(end_validity__gte=periodo_filtro),
                )
                if tags.exists():
                    tag = tags.first().tag
                    choice_q = Choice.objects.filter(
                        name="WORKPLACE_TAG", app_label="rh", value=tag
                    ).first()
                    evento = Evento.objects.get(numero=choice_q.description)

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

            icons_titular = self.get_icons_titular(record, lotacao)
            icons_substituto = self.get_icons_substituto(record, lotacao)

            titular_ativo = "Não"
            titular_pgto = "Não"
            titular_origem_pgto = "-"
            titular_conferencia_desig_comarca = ""
            for icon_reg in icons_titular:
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Titular Ativo":
                    titular_ativo = "Sim"
            #    if 'alt' in icon_reg.keys() and icon_reg['alt'] == 'Pago':
            #        titular_pgto = 'Sim'
            #    if 'alt' in icon_reg.keys() and 'Origem pgto' in icon_reg['alt']:
            #        titular_origem_pgto = icon_reg['alt']
            #    if 'iconCls' in icon_reg.keys() and ('icon-status-away' in icon_reg['iconCls'] or 'icon-status-busy' in icon_reg['iconCls']):
            #        titular_conferencia_desig_comarca = icon_reg['title']

            substituto_ativo = "Não"
            substituto_pgto = "Não"
            substituto_origem_pgto = "-"
            substituto_conferencia_comarca = ""
            for icon_reg in icons_substituto:
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Substituto Ativo":
                    substituto_ativo = "Sim"
            #    if 'alt' in icon_reg.keys() and icon_reg['alt'] == 'Pago':
            #        substituto_pgto = 'Sim'
            #    if 'alt' in icon_reg.keys() and 'Origem pgto' in icon_reg['alt']:
            #        substituto_origem_pgto = icon_reg['alt']
            #    if 'iconCls' in icon_reg.keys() and 'icon-status-away' in icon_reg['iconCls']:
            #        substituto_conferencia_comarca = icon_reg['title']

            rst.append(
                {
                    "Comarca": comarca_txt,
                    "Designação Titular": (
                        record.servidor_designacao
                        if record.servidor_designacao
                        else "-"
                    ),
                    "Titular Matricula": record.servidor.matricula,
                    "Titular Nome": record.servidor.pessoa_fisica.nome,
                    "Titular Ativo?": titular_ativo,
                    "Titular - Conferência de Designação/Comarca": titular_conferencia_desig_comarca,
                    "Titular - Pgto": titular_pgto,
                    "Titular - Origem Pgto": titular_origem_pgto,
                    "Titular - Dias a Receber": dias_receber_titular,
                    "Substituto Matricula": (
                        record.substituto.matricula if record.substituto else ""
                    ),
                    "Substituto Nome": (
                        record.substituto.pessoa_fisica.nome
                        if record.substituto
                        else ""
                    ),
                    "Substituto Ativo?": substituto_ativo,
                    "Subtituto - Conferência de Comarca": substituto_conferencia_comarca,
                    "Substituto - Pgto": substituto_pgto,
                    "Substituto - Origem Pgto": substituto_origem_pgto,
                    "Substituto - Dias a Receber": dias_receber_substituto,
                    "Data Início": record.data_inicio if record.data_inicio else "",
                    "Data Fim": record.data_fim if record.data_fim else "",
                    "Evento (%)": evento.titulo if evento else "-",
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class GMGratAuxCoordenacao(RestfulDRY):

    _model = GratAuxiliarCoordenacao

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.aux_coordenation.gratificacao.Manage")'
        )

    def model_to_dict(self, instance):
        params = super(GMGratAuxCoordenacao, self).model_to_dict(instance)

        params.update({"periodo": f"{instance.ano}/{instance.mes}"})
        params.update({"titular": str(instance.mov_aux_coord.servidor)})
        params.update({"substituto": str(instance.mov_aux_coord.substituto)})

        return params


class GMWorkAssignmentRestful(RestfulDRY):

    _model = ServidorLotacao

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__chefe_imediato__pessoa_fisica__nome__icontains",
        "servidor__pessoa_fisica__cpf__icontains",
        "servidor__pessoa_fisica__rg__icontains",
        "servidor__matricula__icontains",
        "servidor__matricula_origem__icontains",
        "servidor__numero_cartao_ponto__icontains",
        "servidor__tipo__icontains",
        "lotacao__nome__icontains",
        "lotacao__sigla__icontains",
        "lotacao__responsavel__pessoa_fisica__nome__icontains",
    )

    exclude_fields = ["auditablemixins_ptr", "audittimestampmodel_ptr"]

    force_persist_boolean_fields = ["ativo", "designacao", "provisorio"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.aux_coordenation.workassignment.Manage")'
        )

    def get_query(self):
        return super(GMWorkAssignmentRestful, self).get_query()

    def model_to_dict(self, instance):
        params = super(GMWorkAssignmentRestful, self).model_to_dict(instance)
        params.update(
            {
                "created_by_departure_unicode": (
                    instance.created_by_departure.__str_restful__()
                    if instance.created_by_departure
                    else ""
                )
            }
        )
        params.update(
            {
                "changed_by_departure_unicode": (
                    instance.changed_by_departure.__str_restful__()
                    if instance.changed_by_departure
                    else ""
                )
            }
        )
        params.update(
            {
                "chefe_imediato_unicode": (
                    str(instance.servidor.chefe_imediato)
                    if instance.servidor.chefe_imediato
                    else ""
                )
            }
        )
        params.update(
            {
                "chefe_lotacao_unicode": (
                    str(instance.lotacao.responsavel)
                    if instance.lotacao and instance.lotacao.responsavel
                    else ""
                )
            }
        )
        params.update(
            {
                "quadro_unicode": (
                    str(instance.movimentacao_posse.description_possession)
                    if instance.movimentacao_posse
                    else ""
                )
            }
        )
        owner = instance.lotacao.owner.first() or "" if instance.lotacao else ""
        params.update({"owner_employee_unicode": str(owner)})

        type_by_possession = instance.servidor.type_by_possession
        params.update({"type_by_possession": str(type_by_possession)})

        situation_icons = {
            True: "icon-core-success",
            False: "icon-core-delete",
        }

        obj = []
        icon_situation = {
            "iconCls": "icon-core %s" % situation_icons.get(instance.ativo),
            "title": "Ativo" if instance.ativo else "Encerrado",
        }
        icon_main = {
            "iconCls": (
                "icon-core %s" % "icon-core-document-arrow"
                if instance.main
                else "icon-core-blank"
            ),
            "title": "Principal" if instance.main else "",
        }
        icon_responsible = {
            "iconCls": (
                "icon-core %s" % "icon-core-add-selected"
                if instance.responsible
                else "icon-core-blank"
            ),
            "title": "Responsável" if instance.responsible else "Não é Responsável",
        }
        icon_owner = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-admin"
                if instance.owner
                else "icon-core-blank"
            ),
            "title": "Titular" if instance.owner else "Não é titular",
        }

        with_prejudice = False
        without_prejudice = False
        action_collaborating = False
        action_helping = False
        action_adjunct = False

        if instance.prejudice == 1:
            with_prejudice = True
        elif instance.prejudice == 2:
            without_prejudice = True

        if instance.action == 1:
            action_helping = True
        elif instance.action == 2:
            action_collaborating = True
        elif instance.action == 3:
            action_adjunct = True

        icon_with_prejudice = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-minus"
                if with_prejudice
                else "icon-core-blank"
            ),
            "title": "Com prejuizo" if with_prejudice else "",
        }
        icon_without_prejudice = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-update-manage"
                if without_prejudice
                else "icon-core-blank"
            ),
            "title": "Sem prejuizo" if without_prejudice else "",
        }
        icon_action_collaborating = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-set-employee"
                if action_collaborating
                else "icon-core-blank"
            ),
            "title": "Colaborando" if action_collaborating else "",
        }
        icon_action_helping = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-users"
                if action_helping
                else "icon-core-blank"
            ),
            "title": "Coadjuvando" if action_helping else "",
        }
        icon_action_adjunct = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-balloons"
                if action_adjunct
                else "icon-core-blank"
            ),
            "title": "Adjunto" if action_adjunct else "",
        }

        obj.append(icon_situation)
        obj.append(icon_main)
        obj.append(icon_responsible)
        obj.append(icon_owner)
        obj.append(icon_with_prejudice)
        obj.append(icon_without_prejudice)
        obj.append(icon_action_collaborating)
        obj.append(icon_action_helping)
        obj.append(icon_action_adjunct)

        params.update({"icons": obj})
        return params
