# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import get_current_user
from standard.models import Configuration
from django.db.models import Q
from django.template.defaultfilters import slugify
from datetime import datetime
from decimal import Decimal, ROUND_UP
from corregedoria.prontuary.models import (
    Prontuary,
    GeneralData,
    ListIndication,
    InstitutionalParticipation,
    CoursesParticipation,
    PerformanceParticularDifficulty,
    TrainingImprovement,
    InstitutionalContribution,
    IntegrateStrategicWorkGroup,
    IntegrateWorkGroup,
    ExerciseInRole,
    Promotion,
    Removal,
    Permutation,
    ExerciseInRole,
    Exercise,
    Replacement,
    DesignationCumulation,
    AdministrativeFunction,
    PartiesHearings,
    JointAction,
    Exoneration,
    Retirement,
    Departure,
    Availability,
    Punishment,
)
from rh.models import Servidor as Employee
from raf.models import Activity, WorkerLocation, FunctionalActivityReport as Raf

log = getLogger(__name__)


class PRONTUARYProntuary(RestfulDRY):
    _model = Prontuary
    force_upper = False

    full_text_index = ("employee__pessoa_fisica__nome__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.prontuary.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYProntuary, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "employee_id": instance.employee.pk,
                "employee_matricula": instance.employee.matricula,
                "employee_nome": instance.employee.pessoa_fisica.nome,
            }
        )
        return _dict_

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=prontuary.rendered)
        self.renderer(rst)

    def get_generaldata(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            generaldata = GeneralData.objects.filter(prontuary=prontuary).first()
            data = []
            data.append(
                {
                    "vitality_date": (
                        generaldata.vitality_date.strftime("%d/%m/%Y")
                        if generaldata
                        else None
                    ),
                    "vitality_doc": generaldata.vitality_doc if generaldata else None,
                    "seniority_position": (
                        generaldata.seniority_position if generaldata else None
                    ),
                    "ordinance_seniority_position": (
                        generaldata.ordinance_seniority_position
                        if generaldata
                        else None
                    ),
                    "public_service_time": (
                        generaldata.public_service_time if generaldata else None
                    ),
                }
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=1,
                collection=data,
            )
        return self.renderer(rst)

    def saveGeneralData(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            generaldata = GeneralData.objects.filter(prontuary=prontuary).first()
            if generaldata is None:
                generaldata = GeneralData()
                generaldata.prontuary = prontuary
            generaldata.vitality_date = (
                datetime.strptime(params.get("vitality_date"), "%d/%m/%Y").date()
                if params.get("vitality_date") != ""
                else None
            )
            generaldata.vitality_doc = params.get("vitality_doc")
            generaldata.seniority_position = int(params.get("seniority_position"))
            generaldata.ordinance_seniority_position = params.get(
                "ordinance_seniority_position"
            )
            generaldata.public_service_time = params.get("public_service_time")
            generaldata.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
            )
        return self.renderer(rst)

    def checklistindication(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            listindication = ListIndication.objects.filter(prontuary=prontuary).first()
            if listindication is None:
                listindication = ListIndication()
                listindication.prontuary = prontuary
                listindication.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                listindication=listindication.pk,
            )
        return self.renderer(rst)

    def checkinstitutionalparticipation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            institutionalparticipation = InstitutionalParticipation.objects.filter(
                prontuary=prontuary
            ).first()
            if institutionalparticipation is None:
                institutionalparticipation = InstitutionalParticipation()
                institutionalparticipation.prontuary = prontuary
                institutionalparticipation.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                institutionalparticipation=institutionalparticipation.pk,
            )
        return self.renderer(rst)

    def checkcoursesparticipation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            coursesparticipation = CoursesParticipation.objects.filter(
                prontuary=prontuary
            ).first()
            if coursesparticipation is None:
                coursesparticipation = CoursesParticipation()
                coursesparticipation.prontuary = prontuary
                coursesparticipation.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Frequencia e Aproveitamento em Cursos do Prontuário Individual salvos com sucesso.",
                coursesparticipation=coursesparticipation.pk,
            )
        return self.renderer(rst)

    def checkperformanceparticulardifficulty(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            performanceparticulardifficulty = (
                PerformanceParticularDifficulty.objects.filter(
                    prontuary=prontuary
                ).first()
            )
            if performanceparticulardifficulty is None:
                performanceparticulardifficulty = PerformanceParticularDifficulty()
                performanceparticulardifficulty.prontuary = prontuary
                performanceparticulardifficulty.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Frequencia e Aproveitamento em Cursos do Prontuário Individual salvos com sucesso.",
                performanceparticulardifficulty=performanceparticulardifficulty.pk,
            )
        return self.renderer(rst)

    def checktrainingimprovement(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            trainingimprovement = TrainingImprovement.objects.filter(
                prontuary=prontuary
            ).first()
            if trainingimprovement is None:
                trainingimprovement = TrainingImprovement()
                trainingimprovement.prontuary = prontuary
                trainingimprovement.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Frequencia e Aproveitamento em Cursos do Prontuário Individual salvos com sucesso.",
                trainingimprovement=trainingimprovement.pk,
            )
        return self.renderer(rst)

    def checkinstitutionalcontribution(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            institutionalcontribution = InstitutionalContribution.objects.filter(
                prontuary=prontuary
            ).first()
            if institutionalcontribution is None:
                institutionalcontribution = InstitutionalContribution()
                institutionalcontribution.prontuary = prontuary
                institutionalcontribution.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                institutionalcontribution=institutionalcontribution.pk,
            )
        return self.renderer(rst)

    def checkintegratestrategicworkgroup(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            integratestrategicworkgroup = IntegrateStrategicWorkGroup.objects.filter(
                prontuary=prontuary
            ).first()
            if integratestrategicworkgroup is None:
                integratestrategicworkgroup = IntegrateStrategicWorkGroup()
                integratestrategicworkgroup.prontuary = prontuary
                integratestrategicworkgroup.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                integratestrategicworkgroup=integratestrategicworkgroup.pk,
            )
        return self.renderer(rst)

    def checkexerciseinrole(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            exerciseinrole = ExerciseInRole.objects.filter(prontuary=prontuary).first()
            if exerciseinrole is None:
                exerciseinrole = ExerciseInRole()
                exerciseinrole.prontuary = prontuary
                exerciseinrole.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                exerciseinrole=exerciseinrole.pk,
            )
        return self.renderer(rst)

    def checkexercise(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            exercise = Exercise.objects.filter(prontuary=prontuary).first()
            if exercise is None:
                exercise = ExerciseInRole()
                exercise.prontuary = prontuary
                exercise.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                exercise=exercise.pk,
            )
        return self.renderer(rst)

    def checkintegrateworkgroup(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            integrateworkgroup = IntegrateWorkGroup.objects.filter(
                prontuary=prontuary
            ).first()
            if integrateworkgroup is None:
                integrateworkgroup = IntegrateWorkGroup()
                integrateworkgroup.prontuary = prontuary
                integrateworkgroup.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                integrateworkgroup=integrateworkgroup.pk,
            )
        return self.renderer(rst)

    def checkpromotion(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            promotion = Promotion.objects.filter(prontuary=prontuary).first()
            if promotion is None:
                promotion = Promotion()
                promotion.prontuary = prontuary
                promotion.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                promotion=promotion.pk,
            )
        return self.renderer(rst)

    def checkremoval(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            removal = Removal.objects.filter(prontuary=prontuary).first()
            if removal is None:
                removal = Removal()
                removal.prontuary = prontuary
                removal.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                removal=removal.pk,
            )
        return self.renderer(rst)

    def checkpermutation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            permutation = Permutation.objects.filter(prontuary=prontuary).first()
            if permutation is None:
                permutation = Permutation()
                permutation.prontuary = prontuary
                permutation.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                permutation=permutation.pk,
            )
        return self.renderer(rst)

    def checkexercise(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            exercise = Exercise.objects.filter(prontuary=prontuary).first()
            if exercise is None:
                exercise = Exercise()
                exercise.prontuary = prontuary
                exercise.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                exercise=exercise.pk,
            )
        return self.renderer(rst)

    def checkreplacement(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            replacement = Replacement.objects.filter(prontuary=prontuary).first()
            if replacement is None:
                replacement = Replacement()
                replacement.prontuary = prontuary
                replacement.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                replacement=replacement.pk,
            )
        return self.renderer(rst)

    def checkdesignationcumulation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            designationcumulation = DesignationCumulation.objects.filter(
                prontuary=prontuary
            ).first()
            if designationcumulation is None:
                designationcumulation = DesignationCumulation()
                designationcumulation.prontuary = prontuary
                designationcumulation.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                designationcumulation=designationcumulation.pk,
            )
        return self.renderer(rst)

    def checkadministrativefunction(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            administrativefunction = AdministrativeFunction.objects.filter(
                prontuary=prontuary
            ).first()
            if administrativefunction is None:
                administrativefunction = AdministrativeFunction()
                administrativefunction.prontuary = prontuary
                administrativefunction.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                administrativefunction=administrativefunction.pk,
            )
        return self.renderer(rst)

    def checkpartieshearings(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            partieshearings = PartiesHearings.objects.filter(
                prontuary=prontuary
            ).first()
            if partieshearings is None:
                partieshearings = PartiesHearings()
                partieshearings.prontuary = prontuary
                partieshearings.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                partieshearings=partieshearings.pk,
            )
        return self.renderer(rst)

    def checkjointaction(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            jointaction = JointAction.objects.filter(prontuary=prontuary).first()
            if jointaction is None:
                jointaction = JointAction()
                jointaction.prontuary = prontuary
                jointaction.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                jointaction=jointaction.pk,
            )
        return self.renderer(rst)

    def checkexoneration(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            exoneration = Exoneration.objects.filter(prontuary=prontuary).first()
            if exoneration is None:
                exoneration = Exoneration()
                exoneration.prontuary = prontuary
                exoneration.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                exoneration=exoneration.pk,
            )
        return self.renderer(rst)

    def checkretirement(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            retirement = Retirement.objects.filter(prontuary=prontuary).first()
            if retirement is None:
                retirement = Retirement()
                retirement.prontuary = prontuary
                retirement.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                retirement=retirement.pk,
            )
        return self.renderer(rst)

    def checkdeparture(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            departure = Departure.objects.filter(prontuary=prontuary).first()
            if departure is None:
                departure = Departure()
                departure.prontuary = prontuary
                departure.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                departure=departure.pk,
            )
        return self.renderer(rst)

    def checkavailability(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            availability = Availability.objects.filter(prontuary=prontuary).first()
            if availability is None:
                availability = Availability()
                availability.prontuary = prontuary
                availability.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                availability=availability.pk,
            )
        return self.renderer(rst)

    def checkpunishment(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary")) if params.get("prontuary") != "" else 0
            ).first()
            punishment = Punishment.objects.filter(prontuary=prontuary).first()
            if punishment is None:
                punishment = Punishment()
                punishment.prontuary = prontuary
                punishment.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados Gerais do Prontuário Individual salvos com sucesso.",
                punishment=punishment.pk,
            )
        return self.renderer(rst)

    def reload_listemployees(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            for s in Employee.objects.filter(tipo="M"):
                if Prontuary.objects.filter(employee=s).exists() is False:
                    p = Prontuary()
                    p.employee = s
                    p.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Lista recarregada com sucesso.",
            )
        return self.renderer(rst)

    def productivity(self, args=[]):

        rst = {
            "success": False,
            "message": "Nada foi feito ainda.",
            "count": 0,
            "collection": [],
        }

        try:
            # trabalho atual...
            # Activity.objects.filter(
            # Q(workerlocation__raf__employee__pessoa_fisica__nome__icontains='andre ramos varanda')
            # | Q(workerlocation__raf__yearbase__title=u'2017')).aggregate(Sum('amount_athenas'))

            params = self.request.POST
            activity = True
            data = []
            if activity:
                data.append(
                    {
                        "teste_mensagem": "oiê... este é o primeiro retorno...",
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=1,
                collection=data,
            )

        return self.renderer(rst)
