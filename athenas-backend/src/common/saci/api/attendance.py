# -*- coding: utf-8 -*-
from django.db.models import Q
from django.template import loader

from common.internal_security.api.person import ISecPerson
from common.saci.models import Attendance, Step
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from edocs.protocolo.models import OrgaoGeral
from judicial.models import Attached, PartLawsuit
from rh.models import Servidor, ServidorLotacao

log = getLogger(__name__)


class SACIAttendanceRestful(RestfulDRY):

    _model = Attendance

    force_upper = False

    force_orm_single = True

    exclude_fields = ["attendance_ptr"]

    force_persist_boolean_fields = [
        "contains_represented",
        "competence_others",
        "confidential",
    ]

    full_text_index = (
        "protocol__assunto__icontains",
        "protocol__codigo__icontains",
    )

    def get_params(self, *args, **kwargs):
        params = super(SACIAttendanceRestful, self).get_params(*args, **kwargs)

        if not params.get("typology"):
            params.pop("typology", None)

        if not params.get("department"):
            params.pop("department", None)

        return params

    def restrict_model_to_dict(self, _dict_):
        for key, value in _dict_.items():
            if key not in ["id", "pk", "protocol_unicode", "icons", "can_read"]:
                if isinstance(value, str):
                    value = "CONTEÚDO RESTRITO"
                elif isinstance(value, bool):
                    value = None
                elif isinstance(value, (int, float)):
                    value = 0
                else:
                    value = None

                _dict_[key] = value

    def model_to_dict(self, instance):
        _dict_ = super(SACIAttendanceRestful, self).model_to_dict(instance)

        control = getattr(instance, "attendance_control", None)
        control_type = getattr(control, "control_type", None)

        _dict_.update(
            {
                "icons": instance.icons,
                "protocol_unicode": (
                    instance.protocol.codigo if instance.protocol else "Não protocolado"
                ),
                "movement": (
                    instance.protocol.movimentacoes.get(passo=0).pk
                    if instance.protocol.movimentacoes.exists()
                    else None
                ),
                # Controle de Acesso (app document_access)
                "control": getattr(control, "id", 0),
                "control_type": getattr(control_type, "id", 0),
                "can_read": instance.can_read,
            }
        )

        if not instance.can_read:
            self.restrict_model_to_dict(_dict_)

        return _dict_

    def get_query(self):
        query = super(SACIAttendanceRestful, self).get_query()
        return query.filter(deleted=False)

    def movement(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        try:
            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            if "destination" in params and not params.get("destination"):
                raise Exception('O "Encaminhar para" deve ser informado corretamente.')
            else:
                params.update(
                    destination=OrgaoGeral.objects.filter(
                        pk=int(params.get("destination") or 0)
                    ).first()
                )

            if "justification" in params and not params.get("justification"):
                raise Exception("Preencha a justificativa.")

            required_employee = params.get("required_employee", "off").lower() == "on"

            if params.get("required_employee"):
                params.pop("required_employee")

            if not params.get("employee") and required_employee:
                raise Exception("Selecione o Membro responsável pelo atendimento.")
            elif params.get("employee"):
                params.update(
                    employee=Servidor.objects.get(pk=int(params.get("employee")))
                )
            else:
                params.update(employee=employee_from_user(self.request.user))

            attendance = self.get_query().get(pk=args[0])

            attendance.movement(**params)

            rst.update(success=True, message="Encaminhamento realizado.")

        except self.Model.DoesNotExist:
            rst.update(message="Este atendimento não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def finalize(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        try:
            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            if "competence_others" in params:
                params.update(
                    competence_others=params.get("competence_others", "off").lower()
                    == "on"
                )

            if not params.get("destination", 0) and params.get("competence_others"):
                raise Exception(
                    'Se atendimento não compete ao MPE, o campo "Endereçar à" deve ser preenchido.'
                )
            else:
                params.update(
                    destination=OrgaoGeral.objects.filter(
                        pk=int(params.get("destination") or 0)
                    ).first()
                )

            if "feedback" in params and not params.get("feedback"):
                raise Exception("O parecer deve ser preenchido.")

            required_employee = params.get("required_employee", "off").lower() == "on"

            if params.get("required_employee"):
                params.pop("required_employee")

            if not params.get("employee") and required_employee:
                raise Exception("Selecione o Membro responsável pelo atendimento.")
            elif params.get("employee"):
                params.update(
                    employee=Servidor.objects.get(pk=int(params.get("employee")))
                )
            else:
                params.update(employee=employee_from_user(self.request.user))

            attendance = self.get_query().get(pk=args[0])

            attendance.finalize(**params)

            rst.update(success=True, message="Atendimento finalizado.")

        except self.Model.DoesNotExist:
            rst.update(message="Este atendimento não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def check_to_sign(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        try:
            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            attendance = self.get_query().get(pk=args[0])
            attendance.save()
            attendance.check_to_sign()

            rst.update(success=True, message="Atendimento checado.")

        except self.Model.DoesNotExist:
            rst.update(message="Este atendimento não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def after_generate_lawsuit(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        try:
            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            attendance = self.Model.objects.get(
                pk=int(params.get("attendance", 0) or 0)
            )
            attendance.after_generate_lawsuit()

            part = PartLawsuit.objects.get(pk=int(params.get("part", 0) or 0))

            for attach in attendance.attached.filter():
                obj = Attached(
                    attached_document=part,
                    title=attach.title,
                    file_descriptor=attach.file_descriptor,
                )
                obj.skip_read_only_validate = True
                obj.save()

        except self.Model.DoesNotExist:
            rst.update(message="Este atendimento não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True, message="Atendimento gerou um procedimento extrajudicial."
            )

        self.renderer(rst)

    def renderer_document_to_print(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            attendance = self.get_query().get(pk=self.request.GET.get("attendance"))
        except Exception as e:
            rst.update(message=str(e))
        else:
            pages = []
            extra_pages = []
            pure = self.request.GET.get("pure", "off").lower() == "on"

            if attendance.protocol.out_court_lawsuits.exists():
                pages = [
                    {
                        "at": None,
                        "page": "<h2>O Atendimento faz parte de um processo do E-EXT</h2>",
                    }
                ]
            else:

                pages = [{"at": None, "page": attendance.rendered}]

                extra_pages += attendance.extra_pages_attached

            pages += sorted(extra_pages, key=lambda d: d.get("at"))

            rst.update(
                documents=[doc.get("page") for doc in pages],
                success=True,
                message="Arquivo gerado com sucesso.!",
            )

            if not pure:
                self.response.write(
                    loader.get_template("saci/printer.html").render(rst)
                )
            else:
                self.response["Content-Type"] = "text/plain"
                self.response.write(
                    "".join(
                        [
                            doc.get("page")
                            for doc in pages
                            if isinstance(doc.get("page"), str)
                        ]
                    )
                    .encode("ascii", "xmlcharrefreplace")
                    .encode("base64")
                )

    def read_render(self, args=[]):
        result = {"success": False, "message": "nada foi feito ainda"}

        try:
            attendance = self.get_query().get(pk=self.request.GET.get("pk"))
        except self.Model.DoesNotExist:
            result.update(
                message="Não foi encontrado o atendimento com o id fornecido."
            )
        else:
            if attendance.protocol.out_court_lawsuits.exists():
                result.update(
                    success=True,
                    content="<h2>O Atendimento faz parte de um processo do E-EXT</h2>",
                    extra_pages=[],
                )
            else:
                result.update(
                    success=True,
                    content=attendance.rendered,
                    extra_pages=attendance.extra_pages,
                )

        self.renderer(result)

    def sign(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda", "count": 0}

        try:
            query = self.get_query().filter(pk__in=self.request.POST.getlist("pkset"))
            total = query.count()

            for attendance in query:
                attendance.sign()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True if total > 0 else False,
                count=total,
                message=(
                    "atualizados com sucesso"
                    if total > 0
                    else "nenhum item foi atualizado."
                ),
            )

        self.renderer(rst)

    def normalize_params(self):
        params = {}
        for key in list(self.request.REQUEST.keys()):
            value = self.request.REQUEST.getlist(key)
            if len(value) > 1:
                params.update({key: value})
            else:
                params.update({key: value[0]})
        return params

    def validate_control_params(self, params):
        if not params.get("control_type"):
            raise Exception(
                "Não posso classificar uma informação sem um Nível de Acesso."
            )

        if not params.get("legal_prerogative"):
            raise Exception(
                "Não posso classificar uma informação sem uma Hipótese Legal."
            )

        if not params.get("justification"):
            raise Exception(
                "Não posso classificar uma informação sem uma Justificativa."
            )

    def access_control(self, args=[]):
        from common.saci.signals.custom import access_control_signal

        result = {"success": False, "message": "Nothing done yet!"}

        try:
            attendance = self.get_query().get(pk=args[0])
            params = self.normalize_params()
            self.validate_control_params(params)

            access_control_signal.send(
                sender=self.Model,
                attendance=attendance,
                control_type_id=params.get("control_type"),
                legal_prerogative_id=params.get("legal_prerogative"),
                justification=params.get("justification"),
            )
        except Exception as e:
            result.update(message=str(e))
        else:
            result.update(
                {
                    "success": True,
                    "message": "Controle configurado com sucesso!",
                }
            )

        self.renderer(result)


class SACIClerkRestful(SACIAttendanceRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.saci.clerk.Manage")')

    def get_query(self):
        query = super(SACIClerkRestful, self).get_query()
        employee = employee_from_user(get_current_user())

        work_locations = employee.work_locations.filter()

        return query.filter(
            Q(department__pk__in=work_locations),
            Q(protocol__out_court_lawsuits__isnull=True),
        )


class SACIProsecutorRestful(SACIAttendanceRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.saci.prosecutor.Manage")')

    def get_query(self):
        query = super(SACIProsecutorRestful, self).get_query()

        employee = employee_from_user(get_current_user())

        work_locations = employee.work_locations.filter()

        return query.filter(
            Q(department__pk__in=work_locations),
            Q(protocol__out_court_lawsuits__isnull=True),
        )


class SACIStepRestful(RestfulDRY):

    _model = Step

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {
                "content": "Não há informações a serem exibidas",
            },
        }

        try:
            step = self.get_query().get(pk=args[0])
            rst.update(
                success=True,
                document={"message": "Encaminhamento", "content": step.rendered},
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não foi possível encontrar o documento desejado. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def prosecutor_location(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }

        try:

            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            department = int(params.get("department", 0) or 0)

            if department:
                query = (
                    ServidorLotacao.work_assignment_exercise(workplace=department)
                    .filter(servidor__tipo="M")
                    .order_by("servidor__pk")
                    .distinct("servidor")
                )

                if not query.exists():
                    employee = employee_from_user(get_current_user())
                    query = (
                        ServidorLotacao.work_assignment_exercise(workplace=department)
                        .filter(servidor=employee)
                        .order_by("servidor__pk")
                        .distinct("servidor")
                    )

            else:
                query = None

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=query.count() if query else 0,
                collection=[
                    {
                        "pk": wl.servidor.pk,
                        "description": str(wl.servidor.pessoa_fisica.nome),
                    }
                    for wl in query
                ],
            )

        self.renderer(rst)


class SACIAQueuePersonRestful(ISecPerson):

    def get_query(self):
        employee = employee_from_user(get_current_user())

        work_locations = employee.work_locations.filter()

        attendance = Attendance.objects.filter(
            Q(department__pk__in=work_locations),
            Q(signed_at=None),
            Q(protocol__out_court_lawsuits__isnull=True),
        )

        return self.Model.objects.filter(in_attendance__pk__in=attendance).order_by(
            "in_attendance__steps__created_at"
        )
