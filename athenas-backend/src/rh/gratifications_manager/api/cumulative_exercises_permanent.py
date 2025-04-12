import json

from contrib.newrest import RestfulDRY
from contrib.decorator import login_required
from contrib.utils import getLogger, get_json_engine
from contrib.middleware import get_current_user

from engine.mq.models import Task
from rh.models import (
    PeriodoExercCumulPermanente,
    ExercCumulPermanente,
    DesigsExercCumulPermanente,
)
from rh.gfp.models import Evento, Servidor

from rh.gratifications_manager.tasks_cumulative_exercises_permanent import (
    consolidar_periodo_task,
)
from rh.gfp.gcpp_utils import criar_gcpp

log = getLogger(__name__)
json_engine = get_json_engine()


class GMPeriodoExercCumulPermanente(RestfulDRY):

    _model = PeriodoExercCumulPermanente

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.cumulative_exercises_permanent.periodo.Manage")'
        )

    def model_to_dict(self, instance):
        params = super(GMPeriodoExercCumulPermanente, self).model_to_dict(instance)
        params.update({"periodo": instance.__str__()})

        return params

    @login_required("JSON")
    def consolidar_periodo(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        Task.start(
            consolidar_periodo_task,
            description=f"Consolidação de período.",
            user=self.request.user.id,
            periodo_id=self.request.POST.get("periodo_id"),
        )

        obj["message"] = f"Iniciando consolidação de período."
        self.response.write(json_engine.encode(obj))


class GMExercCumulPermanenteConsolidado(RestfulDRY):

    _model = ExercCumulPermanente

    full_text_index = (
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__nome__icontains",
    )

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Manage")'
        )

    def get_status_icon(self, instance):
        icons_status = {
            "AVAL": "icon-fopag icon-status-away",
            "DEFER": "icon-fopag icon-status",
            "INDEFER": "icon-fopag icon-status-busy",
        }

        return icons_status[instance.status]

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        icons.append(
            {
                "iconCls": self.get_status_icon(instance),
                "title": instance.get_status_display(),
                "alt": instance.get_status_display(),
            }
        )

        return icons

    def model_to_dict(self, instance):
        params = super(GMExercCumulPermanenteConsolidado, self).model_to_dict(instance)
        params.update(
            {
                "icons": self.get_icons(instance),
                "status": instance.get_status_display(),
            }
        )

        return params

    def get_query(self):
        q = ExercCumulPermanente.objects.filter(periodo__in=[])

        periodo_id = None
        getting_params = self.get_params().get("filter", "[]")
        params_list = json.loads(getting_params)

        if params_list != []:
            try:
                periodo_id = [
                    x["value"] for x in params_list if x["property"] == "periodo"
                ][0]
            except:
                periodo_id = None

            if periodo_id != None:
                q = ExercCumulPermanente.objects.filter(periodo_id=periodo_id)

        return q

    def deferir_exerc_cumul_perm(self, *args):
        obj = {
            "success": False,
            "message": "",
        }

        try:
            ex_cum_perm = ExercCumulPermanente.objects.get(
                pk=self.request.POST.get("exerc_cumul_perm_id")
            )

            if ex_cum_perm.status == "DEFER":
                obj["message"] = "O registro selecionado já está Deferido."
            else:
                if ex_cum_perm.qtd_dias_deferido is None:
                    ex_cum_perm.qtd_dias_deferido = ex_cum_perm.qtd_dias_consolidado

                if ex_cum_perm.pct_deferido is None:
                    ex_cum_perm.pct_deferido = ex_cum_perm.pct_consolidado

                ex_cum_perm.status = "DEFER"
                ex_cum_perm.save()

                criar_gcpp(
                    servidor=ex_cum_perm.servidor,
                    evento=Evento.objects.get(numero="00800"),
                    qtd_dias=ex_cum_perm.qtd_dias_deferido,
                    periodo_ano=ex_cum_perm.periodo.ano,
                    periodo_mes=ex_cum_perm.periodo.mes,
                    servidor_conferido_por=Servidor.objects.get(
                        user=get_current_user()
                    ),
                    modulo_origem="exercício cumulativo permanente",
                    pct=ex_cum_perm.pct_deferido,
                )

                obj["success"] = True
                obj["message"] = "Registro deferido e criado no GCPP com sucesso ."
        except:
            obj["message"] = (
                "Erro no processamento para deferir o registro selecionado."
            )

        self.response.write(json_engine.encode(obj))

    def indeferir_exerc_cumul_perm(self, *args):
        obj = {
            "success": False,
            "message": "",
        }

        try:
            exerc_cumul_perm = ExercCumulPermanente.objects.get(
                pk=self.request.POST.get("exerc_cumul_perm_id")
            )

            if exerc_cumul_perm.status == "DEFER":
                obj["message"] = "O registro selecionado está Deferido."
            elif exerc_cumul_perm.status == "INDEFER":
                obj["message"] = "O registro selecionado já está Indeferido."
            else:
                exerc_cumul_perm.status = "INDEFER"
                exerc_cumul_perm.save()

                obj["success"] = True
                obj["message"] = "Registro indeferido com sucesso."
        except:
            obj["message"] = (
                "Erro no processamento para indeferir o registro selecionado."
            )

        self.response.write(json_engine.encode(obj))


class GMExercCumulPermanenteDesignacoes(RestfulDRY):

    _model = DesigsExercCumulPermanente

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Manage")'
        )

    def get_query(self):
        getting_params = self.get_params()
        exerc_cumul_perm_pk = getting_params.get("exerc_cumul_perm_pk")

        return (
            super(GMExercCumulPermanenteDesignacoes, self)
            .get_query()
            .filter(exerc_cumul_perm=exerc_cumul_perm_pk)
        )

    def get_icons(self, instance):
        icons = []

        icons.append(
            {
                "iconCls": (
                    "icon-core icon-core-success"
                    if instance.ativo
                    else "icon-core icon-core-delete"
                ),
                "title": "Ativo" if instance.ativo else "Encerrado",
            }
        )

        if instance.principal:
            icons.append(
                {
                    "iconCls": "icon-core icon-core-document-arrow",
                    "title": "Principal",
                }
            )

        if instance.responsavel:
            icons.append(
                {
                    "iconCls": "icon-core icon-core-add-selected",
                    "title": "Responsável",
                }
            )

        if instance.titular:
            icons.append(
                {
                    "iconCls": "icon-core icon-core icon-core-admin",
                    "title": "Titular",
                }
            )

        if instance.coordenador:
            icons.append(
                {
                    "iconCls": "icon-core icon-core icon-core-run",
                    "title": "Coordenador",
                }
            )

        if instance.acao == 1:
            icons.append(
                {
                    "iconCls": "icon-core icon-core icon-core-users",
                    "title": "Coadjuvando",
                }
            )

        if instance.acao == 2:
            icons.append(
                {
                    "iconCls": "icon-core icon-core icon-core-set-employee",
                    "title": "Colaborando",
                }
            )

        if instance.acao == 3:
            icons.append(
                {
                    "iconCls": "icon-core icon-core icon-core-balloons",
                    "title": "Adjunto",
                }
            )

        if instance.prejuizo == 2:
            icons.append(
                {
                    "iconCls": "icon-core icon-core icon-core-update-manage",
                    "title": "Sem prejuizo",
                }
            )

        if instance.cumulativa:
            icons.append(
                {
                    "iconCls": "icon-fopag icon-arrow-repeat",
                    "title": "Cumulativa",
                }
            )

        return icons

    def model_to_dict(self, instance):
        params = super(GMExercCumulPermanenteDesignacoes, self).model_to_dict(instance)
        params.update(
            {
                "servidor": str(instance.exerc_cumul_perm.servidor),
                "icons": self.get_icons(instance),
            }
        )

        return params
