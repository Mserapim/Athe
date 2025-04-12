import ast
import base64
from calendar import monthrange
from celery import Celery
import datetime as dt
from datetime import date, datetime
import json
import os
import pdfkit

from default.websocket import RemoteEmmiter
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.template import loader

from common.usefulday.models import NonWorkingDay
from contrib.decorator import login_required
from contrib.middleware import get_current_user, set_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from engine.mq.models import Task
from rh.dayoff.const import *
from rh.models import Lotacao, Servidor, ServidorLotacao
from rh.pvf.const import *
from rh.pvf.models import PortalRequest
from rh.pvf.utils.calendar_utils import (
    get_event_birthday,
    get_event_licenses,
    get_event_substitutions,
    get_event_usufructs,
    get_workers_from_workplace,
    get_event_days,
    get_non_working_day,
    get_eventos_plantao,
)


log = getLogger(__name__)
app = Celery("pvf")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


class PVFCalendarRestful(RestfulDRY):
    _model = PortalRequest

    def get_type_employee(self):
        """
        Retorna se o usuário é responsável (Manager) de uma ou mais lotações.
        """
        try:
            employee = employee_from_user(get_current_user())
            workplaces = Lotacao.objects.filter(responsavel=employee.id)
            if len(workplaces) > 0:
                return "M"  # Manager
            else:
                return "S"
        except Exception as e:
            log.error(e)
            return "S"

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.pvf.reports.Calendar", {type_employee: "%s"})'
            % self.get_type_employee()
        )

    def get_year(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            years = []
            start_year = datetime.today().year - 1
            data_year = datetime.today().year + 5
            while data_year >= start_year:
                years.append(data_year)
                data_year = data_year - 1

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

    def filter_teams(self, workplaces):
        places = []
        for workplace in workplaces:
            workplaces_below = Lotacao.objects.filter(pai=workplace)
            places.append({"pk": workplace.pk, "description": str(workplace)})
            for workplace_below in workplaces_below:
                places.append(
                    {"pk": workplace_below.pk, "description": str(workplace_below)}
                )

        return places

    def get_teams(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            employee = employee_from_user(get_current_user())
            workplaces = Lotacao.objects.filter(responsavel=employee.id)

            workplace_json = [
                {"pk": int(9999), "description": "Todas as equipes"},
                {"pk": int(9998), "description": "Nenhuma equipe selecionada"},
            ] + self.filter_teams(workplaces)

            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(workplaces),
                collection=workplace_json,
            )

        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    @login_required("JSON")
    def create_calendar_pdf(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        employee = employee_from_user(get_current_user())
        month = self.request.POST.get("month")
        year = self.request.POST.get("year")
        type_report = self.request.POST.get("type_report")
        team = self.request.POST.get("team")
        responsible_workplaces = Lotacao.objects.filter(responsavel=employee.id)
        try:
            task = Task(owner=get_current_user())
            task.save()
            calendar_report(
                task,
                f"Agenda",
                success=f"""<p> Agenda.
                <a href="/athenas/PVFCalendarRestful/viewer/?uuid=%(uuid)s" target="_blank">Visualizar Agenda</a>.
                </p>""",
                user=get_current_user().pk,
                month=month,
                year=year,
                calendar_type=int(type_report),
                team=int(team),
                responsible_workplaces=responsible_workplaces,
            )
            obj.update(
                success=True,
                message="Aguarde o sistema fará o download do agenda solicitada.",
                uuid=task.uuid,
            )

        except Exception as e:
            log.error(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

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
                    "<h1>Erro ao Carregar a Agenda.</h1>"
                )
        except Exception as e:
            log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Erro ao Carregar a Agenda.</h1>"
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

    def viewer_header(self, *args):
        tpl = loader.get_template("header_report.html")
        self.response.write(tpl.render({}))


@app.task()
def calendar_report(
    task,
    hook,
    success,
    user,
    month=None,
    year=None,
    calendar_type=None,
    team=None,
    responsible_workplaces=None,
    origem_apiv2=False,
):
    """
    Está Task é responsável por renderizar um template html e criar arquivo pdf para o calendário do Vida Funcional
    """
    YEARLY = "9999"

    state = "failed"
    task = Task.objects.get(uuid=task.uuid)
    has_exception = None
    message = "'<p>Gerando Calendário...</p>'"
    employee = employee_from_user(get_current_user())
    workers = None
    context = {}

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        options = {
            "--footer-font-size": "10",
            "--header-font-size": "10",
            "--footer-spacing": "5",
            "--margin-top": "0mm",
            "--margin-bottom": "15mm",
            "--margin-left": "0mm",
            "--margin-right": "0mm",
            "--footer-line": "",
        }

        lotacoes_responsavel = Lotacao.objects.filter(responsavel=employee.id)
        if lotacoes_responsavel:
            lotacoes_filhas = Lotacao.objects.filter(pai__in=lotacoes_responsavel)
            lotacoes = lotacoes_filhas.union(lotacoes_responsavel)
            context["team"] = str(lotacoes.last()).title()
            workers = get_workers_from_workplace(workplaces=lotacoes, employee=employee)
        else:
            workers = [employee.id]
            lotacao = (
                ServidorLotacao.objects.filter(servidor=employee)
                .order_by("-data_vigencia_inicio")
                .first()
            )
            if lotacao:
                context["team"] = str(lotacao).title()
            else:
                context["team"] = ""

        try:
            context["dates"] = {}
            if not month == YEARLY:
                days_in_month = monthrange(int(year), int(month))[1]
                for i in range(1, days_in_month + 1):
                    context["dates"][str(i)] = dt.date(
                        day=i, month=int(month), year=int(year)
                    )

                context["month"] = month
            else:
                for month_in_year in range(1, 13):
                    days_in_month = monthrange(int(year), int(month_in_year))[1]
                    for day in range(1, days_in_month + 1):
                        day_of_year = (
                            date(int(year), month_in_year, int(day)).timetuple().tm_yday
                        )
                        context["dates"][str(day_of_year)] = dt.date(
                            day=int(day), month=int(month_in_year), year=int(year)
                        )

                month = None
                context["month"] = month

        except Exception as e:
            log.error(e)

        with open("static/images/logo-report-mpmt.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        context["logo_mpmt"] = encoded_string.decode("utf-8")
        context["year"] = year
        context["non_working_day"] = get_non_working_day(NonWorkingDay.objects.all())
        context["employee"] = employee
        context["birth_day"] = get_event_birthday(employee, year, month, workers)
        context["absence_event"], context["request_absence_event"] = get_event_licenses(
            employee, month, year, workers
        )
        context["usufruct_event"] = get_event_usufructs(employee, month, year, workers)
        context["substitution_event"] = get_event_substitutions(
            employee, month, year, workers
        )
        context["plantao_eventos"] = get_eventos_plantao(employee, month, year, workers)
        html_calendar = "calendar.html"

        if calendar_type == 2:  # Calendario Reduzido
            events = {}
            events.update(context["birth_day"])
            events.update(context["usufruct_event"])
            events.update(context["request_absence_event"])
            events.update(context["absence_event"])
            events.update(context["substitution_event"])
            events.update(context["plantao_eventos"])
            context["events"] = events
            context["dates"] = get_event_days(events, context["dates"])

        html = loader.render_to_string(html_calendar, context)

        output = pdfkit.from_string(html, output_path=False, options=options)
        task.data = {
            "file": base64.b64encode(output),
            "mimetype": "application/pdf",
            "extension": "pdf",
            "filename": "Agenda",
        }
        if not origem_apiv2:
            RemoteEmmiter.emmit_for_user(
                get_current_user(),
                "calendar-report",
                path=f"/athenas/PVFCalendarRestful/viewer/?uuid={task.uuid}",
                filename="Agenda",
            )

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = err

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        log.error(has_exception)
        raise has_exception
