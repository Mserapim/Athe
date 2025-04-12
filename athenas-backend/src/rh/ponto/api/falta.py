# -*- coding: utf-8 -*-

import json
from datetime import datetime

from django.http import QueryDict
from django.core.exceptions import ValidationError
from django import forms as django_forms
from django.db.models import Q

from contrib import extjs
from contrib.newrest import RestfulDRY
from contrib.nil import nil_datetime, nil_pk, nil_unicode
from contrib.utils import DateUtils, get_json_engine, getLogger
from contrib.decorator import login_required

from rh.models import Servidor, MovimentacaoTeletrabalho, MovimentacaoPosse
from rh.ponto.models import Falta, RemocaoFalta
from rh.pvf.models import SendingTimeSheet
from standard.models import Choice, JustificationItem
from engine.mq.models import Task

from rh.ponto.tasks_falta import processar_faltas_task, atribuir_comp_desc_task
from rh.ponto.utils import get_start_end_date, atribuir_por_falta, processar_por_falta

json_engine = get_json_engine()
log = getLogger(__name__)


class PONTFalta(RestfulDRY):

    _model = Falta

    DIAS_SEMANA = (
        "Segunda-feira",
        "Terça-feira",
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
        "Sábado",
        "Domingo",
    )

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.falta.Manage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        motivo = "Injustificado"
        if instance.point_justification.exists():
            motivo = JustificationItem.objects.get(
                value=instance.point_justification.last().reason_type
            ).name

        rst.update(
            icons=self.get_icons(instance),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            observacao=instance.observacao,
            servidor=nil_pk(instance.servidor, None),
            servidor_unicode=str(instance.servidor) or None,
            data_inicio_unicode="%s - %s "
            % (
                DateUtils.date_to_str(instance.data),
                self.DIAS_SEMANA[instance.data.weekday()],
            ),
            data_fim_unicode="%s - %s "
            % (
                DateUtils.date_to_str(instance.data_fim) if instance.data_fim else "",
                (
                    self.DIAS_SEMANA[instance.data_fim.weekday()]
                    if instance.data_fim
                    else ""
                ),
            ),
            motivo=motivo,
            origem=instance.get_origem_display(),
            situacao=instance.get_situacao_display(),
            days=instance.get_days,
            data_remocao=(
                DateUtils.date_to_str(instance.remocao_falta.first().data_remocao)
                if instance.remocao_falta.exists()
                else ""
            ),
            anotacao_falta=instance.get_anotacao_falta,
        )

        return rst

    def get_icons(self, instance):
        if instance.pag_pessoal_faltas.exists():
            if instance.pag_pessoal_faltas.first().status == "analise":
                title = "Em Análise"
                icon = "icon-status-away"
            elif instance.pag_pessoal_faltas.first().status == "apto":
                title = "Apto para Pgto"
                icon = "icon-status"
            elif instance.pag_pessoal_faltas.first().status == "inapto":
                title = "Inapto para Pgto"
                icon = "icon-status-busy"
            elif instance.pag_pessoal_faltas.first().status == "pago":
                title = "Pago"
                icon = "icon-cash"
            elif instance.pag_pessoal_faltas.first().status == "calculado":
                title = "Calculado"
                icon = "icon-status-offline"
        else:
            return {
                "iconCls": "",
                "title": "",
                "alt": "",
            }

        return {
            "iconCls": f"icon-fopag {icon}",
            "title": title,
            "alt": title,
        }

    def queryTodos(self, **kwargs):
        q = Falta.objects.filter()

        if kwargs.get("filtro_ano") != "TODOS" and kwargs.get("filtro_mes") != "0":
            q = q.filter(
                Q(
                    Q(data__lte=kwargs.get("data_fim"))
                    & Q(
                        Q(data_fim__gte=kwargs.get("data_inicio"))
                        | Q(data_fim__isnull=True)
                    )
                )
            )

        if kwargs.get("filtro_txt", False) not in ["", None]:
            q = q.filter(
                Q(servidor__matricula__icontains=kwargs.get("filtro_txt"))
                | Q(servidor__pessoa_fisica__nome__icontains=kwargs.get("filtro_txt"))
                | Q(evento__numero__icontains=kwargs.get("filtro_txt"))
            )

        situacoes = kwargs.get("filtro_situacao")
        if situacoes != [""]:
            filtro_situacao = self.get_lista_true_false(situacoes)
            q = q.filter(servidor__ativo__in=filtro_situacao)

        filtro_tipo = kwargs.get("filtro_tipo")
        if filtro_tipo != [""]:
            q = q.filter(servidor__type_by_possession__in=filtro_tipo)

        tipo_falta = (kwargs.get("filtro_tipo_falta"),)
        if tipo_falta != [""]:
            filtro_tipo_falta = self.get_lista_true_false(list(tipo_falta)[0])
            q = q.filter(justificado__in=filtro_tipo_falta)

        filtro_situacao_falta = (kwargs.get("filtro_situacao_falta"),)
        if filtro_situacao_falta != [""]:
            q = q.filter(situacao__in=list(filtro_situacao_falta)[0])

        impacto_financeiro = (kwargs.get("filtro_impacto_financeiro"),)
        if impacto_financeiro != [""]:
            filtro_impacto_financeiro = self.get_lista_true_false(
                list(impacto_financeiro)[0]
            )
            q = q.filter(payroll__in=filtro_impacto_financeiro)

        query = Servidor.objects.filter(falta__in=q).distinct()

        return query

    def get_lista_true_false(self, items):
        lista = []
        for item in items:
            if item == "true":
                lista.append(True)
            if item == "false":
                lista.append(False)
        return lista

    @login_required("JSON")
    def processar_faltas(self, *args):
        success = True
        message = "Nada foi feito ainda."

        if "falta_ids" in self.request.POST:
            # Realiza o processamento para as Faltas selecionadas
            falta_ids_request = self.request.POST.getlist("falta_ids")
            query = Falta.objects.filter(situacao=1).exclude(
                Q(payroll=True)
                & Q(Q(competencia_desconto__isnull=True) | Q(competencia_desconto=""))
            )
            if falta_ids_request[0] == "todos":
                # Processa todas as Faltas da grid (de acordo com as regras dos filtros abaixo)
                servidor_ids = self.request.POST.getlist("servidor_ids")
                filtro_situacao_falta = self.request.POST.getlist(
                    "filtro_situacao_falta"
                )
                query = query.filter(servidor__pk__in=servidor_ids)
            else:
                query = query.filter(pk__in=falta_ids_request)

            falta_ids = query.values_list("id", flat=True)
            success, message = processar_por_falta(falta_ids, self.request.user.id)
        else:
            # Realiza o processamento para as Faltas dos Servidores selecionados
            (
                servidor_ids,
                filtro_ano,
                filtro_mes,
                filtro_txt,
                filtro_situacao,
                filtro_tipo,
                filtro_tipo_falta,
                filtro_situacao_falta,
                filtro_impacto_financeiro,
            ) = self.get_post_params()

            reference = f"{filtro_mes}/{filtro_ano}"
            data_inicio, data_fim = get_start_end_date(reference)

            if servidor_ids[0] == "todos":
                q_servidores = self.queryTodos(
                    filtro_ano=filtro_ano,
                    filtro_mes=filtro_mes,
                    filtro_txt=filtro_txt,
                    filtro_situacao=filtro_situacao,
                    filtro_tipo=filtro_tipo,
                    filtro_tipo_falta=filtro_tipo_falta,
                    filtro_situacao_falta=filtro_situacao_falta,
                    filtro_impacto_financeiro=filtro_impacto_financeiro,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )
            else:
                q_servidores = Servidor.objects.filter(pk__in=servidor_ids)

            try:
                Task.start(
                    processar_faltas_task,
                    description=f"Processar Faltas - Competência {reference}",
                    user=self.request.user.id,
                    employee_id=[servidor.pk for servidor in q_servidores],
                    reference=reference,
                )

                message = "Iniciando Processamento de Faltas!"
            except:
                success = False
                message = "ERRO ao Processar Faltas!"

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))

    @login_required("JSON")
    def atribuir_comp_desc(self, *args):
        success = True
        message = "Nada foi feito ainda."

        competencia_desconto = self.request.POST.getlist("competencia_desconto")[0]
        if "falta_ids" in self.request.POST:
            # Atribui Competência para as Faltas selecionadas na grid
            falta_ids = self.request.POST.getlist("falta_ids")
            if falta_ids[0] == "todos":
                # Atribui Competência para todas as Faltas da grid
                servidor_ids = self.request.POST.getlist("servidor_ids")
                filtro_situacao_falta = self.request.POST.getlist(
                    "filtro_situacao_falta"
                )
                query = Falta.objects.filter(servidor__pk__in=servidor_ids)

                if filtro_situacao_falta != [""]:
                    query.filter(situacao__in=list(filtro_situacao_falta))
                falta_ids = query.values_list("id", flat=True)

            success, message = atribuir_por_falta(
                falta_ids, self.request.user.id, competencia_desconto
            )
        else:
            # Atribui Competência para as Faltas dos Servidores selecionados
            (
                servidor_ids,
                filtro_ano,
                filtro_mes,
                filtro_txt,
                filtro_situacao,
                filtro_tipo,
                filtro_tipo_falta,
                filtro_situacao_falta,
                filtro_impacto_financeiro,
            ) = self.get_post_params()

            reference = f"{filtro_mes}/{filtro_ano}"
            data_inicio, data_fim = get_start_end_date(reference)

            if servidor_ids[0] == "todos":
                q_servidores = self.queryTodos(
                    filtro_ano=filtro_ano,
                    filtro_mes=filtro_mes,
                    filtro_txt=filtro_txt,
                    filtro_situacao=filtro_situacao,
                    filtro_tipo=filtro_tipo,
                    filtro_tipo_falta=filtro_tipo_falta,
                    filtro_situacao_falta=filtro_situacao_falta,
                    filtro_impacto_financeiro=filtro_impacto_financeiro,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )
            else:
                q_servidores = Servidor.objects.filter(pk__in=servidor_ids)

            try:
                Task.start(
                    atribuir_comp_desc_task,
                    description=f"Atribuir Competência de Desconto.",
                    user=self.request.user.id,
                    employee_id=[servidor.pk for servidor in q_servidores],
                    reference=reference,
                    competencia_desconto=competencia_desconto,
                )

                message = "Iniciando Atribuição de Competência de Desconto!"
            except:
                success = False
                message = "ERRO ao Atribuir Competência de Desconto!"

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))

    def get_post_params(self):
        servidor_ids = self.request.POST.getlist("servidor_ids")
        filtro_ano = self.request.POST.get("filtro_ano")
        filtro_mes = self.request.POST.get("filtro_mes")
        filtro_txt = self.request.POST.get("filtro_txt")
        filtro_situacao = self.request.POST.getlist("filtro_situacao")
        filtro_tipo = self.request.POST.getlist("filtro_tipo")
        filtro_tipo_falta = self.request.POST.getlist("filtro_tipo_falta")
        filtro_situacao_falta = self.request.POST.getlist("filtro_situacao_falta")
        filtro_impacto_financeiro = self.request.POST.getlist(
            "filtro_impacto_financeiro"
        )
        return (
            servidor_ids,
            filtro_ano,
            filtro_mes,
            filtro_txt,
            filtro_situacao,
            filtro_tipo,
            filtro_tipo_falta,
            filtro_situacao_falta,
            filtro_impacto_financeiro,
        )

    @login_required("JSON")
    def anos_falta(self, args=[]):
        obj = {"root": []}

        if "only" not in args:
            obj.get("root").append({"pk": 0, "description": "TODOS"})

        for f in Falta.objects.order_by("-data__year").values("data__year").distinct():
            obj.get("root").append(
                {"pk": f.get("data__year"), "description": f.get("data__year")}
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json_engine.encode(obj))

    def get_reference(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            references = []
            qtd_reference = 7
            data_year = datetime.today().year
            data_month = datetime.today().month
            count = 0
            while count < qtd_reference:
                references.append((data_month, data_year))
                data_year = data_year - 1 if data_month == 1 else data_year
                data_month = 12 if data_month == 1 else data_month - 1
                count = count + 1

            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(references),
                collection=[
                    {
                        "pk": reference[0],
                        "description": str(reference[0]) + "/" + str(reference[1]),
                    }
                    for reference in references
                ],
            )

        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))


class PReportFalta(extjs.ExtReportBuild):

    class Form(django_forms.Form):
        servidor = django_forms.CharField()
        tipo = django_forms.CharField()
        data_inicial = django_forms.DateField()
        data_final = django_forms.DateField()

    report_src = "/to/mpe/rh/servidor/faltas/main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/servidor/faltas/",
        }
    ]

    def get_generated_filename(self):
        report_servidor = "RelatórioFaltas.pdf"
        report_servidor = report_servidor.encode("utf-8")
        return report_servidor


class PONTFaltaEmployeeRestful(RestfulDRY):
    _model = Falta

    EXCLUDE_TYPE_BY_POSSESSION = [
        "COE",
        "XXX",
        "BFP",
        "MAP",
        "SAP",
        "CTR",
        "TCR",
        "JCA",
        "MEC2",
        "MEC",
        "EFC",
        "MCM2",
        "MCM",
        "MCM",
        "MEL",
        "MBR2",
        "MBR",
    ]

    full_text_index = (
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__pessoa_fisica__cpf__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("ponto.falta.employee.Manage")')

    def do_filter(self, query, force_filter=None):
        """Aplica o filtro na query.

        :param query: QuerySet a ser aplicada um filtro.

        :returns: QuerySet com filtro aplicado.

        Parâmetros do Request.Method
        filter deve ser uma lista de dicionários com as seguintes chaves
        filter=[{'stage':____,'property':____,'value':____},{...}]
        stage deve ser um inteiro, zero ou positivo para utilizar filter, ou negativo para utilizar exclude
        dicionários com stage iguais serão tratados com "OR",
        dicionários com stage diferentes serão tratados com "AND"
        """

        def fn(f):
            return {f.get("property"): self._filter_eval_value(f.get("value"))}

        try:
            flist = None
            if not force_filter:
                flist = json.loads(self.get_params().get("filter", "[]"))
            else:
                flist = force_filter
        except KeyError as e:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % e
            )
        except Exception as e:
            log.exception(e)
            raise (e)
        else:

            stages = {}
            ver_todos = [False]
            for f in flist:
                stage = int(f.get("stage", 0) or 0)
                stage_list = stages.get(stage, [])
                stage_list.append(f)
                stages.update({stage: stage_list})
                if f["property"] == "ver_todos":
                    ver_todos = f["value"]

            if len(ver_todos) == 1 and ver_todos[0]:

                query = Servidor.objects.all()

                for key in sorted(stages.keys()):
                    stage_list = stages.get(key)
                    fquery = None
                    for part in stage_list:
                        if part["property"] == "servidor__type_by_possession__in":
                            part["property"] = "type_by_possession__in"
                        if part["property"] == "servidor__ativo__in":
                            part["property"] = "ativo__in"
                        if (
                            part["property"]
                            == "servidor__movimentacaopessoal__movimentacaoteletrabalho__ativo__in"
                        ):
                            part["property"] = (
                                "movimentacaopessoal__movimentacaoteletrabalho__ativo__in"
                            )
                        if part["property"] != "ver_todos":
                            fquery = (
                                Q(fquery | Q(**fn(part))) if fquery else Q(**fn(part))
                            )

                    if str(fquery).find("ver_todos") != 8 and (
                        str(fquery).find("type_by_possession__in") == 8
                        or str(fquery).find("ativo__in") == 8
                        or str(fquery).find(
                            "movimentacaopessoal__movimentacaoteletrabalho__ativo__in"
                        )
                        == 8
                    ):
                        if fquery is not None and key >= 0:
                            query = query.filter(fquery)
                        elif fquery is not None and key < 0:
                            query = query.exclude(fquery)

                query = query.exclude(
                    type_by_possession__in=self.EXCLUDE_TYPE_BY_POSSESSION
                )

            else:
                for key in sorted(stages.keys()):
                    stage_list = stages.get(key)
                    fquery = None

                    for part in stage_list:
                        fquery = Q(fquery | Q(**fn(part))) if fquery else Q(**fn(part))

                    if str(fquery).find("ver_todos") != 8:
                        if fquery is not None and key >= 0:
                            query = query.filter(fquery)
                        elif fquery is not None and key < 0:
                            query = query.exclude(fquery)

                query = query.exclude(
                    servidor__type_by_possession__in=self.EXCLUDE_TYPE_BY_POSSESSION
                )

            if self.full_text_index and self.request.GET.get("keyword"):
                qf = None

                if isinstance(query.first(), Servidor):
                    for index in self.full_text_index:
                        index = index.replace("servidor__", "")
                        q = Q(**{index: self.request.GET.get("keyword")})
                        qf = q if qf is None else Q(qf | q)

                else:
                    for index in self.full_text_index:
                        q = Q(**{index: self.request.GET.get("keyword")})
                        qf = q if qf is None else Q(qf | q)

                query = query.filter(qf)
        return query

    def do_get(self, pk=None):
        """Executa uma requisição GET

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância ou conjunto de instâncias.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        if pk is not None:
            # Buscar um item
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
            # Trazer a lista de itens
            try:
                query = self.get_query()
                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if isinstance(query.first(), Servidor):
                    pass
                else:
                    if "keyword" in self.request.GET:
                        query = self.do_full_text_filter(query)
                    if "sort" in self.request.GET:
                        query = self.do_sort(query)

                    query = self.remove_projection(query)

                    faltas = (
                        query.values_list("pk")
                        .order_by("servidor__pk")
                        .distinct("servidor__pk")
                    )
                    query = Falta.objects.filter(pk__in=faltas).order_by(
                        "servidor__pessoa_fisica__nome"
                    )

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

    def model_to_dict(self, instance):
        rst = super(PONTFaltaEmployeeRestful, self).model_to_dict(instance)

        servidor = instance if isinstance(instance, Servidor) else instance.servidor

        lsts = self.get_last_sending_time_sheet(servidor)
        departures = servidor.departures().first()
        effective, commission = self.get_effective_and_commission(servidor)

        q_mov_posse = MovimentacaoPosse.objects.filter(servidor=servidor)
        dt_posse = q_mov_posse.last().data_posse if q_mov_posse.exists() else None

        rst.update(
            servidor_pk=servidor.pk,
            ativo=servidor.ativo,
            matricula=servidor.matricula,
            pessoa_fisica_unicode=servidor.pessoa_fisica.nome,
            type_by_possession_display=servidor.get_type_by_possession_display(),
            departure_unicode=departures.__str_restful__() if departures else "",
            effective_unicode=str(effective),
            commission_unicode=str(commission),
            last_sendindg_time_sheet=(
                f"{lsts.reference_month}/{lsts.reference_year}"
                if lsts
                else "Não Encontrado"
            ),
            status=(
                Choice.objects.get(
                    app_label="pvf", name="REQUEST_STATUS", value=lsts.status
                ).label
                if lsts
                else ""
            ),
            in_telework=(
                "SIM"
                if MovimentacaoTeletrabalho.objects.filter(
                    servidor=servidor, ativo=True
                )
                else "NÃO"
            ),
            servidor_created_by_unicode=nil_unicode(servidor.created_by, None),
            servidor_created_at=DateUtils.date_to_str(servidor.created_at),
            servidor_modified_by_unicode=nil_unicode(servidor.modified_by, None),
            servidor_modified_at=DateUtils.date_to_str(servidor.modified_at),
            dt_posse=DateUtils.date_to_str(dt_posse) if dt_posse else "",
        )

        return rst

    def get_effective_and_commission(self, instance):
        effective = ""
        commission = ""

        possessions = instance.posses_ativas
        if not instance.ativo:
            possessions = instance.posses

        effectives = possessions.filter(quadro__cargo__tipo_lei_cargo="EF")
        if effectives.exists():
            ef = effectives.latest("data_exercicio")
            effective = ef.quadro
        if instance.ativo or (not effective):
            commissions = possessions.filter(
                quadro__cargo__tipo_lei_cargo__in=("CM", "FC")
            )
            if commissions.exists():
                cm = commissions.latest("data_exercicio")
                commission = cm.quadro

        if not effective:
            effective = "Não encontrado"
        if not commission:
            commission = "Não encontrado"

        return effective, commission

    def get_last_sending_time_sheet(self, instance):
        query = (
            SendingTimeSheet.objects.filter(employee=instance)
            .order_by("-reference_year", "-reference_month", "-id")
            .first()
        )
        return query


class PONTRemocaoFalta(RestfulDRY):

    _model = RemocaoFalta

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.falta.remocao_falta.Manage")')

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            try:
                faltas = self.request.POST.getlist("falta")
                for falta in faltas:
                    ordinary_dict = {
                        "observacao": self.request.POST["observacao"],
                        "anexo": self.request.POST["anexo"],
                        "servidor": self.request.POST["servidor"],
                        "falta": falta,
                    }
                    qdict = QueryDict("", mutable=True)
                    qdict.update(ordinary_dict)

                    params = self.get_params(qdict, check_case=True)
                    inst = self.factoryModel(**params)

                    if self.use_full_clean:
                        inst.full_clean()

                    inst.save()
                    self.fill_instance_m2m(inst, params)

            except ValidationError as e:
                log.exception(e)
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                try:
                    errors = [
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ]
                    rst.update(message=str(errors[0]["values"][0]))
                except:
                    rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistido com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst
