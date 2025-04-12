from contrib.controller import DefaultController
from engine.mq.models import Task
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.utils import getLogger, get_json_engine
from django.http import HttpResponseBadRequest, HttpResponseNotFound
import ast
from datetime import datetime
import base64
from rh.pvf.tasks import point_sheet_report
from rh.models import Servidor


log = getLogger(__name__)
json = get_json_engine()


class PointSheetReport(DefaultController):
    def get_year(self, *args):
        import json

        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            years = []
            current_year = datetime.today().year
            year_corte = 2010
            while current_year >= year_corte:
                years.append(year_corte)
                year_corte = year_corte + 1
            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(years),
                collection=[{"pk": year, "description": str(year)} for year in years],
            )
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    @login_required("JSON")
    def create_pdf(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            month = self.request.POST.get("month")
            year = self.request.POST.get("year")
            employee_id = self.request.POST.get("employee", None)
            user = get_current_user().pk
            if employee_id:
                user = Servidor.objects.get(pk=employee_id).user.pk
            path = "pointsheet/template.html"
            task = Task.start(
                point_sheet_report,
                f"Gerando Relatório",
                success=f"""<p> Folha Ponto.
                <a href="/athenas/PointSheetReport/viewer/?uuid=%(uuid)s" target="_blank">Visualizar Folha Ponto</a>.
                </p>""",
                user=user,
                month=month,
                year=year,
                html_path=path,
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=True,
                uuid=task.uuid,
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def viewer(self, *args):
        try:
            task = Task.objects.get(
                uuid=(
                    self.request.GET.get("uuid")
                    if self.request.method == "GET"
                    else self.request.POST.get("uuid")
                ),
                owner=get_current_user(),
            )
            if task.state == "ready":
                data = ast.literal_eval(task.data)
                file = base64.b64decode(data.get("file"))
                self.response["Content-Type"] = "application/pdf"
                self.response.write(file)
                task.mark_finished()
                task.data = ""
                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Carregando relatório folha ponto.</h1>"
                )
        except Exception as e:
            log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Aguardando solicitação do folha ponto.</h1>"
            )

    @login_required("JSON")
    def marker(self, *args):
        try:
            task = Task.objects.get(
                uuid=self.request.POST.get("uuid"), owner=get_current_user()
            )
            if task.finished == False:
                task.mark_finished()
                task.data = ""
                task.save()
        except Exception as e:
            log.exception(e)
