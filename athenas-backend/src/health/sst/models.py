# -*- coding: utf-8 -*-

from django.db import models

from datetime import date

from contrib.utils import DateUtils
from health.models import Exam
from health.const import NOT_SUPPLIED, YES_OP, NO_OP
from standard.models import AuditTimestampModel, Choice, ListDatedModel


class WorkAccidentCommunication(AuditTimestampModel):
    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="workaccidentecommunication",
        on_delete=models.CASCADE,
    )
    accident_date = models.DateTimeField("Data e hora do acidente")
    type_accident = models.PositiveSmallIntegerField(
        "Tipo de acidente",
        default=1,
        choices=Choice.get_choices_for("sst", "TYPE_ACCIDENT"),
    )
    work_hours_before_accident = models.CharField(
        "Horas trabalhadas antes do acidente", max_length=4, null=True, blank=True
    )
    type_cat = models.PositiveSmallIntegerField(
        "Tipo da CAT", default=1, choices=Choice.get_choices_for("sst", "TYPE_CAT")
    )
    death = models.BooleanField("Indicativo de óbito", default=False, blank=True)
    death_date = models.DateTimeField("Data do óbito", null=True, blank=True)
    police_communication = models.BooleanField(
        "Comunicação à polícia", default=False, blank=True
    )
    causer_agent_accident = models.ForeignKey(
        "CauserAgentAccident",
        verbose_name="Agente causador",
        related_name="workaccidentecommunication",
        on_delete=models.PROTECT,
    )
    initiator_cat = models.PositiveSmallIntegerField(
        "Quem iniciou a CAT",
        default=1,
        choices=Choice.get_choices_for("sst", "INITIATOR_CAT"),
    )
    note_cat = models.CharField("Observação CAT", max_length=999, null=True, blank=True)
    last_work_date = models.DateField("Último dia trabalhado", null=True, blank=True)
    leave_work_accident = models.PositiveSmallIntegerField(
        "Afastamento do trabalho",
        default=1,
        choices=Choice.get_choices_for("sst", "YES_NO_NOT_SUPPLIED"),
    )

    type_address_accident = models.PositiveSmallIntegerField(
        "Tipo de local do acidente",
        default=1,
        choices=Choice.get_choices_for("sst", "TYPE_ADDRES_ACCIDENT"),
    )

    address_description = models.CharField(
        "Descrição do local do acidente", max_length=255, null=True, blank=True
    )
    address = models.ForeignKey(
        "rh.Endereco",
        verbose_name="Endereço do acidente",
        related_name="workaccidentecommunication",
        on_delete=models.PROTECT,
    )

    body_part = models.ForeignKey(
        "BodyPart",
        verbose_name="Parte do corpo atingida",
        related_name="workaccidentecommunication",
        on_delete=models.PROTECT,
    )
    laterality = models.PositiveSmallIntegerField(
        "Lateralidade", default=1, choices=Choice.get_choices_for("sst", "LATERALITY")
    )

    causer_agent = models.ForeignKey(
        "CauserAgent",
        verbose_name="Agente causador",
        related_name="workaccidentecommunication",
        on_delete=models.PROTECT,
    )

    attest_date = models.DateTimeField("Data e horário de atendimento")
    hospitalization = models.BooleanField("Internação", default=False, blank=True)
    duration_treatment = models.SmallIntegerField("Duração estimada do tratamento")
    leave_work_treatment = models.PositiveSmallIntegerField(
        "Afastamento do trabalho para tratamento",
        default=1,
        choices=Choice.get_choices_for("sst", "YES_NO_NOT_SUPPLIED"),
    )
    nature_injury = models.ForeignKey(
        "Injury",
        verbose_name="Natureza da lesão",
        related_name="workaccidentecommunication",
        on_delete=models.PROTECT,
    )
    nature_injury_description = models.CharField(
        "Descrição da natureza da lesão", max_length=200, null=True, blank=True
    )
    diagnosis = models.CharField(
        "Provável diagnóstico", max_length=100, null=True, blank=True
    )
    cid = models.CharField("CID", max_length=4)  # TODO: UTILIZAR TABELA DO CID????
    note_attest = models.CharField("Observação", max_length=255, null=True, blank=True)
    doctor_attest = models.ForeignKey(
        "rh.PessoaFisica",
        verbose_name="Médico atestado",
        related_name="workaccidentecommunication",
        on_delete=models.PROTECT,
    )
    previous = models.ForeignKey(
        "WorkAccidentCommunication",
        verbose_name="CAT anterior",
        related_name="workaccidentecommunication",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Comunicação de Acidente de Trabalho"
        ordering = ("accident_date", "employee")
        unique_together = ("accident_date", "type_accident", "employee")

    def __str__(self):
        return f"{self.employee}: {DateUtils.datetime_to_str(self.accident_date)}"

    def validate_accident_date(self):
        """Hora do acidente, no formato HHMM.
        Validação:
            Preenchimento obrigatório se tpAcid = [1] ou se(tpAcid=[3] e dtAcid >= [2022-01-26]).
            Não informar se tpAcid = [2].
            Se preenchida, deve estar no intervalo entre[0000] e[2359], criticando inclusive a segunda parte
                do número, que indica os minutos, que deve ser menor ou igual a 59.
            Se tpCat = [2, 3], deve ser informado valor igual ao preenchido no evento de CAT anterior,
                quando informado em nrRecCatOrig."""
        hours = self.accident_date.strftime("%H%M").replace(":", "")
        if (
            self.type_accident == 1
            or (
                self.type_accident == 3
                and self.accident_date.date() >= date(2022, 1, 26)
            )
        ) and hours == "0000":
            raise Exception(
                f"Quando {self.get_type_accident_display()} é necessário informar {self._meta.get_field('accident_date').verbose_name}"
            )
        elif self.type_accident == 2 and hours != "0000":
            raise Exception(
                f"Quando {self.get_type_accident_display()} não é necessário informar {self._meta.get_field('accident_date').verbose_name}"
            )
        return True

    def validate_doctor_test(self):
        professional_council = self.doctor_attest.professional_council
        if not professional_council:
            raise Exception(
                "É obrigatório documento de Conselho: CRM, CRO ou RMS para médico."
            )
        elif not professional_council.professional_council_issuer:
            raise Exception(
                "É obrigatório documento de Conselho com emissor: CRM, CRO ou RMS para médico."
            )
        elif professional_council.professional_council_issuer.valor not in (
            "CRM",
            "CRO",
            "RMS",
        ):
            raise Exception(
                "É obrigatório documento de Conselho com emissor: CRM, CRO ou RMS para médico."
            )
        elif not professional_council.numero:
            raise Exception(
                "É obrigatório número de documento de Conselho: CRM, CRO ou RMS para médico."
            )
        elif len(professional_council.numero) > 14:
            raise Exception(
                "É obrigatório número de documento de Conselho menor que 15 para médico."
            )
        elif not professional_council.estado_expedicao:
            raise Exception(
                "É obrigatório UF de expedição de documento de Conselho para médico."
            )
        return True

    def validate_cid(self):
        if len(self.cid) not in (3, 4):
            raise Exception("CID deve ter tamanho entre 3 e 4.")
        return True

    def validate_work_hours_before_accident(self):
        """Horas trabalhadas antes da ocorrência do acidente, no formato HHMM.
        Validação: Preenchimento obrigatório se tpAcid = [1] ou se(tpAcid=[3] e dtAcid >= [2022-07-20]).
        Não informar se tpAcid = [2]. Se preenchida, deve estar no intervalo entre[0000] e[9959],
         criticando inclusive a segunda parte do número, que indica os minutos, que deve ser menor ou igual a 59.
        """
        hours = self.work_hours_before_accident
        if (
            self.type_accident == 1
            or (
                self.type_accident == 3
                and self.accident_date.date() >= date(2022, 7, 20)
            )
        ) and (len(hours) > 4 or len(hours) < 4):
            message = f"Quando {self.get_type_accident_display()}"
            message += f" é necessário informar {self._meta.get_field('work_hours_before_accident').verbose_name}"
            raise Exception(message)
        elif self.type_accident == 2 and hours:
            message = f"Quando {self.get_type_accident_display()}"
            message += f"não é necessário informar {self._meta.get_field('work_hours_before_accident').verbose_name}"
            raise Exception(message)

        if not self.work_hours_before_accident.isdigit():
            raise Exception(
                f"É necessário informar {self._meta.get_field('work_hours_before_accident').verbose_name} com dígitos"
            )
        return True

    def validate_last_work_date(self):
        """Validação:
        Preenchimento obrigatório se {dtAcid} >= [2023-01-16]).
        Se informada, deve ser uma data igual ou anterior à data atual e igual ou posterior à data de admissão do trabalhador.
        """
        if self.accident_date.date() >= date(2023, 1, 16) and not self.last_work_date:
            raise Exception(
                f"É necessário informar {self._meta.get_field('last_work_date').verbose_name}"
            )
        if self.type_cat == 2 and not self.last_work_date:
            raise Exception(
                f"É necessário informar {self._meta.get_field('last_work_date').verbose_name}"
            )
        return True

    def validate_death(self):
        """Houve óbito? Valores válidos: S - Sim N - Não Validação:
        Se o tpCat for igual a [3], o campo deverá sempre ser preenchido com [S].
        Se o tpCat for igual a [2], o campo deverá sempre ser preenchido com [N]."""
        if self.type_cat == 3 and not self.death:
            raise Exception(
                f"É necessário marcar {self._meta.get_field('death').verbose_name}"
            )
        elif self.type_cat == 2 and self.death:
            raise Exception(
                f"É necessário desmarcar {self._meta.get_field('death').verbose_name}"
            )
        return True

    def validate_death_date(self):
        """Data do óbito. Validação: Deve ser uma data válida, igual ou posterior a dtAcid e igual ou anterior à data atual.
        Preenchimento obrigatório e exclusivo se indCatObito = [S]."""
        if self.death and not self.death_date:
            raise Exception(
                f"É necessário informar {self._meta.get_field('death_date').verbose_name}"
            )

        if self.death_date and self.death_date < self.accident_date:
            message = f"É necessário informar {self._meta.get_field('death_date').verbose_name} maior ou igual"
            message += f"a {self._meta.get_field('accident_date').verbose_name}"
            raise Exception(message)
        return True

    def validate_leave_work_accident(self):
        """Houve afastamento? Valores válidos: S - Sim N - Não Validação: Preenchimento obrigatório se dtAcid >= [2023-01-16])."""
        if (
            self.accident_date.date() >= date(2023, 1, 16)
            and self.leave_work_accident is NOT_SUPPLIED
        ):
            raise Exception(
                f"É necessário informar {self._meta.get_field('leave_work_accident').verbose_name}"
            )
        return True

    def validate_leave_work_treatment(self):
        """Indicativo de afastamento do trabalho durante o tratamento.
        Valores válidos: S - Sim N - Não Validação:
            Se o campo indCatObito for igual a [S], o campo deve sempre ser preenchido com [N].
        """
        if self.death and self.leave_work_treatment in (YES_OP, NO_OP):
            raise Exception(
                f"É necessário desmarcar {self._meta.get_field('leave_work_treatment').verbose_name}"
            )
        return True

    def validate_address(self):
        if not self.address:
            message = (
                f"É necessário informar {self._meta.get_field('address').verbose_name}"
            )
            message += f" quando {self.get_type_address_accident_display()}"
            raise Exception(message)
        return True

    def validate_address_cep(self):
        """Código de Endereçamento Postal - CEP. Validação:
        Preenchimento obrigatório se tpLocal = [1, 3, 5].
        Não preencher se tpLocal = [2].
        Se preenchido, deve ser informado apenas com números, com 8 (oito) posições."""
        if self.type_address_accident in (1, 3, 5):
            self.validate_address()
            if self.address and not self.address.cep:
                message = f"É necessário informar CEP de {self._meta.get_field('address').verbose_name}"
                message += f" quando {self.get_type_address_accident_display()}"
                raise Exception(message)
        return True

    def validate_address_cod_munic(self):
        """Preencher com o código do município, conforme tabela do IBGE. Validação:
        Preenchimento obrigatório se tpLocal = [1, 3, 4, 5].
        Não preencher se tpLocal = [2].
        Se informado, deve ser um código válido e existente na tabela do IBGE."""
        if self.type_address_accident in (1, 3, 4, 5):
            self.validate_address()
            if self.address and not self.address.municipio.ibge:
                message = f"É necessário informar Código do IBGE de {self._meta.get_field('address').verbose_name}"
                message += f" quando {self.get_type_address_accident_display()}"
                raise Exception(message)
        return True

    def validate_address_uf(self):
        """Preencher com a sigla da Unidade da Federação - UF.
        Valores válidos: AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO
        Validação:
        Preenchimento obrigatório se tpLocal = [1, 3, 4, 5].
        Não preencher se tpLocal = [2]."""
        if self.type_address_accident in (1, 3, 4, 5):
            self.validate_address()
            if self.address and not self.address.municipio.estado.sigla:
                message = f"É necessário informar UF de {self._meta.get_field('address').verbose_name}"
                message += f" quando {self.get_type_address_accident_display()}"
                raise Exception(message)
        return True

    def save(self, *args, **kargs):
        self.validate_accident_date()
        self.validate_doctor_test()
        self.validate_cid()
        self.validate_work_hours_before_accident()
        self.validate_last_work_date()
        self.validate_death()
        self.validate_death_date()
        self.validate_leave_work_accident()
        self.validate_address_cep()
        self.validate_address_cod_munic()
        self.validate_address_uf()
        super(WorkAccidentCommunication, self).save(*args, **kargs)


class CauserAgentQuerySet(models.QuerySet):
    def get_by_natural_key(self, code, *args):
        return self.get(code=code)


class CauserAgent(AuditTimestampModel):
    code = models.CharField(max_length=10, verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=800, verbose_name="Descrição", default="", blank=True
    )

    objects = CauserAgentQuerySet.as_manager()

    class Meta:
        verbose_name = "Agente Causador do Acidente de Trabalho"

    def __str__(self):
        return f"{self.code}: {self.title}"

    def natural_key(self):
        return self.code


class CauserAgentAccidentQuerySet(models.QuerySet):
    def get_by_natural_key(self, code, *args):
        return self.get(code=code)


class CauserAgentAccident(AuditTimestampModel):

    code = models.CharField(max_length=10, verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=800, verbose_name="Descrição", default="", blank=True
    )

    objects = CauserAgentAccidentQuerySet.as_manager()

    class Meta:
        verbose_name = "Agente Causador ou Situação do Acidente de Trabalho"

    def __str__(self):
        return f"{self.code}: {self.title}"

    def natural_key(self):
        return self.code


class BodyPartQuerySet(models.QuerySet):
    def get_by_natural_key(self, code, *args):
        return self.get(code=code)


class BodyPart(AuditTimestampModel):

    code = models.CharField(max_length=10, verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=800, verbose_name="Descrição", default="", blank=True
    )

    objects = BodyPartQuerySet.as_manager()

    class Meta:
        verbose_name = "Parte do corpo atingida"

    def __str__(self):
        return f"{self.code}: {self.title}"

    def natural_key(self):
        return self.code


class InjuryQuerySet(models.QuerySet):
    def get_by_natural_key(self, code, *args):
        return self.get(code=code)


class Injury(AuditTimestampModel):

    code = models.CharField(max_length=10, verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=800, verbose_name="Descrição", default="", blank=True
    )

    objects = InjuryQuerySet.as_manager()

    class Meta:
        verbose_name = "Lesão"

    def __str__(self):
        return f"{self.code}: {self.title}"

    def natural_key(self):
        return self.code


class MonitorOccupationalHealth(AuditTimestampModel):
    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="monitoroccupationalhealth",
        on_delete=models.CASCADE,
    )
    monitoring_date = models.DateTimeField("Data")
    type_aso = models.PositiveSmallIntegerField(
        "Tipo", default=99, choices=Choice.get_choices_for("sst", "TYPE_ASO")
    )
    result = models.BooleanField("Resultado", default=False, blank=True)

    doctor = models.ForeignKey(
        "rh.PessoaFisica",
        verbose_name="Médico ASO",
        related_name="monitoroccupationalhealth",
        on_delete=models.PROTECT,
    )
    doctor_manager = models.ForeignKey(
        "rh.PessoaFisica",
        verbose_name="Médico PCMSO",
        related_name="monitoroccupationalhealth_doctormanager",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Monitoramento da Saúde do Trabalhador"
        ordering = ("employee",)

    def __str__(self):
        return f"{self.employee}: {DateUtils.datetime_to_str(self.monitoring_date)}"

    def validate_doctor_test(self):
        professional_council = self.doctor.professional_council
        if not professional_council:
            raise Exception("É obrigatório documento de Conselho: CRM, CRO ou RMS.")
        elif not professional_council.professional_council_issuer:
            raise Exception(
                "É obrigatório documento de Conselho com emissor: CRM, CRO ou RMS."
            )
        elif professional_council.professional_council_issuer.valor not in (
            "CRM",
            "CRO",
            "RMS",
        ):
            raise Exception(
                "É obrigatório documento de Conselho com emissor: CRM, CRO ou RMS."
            )
        elif not professional_council.numero:
            raise Exception(
                "É obrigatório número de documento de Conselho: CRM, CRO ou RMS."
            )
        elif len(professional_council.numero) > 14:
            raise Exception(
                "É obrigatório número de documento de Conselho menor que 15."
            )
        elif not professional_council.estado_expedicao:
            raise Exception("É obrigatório UF de expedição de documento de Conselho.")
        return True

    def validate_doctor_manager_test(self):
        if self.doctor_manager:
            professional_council = self.doctor_manager.professional_council
            if not professional_council:
                raise Exception("É obrigatório documento de Conselho: CRM, CRO ou RMS.")
            elif not professional_council.professional_council_issuer:
                raise Exception(
                    "É obrigatório documento de Conselho com emissor: CRM, CRO ou RMS."
                )
            elif professional_council.professional_council_issuer.valor not in (
                "CRM",
                "CRO",
                "RMS",
            ):
                raise Exception(
                    "É obrigatório documento de Conselho com emissor: CRM, CRO ou RMS."
                )
            elif not professional_council.numero:
                raise Exception(
                    "É obrigatório número de documento de Conselho: CRM, CRO ou RMS."
                )
            elif len(professional_council.numero) > 14:
                raise Exception(
                    "É obrigatório número de documento de Conselho menor que 15."
                )
            elif not professional_council.estado_expedicao:
                raise Exception(
                    "É obrigatório UF de expedição de documento de Conselho."
                )
        return True

    def save(self, *args, **kargs):
        self.validate_doctor_test()
        self.validate_doctor_manager_test()
        super(MonitorOccupationalHealth, self).save(*args, **kargs)

    def release(self):
        """Este método muda o result para True.

        Returns:

        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        self.result = True
        if self.diff:
            self.save()


class ExamSst(Exam):
    monitor_occupational_health = models.ForeignKey(
        MonitorOccupationalHealth,
        verbose_name="Monitoração de saúde",
        related_name="examsst",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def save(self, *args, **kargs):
        self.employee = self.monitor_occupational_health.employee
        super(ExamSst, self).save(*args, **kargs)


class HarmfulAgentQuerySet(models.QuerySet):
    def get_by_natural_key(self, code, *args):
        return self.get(code=code)


class HarmfulAgent(AuditTimestampModel):
    code = models.CharField(max_length=10, verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=800, verbose_name="Descrição", default="", blank=True
    )

    objects = HarmfulAgentQuerySet.as_manager()

    class Meta:
        verbose_name = "Agente Nocivo"

    def __str__(self):
        return f"{self.code}: {self.title}"

    def natural_key(self):
        return self.code


class EnvironmentWorkingCondition(ListDatedModel, AuditTimestampModel):

    OVERLAP_FIELDS = ["workplace", "type_environment", "description_departament"]

    workplace = models.ForeignKey(
        "rh.lotacao",
        verbose_name="Lotação",
        related_name="environmentworkingcondition",
        on_delete=models.PROTECT,
    )
    responsible = models.ForeignKey(
        "rh.PessoaFisica",
        verbose_name="Responsável",
        related_name="environmentworkingcondition",
        on_delete=models.PROTECT,
    )
    type_environment = models.PositiveSmallIntegerField(
        "Tipo de ambiente",
        default=1,
        choices=Choice.get_choices_for("sst", "TYPE_ENVIRONMENT"),
    )
    description_departament = models.CharField(
        "Descrição do lugar administrativo", max_length=100
    )

    # TODO: DEFINIR LOTAÇÃO TRIBUTÁRIA

    class Meta:
        verbose_name = "Condição Ambiental de Trabalho"

    def __str__(self):
        return f"{self.get_type_environment_display()}: {self.description_departament}"


class Epi(AuditTimestampModel):
    code = models.CharField(max_length=255, verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=999, verbose_name="Descrição", default="", blank=True
    )

    class Meta:
        verbose_name = "EPI"

    def __str__(self):
        return f"{self.code}: {self.title}"

    def natural_key(self):
        return self.code


class EnvironmentHarmfulAgent(AuditTimestampModel):
    environment_working_condition = models.ForeignKey(
        EnvironmentWorkingCondition,
        verbose_name="Condição Ambiental de Trabalho",
        related_name="environmentharmfulagent",
        on_delete=models.PROTECT,
    )
    harmful_agent = models.ForeignKey(
        HarmfulAgent,
        verbose_name="Agente Nocivo",
        related_name="harmfulagent",
        on_delete=models.PROTECT,
    )
    epis = models.ManyToManyField(
        Epi, verbose_name="EPI", related_name="environmentharmfulagent", blank=True
    )
    type_evaluation = models.PositiveSmallIntegerField(
        "Tipo de avaliação do agente nocivo.",
        default=99,
        choices=Choice.get_choices_for("sst", "TYPE_EVALUATION"),
    )
    intensity = models.DecimalField(
        "Intensidade, concentração ou dose da exposição",
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )
    limit = models.DecimalField(
        "Limite de tolerância calculado para agentes específicos",
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )
    measure_unit = models.PositiveSmallIntegerField(
        "Dose ou unidade de medida da intensidade ou concentração do agente.",
        default=1,
        choices=Choice.get_choices_for("sst", "MEASURE_UNIT"),
    )
    measurement = models.CharField(
        "Técnica utilizada para medição da intensidade ou concentração",
        max_length=100,
        null=True,
        blank=True,
    )
    description = models.CharField(
        "Descrição do agente nocivo", max_length=100, null=True, blank=True
    )

    epc = models.PositiveSmallIntegerField(
        "Implementa medidas de proteção coletiva(EPC)",
        default=99,
        choices=Choice.get_choices_for("sst", "TYPE_EPC"),
    )
    efficiency_epc = models.BooleanField(
        "Os EPCs são eficazes na neutralização do risco ao trabalhador?",
        default=False,
        blank=True,
    )
    epi = models.PositiveSmallIntegerField(
        "Utilização de EPI",
        default=99,
        choices=Choice.get_choices_for("sst", "TYPE_EPI"),
    )
    efficiency_epi = models.BooleanField(
        "Os EPIs são eficazes na neutralização do risco ao trabalhador?",
        default=False,
        blank=True,
    )
    implement_protection = models.BooleanField(
        "Foi tentada a implementação de medidas de proteção coletiva?",
        default=False,
        blank=True,
    )
    working_condition = models.BooleanField(
        "Foram observadas as condições de funcionamento do EPI?",
        default=False,
        blank=True,
    )
    uninterrupted_use = models.BooleanField(
        "Foi observado o uso ininterrupto do EPI ao longo do tempo?",
        default=False,
        blank=True,
    )
    expiry_date_on_purchase = models.BooleanField(
        "Foi observado o prazo de validade do CA no momento da compra do EPI?",
        default=False,
        blank=True,
    )
    change_frequency = models.BooleanField(
        "É observada a periodicidade de troca?", default=False, blank=True
    )
    sanitation = models.BooleanField(
        "É observada a higienização conforme orientação do fabricante nacional ou importador?",
        default=False,
        blank=True,
    )
    note = models.CharField("Observação", max_length=999, null=True, blank=True)

    class Meta:
        verbose_name = "Agente Nocivo do Ambiente"

    def __str__(self):
        return f"{self.environment_working_condition}: {self.harmful_agent}"

    def validate_type_evaluation(self):
        """Tipo de avaliação do agente nocivo. Valores válidos:
        1 - Critério quantitativo
        2 - Critério qualitativo
        Validação: Preenchimento obrigatório e exclusivo se codAgNoc for diferente de[09.01.001].
        """
        if self.harmful_agent.code != "09.01.001" and self.type_evaluation == 99:
            raise Exception(
                f"É necessário informar {self._meta.get_field('type_evaluation').verbose_name}"
            )

    def validate_intensity(self):
        """Intensidade, concentração ou dose da exposição do trabalhador ao agente nocivo cujo critério de avaliação seja quantitativo.
        Validação: Preenchimento obrigatório e exclusivo se tpAval = [1]."""
        if self.type_evaluation == 1 and not self.intensity:
            raise Exception(
                f"É necessário informar {self._meta.get_field('intensity').verbose_name}"
            )
        elif self.type_evaluation != 1 and self.intensity:
            raise Exception(
                f"Não informe {self._meta.get_field('intensity').verbose_name}"
            )

    def validate_limit(self):
        """Limite de tolerância calculado para agentes específicos, conforme técnica de medição exigida na legislação.
        Validação: Preenchimento obrigatório e exclusivo se tpAval = [1] e codAgNoc = [01.18.001, 02.01.014].
        """
        if (
            self.type_evaluation == 1
            and self.harmful_agent.code in ("01.18.001", "02.01.014")
            and not self.limit
        ):
            raise Exception(
                f"É necessário informar {self._meta.get_field('limit').verbose_name}"
            )
        elif (
            self.type_evaluation != 1
            and self.harmful_agent.code not in ("01.18.001", "02.01.014")
            and self.limit
        ):
            raise Exception(f"Não informe {self._meta.get_field('limit').verbose_name}")

    def validate_measure_unit(self):
        """Dose ou unidade de medida da intensidade ou concentração do agente.
        Validação: Preenchimento obrigatório e exclusivo se tpAval = [1]."""
        if self.type_evaluation == 1 and (
            not self.measure_unit or self.measure_unit == 99
        ):
            raise Exception(
                f"É necessário informar {self._meta.get_field('measure_unit').verbose_name}"
            )
        elif self.type_evaluation not in (1, 99) and self.measure_unit != 99:
            raise Exception(
                f"Não informe {self._meta.get_field('measure_unit').verbose_name}"
            )

    def validate_measurement(self):
        """Técnica utilizada para medição da intensidade ou concentração.
        Validação: Preenchimento obrigatório e exclusivo se tpAval = [1]."""
        if self.type_evaluation == 1 and not self.measurement:
            raise Exception(
                f"É necessário informar {self._meta.get_field('measurement').verbose_name}"
            )
        elif self.type_evaluation != 1 and self.measurement:
            raise Exception(
                f"Não informe {self._meta.get_field('measurement').verbose_name}"
            )

    def validate_description(self):
        """Validação: Preenchimento obrigatório se codAgNoc =
        [01.01.001, 01.02.001, 01.03.001, 01.04.001, 01.05.001,
         01.06.001, 01.07.001, 01.08.001, 01.09.001, 01.10.001,
         01.12.001, 01.13.001, 01.14.001, 01.15.001, 01.16.001,
         01.17.001, 01.18.001, 05.01.001]."""
        if self.harmful_agent.code in (
            "01.01.001",
            "01.02.001",
            "01.03.001",
            "01.04.001",
            "01.05.001",
            "01.06.001",
            "01.07.001",
            "01.08.001",
            "01.09.001",
            "01.10.001",
            "01.12.001",
            "01.13.001",
            "01.14.001",
            "01.15.001",
            "01.16.001",
            "01.17.001",
            "01.18.001",
            "05.01.001",
        ):
            raise Exception(
                f"É necessário informar {self._meta.get_field('description').verbose_name}"
            )

    def save(self, *args, **kargs):
        self.validate_type_evaluation()
        self.validate_intensity()
        self.validate_limit()
        self.validate_measure_unit()
        self.validate_measurement()
        super(EnvironmentHarmfulAgent, self).save(*args, **kargs)


class ExposureEmployeeEnvironment(ListDatedModel, AuditTimestampModel):

    OVERLAP_FIELDS = ["employee", "environment_working_condition"]

    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="exposureemployeeenvironment",
        on_delete=models.CASCADE,
    )

    # TODO: MODIFICAR PARA MANYTOMANY AFIM DE ATENDER À MODELAGEM DO ESOCIAL, APENAS PARA AVULSOS!!!
    environment_working_condition = models.ForeignKey(
        EnvironmentWorkingCondition,
        verbose_name="Condição Ambiental de Trabalho",
        related_name="exposureemployeeenvironment",
        on_delete=models.PROTECT,
    )
    description_activity = models.CharField("Descrição das atividade", max_length=999)

    class Meta:
        verbose_name = "Exposição do Servidor"

    def __str__(self):
        message = f"{self.environment_working_condition}: {self.employee} - {DateUtils.date_to_str(self.start_validity)}"
        if self.end_validity:
            message += f" -> {DateUtils.date_to_str(self.start_validity)}"
        return message
