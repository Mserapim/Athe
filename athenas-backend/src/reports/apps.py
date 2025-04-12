import importlib
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    name = "reports"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "reports.api.base_reports",
        "reports.api.mpmt.ceaf.capacitation.capacitation",
        "reports.api.mpmt.defin.provider_entry",
        "reports.api.mpmt.gfp.cubo",
        "reports.api.mpmt.gfp.lista",
        "reports.api.mpmt.gfp.paycheck_conference",
        "reports.api.mpmt.gfp.progression",
        "reports.api.mpmt.pvf.point_sheet",
        "reports.api.mpmt.reportmodels.identificationpdf",
        "reports.api.mpmt.reportmodels.identificationodt",
        "reports.api.mpmt.pvf.shiftcontrol",
        "reports.api.mpmt.pvf.negativepoint",
        "reports.api.mpmt.pvf.approversvdf",
        "reports.api.mpmt.pvf.telework",
        "reports.api.mpmt.rh.teletrabalho",
        "reports.api.mpmt.rh.teletrabalho_competencia",
        "reports.api.mpmt.rh.relatorio_semestral",
        "reports.api.mpmt.gfp.contracheque",
        "reports.api.mpmt.gfp.ficha_financeira",
        "reports.api.mpmt.rh.lista_beneficiarios",
        "reports.api.mpmt.rh.gestor_folha_ponto",
        "reports.api.mpmt.rh.servidores_por_lotacao",
        "reports.api.mpmt.rh.cargo_quadros",
        # Anotação Pessoal
        "reports.api.mpmt.anotacao_pessoal.anotacao.anotacao_pessoal",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:


        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    js_paths = ()

    for path in js_paths:
        Application.register_javascript(path, scope="reports")
