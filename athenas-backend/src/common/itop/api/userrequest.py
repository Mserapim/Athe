# -*- coding: utf-8 -*-

import json
import locale
from contrib.controller import DefaultController
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import get_current_user
from common.itop.api.rest import Api
from rh.models import Lotacao, Servidor, Telefone
from django.template import loader
from django.utils.html import strip_tags
from datetime import datetime
from django.conf import settings

log = getLogger(__name__)


class CIUserRequest(DefaultController):

    STATUS_MAP = {
        "approved": "Aprovado",
        "assigned": "Em atendimento",
        "closed": "Fechado",
        "new": "Aguardando atendimento",
        "pending": "Pendência",
        "rejected": "Rejeitado",
        "resolved": "Resolvido",
        "waiting_for_approval": "Aguardando Aprovação",
    }

    ORIGIN_MAP = {
        "E-DOC": "E-DOC",
        "mail": "Email",
        "monitoramento": "Monitoramento",
        "phone": "Telefone",
        "portal": "Portal",
        "presencial": "Presencial",
        "ura": "URA",
        "siatu": "Siatu",
    }

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.itop.userrequest.UserRequestManage")')

    def get_logged_employee(self, *args):
        """
        Retorna o usuário logado
        """
        obj = {}
        user = get_current_user()
        try:
            employee = Servidor.objects.get(user=user)
            if employee:
                obj["logged_employee_name"] = employee.pessoa_fisica.nome

        except Servidor.DoesNotExist:
            obj["logged_employee"] = None

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def work_locations_itop(self, args=[]):
        """
        Retorna as lotações que o usuário possui exercício.
        """
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }

        try:
            employee = employee_from_user(self.request.user)
            if not employee:
                raise Exception("Servidor não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=employee.work_locations_effective_exercise.count(),
                collection=[
                    {
                        "pk": wl.id,
                        "description": str(wl),
                        "id_itop": wl.id_itop,
                    }
                    for wl in employee.work_locations_effective_exercise.filter(
                        id_itop__isnull=False
                    )
                ],
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(rst))

    def get_location_phone(self, args=[]):
        """
        Retorna o telefone da lotação selecionada.
        """
        obj = {}

        general_organ = self.request.REQUEST.get("general_organ")
        try:
            phone = Telefone.objects.filter(general_organ=general_organ).last().numero
        except Exception:
            phone = ""

        obj.update(location_phone=phone)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_user_request(self, args=[]):
        """
        Retorna todas os chamados com ciclo ativo no iTop para o usuário logado.
        """
        user = get_current_user()
        obj = {"count": 0, "collection": []}

        rest = Api()

        rest.connect(
            getattr(settings, "ITOP_URL"),
            getattr(settings, "ITOP_VERSION"),
            getattr(settings, "ITOP_USER"),
            getattr(settings, "ITOP_PWD"),
        )

        keyword = self.request.GET.get("keyword")
        if not keyword:
            keyword = ""

        tickets = rest.get(
            "UserRequest",
            "SELECT ur FROM UserRequest AS ur\
                JOIN Person AS p ON ur.caller_id = p.id\
                JOIN User AS u ON u.contactid = p.id\
                WHERE ur.ref LIKE '%{}%' AND ((u.login = '{}') AND (ur.status NOT IN ('closed')))".format(
                keyword, user
            ),
            "id, ref, status, start_date, caller_id_friendlyname, location_name",
        )

        if tickets["code"] == 0:
            if tickets["objects"]:
                if len(tickets["objects"]) > 0:
                    obj.update(
                        count=len(tickets["objects"]),
                        collection=[
                            {
                                "status": self.STATUS_MAP.get(
                                    "{v[fields][status]}".format(v=value)
                                ),
                                "location_name": "{v[fields][location_name]}".format(
                                    v=value
                                ),
                                "start_date": "{v[fields][start_date]}".format(v=value),
                                "caller_id_friendlyname": "{v[fields][caller_id_friendlyname]}".format(
                                    v=value
                                ),
                                "ref": "{v[fields][ref]}".format(v=value),
                                "id": "{v[fields][id]}".format(v=value),
                            }
                            for i, value in list(tickets["objects"].items())
                        ],
                    )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def create_user_request(self, *args):
        """
        Cria um novo chamado no iTop.
        """
        obj = {"success": False, "message": "Nada foi feito ainda."}

        user = get_current_user()
        general_organ_id = self.request.REQUEST.get("general_organ_id")
        phone = self.request.REQUEST.get("phone")
        description = self.request.REQUEST.get("description")

        if general_organ_id == "":
            general_organ_id = 0

        if len(phone) < 10 or len(description) < 5:
            obj.update(
                message="Verifique o preenchimento dos campos telefone e descrição."
            )

        else:
            try:
                location = Lotacao.objects.get(orgaogeral_ptr=general_organ_id)
                location_itop = location.id_itop
            except Lotacao.DoesNotExist:
                location_itop = None
                obj.update(
                    message="A lotação informada não foi encontrada no banco de dados."
                )

            rest = Api()
            rest.connect(
                getattr(settings, "ITOP_URL"),
                getattr(settings, "ITOP_VERSION"),
                getattr(settings, "ITOP_USER"),
                getattr(settings, "ITOP_PWD"),
            )
            userrequest_create = rest.create(
                "UserRequest",
                comment="Via Athenas",
                output_fields="ref",
                org_id="SELECT Organization WHERE name = 'MPTO'",
                caller_id="SELECT Person AS p JOIN User AS u ON u.contactid = p.id WHERE u.login = '{}'".format(
                    user
                ),
                location_id=location_itop,
                origin=getattr(settings, "ITOP_ORIGEM"),
                phone="{}".format(phone),
                description="{}".format(description),
            )

            if userrequest_create["code"] == 0:
                obj.update(success=True, message="Solicitação adicionada com sucesso.")

            else:
                obj.update(
                    message="Não foi possível criar a solicitação. Verifique os dados informados e tente novamente."
                )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def _get_user_request(self, request):
        """
        Pega uma requisição de usuário e retorna uma parte dos dados (objects) obtidos pelo ITop.
        """

        user = get_current_user()
        rest = Api()
        rest.connect(
            getattr(settings, "ITOP_URL"),
            getattr(settings, "ITOP_VERSION"),
            getattr(settings, "ITOP_USER"),
            getattr(settings, "ITOP_PWD"),
        )

        ticket = None

        if request:
            ticket = rest.get(
                "UserRequest",
                "SELECT ur FROM UserRequest AS ur\
                    JOIN Person AS p ON ur.caller_id = p.id\
                    JOIN User AS u ON u.contactid = p.id\
                    WHERE ur.id = '{}' AND ((u.login = '{}'))".format(
                    request, user
                ),
                "id, ref, status, start_date, caller_id_friendlyname, location_name,\
                origin, location_id, phone, description, solution, team_id_friendlyname,\
                agent_id_friendlyname, approver_id_friendlyname, assignment_date,\
                resolution_date, time_spent",
            )

        return ticket["objects"]

    def format_date(self, date_str):
        """
        Recebe uma data (string) e a devolve formatada como '%d/%m/%Y às %H:%M:%S'
        """
        formated = ""

        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            formated = datetime.strftime(date, "%d/%m/%Y às %H:%M:%S")

        return formated

    def format_spent_time(self, seconds):
        m, s = divmod(int(seconds or 0), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        return "%dd %dh %dm" % (d, h, m)

    def prepare_page(self, ticket):
        """
        Prepara o conjunto de dados para preenchimento dos placeholders no template
        """

        tpl = loader.get_template("itop/userrequest.html")
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        ticket = list(ticket.values())[0].get("fields")

        start_date = self.format_date(ticket.get("start_date"))
        assignment_date = self.format_date(ticket.get("assignment_date"))
        resolution_date = self.format_date(ticket.get("resolution_date"))

        return tpl.render(
            {
                "userRequest": {
                    "ref": ticket.get("ref"),
                    "status": self.STATUS_MAP.get(ticket.get("status")),
                    "origin": self.ORIGIN_MAP.get(ticket.get("origin")),
                    "caller_id_friendlyname": ticket.get("caller_id_friendlyname"),
                    "location_name": ticket.get("location_name"),
                    "phone": ticket.get("phone"),
                    "description": strip_tags(ticket.get("description")),
                    "solution": ticket.get("solution"),
                    "team_id_friendlyname": ticket.get("team_id_friendlyname"),
                    "agent_id_friendlyname": ticket.get("agent_id_friendlyname"),
                    "approver_id_friendlyname": ticket.get("approver_id_friendlyname"),
                    "start_date": start_date,
                    "assignment_date": assignment_date,
                    "resolution_date": resolution_date,
                    "time_spent": self.format_spent_time(ticket.get("time_spent")),
                }
            }
        )

    def renderer_as_json(self, obj):
        """
        Responde a requisição processada em formato JSON
        """
        indent = None

        if "HTTP_JSINDENT" in self.request.META:
            indent = int(self.request.META.get("HTTP_JSINDENT", 4) or 0)
        else:
            indent = None

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(obj, indent=indent))

    def renderer_document(self, args=[]):
        """
        Processa a requisição do cliente para produzir o documento a ser exibido no Tile
        """
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem informações", "appends": []},
        }

        try:
            ticket = self._get_user_request(self.request.GET.get("id", None))

            if len(ticket) > 0:
                content = self.prepare_page(ticket)

                rst.update(
                    message="Página carregada com sucesso!",
                    success=True,
                    document={"content": content, "appends": []},
                )
            else:
                message = "Não foi possível encontrar dados dessa requisição.\nComunique a equipe de TI."
                raise Exception(message)
        except Exception as e:
            rst.update(message=str(e))

        self.renderer_as_json(rst)
