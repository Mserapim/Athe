# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from contrib.daterange import NewDateRange
from contrib.utils import employee_from_user, getLogger, DateUtils
from contrib.decorator import ilru_cache, deprecated
from contrib.middleware import get_current_user
from django.db.models import Q
from datetime import datetime

from rh.dayoff.models import AcquisitionPeriod
from rh.models import Servidor, MovimentacaoSubstituicao
from standard.models import RunCodeManager
from rh.models import Servidor, ServidorLotacao, MovimentacaoRequisicao
from rh.dayoff.models import Usufruct
from rh.dayoff.const import (
    USU_AUTORIZED_CI,
    USU_CANCELED,
    USU_CHANGED,
    USU_CHANGING,
    USU_ENJOYED,
    USU_ENJOYING,
    USU_HOMOLOGATED,
    USU_INTERRUPTED,
    USU_NEW,
    USU_NOT_AUTHORIZED,
    USU_SM,
    USU_SOLD,
    USU_SUBSTITUTE,
    USU_SUSPENDED,
    ACQP_CREATION_CREATED,
    ACQP_CREATION_ERROR,
    ACQP_CREATION_REMOVED,
    ACQP_CREATION_UPDATED,
    ACQP_WAIT,
    ACQP_FINISHED,
)

log = getLogger(__name__)

CREATE_OR_UPDATE = 1
CREATE_IF_NOT_EXIST = 2
DELETE_AND_CREATE = 3


def check_limit(conflicts, limit):
    return len(conflicts) == limit


@RunCodeManager.register("dayoff-base")
class DayOffBase(object):
    typeof = "DAYOFF"
    title = "Código de validações base"
    description = ""

    REMOVE_IF_ZERO_DAYS = False
    CAN_UPDATE_ON_GENETARE = True

    def __init__(self, group_period=None, employee=None, acq_period=None, **kwargs):
        self.group_period = group_period
        self.employee = employee
        self.acq_period = acq_period
        if not self.acq_period and self.group_period and self.employee:
            self.acq_period = self.group_period.acquisitionperiods.filter(
                employee=self.employee
            ).first()
        if self.acq_period:
            if not self.group_period:
                self.group_period = self.acq_period.group_period
            elif self.group_period != self.acq_period.group_period:
                raise Exception("Dados inválidos! Período divergente.")

            if not self.employee:
                self.employee = self.acq_period.employee
            elif self.employee != self.acq_period.employee:
                raise Exception("Dados inválidos! Servidor divergente.")

        self.configure()

    def configure(self):
        pass

    def validate(self, *args, **kwargs):
        self.validate_conflicts(usufruct=kwargs.get("usufruct"))

    def _include_employees_pks_query(self):
        """
        docstring
        """
        return [acqp.employee.pk for acqp in self.group_period.acquisitionperiods.all()]

    def get_acquisition_period_query(self):
        employees_pks = self._include_employees_pks_query()
        q_filter = Q(
            type_by_possession__in=self.group_period.configuration.type_employees.values(
                "cvalue"
            )
        )
        if employees_pks:
            q_filter |= Q(pk__in=employees_pks)
        return Servidor.objects.filter(q_filter)

    def get_acquisition_period_status(self):
        return ACQP_WAIT

    def get_start_date_acquisition(self):
        if self.group_period.start_date_acquisition:
            return self.group_period.start_date_acquisition
        if self.acq_period:
            return self.acq_period.start_date_acquisition
        return None

    def get_end_date_acquisition(self):
        if self.group_period.end_date_acquisition:
            return self.group_period.end_date_acquisition
        if self.acq_period:
            return self.acq_period.end_date_acquisition
        return None

    def get_year_reference(self):
        return self.group_period.year_reference

    def get_start_date_fruition(self):
        return self.group_period.start_date_fruition

    def get_end_date_fruition(self):
        date = self.group_period.end_date_fruition
        if (
            not date
            and self.get_start_date_fruition()
            and self.group_period.configuration.months_max_usufruct
        ):
            date = self.get_start_date_fruition() + relativedelta(
                months=self.group_period.configuration.months_max_usufruct, days=-1
            )
        return date

    def get_previous_period(self):
        return None

    def get_continuous_period(self):
        return True if self.group_period.configuration.continuous_period else False

    def get_blocked(self):
        return (
            self.group_period.blocked
            or self.group_period.year_reference < datetime.now().year
        )

    def get_days(self):
        return self.group_period.configuration.days_per_period

    def get_paid_days(self):
        return 0

    def get_paid_without_payroll(self):
        return False

    def get_indemnified(self):
        return False

    def get_suspended_days(self):
        return 0

    def get_paycheck_event(self):
        return None

    def remove_acquisition_period(self, force_remove=False):

        return {}

    def _initial_defaults_acquisition_period(self):
        acquired_days, info = self.calculate_acquired_days()
        defaults = {
            "start_date_acquisition": self.get_start_date_acquisition(),
            "end_date_acquisition": self.get_end_date_acquisition(),
            "start_date_fruition": self.get_start_date_fruition(),
            "end_date_fruition": self.get_end_date_fruition(),
            # 'days': self.get_days(),
            "days": acquired_days,
            "pendency": True if info else False,
            "info": info,
        }
        if not self.acq_period:
            defaults.update(
                {
                    "status": self.get_acquisition_period_status(),
                    "previous_period": self.get_previous_period(),
                    "continuous_period": self.get_continuous_period(),
                    "blocked": self.get_blocked(),
                    "paid_days_cache": self.get_paid_days(),
                    "paid_without_payroll": self.get_paid_without_payroll(),
                    "indemnified": self.get_indemnified(),
                    "suspended_days": self.get_suspended_days(),
                    "paycheck_event": self.get_paycheck_event(),
                    "automatic_created": True,
                }
            )
        return defaults

    def check_prescribed(self):
        end_date_fruition = self.get_end_date_fruition()
        return end_date_fruition and end_date_fruition < datetime.now().date()

    def validate_substitution(self, start_date, end_date):
        """Este método verifica se existem substituições vigentes no período informado.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        substitutions = MovimentacaoSubstituicao.objects.filter(
            Q(servidor=self.employee)
            & Q(data_inicio__lte=start_date)
            & (Q(data_fim__gte=start_date) | Q(data_fim=None))
        )

        err = ""
        for sub in substitutions[0:3]:
            err += f"Substituição vigente {sub.servidor_substituido} - {sub.afastamento} - {sub}\n"
        if err:
            raise Exception(err)
        return True

    def validate_acquisition_period(self):
        """Este método realiza as validações para criação do período aquisitivo.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        self.validate_acquired_days()
        self.validate_prescribed()
        return True

    def validate_departure_active(self):
        """Este método verifica se existe algum afastamento, que suspende o período aquisitivo(suspend_acquisition_departures), ativo.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        # TODO: VERIFICAR SE ESTE REQUISITO AINDA SERÁ UTILIZADO
        types = [
            v["value"]
            for v in self.group_period.configuration.suspend_acquisition_departures.values(
                "value"
            )
        ]
        departures = self.employee.departures_from_date().filter(tipo__in=types)
        if departures.exists():
            raise Exception(
                f"Servidor {self.employee} possui afastamento ativo: {departures.last()}"
            )
        return True

    def validate_acquired_days(self):
        """Este método verifica se a quantidade de dias adquiridos é 0. Caso seja uma exceção é gerada.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        defaults = self._initial_defaults_acquisition_period()
        if defaults.get("days", 0) == 0:
            info = defaults.get("info")
            if not info:
                info = "Dias adquiridos é igual a 0."
            raise Exception(f"{info}")
        return True

    def validate_prescribed(self):
        """Este método verifica o período aquisitivo está prescrito.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.check_prescribed():
            end_date_fruition = self.get_end_date_fruition()
            end_date_fruition = (
                DateUtils.date_to_str(end_date_fruition) if end_date_fruition else ""
            )
            raise Exception(
                f"Período aquisitivo prescrito, fim de fruição {end_date_fruition}"
            )
        return True

    # @deprecated
    def acquisition_manager(self, start_date=None, end_date=None, task=None):
        """Este método é responsável por rodar a chamada para update_acquisition de todos períodos aquisitivos de um employee.
        O parâmetro de instância employee é obrigatório para que este método funcione.

        Args:
            start_date (datetime.date): data de início de análise dos períodos aquisitivos

        Raise:
            Exception: raise exception quando self.employee não existe
        """
        if not self.employee:
            raise Exception(
                "O parâmetro de instância employee é obrigatório para este método."
            )
        query = AcquisitionPeriod.objects.filter(
            group_period=self.group_period, employee=self.employee
        )
        rs = []
        if start_date:
            query = query.filter(start_date_acquisition__gte=start_date)
        for acqp in query:
            check = (
                NewDateRange(acqp.start_date_acquisition, acqp.end_date_acquisition)
                .intersect(NewDateRange(start_date, end_date))
                .days
                > 0
            )
            if check and acqp.classcode.cls(
                group_period=acqp.group_period, acq_period=acqp
            ).update_acquisition(task=task):
                rs.append(acqp.pk)
        return rs

    # @deprecated
    def update_acquisition(self, task=None):
        """Este método atualiza a aquisição. Caso exista afastamento que influencie na aquisição ela poderá ter a quantidade de dias
        alterada e o estado modificado para Pendência.

        Returns:
            diff(dict): diff do AcquisitionPeriod
        """
        acquired_days, info = self.calculate_acquired_days()
        days = self.acq_period.days
        _diff = {}
        if acquired_days != days or self.acq_period.info != info:
            self.acq_period.days = acquired_days
            self.acq_period.info = info
            self.acq_period.pendency = True if info else False
            self.acq_period.blocked = True if info else False
            self.acq_period.save(validate_prevent=True)
            _diff = self.acq_period.diff
            self.acq_period.update_status(update_usufructs=False, validate_prevent=True)
            log.info(f"{self.employee}: {info}")
        if _diff and task:
            _message = ""
            if _diff.get("pendency"):
                _pendency_new = "Sim" if _diff.get("pendency")[1] else "Não"
                _message = f"Com pendência: {_pendency_new}\n"
            if _diff.get("days"):
                _message = f"{_message}Quantidade de dias mudou de {_diff.get('days')[0]} para {_diff.get('days')[1]}\n"
            if _diff.get("info"):
                _message = f"{_message}Info: {_diff.get('info')[1]}\n"

            if _message:
                _message = (
                    f"Período aquisitivo ({self.acq_period}) atualizado\n{_message}"
                )
                task.info(msg=_message, type_of=2)
        return _diff

    def departures_acqp(self):
        """Este método retorno os afastamentos dos usufrutos: (USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED)

        Returns:
            BaseLicencaAfastamento.queryset
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        if self.acq_period:
            for dep in self.acq_period.usufructs.filter(
                status__in=(USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED)
            ).values("departure"):
                yield dep.get("departure")

    def employee_suspend_acquisition_departure(self, start_date, end_date):
        """Este método retorna um BaseLicencaAfastamento.queryset dos afastamentos que suspendem a aquisição do período aquisitivo.

        Args:
            start_date (date)
            end_date (date)
        Returns:
            BaseLicencaAfastamento.queryset
        """
        types = [
            v["value"]
            for v in self.group_period.configuration.suspend_acquisition_departures.values(
                "value"
            )
        ]
        return (
            self.employee.departures_from_date(start_date=start_date, end_date=end_date)
            .filter(tipo__in=types)
            .exclude(pk__in=[dep for dep in self.departures_acqp()])
        )

    def range_departure_aquisition_suspend(self):
        """Este método retorna um NewDateRange de todos afastamentos que suspendem a aquisição do período aquisitivo.

        Returns:
            NewDateRange
        """
        dr = NewDateRange()
        for dep in self.employee_suspend_acquisition_departure(
            start_date=self.get_start_date_acquisition(),
            end_date=self.get_end_date_acquisition(),
        ):
            dr.add_range(dep.data_inicio, dep.data_fim)
        return dr

    def get_range_exercise(self):
        dr_exercise = NewDateRange()
        # if self.employee.type_by_possession in ('REQ', 'RCM', 'RFC'):
        #     for mov in MovimentacaoRequisicao.objects.filter(servidor=self.employee):
        #         dr_exercise.add_range(mov.data_inicio, mov.data_fim)
        termination_date = self.employee.data_desligamento
        if self.employee.type_by_possession in ("REQ", "RFC", "RCM", "REX"):
            """quando servidor é 'REQ', 'RFC', 'RCM', 'REX', ele possui uma data de previsão de fim"""
            # FIXME: MODIFICAR ESTA ABORDAGEM QUANDO termination_date de 'REQ', 'RFC', 'RCM', 'REX' mudar
            if termination_date and termination_date >= datetime.now().date():
                termination_date = None
            dr_exercise.add_range(self.employee.exercise_date, termination_date)
        else:
            for possession in self.employee.posses:
                dr_exercise.add_range(
                    possession.data_exercicio, possession.data_desligamento
                )
        return dr_exercise

    def calculate_acquired_days(self):
        """Este método calcula a quantidade de dias(get_days) adquiridos considerando os afastamentos que suspendem a aquisição (suspend_acquisition_departures)."""
        info = ""
        days = old_days = self.get_days()
        if self.acq_period and self.acq_period.days > 0:
            old_days = self.acq_period.days

        if self.get_start_date_acquisition():
            dr_acquisition = NewDateRange(
                self.get_start_date_acquisition(), self.get_end_date_acquisition()
            )
            dr_departure = self.range_departure_aquisition_suspend()
            dr_exercise = self.get_range_exercise()
            dr_acquisition = dr_acquisition - dr_departure
            days_intersect_exercise = dr_acquisition.intersect(dr_exercise).days
            days = days_intersect_exercise
            if days != old_days or days == 0:
                info = f"{self.group_period} - A quantidade de dias mudou de {old_days} para {days}."
                if dr_departure.days:
                    info += " Por afastamentos que suspendem a aquisição."
                elif days_intersect_exercise == 0:
                    info += " Servidor foi desligado."
                elif old_days < days:
                    info += " Quantidade de dias aumentou."
        return days, info

    def update_or_create_acquisition_period(self, update_usufructs=True):
        """Este método é realiza update_or_create do Período Aquisitivo.

        Args:
            update_usufructs (bool): True para atualizar os usufrutos do período aquisitivo.

        Returns:
            obj (AcquisitionPeriod): ACQP_CREATION_ERROR ou ACQP_CREATION_UPDATED ou ACQP_CREATION_CREATED
            mode (int):
        """
        obj = None
        mode = ACQP_CREATION_ERROR
        if not self.acq_period:
            self.validate_acquisition_period()
        obj, created = self.group_period.acquisitionperiods.update_or_create(
            employee=self.employee,
            defaults=self._initial_defaults_acquisition_period(),
        )
        mode = ACQP_CREATION_UPDATED if not created else ACQP_CREATION_CREATED
        obj.update_status(validate_prevent=True, update_usufructs=update_usufructs)
        return obj, mode

    def generate_all_acquisition_periods(self, task):
        if self.group_period:

            Klass = self.__class__
            for employee in self.get_acquisition_period_query():
                class_code_acqp = Klass(self.group_period, employee)
                err = None
                try:
                    obj, mode = class_code_acqp.update_or_create_acquisition_period()
                except Exception as e:
                    obj = employee
                    mode = ACQP_CREATION_ERROR
                    err = e
                yield obj, mode, err

    def conflicts(self, usufruct=None, limit=1):
        return len(self.get_conflicts(usufruct=usufruct, limit=limit)) >= 1

    def get_conflicts(self, usufruct=None, limit=1):
        """Este método verifica se existe conflitos para o usufruct informado. Utiliza check_conflicts.
        Utiliza limit para definir quantos conflitos devem ser encontrados.

        Args:
            usufruct (Usufruct): instância de Usufruct
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            (bool): True caso a validação encontre conflitos.
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        conflicts = {}
        # TODO: não produzir conflitos se a data de fim for menor que a data de hoje, não há sentido

        # TODO: LEVAR conflicts_move_substitution, conflicts_substitutes(employee) PARA BASE
        conflicts.update(self.conflicts_agreement(usufruct=usufruct, limit=limit))
        conflicts.update(
            self.conflicts_move_substitution(usufruct=usufruct, limit=limit)
        )
        conflicts.update(self.conflicts_substitutes(usufruct=usufruct, limit=limit))
        print(f"conflicts result {len(conflicts)}")
        # for c in conflicts:
        #     for x in conflicts.get(c):
        #         info = x.get('info')
        #         label_origin = x.get('label_origin')
        #         print(f'{label_origin} - {info}')
        return conflicts

    def validate_conflicts(self, usufruct=None):
        """Este método verifica se existe conflitos para o Usufruct informado. Lançando Exception caso encontre.

        Args:
            usufruct (Usufruct): instância de Usufruct
        Returns:
            (bool): True caso a validação não encontre conflitos.
        Raise:
            Exception: raise exception quando não passa pela validação"""
        self.conflicts_agreement(usufruct=usufruct, raise_exception=True)
        self.conflicts_move_substitution(usufruct=usufruct, raise_exception=True)
        self.conflicts_substitutes(usufruct=usufruct, raise_exception=True)
        return True

    def conflicts_agreement(self, usufruct=None, raise_exception=False, limit=1):
        # antigo conflitos_contratos
        """Este método checa se existe conflitos para o Usufruct informado no sistema de contratos. Retorna os conflitos,
        contudo se raise_exception=True então a Exception é lançada.
        Utiliza limit para definir a quantidade de conflitos devem ser encontrados.

        Args:
            usufruct (Usufruct): instância de Usufruct
            raise_exception (bool): informa se deve gerar Exception quando encontrar conflito
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            conflicts (dict): dicionário com os conflitos encontrados caso a validação encontre conflitos.
                {
                    'pk': 'pk do objeto de origem',
                    'label_origin': 'label de identificação da origem Férias',
                    'employee': 'str do servidor de que conflitou',
                    'info': 'mensagem de erro que será mostrada',
                    'period_conflict': 'str descrevendo o período que conflitou',
                    'days': 'quantidade de dias que conflitou',
                    'created_at': 'quando foi criado',
                    'created_by': 'quem criou',
                    'order': 'ordem de substituição quando existir',
                    'workplace': 'nome do local onde ocorreu o conflito',
                }
        Raise:
            Exception: raise exception quando não passa pela validação"""
        from planejamento.contrato.models import Supervisor

        conflicts = {}
        dr_usufruct = NewDateRange(usufruct.start_date, usufruct.end_date)
        subs = Supervisor.get_employee_substitutes(
            usufruct.employee.matricula, usufruct.start_date, usufruct.end_date
        )
        for sub in subs:
            for emp in Servidor.objects.filter(matricula__in=sub.get("registry", [])):
                usufructs = (
                    Usufruct.objects.exclude(end_date__lt=usufruct.start_date)
                    .exclude(
                        status__in=[
                            USU_CHANGED,
                            USU_SUSPENDED,
                            USU_INTERRUPTED,
                            USU_CANCELED,
                            USU_CANCELED,
                            USU_NOT_AUTHORIZED,
                            USU_SUBSTITUTE,
                        ]
                    )
                    .filter(activity__acquisition_period__employee=emp)
                )
                for u_check in usufructs:
                    days = (
                        NewDateRange(u_check.start_date, u_check.end_date)
                        .intersect(dr_usufruct)
                        .days
                    )
                    if days > 0:
                        period_conflict = "%s à %s" % (
                            DateUtils.date_to_str(u_check.start_date),
                            DateUtils.date_to_str(u_check.end_date),
                        )
                        info = (
                            f"Conflitou ({days}) dias com servidor {emp} do período %s. Contrato substituto em (%s - %s)."
                            % (period_conflict, sub.get("kind"), sub.get("number"))
                        )
                        value = {
                            "pk": u_check.pk,
                            "label_origin": "Contrato - substituto",
                            "employee": f"{emp}",
                            "employee_registry": f"{emp.matricula}",
                            "info": info,
                            "period_conflict": period_conflict,
                            "created_at": DateUtils.date_to_str(u_check.created_at),
                            "created_by": f"{u_check.created_by}",
                            "days": days,
                        }
                        a = conflicts.get(emp.matricula, [])
                        a.append(value)
                        conflicts.update({emp.matricula: a})
                        if raise_exception:
                            raise Exception(info)
                        if check_limit(conflicts, limit):
                            return conflicts
        return conflicts

    def conflicts_departure(self, usufruct=None, raise_exception=False, limit=1):
        # antigo conflitos_afastamento

        # TODO: REMOVER POIS PERDEU O SENTIDO DE CHECAR AFASTAMENTOS QUE JÁ SERÃO CHECADOS NO MOMENTO DE MARCAÇÃO E AUTORIZAÇÃO
        # TODO: REMOVER POIS EXISTE OUTRO MÉTODO QUE OLHA PARA A CONFIGURAÇÃO

        """Este método retorna os conflitos com outros membros/servidores. Retorna array dict caso encontre conflito,
        contudo se raise_exception=True então a Exception é lançada.

        Args:
            usufruct (Usufruct): instância de Usufruct
            raise_exception (bool): informa se deve gerar Exception quando encontrar conflito
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            conflicts (dict): dicionário com os conflitos encontrados caso a validação encontre conflitos.
                {
                    'pk': 'pk do objeto de origem',
                    'label_origin': 'label de identificação da origem Férias',
                    'employee': 'str do servidor de que conflitou',
                    'info': 'mensagem de erro que será mostrada',
                    'period_conflict': 'str descrevendo o período que conflitou',
                    'days': 'quantidade de dias que conflitou',
                    'created_at': 'quando foi criado',
                    'created_by': 'quem criou',
                    'order': 'ordem de substituição quando existir',
                    'workplace': 'nome do local onde ocorreu o conflito',
                }
        Raise:
            Exception: raise exception quando não passa pela validação"""
        from rh.afastamento.models import (
            BaseLicencaAfastamento,
            FeriasAfastamento,
            CANCELED,
        )

        usu_changing = []
        if usufruct.activity.modifieds.exists():
            usu_changing = usufruct.activity.modifieds.all()

        departures = BaseLicencaAfastamento.objects.filter(
            servidor=self.servidor
        ).exclude(estado__in=(CANCELED,))
        departures = FeriasAfastamento.excluir_conflitos(
            servidor=self.servidor,
            query=departures,
            data_inicio=usufruct.start_date,
            data_fim=usufruct.end_date,
            pk=None,
            cancelado=False,
        )
        if departures.exists():
            for old in usu_changing:
                departures = departures.exclude(
                    start_date=old.start_date, data_fim=old.data_fim
                )
        return BaseLicencaAfastamento.verifica_interseccao_periodo(
            self.servidor, usufruct.start_date, usufruct.end_date, departures=departures
        )

    def conflicts_move_substitution(
        self, usufruct=None, raise_exception=False, limit=1
    ):
        # antigo def conflitos_substituicao
        """Este método retorna os conflitos com outros membros/servidores que estão com movimentação de subsituição vigente no mesmo
        período do usufruto.
        Retorna os conflito, contudo se raise_exception=True então a Exception é lançada.

        Args:
            usufruct (Usufruct): instância de Usufruct
            raise_exception (bool): informa se deve gerar Exception quando encontrar conflito
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            conflicts (dict): dicionário com os conflitos encontrados caso a validação encontre conflitos.
                {
                    'pk': 'pk do objeto de origem',
                    'label_origin': 'label de identificação da origem Férias',
                    'employee': 'str do servidor de que conflitou',
                    'info': 'mensagem de erro que será mostrada',
                    'period_conflict': 'str descrevendo o período que conflitou',
                    'days': 'quantidade de dias que conflitou',
                    'created_at': 'quando foi criado',
                    'created_by': 'quem criou',
                    'order': 'ordem de substituição quando existir',
                    'workplace': 'nome do local onde ocorreu o conflito',
                }
        Raise:
            Exception: raise exception quando não passa pela validação"""
        from rh.afastamento.models import BaseLicencaAfastamento

        conflicts = {}
        dr_usufruct = NewDateRange(usufruct.start_date, usufruct.end_date)
        substitutions = BaseLicencaAfastamento.substitutions_conflicts(
            None, usufruct.employee, usufruct.start_date, usufruct.end_date
        )
        for sub in substitutions:
            info = f"Substituindo {sub} - {sub.servidor_substituido}"
            workplace = (
                f"{sub.designation_substituted.lotacao}"
                if sub.designation_substituted
                else ""
            )
            period_conflict = "%s à %s" % (
                DateUtils.date_to_str(sub.data_inicio),
                DateUtils.date_to_str(sub.data_fim) if sub.data_fim else "",
            )
            value = {
                "pk": sub.pk,
                "label_origin": "Substituindo",
                "employee": f"{sub.servidor_substituido}",
                "employee_registry": f"{sub.servidor_substituido.matricula}",
                "info": info,
                "period_conflict": period_conflict,
                "days": NewDateRange(sub.data_inicio, sub.data_fim)
                .intersect(dr_usufruct)
                .days,
                "created_at": DateUtils.date_to_str(sub.created_at),
                "created_by": f"{sub.created_by}",
                "workplace": f"{workplace}",
            }
            _obj = conflicts.get(sub.servidor.matricula, [])
            _obj.append(value)
            conflicts.update({sub.servidor.matricula: _obj})
            if raise_exception:
                raise Exception(info)
            if check_limit(conflicts, limit):
                return conflicts
        return conflicts

    def conflicts_substitutes(self, usufruct=None, raise_exception=False, limit=1):
        """Este método retorna os conflitos com outros membros/servidores utilizando os métodos conflicts_member ou conflicts_employee
        Retorna os conflito, contudo se raise_exception=True então a Exception é lançada.

        Args:
            usufruct (Usufruct): instância de Usufruct
            raise_exception (bool): informa se deve gerar Exception quando encontrar conflito
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            conflicts (dict): dicionário com os conflitos encontrados caso a validação encontre conflitos.
                {
                    'pk': 'pk do objeto de origem',
                    'label_origin': 'label de identificação da origem Férias',
                    'employee': 'str do servidor de que conflitou',
                    'info': 'mensagem de erro que será mostrada',
                    'period_conflict': 'str descrevendo o período que conflitou',
                    'days': 'quantidade de dias que conflitou',
                    'created_at': 'quando foi criado',
                    'created_by': 'quem criou',
                    'order': 'ordem de substituição quando existir',
                    'workplace': 'nome do local onde ocorreu o conflito',
                }
        Raise:
            Exception: raise exception quando não passa pela validação"""
        if self.employee.member_type_by_possession:
            return self.conflicts_member(
                usufruct=usufruct, raise_exception=raise_exception, limit=limit
            )
        return self.conflicts_employee(
            usufruct=usufruct, raise_exception=raise_exception, limit=limit
        )

    @ilru_cache()
    def usufructs_to_check(self):
        """Este método retorna os usufrutos dos servidores que podem conflitar em período de vigência de férias de um mesmo departamento.

        Returns:
            usufructs (querydict): Usufruct querydict.
        """
        """membros"""
        if self.employee.member_type_by_possession:
            return self.usufructs_to_check_member()
        """servidores"""
        return self.usufructs_to_check_employee()

    def usufructs_to_check_employee(self):
        """Este método retorna os usufrutos dos servidores que podem conflitar com o usufruto do servidor que está marcando.
        Busca os usufrutos dos servidores questão no mesmo departamento sem considerar os exercícios em comissões.

        Returns:
            usufructs (querydict): Usufruct querydict.
        """
        work_locations = self.employee.work_locations
        if not work_locations.exists():
            work_locations = self.employee._raw_locations().first()
            work_locations = [work_locations.lotacao] if work_locations else []
        exercises = (
            ServidorLotacao.work_assignment_exercise(
                workplace=[wl.pk for wl in work_locations]
            )
            .exclude(servidor=self.employee)
            .exclude(
                lotacao__pk__in=self.employee.work_assignment.filter(
                    lotacao__in=work_locations
                )
                .filter(commission=True)
                .values("lotacao__pk")
            )
        )
        employees = [
            exer.get("servidor__pk") for exer in exercises.values("servidor__pk")
        ]
        return Usufruct.objects.exclude(
            status__in=[
                USU_CHANGED,
                USU_SUSPENDED,
                USU_NOT_AUTHORIZED,
                USU_SUBSTITUTE,
                USU_INTERRUPTED,
                USU_CANCELED,
                USU_SOLD,
            ]
        ).filter(activity__acquisition_period__employee__pk__in=employees)

    def conflicts_employee(self, usufruct=None, raise_exception=False, limit=1):
        # antigo conflicts(self, pasu, exclude=False):
        """Este método retorna os servidores que conflitam com usufruto informado de acordo com os usufrutos definidos em usufructs_to_check.

        Args:
            usufruct (Usufruct): instância de Usufruct
            raise_exception (bool): informa se deve gerar Exception quando encontrar conflito
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            conflicts (dict): dicionário com os conflitos encontrados caso a validação encontre conflitos.
                {
                    'pk': 'pk do objeto de origem',
                    'label_origin': 'label de identificação da origem Férias',
                    'employee': 'str do servidor de que conflitou',
                    'info': 'mensagem de erro que será mostrada',
                    'period_conflict': 'str descrevendo o período que conflitou',
                    'days': 'quantidade de dias que conflitou',
                    'created_at': 'quando foi criado',
                    'created_by': 'quem criou',
                    'order': 'ordem de substituição quando existir',
                    'workplace': 'nome do local onde ocorreu o conflito',
                }
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        dr_usufruct = NewDateRange(usufruct.start_date, usufruct.end_date)
        conflicts = {}
        for u_check in self.usufructs_to_check().exclude(
            end_date__lt=usufruct.start_date
        ):
            days = (
                NewDateRange(u_check.start_date, u_check.end_date)
                .intersect(dr_usufruct)
                .days
            )
            if days > 0:
                workplace = ""
                period_conflict = "%s à %s" % (
                    DateUtils.date_to_str(u_check.start_date),
                    DateUtils.date_to_str(u_check.end_date),
                )
                info = f"Conflitou ({days}) dias com servidor {u_check.employee} do período {period_conflict}."
                value = {
                    "pk": u_check.pk,
                    "label_origin": "Férias",
                    "employee": f"{u_check.employee}",
                    "employee_registry": f"{u_check.employee.matricula}",
                    "info": info,
                    "period_conflict": period_conflict,
                    "days": days,
                    "created_at": DateUtils.date_to_str(u_check.created_at),
                    "created_by": f"{u_check.created_by}",
                    "order": "",
                    "workplace": f"{workplace}",
                }
                _obj = conflicts.get(u_check.employee.matricula, [])
                _obj.append(value)
                conflicts.update({u_check.employee.matricula: _obj})
                if raise_exception:
                    raise Exception(info)
                if check_limit(conflicts, limit):
                    return conflicts
        return conflicts

    @ilru_cache()
    def _registry_substitutes(self):
        return self.employee.my_substitute_employee_vacation().values_list("matricula")

    def usufructs_to_check_member(self):
        """Este método retorna os usufrutos dos membros que podem conflitar com o usufruto do servidor que está marcando.
        Busca os usufrutos dos servidores questão na tabela de substituição do local onde o membro é titular.

        Returns:
            usufructs (querydict): Usufruct querydict.
        """
        registry_substitutes = self._registry_substitutes()
        usufructs = Usufruct.objects.exclude(
            status__in=[
                USU_CHANGED,
                USU_SUSPENDED,
                USU_NOT_AUTHORIZED,
                USU_SUBSTITUTE,
                USU_INTERRUPTED,
                USU_CANCELED,
                USU_SOLD,
            ]
        )
        if len(registry_substitutes) > 0:
            usufructs = usufructs.filter(
                activity__acquisition_period__employee__matricula__in=registry_substitutes
            )
        else:
            usufructs = usufructs.filter(
                activity__acquisition_period__employee__tipo=self.employee.tipo
            )
        return usufructs

    def conflicts_member(self, usufruct=None, raise_exception=False, limit=1):
        # antigo conflicts(self, pasu, exclude=False):
        """Este método retorna os membros que conflitam com usufruto informado de acordo com os usufrutos definidos
        em usufructs_to_check_member.

        Args:
            usufruct (Usufruct): instância de Usufruct
            raise_exception (bool): informa se deve gerar Exception quando encontrar conflito
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            conflicts (dict): dicionário com os conflitos encontrados caso a validação encontre conflitos.
                {
                    'pk': 'pk do objeto de origem',
                    'label_origin': 'label de identificação da origem Férias',
                    'employee': 'str do servidor de que conflitou',
                    'info': 'mensagem de erro que será mostrada',
                    'period_conflict': 'str descrevendo o período que conflitou',
                    'days': 'quantidade de dias que conflitou',
                    'created_at': 'quando foi criado',
                    'created_by': 'quem criou',
                    'order': 'ordem de substituição quando existir',
                    'workplace': 'nome do local onde ocorreu o conflito',
                }
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        conflicts = self.conflicts_substitutes_member(
            usufruct=usufruct, raise_exception=raise_exception, limit=limit
        )
        conflicts.update(
            self.conflicts_substitutes_member_when_replace(
                usufruct=usufruct,
                raise_exception=raise_exception,
                limit=limit,
                registry_exclude=conflicts.keys(),
            )
        )
        return conflicts

    def conflicts_substitutes_member(
        self, usufruct=None, raise_exception=False, limit=1
    ):
        # antigo conflicts(self, pasu, exclude=False):
        """Este método retorna os membros substitutos, a partir da tabela de substituição, que conflitam com usufruto enviado.

        Args:
            usufruct (Usufruct): instância de Usufruct
            raise_exception (bool): informa se deve gerar Exception quando encontrar conflito
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            conflicts (dict): dicionário com os conflitos encontrados caso a validação encontre conflitos.
                {
                    'pk': 'pk do objeto de origem',
                    'label_origin': 'label de identificação da origem Férias',
                    'employee': 'str do servidor de que conflitou',
                    'info': 'mensagem de erro que será mostrada',
                    'period_conflict': 'str descrevendo o período que conflitou',
                    'days': 'quantidade de dias que conflitou',
                    'created_at': 'quando foi criado',
                    'created_by': 'quem criou',
                    'order': 'ordem de substituição quando existir',
                    'workplace': 'nome do local onde ocorreu o conflito',
                }
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        dr_usufruct = NewDateRange(usufruct.start_date, usufruct.end_date)
        conflicts = {}
        for u_check in self.usufructs_to_check().exclude(
            end_date__lt=usufruct.start_date
        ):
            days = (
                NewDateRange(u_check.start_date, u_check.end_date)
                .intersect(dr_usufruct)
                .days
            )
            if days > 0:
                # TODO: OTIMIZAR ESSES DOIS FOR
                for employee_workplace in (
                    self.employee.my_replacement_employee_workplace_vacation()
                    .filter(servidor__matricula=u_check.employee.matricula)
                    .values("lotacao", "servidor")
                ):
                    for rpl in self.employee.my_replacement_substitute_vacation(
                        workplace=employee_workplace.get("lotacao"),
                        employee=employee_workplace.get("servidor"),
                    ):
                        workplace = rpl.replaced
                        period_conflict = "%s à %s" % (
                            DateUtils.date_to_str(u_check.start_date),
                            DateUtils.date_to_str(u_check.end_date),
                        )
                        info = f"Conflitou ({days}) dias com servidor {u_check.employee} do período {period_conflict}."
                        value = {
                            "pk": u_check.pk,
                            "label_origin": "Substituto",
                            "employee": f"{u_check.employee}",
                            "employee_registry": f"{u_check.employee.matricula}",
                            "info": info,
                            "period_conflict": period_conflict,
                            "days": days,
                            "created_at": DateUtils.date_to_str(u_check.created_at),
                            "created_by": f"{u_check.created_by}",
                            "order": rpl.order,
                            "workplace": f"{workplace}",
                        }
                        _obj = conflicts.get(u_check.employee.matricula, [])
                        if not self._check_duplicity(_obj, value):
                            _obj.append(value)
                            conflicts.update({u_check.employee.matricula: _obj})
                        if raise_exception:
                            raise Exception(info)
                        if check_limit(conflicts, limit):
                            return conflicts
        return conflicts

    @classmethod
    def _check_duplicity(cls, conflicts, new):
        exists = False
        for conflict in conflicts:
            if conflict.get("employee_registry") == new.get(
                "employee_registry"
            ) and conflict.get("workplace") == new.get("workplace"):
                exists = True
                break
        return exists

    def _registry_employee_when_replace(self, registry_exclude=[]):
        """Este método retorna as matrículas dos servidores dos locais onde o servidor substitui.

        Returns:
            (array): matrículas
        """
        # TODO: ANALISAR SE É POSSÍVEL FAZER CACHE EM where_substitute_employee_vacation
        return [
            emp.matricula
            for emp in self.employee.where_substitute_employee_vacation()
            if emp.matricula not in registry_exclude
        ]

    def chek_conflicts_when_replace(self, usufruct, registry_substitute=[], limit=1):
        # antigo chek_conflicts_when_replace
        """Este método checa se existe conflitos com os locais onde substitui e todos os substitutos estão em conflito.

        :return: list of PeriodoAquisitivoServidorUsufruto
        :rtype: list of PeriodoAquisitivoServidorUsufruto
        """
        # TODO: este método deve ir pro validade
        conflitos = []
        _check_conflitct = self._search_conflict(pasu, registry=registry_substitute)
        registry_conflicted = []
        for _check in _check_conflitct:
            if _check.pas.servidor.matricula not in registry_conflicted:
                registry_conflicted.append(_check.pas.servidor.matricula)

        """condição para gerar conflitos: todos os substitutos terem férias agendadas"""
        if len(registry_conflicted) >= len(registry_substitute):
            conflitos += _check_conflitct

        return conflitos

    def _search_conflict(
        self, usufruct=None, raise_exception=False, limit=1, registry=[]
    ):
        """
        Este método checa conflitos de um usufruto com usufrutos de uma matrícula informada.

        Args:

        """
        usufructs = Usufruct.objects.exclude(
            status__in=[
                USU_CHANGED,
                USU_SUSPENDED,
                USU_NOT_AUTHORIZED,
                USU_SUBSTITUTE,
                USU_INTERRUPTED,
                USU_CANCELED,
                USU_SOLD,
            ]
        ).exclude(activity__acquisition_period__employee=self.employee)
        usufructs = usufructs.filter(
            activity__acquisition_period__employee__matricula__in=registry
        )
        conflicts = {}
        dr_usufruct = NewDateRange(usufruct.start_date, usufruct.end_date)
        for u_check in usufructs.exclude(end_date__lt=usufruct.start_date):
            dr_usu = NewDateRange(u_check.start_date, u_check.end_date)
            days = dr_usu.intersect(dr_usufruct).days
            if days > 0:
                period_conflict = "%s à %s" % (
                    DateUtils.date_to_str(u_check.start_date),
                    DateUtils.date_to_str(u_check.end_date),
                )
                info = f"Conflitou ({days}) dias com servidor {u_check.employee} do período {period_conflict}."
                value = {
                    "pk": u_check.pk,
                    "employee": f"{u_check.employee}",
                    "employee_registry": f"{u_check.employee.matricula}",
                    "info": info,
                    "period_conflict": period_conflict,
                    "days": days,
                    "created_at": DateUtils.date_to_str(u_check.created_at),
                    "created_by": f"{u_check.created_by}",
                    "order": "",
                    "workplace": "",
                }
                _obj = conflicts.get(u_check.employee.matricula, [])
                _obj.append(value)
                conflicts.update({u_check.employee.matricula: _obj})
                if raise_exception:
                    raise Exception(info)
                if check_limit(conflicts, limit):
                    return conflicts
        return conflicts

    def conflicts_substitutes_member_when_replace(
        self, usufruct=None, raise_exception=False, limit=1, registry_exclude=[]
    ):
        """Este método retorna os servidores que conflitam em período de vigência de férias de um mesmo departamento.

        Args:
            usufruct (Usufruct): instância de Usufruct
            raise_exception (bool): informa se deve gerar Exception quando encontrar conflito
            limit (int): limite máximo de conflitos que devem ser encontrados
        Returns:
            conflicts (dict): dicionário com os conflitos encontrados caso a validação encontre conflitos.
                {
                    'pk': 'pk do objeto de origem',
                    'label_origin': 'label de identificação da origem Férias',
                    'employee': 'str do servidor de que conflitou',
                    'info': 'mensagem de erro que será mostrada',
                    'period_conflict': 'str descrevendo o período que conflitou',
                    'days': 'quantidade de dias que conflitou',
                    'created_at': 'quando foi criado',
                    'created_by': 'quem criou',
                    'order': 'ordem de substituição quando existir',
                    'workplace': 'nome do local onde ocorreu o conflito',
                }
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        registry_substituted = self._registry_employee_when_replace(
            registry_exclude=registry_exclude
        )
        conflicts = self._search_conflict(
            usufruct=usufruct,
            raise_exception=raise_exception,
            limit=limit,
            registry=registry_substituted,
        )
        for conflict in conflicts:
            for (
                employee_workplace
            ) in self.employee.where_substitute_employee_workplace_vacation().filter(
                servidor__matricula=conflict
            ):
                for rpl in self.employee.where_replacement_substitute_vacation(
                    workplace=employee_workplace.lotacao,
                    employee=employee_workplace.servidor,
                ):
                    workplace = f"{rpl.replaced}"
                    _obj = conflicts.get(conflict, [])
                    for _value in _obj:
                        _value.update(
                            {
                                "label_origin": "Substituindo",
                                "order": rpl.order,
                                "workplace": f"{workplace}",
                            }
                        )
                        if raise_exception:
                            raise Exception(_value.get("info"))
                    if check_limit(conflicts, limit):
                        return conflicts
        return conflicts
