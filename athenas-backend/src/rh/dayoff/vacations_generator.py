# -*- coding: utf-8 -*-

from rh.dayoff.models import AcquisitionPeriod, GroupPeriod, AcquisitionPeriodAttachment
from dateutil.relativedelta import relativedelta
from rh.pvf.const import (
    REGULAR_VACATIONS,
    INDIVIDUAL_VACATION,
    INTERNS_RECESS,
    RESIDENTS_RECESS,
)
from datetime import datetime
from contrib.utils import getLogger


log = getLogger("db")


class VacationsGenerator(object):
    """
    Classe responsável por gerar o períodos aquisitivo de férias individuais e regulamentares
    """

    def server_period_generator(self, employee):
        if self.first_year_period(
            employee.data_exercicio
        ) and not self.check_vacation_aquisition_period(employee, REGULAR_VACATIONS):
            self.generator_of_server_first_year(employee)
        elif not self.first_year_period(
            employee.data_exercicio
        ) and self.last_period_aquisition(employee, REGULAR_VACATIONS):
            self.generator_of_server_with_more_one_year(employee)

    def member_period_generator(self, employee):
        if self.first_year_period(
            employee.data_exercicio
        ) and not self.check_vacation_aquisition_period(employee, INDIVIDUAL_VACATION):
            self.generator_of_member_first_year(employee)
        elif not self.first_year_period(
            employee.data_exercicio
        ) and self.last_period_aquisition(employee, INDIVIDUAL_VACATION):
            self.generator_of_member_with_more_one_year(employee)

    def trainee_period_generator(self, employee):

        if not self.check_vacation_aquisition_period(employee, INTERNS_RECESS):
            self.generator_of_trainee_resident_first_year(employee)

        if self.second_year_period(employee.data_exercicio):
            self.generator_of_trainee_resident_second_year(employee)

    def resident_period_generator(self, employee):

        if not self.check_vacation_aquisition_period(employee, RESIDENTS_RECESS):
            self.generator_of_trainee_resident_first_year(employee)

        if self.second_year_period(employee.data_exercicio):
            self.generator_of_trainee_resident_second_year(employee)

        if self.third_year_period(employee.data_exercicio):
            self.generator_of_trainee_resident_third_year(employee)

    def generator_of_server_first_year(self, employee):
        start_date_acquisition = employee.data_exercicio
        start_date_fruition = start_date_acquisition + relativedelta(years=1)
        end_date_acquisition = (
            start_date_acquisition + relativedelta(years=1) - relativedelta(days=1)
        )
        description = (
            start_date_acquisition.strftime("%d/%m/%Y")
            + " - "
            + end_date_acquisition.strftime("%d/%m/%Y")
        )
        group_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=REGULAR_VACATIONS,
            year_reference=start_date_acquisition.year,
        ).first()

        acquisition_period = AcquisitionPeriod(
            status=2,
            start_date_acquisition=start_date_acquisition,
            start_date_fruition=start_date_fruition,
            end_date_acquisition=end_date_acquisition,
            days=30,
            suspended_days=0,
            description=description,
            group_period=group_period,
            employee=employee,
            real_days_cache=30,
            days_to_enjoy_cache=30,
            days_not_booked_cache=30,
            paid_days_cache=0,
            paid_without_payroll=False,
            indemnified=False,
            note=False,
            pendency=False,
            continuous_period=False,
            blocked=False,
            automatic_created=False,
        )
        acquisition_period.save()
        acquisition_period_attachment = AcquisitionPeriodAttachment(
            date_start=start_date_acquisition,
            date_end=end_date_acquisition,
            description=description,
            days_law=30,
            acquisition_period=acquisition_period,
        )
        acquisition_period_attachment.save()

    def generator_of_server_with_more_one_year(self, employee):
        start_date_acquisition = self.last_period_aquisition(
            employee, REGULAR_VACATIONS
        )
        end_date_acquisition = self.get_end_date_acquisition_more_year(
            start_date_acquisition
        )
        start_date_fruition = end_date_acquisition + relativedelta(days=1)
        description = (
            start_date_acquisition.strftime("%d/%m/%Y")
            + " - "
            + end_date_acquisition.strftime("%d/%m/%Y")
        )
        group_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=REGULAR_VACATIONS,
            year_reference=start_date_acquisition.year,
        ).first()

        acquisition_period = AcquisitionPeriod(
            status=2,
            start_date_acquisition=start_date_acquisition,
            start_date_fruition=start_date_fruition,
            end_date_acquisition=end_date_acquisition,
            days=30,
            suspended_days=0,
            description=description,
            group_period=group_period,
            employee=employee,
            real_days_cache=30,
            days_to_enjoy_cache=30,
            days_not_booked_cache=30,
            paid_days_cache=0,
            paid_without_payroll=False,
            indemnified=False,
            note=False,
            pendency=False,
            continuous_period=False,
            blocked=False,
            automatic_created=False,
        )
        acquisition_period.save()
        acquisition_period_attachment = AcquisitionPeriodAttachment(
            date_start=start_date_acquisition,
            date_end=end_date_acquisition,
            description=description,
            days_law=30,
            acquisition_period=acquisition_period,
        )
        acquisition_period_attachment.save()

    def generator_of_member_first_year(self, employee):
        start_date_acquisition = employee.data_exercicio
        start_date_fruition = start_date_acquisition + relativedelta(years=1)
        end_date_acquisition = (
            start_date_acquisition + relativedelta(years=1) - relativedelta(days=1)
        )
        description = (
            start_date_acquisition.strftime("%d/%m/%Y")
            + " - "
            + end_date_acquisition.strftime("%d/%m/%Y")
        )
        groups_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=INDIVIDUAL_VACATION,
            year_reference=start_date_acquisition.year,
        )

        for group_period in groups_period:
            acquisition_period = AcquisitionPeriod(
                status=2,
                start_date_acquisition=start_date_acquisition,
                start_date_fruition=start_date_fruition,
                end_date_acquisition=end_date_acquisition,
                days=30,
                suspended_days=0,
                description=description,
                group_period=group_period,
                employee=employee,
                real_days_cache=30,
                days_to_enjoy_cache=30,
                days_not_booked_cache=30,
                paid_days_cache=0,
                paid_without_payroll=False,
                indemnified=False,
                note=False,
                pendency=False,
                continuous_period=False,
                blocked=False,
                automatic_created=False,
            )
            acquisition_period.save()

            acquisition_period_attachment = AcquisitionPeriodAttachment(
                date_start=start_date_acquisition,
                date_end=end_date_acquisition,
                description=description,
                days_law=30,
                acquisition_period=acquisition_period,
            )
            acquisition_period_attachment.save()

    def generator_of_member_with_more_one_year(self, employee):
        start_date_acquisition = self.last_period_aquisition(
            employee, INDIVIDUAL_VACATION
        )
        end_date_acquisition = self.get_end_date_acquisition_more_year(
            start_date_acquisition
        )
        start_date_fruition = end_date_acquisition + relativedelta(days=1)
        description = (
            start_date_acquisition.strftime("%d/%m/%Y")
            + " - "
            + end_date_acquisition.strftime("%d/%m/%Y")
        )
        groups_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=INDIVIDUAL_VACATION,
            year_reference=start_date_acquisition.year,
        )

        for group_period in groups_period:
            acquisition_period = AcquisitionPeriod(
                status=2,
                start_date_acquisition=start_date_acquisition,
                start_date_fruition=start_date_fruition,
                end_date_acquisition=end_date_acquisition,
                days=30,
                suspended_days=0,
                description=description,
                group_period=group_period,
                employee=employee,
                real_days_cache=30,
                days_to_enjoy_cache=30,
                days_not_booked_cache=30,
                paid_days_cache=0,
                paid_without_payroll=False,
                indemnified=False,
                note=False,
                pendency=False,
                continuous_period=False,
                blocked=False,
                automatic_created=False,
            )
            acquisition_period.save()

            acquisition_period_attachment = AcquisitionPeriodAttachment(
                date_start=start_date_acquisition,
                date_end=end_date_acquisition,
                description=description,
                days_law=30,
                acquisition_period=acquisition_period,
            )
            acquisition_period_attachment.save()

    def generator_of_trainee_resident_first_year(self, employee):
        # validar data fim de aquisição e fruição
        # criar função para setar o valor parcial quando o tempo de exercício for menor/fracionário

        start_date_acquisition = employee.data_exercicio
        parcial = (
            True
            if employee.termination_date
            and employee.termination_date
            < start_date_acquisition + relativedelta(years=1)
            else False
        )

        start_date_fruition = (
            start_date_acquisition + relativedelta(years=1)
            if not parcial
            else employee.termination_date - relativedelta(months=3)
        )
        end_date_acquisition = (
            start_date_acquisition + relativedelta(years=1) - relativedelta(days=1)
            if not parcial
            else employee.termination_date - relativedelta(days=1)
        )
        end_date_fruition = (
            start_date_fruition + relativedelta(months=4) - relativedelta(days=1)
            if not parcial
            else employee.termination_date - relativedelta(days=1)
        )
        description = (
            start_date_acquisition.strftime("%d/%m/%Y")
            + " - "
            + end_date_acquisition.strftime("%d/%m/%Y")
        )
        fraction_period = None
        if parcial:
            delta = relativedelta(employee.termination_date, start_date_acquisition)
            fraction_period = delta.months + (delta.years * 12)

        sub_type_of_usufruct = (
            RESIDENTS_RECESS if employee.type_by_possession == "RES" else INTERNS_RECESS
        )
        group_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=sub_type_of_usufruct,
            year_reference=start_date_acquisition.year,
        ).first()
        if not AcquisitionPeriod.objects.filter(
            group_period=group_period, employee=employee
        ):
            acquisition_period, created = AcquisitionPeriod.objects.get_or_create(
                status=2,
                start_date_acquisition=start_date_acquisition,
                start_date_fruition=start_date_fruition,
                end_date_acquisition=end_date_acquisition,
                end_date_fruition=end_date_fruition,
                description=description,
                group_period=group_period,
                employee=employee,
                paid_without_payroll=False,
                indemnified=False,
                note=False,
                pendency=False,
                continuous_period=False,
                blocked=False,
                automatic_created=False,
                defaults={
                    "real_days_cache": 30 if not parcial else fraction_period * 2.5,
                    "days_to_enjoy_cache": 30 if not parcial else fraction_period * 2.5,
                    "days_not_booked_cache": (
                        30 if not parcial else fraction_period * 2.5
                    ),
                    "days": 30 if not parcial else fraction_period * 2.5,
                    "suspended_days": 0,
                    "paid_days_cache": 0,
                },
            )
            acquisition_period_attachment = (
                AcquisitionPeriodAttachment.objects.get_or_create(
                    date_start=start_date_acquisition,
                    date_end=end_date_acquisition,
                    description=description,
                    acquisition_period=acquisition_period,
                    defaults={
                        "days_law": 30 if not parcial else fraction_period * 2.5,
                    },
                )
            )

    def generator_of_trainee_resident_second_year(self, employee):

        termination_date = (
            employee.termination_date - relativedelta(days=1)
            if employee.termination_date
            and employee.termination_date
            < employee.data_exercicio + relativedelta(years=2) - relativedelta(days=1)
            else employee.data_exercicio
            + relativedelta(years=2)
            - relativedelta(days=1)
        )
        start_date_acquisition = (
            employee.data_exercicio + relativedelta(years=1) - relativedelta(days=1)
        )
        parcial = (
            True
            if employee.termination_date
            and employee.termination_date
            < start_date_acquisition + relativedelta(years=1)
            else False
        )
        end_date_acquisition = (
            employee.data_exercicio + relativedelta(years=2) - relativedelta(days=1)
            if not parcial
            else employee.termination_date - relativedelta(days=1)
        )

        end_date_fruition = termination_date
        start_date_fruition = end_date_fruition - relativedelta(months=4)
        description = (
            start_date_acquisition.strftime("%d/%m/%Y")
            + " - "
            + end_date_acquisition.strftime("%d/%m/%Y")
        )

        if parcial:
            delta = relativedelta(employee.termination_date, start_date_acquisition)
            fraction_period = delta.months + (delta.years * 12)

        sub_type_of_usufruct = (
            RESIDENTS_RECESS if employee.type_by_possession == "RES" else INTERNS_RECESS
        )
        group_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=sub_type_of_usufruct,
            year_reference=start_date_acquisition.year,
        ).first()
        if not AcquisitionPeriod.objects.filter(
            group_period=group_period, employee=employee
        ):
            acquisition_period, created = AcquisitionPeriod.objects.get_or_create(
                status=2,
                start_date_acquisition=start_date_acquisition,
                start_date_fruition=start_date_fruition,
                end_date_acquisition=end_date_acquisition,
                end_date_fruition=end_date_fruition,
                description=description,
                group_period=group_period,
                employee=employee,
                paid_without_payroll=False,
                indemnified=False,
                note=False,
                pendency=False,
                continuous_period=False,
                blocked=False,
                automatic_created=False,
                defaults={
                    "real_days_cache": 30 if not parcial else fraction_period * 2.5,
                    "days_to_enjoy_cache": 30 if not parcial else fraction_period * 2.5,
                    "days_not_booked_cache": (
                        30 if not parcial else fraction_period * 2.5
                    ),
                    "days": 30 if not parcial else fraction_period * 2.5,
                    "suspended_days": 0,
                    "paid_days_cache": 0,
                },
            )
            acquisition_period_attachment = (
                AcquisitionPeriodAttachment.objects.get_or_create(
                    date_start=start_date_acquisition,
                    date_end=end_date_acquisition,
                    description=description,
                    acquisition_period=acquisition_period,
                    defaults={
                        "days_law": 30 if not parcial else fraction_period * 2.5,
                    },
                )
            )

    def generator_of_trainee_resident_third_year(self, employee):

        termination_date = (
            employee.termination_date - relativedelta(days=1)
            if employee.termination_date
            and employee.termination_date
            < employee.data_exercicio + relativedelta(years=2) - relativedelta(days=1)
            else employee.data_exercicio
            + relativedelta(years=2)
            - relativedelta(days=1)
        )
        start_date_acquisition = (
            employee.data_exercicio + relativedelta(years=2) - relativedelta(days=1)
        )
        parcial = (
            True
            if employee.termination_date
            and employee.termination_date
            < start_date_acquisition + relativedelta(years=1)
            else False
        )
        end_date_acquisition = (
            employee.data_exercicio + relativedelta(years=3) - relativedelta(days=1)
            if not parcial
            else employee.termination_date - relativedelta(days=1)
        )

        end_date_fruition = termination_date
        start_date_fruition = end_date_fruition - relativedelta(months=4)
        description = (
            start_date_acquisition.strftime("%d/%m/%Y")
            + " - "
            + end_date_acquisition.strftime("%d/%m/%Y")
        )

        if parcial:
            delta = relativedelta(employee.termination_date, start_date_acquisition)
            fraction_period = delta.months + (delta.years * 12)

        sub_type_of_usufruct = (
            RESIDENTS_RECESS if employee.type_by_possession == "RES" else INTERNS_RECESS
        )
        group_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=sub_type_of_usufruct,
            year_reference=start_date_acquisition.year,
        ).first()
        if not AcquisitionPeriod.objects.filter(
            group_period=group_period, employee=employee
        ):
            acquisition_period, created = AcquisitionPeriod.objects.get_or_create(
                status=2,
                start_date_acquisition=start_date_acquisition,
                start_date_fruition=start_date_fruition,
                end_date_acquisition=end_date_acquisition,
                end_date_fruition=end_date_fruition,
                description=description,
                group_period=group_period,
                employee=employee,
                paid_without_payroll=False,
                indemnified=False,
                note=False,
                pendency=False,
                continuous_period=False,
                blocked=False,
                automatic_created=False,
                defaults={
                    "real_days_cache": 30 if not parcial else fraction_period * 2.5,
                    "days_to_enjoy_cache": 30 if not parcial else fraction_period * 2.5,
                    "days_not_booked_cache": (
                        30 if not parcial else fraction_period * 2.5
                    ),
                    "days": 30 if not parcial else fraction_period * 2.5,
                    "suspended_days": 0,
                    "paid_days_cache": 0,
                },
            )
            acquisition_period_attachment = (
                AcquisitionPeriodAttachment.objects.get_or_create(
                    date_start=start_date_acquisition,
                    date_end=end_date_acquisition,
                    description=description,
                    acquisition_period=acquisition_period,
                    defaults={
                        "days_law": 30 if not parcial else fraction_period * 2.5,
                    },
                )
            )

    def first_year_period(self, data_exercicio):
        if data_exercicio:
            future_date = data_exercicio + relativedelta(years=1)
            if datetime.today().date() < future_date:
                return True
            else:
                return False

        return False

    def second_year_period(self, data_exercicio):
        if data_exercicio:

            end_first_year = data_exercicio + relativedelta(years=1)
            end_second_year = data_exercicio + relativedelta(years=2)
            if (
                datetime.today().date() > end_first_year
                and datetime.today().date() < end_second_year
            ):
                return True
            else:
                return False

        return False

    def third_year_period(self, data_exercicio):
        if data_exercicio:

            end_second_year = data_exercicio + relativedelta(years=2)
            end_third_year = data_exercicio + relativedelta(years=3)
            if (
                datetime.today().date() > end_second_year
                and datetime.today().date() < end_third_year
            ):
                return True
            else:
                return False

        return False

    def check_end_trainee_date(self, period):
        if period == 1:
            pass
        if period == 2:
            pass
        pass

    def check_vacation_aquisition_period(sefl, employee, type_vacation):
        return AcquisitionPeriod.objects.filter(
            employee=employee,
            group_period__configuration__sub_type_of_usufruct=type_vacation,
        ).exists()

    def last_period_aquisition(self, employee, type_vacation):
        acq_period = (
            AcquisitionPeriod.objects.filter(
                employee=employee,
                group_period__configuration__sub_type_of_usufruct=type_vacation,
            )
            .order_by("-start_date_acquisition")
            .first()
        )
        if acq_period:
            if acq_period.end_date_acquisition < datetime.today().date():
                return acq_period.end_date_acquisition + relativedelta(days=1)
            else:
                return None

        return None

    def get_end_date_acquisition_more_year(self, start_date_acquisition):
        end_date_acquisition = (
            start_date_acquisition + relativedelta(years=1) - relativedelta(days=1)
        )
        if end_date_acquisition.year < 2022:
            return (
                start_date_acquisition + relativedelta(years=1) - relativedelta(days=1)
            )
        else:
            return datetime.strptime(
                f"31/12/{start_date_acquisition.year}", "%d/%m/%Y"
            ).date()
