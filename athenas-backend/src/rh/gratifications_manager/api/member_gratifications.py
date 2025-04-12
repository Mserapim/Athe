import json

from django.db.models import Q, Count

from contrib.newrest import RestfulDRY
from contrib.decorator import login_required
from contrib.utils import getLogger, get_json_engine, DateUtils
from contrib.middleware import get_current_user

from engine.mq.models import Task
from rh.models import PeriodoGratMembros, GratMembros, Gratificacao, ServidorLotacao
from rh.gfp.models import Evento, Servidor, Folha

from rh.gratifications_manager.tasks_member_gratifications import (
    consolidar_grat_membros_periodo_task,
    deferir_todos_gratificacoes_membro_task,
)
from rh.gratifications_manager.gm_utils import buscar_registro_gcpp
from rh.gfp.gcpp_utils import criar_gcpp

log = getLogger(__name__)
json_engine = get_json_engine()


class GMPeriodoGratMembros(RestfulDRY):

    _model = PeriodoGratMembros

    @login_required("JSON")
    def json(self, args=[]):
        eventos = (
            Gratificacao.objects.values("evento__numero", "evento__titulo")
            .annotate(total=Count("evento"))
            .order_by("evento")
        )
        params = {
            "eventos": [
                {
                    "numero": e["evento__numero"],
                    "titulo": f"{e['evento__numero']} | {e['evento__titulo']}",
                }
                for e in eventos
            ],
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(
            f"Ext._create('rh.gratifications_manager.member_gratifications.periodo.Manage', {params})"
        )

    def model_to_dict(self, instance):
        params = super(GMPeriodoGratMembros, self).model_to_dict(instance)
        params.update({"periodo": instance.__str__()})

        return params

    @login_required("JSON")
    def consolidar_periodo(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        periodo = PeriodoGratMembros.objects.get(pk=self.request.POST.get("periodo_id"))

        folha = Folha.objects.filter(
            tipo_folha__titulo="NORMAL",
            periodo__ano=periodo.ano,
            periodo__mes=periodo.mes,
        )

        if folha.exists() is False:
            obj["success"] = False
            obj["message"] = (
                "Não é possível realizar o cálculo. Não existe Folha do tipo 'NORMAL' no período selecionado."
            )
        else:
            Task.start(
                consolidar_grat_membros_periodo_task,
                description=f"Consolidação de período.",
                user=self.request.user.id,
                periodo_id=periodo.pk,
            )
            obj["message"] = f"Iniciando consolidação de período."

        self.response.write(json_engine.encode(obj))


class GMGratMembros(RestfulDRY):

    _model = GratMembros

    full_text_index = (
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__nome__icontains",
    )

    def do_filter(self, query, force_filter=None):
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
            for f in flist:
                if f["property"] != "evento__numero__in":
                    stage = int(f.get("stage", 0) or 0)
                    stage_list = stages.get(stage, [])
                    stage_list.append(f)
                    stages.update({stage: stage_list})

            for key in sorted(stages.keys()):
                stage_list = stages.get(key)
                fquery = None

                for part in stage_list:
                    fquery = Q(fquery | Q(**fn(part))) if fquery else Q(**fn(part))

                if fquery is not None and key >= 0:
                    query = query.filter(fquery)
                elif fquery is not None and key < 0:
                    query = query.exclude(fquery)

        return query

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

                flist = json.loads(self.get_params().get("filter", "[]"))
                if len(flist) > 0:
                    for f in flist:
                        if f["property"] == "evento__numero__in":
                            eventos = f["value"]
                            query = query.filter(
                                gratificacoes__evento__numero__in=eventos
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

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.member_gratifications.membros_consolidados.Manage")'
        )

    def get_status_icon(self, instance):
        if instance.servidor.ativo:
            return "icon-core icon-core-success"
        else:
            return "icon-core icon-core-delete"

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        txt = "Ativo" if instance.servidor.ativo else "Inativo"
        icons.append(
            {
                "iconCls": self.get_status_icon(instance),
                "title": txt,
                "alt": txt,
            }
        )

        return icons

    def model_to_dict(self, instance):
        params = super(GMGratMembros, self).model_to_dict(instance)
        first_possession_date = instance.servidor.first_possession_date

        params.update(
            {
                "data_posse": (
                    DateUtils.date_to_str(first_possession_date)
                    if first_possession_date
                    else None
                )
            }
        )
        params.update(
            {
                "data_exercicio": (
                    DateUtils.date_to_str(instance.servidor.exercise_date)
                    if instance.servidor.exercise_date
                    else None
                )
            }
        )
        params.update(
            {
                "data_desligamento": (
                    DateUtils.date_to_str(instance.servidor.termination_date)
                    if instance.servidor.termination_date
                    else None
                )
            }
        )

        cargo_efetivo = ""
        cargo_comissao = ""
        cargo_eletivo = ""

        posses = instance.servidor.posses_ativas
        if not instance.servidor.ativo:
            posses = instance.servidor.posses

        efetivos = posses.filter(quadro__cargo__tipo_lei_cargo="EF")
        if efetivos.exists():
            ef = efetivos.latest("data_exercicio")
            cargo_efetivo = ef.quadro
        if instance.servidor.ativo or (not cargo_efetivo):
            comissoes = posses.filter(quadro__cargo__tipo_lei_cargo__in=("CM", "FC"))
            if comissoes.exists():
                cm = comissoes.latest("data_exercicio")
                cargo_comissao = cm.quadro
            eletivos = posses.filter(quadro__cargo__tipo_lei_cargo="EL")
            if eletivos.exists():
                cargo_eletivo = eletivos.latest("data_exercicio").quadro

        if not cargo_efetivo and not cargo_comissao:
            cargo_efetivo = "Não encontrado"
            cargo_comissao = "Não encontrado"

        params.update(
            {
                "icons": self.get_icons(instance),
                "cargo_efetivo": str(cargo_efetivo),
                "cargo_comissao": str(cargo_comissao),
                "cargo_eletivo": str(cargo_eletivo),
            }
        )

        cargos = instance.servidor.departures().first()
        params.update({"afastamento": ""})
        if cargos:
            params.update({"afastamento": cargos.__str_restful__()})

        return params

    @login_required("JSON")
    def consolidar_grat_membro_periodo(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        grat_membro = GratMembros.objects.get(
            pk=self.request.POST.get("grat_membro_id")
        )

        folha = Folha.objects.filter(
            tipo_folha__titulo="NORMAL",
            periodo__ano=grat_membro.periodo.ano,
            periodo__mes=grat_membro.periodo.mes,
        )

        calcular = True
        if folha.exists() is False:
            calcular = False
            obj["success"] = False
            obj["message"] = (
                "Não é possível realizar o cálculo. Não existe Folha do tipo 'NORMAL' no período selecionado."
            )
        elif grat_membro.gratificacoes.exists():
            grats_calcular = []
            for grat in grat_membro.gratificacoes.all():
                if grat.status != "INDEFER":
                    gcpp = buscar_registro_gcpp(
                        grat_membro.servidor,
                        grat.evento,
                        grat_membro.periodo.ano,
                        grat_membro.periodo.mes,
                    )
                    if gcpp.exists() is False or (
                        gcpp.exists() and gcpp.first().status not in ["pago", "inapto"]
                    ):
                        grats_calcular.append(grat)

            if len(grats_calcular) == 0:
                calcular = False
                obj["success"] = False
                obj["message"] = (
                    "Não é possível realizar o cálculo. Não há registros de gratificações em avaliação."
                )

        if calcular:
            Task.start(
                consolidar_grat_membros_periodo_task,
                description=f"Consolidação de período.",
                user=self.request.user.id,
                periodo_id=grat_membro.periodo.pk,
                servidor_id=grat_membro.servidor.pk,
            )
            obj["message"] = f"Iniciando consolidação de período."

        self.response.write(json_engine.encode(obj))


class GMDesignacoes(RestfulDRY):

    _model = ServidorLotacao

    def get_query(self):
        def fn(f):
            return {f.get("property"): self._filter_eval_value(f.get("value"))}

        desigs_ids = []
        query = self.Model.objects.filter()
        if "filter" in self.request.GET:
            flist = json.loads(self.get_params().get("filter", "[]"))
            grat_membro_pk = fn(flist[0])["pk"]

            desigs_ids = [
                desig.pk
                for desig in GratMembros.objects.get(
                    pk=grat_membro_pk
                ).designacoes.all()
            ]
            query = query.filter(pk__in=desigs_ids)

        return query

    def do_get(self, pk=None):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        if pk is not None:
            rst = super().do_get(pk)
        else:
            try:
                query = self.get_query()

                query = self.do_page(query)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                log.exception(str(e))
                rst.update(message=str(e))
            else:
                try:
                    rst.update(count=query.count())
                    rst.update(
                        {
                            "collection": [
                                self.model_to_dict(record) for record in query
                            ],
                            "success": True,
                            "message": "Processado com sucesso!",
                        }
                    )
                except Exception as e:
                    log.exception(str(e))
                    rst.update(message=str(e))

        return rst

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.member_gratifications.designacoes.Manage")'
        )


class GMGratificacoes(RestfulDRY):

    _model = Gratificacao

    full_text_index = ("evento__numero__iexact",)

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.member_gratifications.gratificacoes.Manage")'
        )

    def get_icons(self, instance):
        obj = []

        if instance.status == "INDEFER":
            title_status = "Indeferido"
            icon_status = "icon-status-busy"
        elif instance.status == "DEFER":
            title_status = "Deferido"
            icon_status = "icon-status"
        elif instance.status == "AVAL":
            title_status = "Avaliar"
            icon_status = "icon-status-away"

        obj.append(
            {
                "iconCls": f"icon-fopag {icon_status}",
                "title": title_status,
                "alt": title_status,
            }
        )

        gcpp = buscar_registro_gcpp(
            instance.grat_membro.servidor,
            instance.evento,
            instance.grat_membro.periodo.ano,
            instance.grat_membro.periodo.mes,
        )
        if gcpp.exists() and gcpp.first().status == "pago":
            title = "Pago"
            obj.append(
                {
                    "iconCls": "icon-fopag icon-cash",
                    "title": title,
                    "alt": title,
                }
            )

        return obj

    def model_to_dict(self, instance):
        params = super(GMGratificacoes, self).model_to_dict(instance)

        params.update(
            {
                "servidor_unicode": str(instance.grat_membro.servidor),
                "icons": self.get_icons(instance),
                "grat_membro_id": instance.grat_membro.id,
            }
        )

        return params

    def deferir_gratificacao_membro(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        gratificacao = Gratificacao.objects.get(
            pk=self.request.POST.get("gratificacao_id")
        )

        if gratificacao.status == "DEFER":
            obj["success"] = False
            obj["message"] = "A gratificação já está deferida."
        else:
            gcpp = buscar_registro_gcpp(
                gratificacao.grat_membro.servidor,
                gratificacao.evento,
                gratificacao.grat_membro.periodo.ano,
                gratificacao.grat_membro.periodo.mes,
            )

            if gcpp.exists() and gcpp.first().status == "pago":
                obj["message"] = (
                    f"O registro de gratificação selecionado já está deferido e pago no GCPP."
                )
            elif gcpp.exists() and gcpp.first().status == "inapto":
                obj["message"] = (
                    f"O registro de gratificação selecionado já está deferido e está inapto para pagamento no GCPP."
                )
            else:
                gratificacao.status = "DEFER"
                if gratificacao.qtd_dias_deferido is None:
                    gratificacao.qtd_dias_deferido = gratificacao.qtd_dias_consolidado

                gratificacao.save()

                if gratificacao.qtd_dias_deferido == 0:
                    obj["message"] = (
                        f"Registro de gratificação deferido. Como a quantidade de dias deferido é zero, não foi registrado no GCPP."
                    )
                else:
                    criar_gcpp(
                        servidor=gratificacao.grat_membro.servidor,
                        evento=gratificacao.evento,
                        qtd_dias=gratificacao.qtd_dias_deferido,
                        periodo_ano=gratificacao.grat_membro.periodo.ano,
                        periodo_mes=gratificacao.grat_membro.periodo.mes,
                        servidor_conferido_por=Servidor.objects.get(
                            user=get_current_user()
                        ),
                        modulo_origem="gratificações",
                    )
                    obj["message"] = (
                        f"Registro de gratificação deferido e registrado no GCPP com sucesso."
                    )

        self.response.write(json_engine.encode(obj))

    def indeferir_gratificacao_membro(self, *args):
        obj = {
            "success": False,
            "message": "",
        }

        gratificacao = Gratificacao.objects.get(
            pk=self.request.POST.get("gratificacao_id")
        )

        gcpp = buscar_registro_gcpp(
            gratificacao.grat_membro.servidor,
            gratificacao.evento,
            gratificacao.grat_membro.periodo.ano,
            gratificacao.grat_membro.periodo.mes,
        )

        if gratificacao.status == "INDEFER":
            obj["message"] = "A gratificação já está indeferida."
        elif gcpp.exists() and gcpp.first().status == "pago":
            obj["message"] = (
                f"O registro de gratificação selecionado já está pago no GCPP."
            )
        elif gcpp.exists() and gcpp.first().status == "inapto":
            obj["message"] = (
                f"O registro de gratificação selecionado está inapto para pagamento no GCPP."
            )
        else:
            if gcpp.exists():
                gcpp.delete()

            gratificacao.status = "INDEFER"
            gratificacao.save()

            obj["success"] = True
            obj["message"] = f"Registro de gratificação indeferido com sucesso."

        self.response.write(json_engine.encode(obj))

    def deferir_todos_gratificacao_membro(self, *args):

        obj = {
            "success": True,
            "message": "",
        }

        grat_membro_id = self.request.POST.get("grat_membro_id")

        q_gratificacoes = Gratificacao.objects.filter(
            grat_membro__id=grat_membro_id, status="AVAL"
        )

        if q_gratificacoes.exists() is False:
            obj = {
                "success": False,
                "message": "Não é possível deferir as gratificações, não há gratificações em avaliação.",
            }
        else:
            try:
                Task.start(
                    deferir_todos_gratificacoes_membro_task,
                    description=f"Processamento para deferir todas as gratificações de um Membro. ",
                    user=self.request.user.id,
                    grat_membro_id=grat_membro_id,
                )

                obj[
                    "message"
                ] = """Iniciando processamento para deferir as gratificações de um membro
                (somente os registros que não estiverem DEFERIDO ou INDEFERIDO)."""
            except:
                obj["success"] = False
                obj["message"] = "Erro no processamento para deferir as gratificações."

        self.response.write(json_engine.encode(obj))
