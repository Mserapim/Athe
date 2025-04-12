# -*- coding: utf-8 -*-
import json
from datetime import datetime

from . import util
from contrib.br import br_month
from contrib.daterange import NewDateRange
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.nil import nil_unicode
from contrib.utils import employee_from_user, getLogger
from django.db.models import Q
from engine.mq.models import Task

# from raf.models import *
from raf.models import (
    FunctionalActivityReport,
    Solicitation,
    TrustRelationship,
    WorkerLocation,
    YearBase,
)
from raf.tasks import (
    drop_eext2atheans,
    drop_eproc2atheans,
    drop_raf,
    import_eext,
    import_eproc,
    process_raf,
    recalculate_balance_raf,
)

# from rh.models import *
from rh.models import Servidor

log = getLogger(__name__)


class RAFFunctionalActivityReport(RestfulDRY):

    force_upper = False

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
    )

    _model = FunctionalActivityReport

    def json(self, args=[]):
        management_enable = 0
        if get_current_user().has_perm("raf.can_management_raf"):
            management_enable = 1
        values = {
            "management_enable": management_enable,
        }
        dicio = {"values": values}
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("raf.functionalactivityreport.Launcher", %s)'
            % json.dumps(dicio)
        )

    def get_query(self):
        return FunctionalActivityReport.objects.all().order_by(
            "employee__pessoa_fisica__nome"
        )

    def model_to_dict(self, instance):
        rst = super(RAFFunctionalActivityReport, self).model_to_dict(instance)
        rst.update(
            {
                "icons": instance.icons,
                "icons_list": instance.icons_list,
                "employee_unicode": nil_unicode(
                    instance.employee.pessoa_fisica.nome, None
                ),
                "employee_matricula": nil_unicode(instance.employee.matricula, None),
                "yearbase_unicode": nil_unicode(instance.yearbase, None),
                "submitted_by_unicode": nil_unicode(instance.submitted_by, None),
                "submitted": instance.submitted,
            }
        )
        return rst

    def raf_trust_relation_query(self):
        query = super(RAFFunctionalActivityReport, self).get_query()
        employee = employee_from_user(get_current_user())
        query_set = Q(
            Q(employee=employee)
            | Q(
                employee__pk__in=TrustRelationship.objects.filter(
                    trust_employee=employee, activated=True
                ).values_list("employee")
            )
        )
        if get_current_user().has_perm("raf.can_management_raf"):
            query_set = Q(
                Q(employee__pk__in=Servidor.objects.filter(tipo="M").values("pk"))
                | Q(pk=employee.pk)
            )
        return query.filter(query_set)

    def all_rafs(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        params = util.request_params(self)
        query = Q(Q(employee__pk=params.get("employee", 0)))
        data = [
            {
                "pk": raf.pk,
                "employee_unicode": nil_unicode(raf.employee, None),
                "employee": nil_unicode(raf.employee.pk, None),
                "employee_matricula": nil_unicode(raf.employee.matricula, None),
                "month": raf.month,
                "month_unicode": br_month(raf.month),
                "year": raf.year,
                "icons": raf.icons,
                "icons_list": raf.icons_list,
            }
            for raf in self.raf_trust_relation_query().filter(query)
        ]
        rst.update(
            success=True,
            message="Dados encontrados com sucesso.",
            count=self.get_query().count(),
            collection=data,
        )
        return self.renderer(rst)

    def all_rafstatus(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        # params = util.request_params(self)
        data = [
            {
                "month": raf["month"],
                "month_unicode": br_month(raf["month"]),
                "year": raf["year"],
            }
            for raf in FunctionalActivityReport.objects.all()
            .values("year", "month")
            .distinct("year", "month")
        ]
        rst.update(
            success=True,
            message="Dados encontrados com sucesso.",
            count=FunctionalActivityReport.objects.all()
            .values("year", "month")
            .distinct("year", "month")
            .count(),
            collection=data,
        )
        return self.renderer(rst)

    def get_historicRAF(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        params = util.request_params(self)
        raf = FunctionalActivityReport.objects.get(pk=params.get("raf", 0))
        historic = raf.historics.all().order_by("created_at")
        data = [
            {
                "action": h.get_action_display(),
                "dt_action": h.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                "employee_unicode": Servidor.objects.filter(user=h.created_by)
                .values_list("pessoa_fisica__nome")
                .first(),
            }
            for h in historic
        ]
        rst.update(
            success=True,
            message="Dados encontrados com sucesso.",
            count=historic.count(),
            collection=data,
        )
        return self.renderer(rst)

    def submit(self, args=[]):
        rst = {"sucess": False, "message": "Nada foi feito."}
        try:
            raf = self.get_query().get(pk=args[0])
            raf.submit()
        except self.Model.DoesNotExist:
            rst.update(message="RAF não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="RAF foi submetido com sucesso.")
        return self.renderer(rst)

    def open(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            raf = self.get_query().get(pk=args[0])
            raf.open()
        except self.Model.DoesNotExist:
            rst.update(message="RAF não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="RAF foi aberto com sucesso.")
        return self.renderer(rst)

    def openAll(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            reference = args[0]
            month = reference.split(".")[0]
            year = reference.split(".")[1]
            for raf in FunctionalActivityReport.objects.filter(month=month, year=year):
                if raf.departure is not True and raf.submitted_by_id is None:
                    raf.open()
        except self.Model.DoesNotExist:
            rst.update(message="Erro ao abrir rafs não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="RAFs abertos com sucesso.")
        return self.renderer(rst)

    def close(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            raf = self.get_query().get(pk=args[0])
            raf.close()
        except self.Model.DoesNotExist:
            rst.update(message="RAF não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="RAF foi fechado com sucesso.")
        return self.renderer(rst)

    def closeAll(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            reference = args[0]
            month = reference.split(".")[0]
            year = reference.split(".")[1]
            for raf in FunctionalActivityReport.objects.filter(month=month, year=year):
                raf.close()
        except self.Model.DoesNotExist:
            rst.update(message="Erro ao fechar rafs.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="RAFs fechados com sucesso.")
        return self.renderer(rst)

    def createRAF(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            month = int(self.request.POST.get("month"))
            year = int(self.request.POST.get("year"))
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            list_of_employees = Servidor.objects.filter(tipo="M", ativo=True)
            if employee:
                list_of_employees = list_of_employees.filter(pk=employee)

            FunctionalActivityReport.create_raf_from(
                list_employee=list_of_employees, month=month, year=year
            )

            # month_reference = NewDateRange.from_month(month=month, year=year)
            # for membro in list_of_employees.order_by('pessoa_fisica__nome'):
            #     if membro.ativo:
            #         raf = FunctionalActivityReport.objects.filter(employee=membro, month=month, year=year).first()
            #         if raf is None:
            #             raf = FunctionalActivityReport()
            #             raf.employee = membro
            #             raf.month = month
            #             raf.year = year
            #             raf.yearbase = YearBase.objects.get(activated=True)
            #             raf.closed = True
            #             raf.save()
            #         listaD = membro._raw_locations()
            #         listaExercicio = listaD.filter(~Q(lotacao__executionorgan=None) & Q(designacao=True) & Q(Q(data_vigencia_inicio__range=[month_reference.first, month_reference.last]) | Q(Q(data_vigencia_inicio__lte=month_reference.first) & Q(Q(data_vigencia_fim__range=[month_reference.first, month_reference.last]) | Q(data_vigencia_fim__gte=month_reference.last) | Q(data_vigencia_fim=None)))))
            #         if listaExercicio.count() > 0:
            #             for d in listaExercicio.order_by('lotacao__nome'):
            #                 worklocation = WorkerLocation.objects.filter(raf=raf, location=d.lotacao).first()
            #                 if worklocation is None:
            #                     worklocation = WorkerLocation()
            #                     worklocation.raf = raf
            #                     worklocation.location = d.lotacao
            #                     worklocation.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="RAFs criados/editados com sucesso.")
        return self.renderer(rst)

    def dropRAF(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            month = int(self.request.POST.get("month"))
            year = int(self.request.POST.get("year"))
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            activity = self.request.POST.get("activity")
            adjustment = self.request.POST.get("adjustment")
            Task.start(
                drop_raf,
                month=month,
                year=year,
                employee=employee,
                activity=activity,
                adjustment=adjustment,
                user=get_current_user().pk,
            )
            ret = True
            message = "A remoção foi solicitada com sucesso.<br />Você será avisado ao final da operação."
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=ret, message=message)
        return self.renderer(rst)

    def addWorkerLocation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            praf = params.get("raf", 0)
            location = params.get("workerlocation", 0)
            raf = FunctionalActivityReport.objects.filter(pk=praf).first()
            if raf:
                raf.addWorkerLocation(location=int(location))
        except self.Model.DoesNotExist:
            rst.update(message="RAF não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            txt = "Órgão de Execução adicionado com sucesso."
            rst.update(success=True, message=txt)
        self.renderer(rst)

    def delWorkerLocation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = util.request_params(self)
            praf = params.get("raf", 0)
            location = params.get("workerlocation", 0)
            raf = FunctionalActivityReport.objects.filter(pk=praf).first()
            workerlocation = WorkerLocation.objects.filter(
                raf=raf, location=location
            ).first()
            if workerlocation:
                if workerlocation.activities.count() == 0:
                    workerlocation.delete()
                else:
                    txt = "Órgão de Execução possui atividades registradas, remoção não permitida."
            else:
                txt = "Órgão de Execução não vinculado ao RAF."
        except Exception as e:
            rst.update(message=str(e))
        else:
            txt = "Órgão de Execução removido com sucesso."
            rst.update(success=True, message=txt)
        self.renderer(rst)

    def importEproc2AthenasRAF(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            initialdate = self.request.POST.get("initialdate")
            finaldate = self.request.POST.get("finaldate")
            instance = int(self.request.POST.get("instancia"))
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            Task.start(
                import_eproc,
                initialdate=initialdate,
                finaldate=finaldate,
                instance=instance,
                employee=employee,
                user=get_current_user().pk,
                success="""<p>Importação concluída com sucesso</p>""",
            )
            ret = True
            message = "A importação foi solicitada com sucesso.<br />Você será avisado ao final da operação."
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=ret, message=message)
        return self.renderer(rst)

    def importEExt2AthenasRAF(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            initialdate = self.request.POST.get("initialdate")
            finaldate = self.request.POST.get("finaldate")
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            Task.start(
                import_eext,
                initialdate=initialdate,
                finaldate=finaldate,
                instance=0,
                employee=employee,
                user=get_current_user().pk,
                success="""<p>Importação concluída com sucesso</p>""",
            )
            ret = True
            message = "A importação foi solicitada com sucesso.<br />Você será avisado ao final da operação."
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=ret, message=message)
        return self.renderer(rst)

    def dropEproc2AthenasRAF(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            month = int(self.request.POST.get("month"))
            year = self.request.POST.get("year")
            instance = self.request.POST.get("instancia")
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            processed = self.request.POST.get("processed")
            Task.start(
                drop_eproc2atheans,
                month=month,
                year=year,
                employee=employee,
                instance=instance,
                processed=processed,
                user=get_current_user().pk,
            )
            ret = True
            message = "A remoção foi solicitada com sucesso.<br />Você será avisado ao final da operação."
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=ret, message=message)
        return self.renderer(rst)

    def dropEExt2AthenasRAF(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            month = int(self.request.POST.get("month"))
            year = self.request.POST.get("year")
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            processed = self.request.POST.get("processed")
            Task.start(
                drop_eext2atheans,
                month=month,
                year=year,
                employee=employee,
                instance=0,
                processed=processed,
                user=get_current_user().pk,
            )
            ret = True
            message = "A remoção foi solicitada com sucesso.<br />Você será avisado ao final da operação."
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=ret, message=message)
        return self.renderer(rst)

    def processRAF(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            month = self.request.POST.get("month")
            year = self.request.POST.get("year")
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            Task.start(
                process_raf,
                month=month,
                year=year,
                employee=employee,
                user=get_current_user().pk,
            )
            ret = True
            message = "O processamento foi solicitado com sucesso.<br />Você será avisado ao final da operação."
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=ret, message=message)
        return self.renderer(rst)

    def defineDate(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            log.info(self.request.POST)
            month = self.request.POST.get("month")
            year = self.request.POST.get("year")
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            generic_date = self.request.POST.get("generic_date")
            action_type = self.request.POST.get("action_type")
            rafs = FunctionalActivityReport.objects.filter(month=month, year=year)
            if employee:
                rafs = rafs.filter(employee=employee)
            for raf in rafs:
                log.info(raf)
                if action_type == "2":
                    raf.open_date = datetime.strptime(generic_date, "%d/%m/%Y")
                    raf.save()
                if action_type == "3":
                    raf.close_date = datetime.strptime(generic_date, "%d/%m/%Y")
                    raf.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Agendamentos realizados com sucesso")
        return self.renderer(rst)

    def recalculateBalanceRAF(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            month = self.request.POST.get("month")
            year = self.request.POST.get("year")
            employee = (
                None
                if self.request.POST.get("employee") == ""
                else int(self.request.POST.get("employee"))
            )
            Task.start(
                recalculate_balance_raf,
                month=month,
                year=year,
                employee=employee,
                user=get_current_user().pk,
            )
            ret = True
            message = "O recálculo dos SALDOS foi solicitado com sucesso.<br />Você será avisado ao final da operação."
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=ret, message=message)
        return self.renderer(rst)

    def send_edoc(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            month = self.request.POST.get("month")
            year = self.request.POST.get("year")
            content = self.request.POST.get("content")

            self._model.send_doc_comunicate(
                month=month, year=year, subject="RAF", content=content
            )

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="E-doc enviado com sucesso.")

        return self.renderer(rst)
