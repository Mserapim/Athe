import datetime
from openpyxl import load_workbook
from rh.models import *
from rh.gfp.models import *
from standard.models import *


class CNMPReport:
    def __init__(self, task=None, feedback=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.workbook = load_workbook(f"{base_dir}/cnmp_data_report.xlsx")
        self.start_line = 7
        self.filename = (
            f'relatorio_cnmp_{datetime.now().strftime("%d-%m-%Y-%H%M")}.xlsx'
        )
        self.file_path = f"{self.directory_tmp()}/{self.filename}"
        self.configuration = {
            "members": {
                "possession": [
                    "MBR",
                    "MEL",
                    "MCM",
                    "MEC",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                ],
                "sheet_name": "Membros(as)",
                "generator": self.generate_member_report,
            },
            "employees": {
                "possession": ["EFE", "ECM", "EFC", "CMS", "REQ", "RCM", "RFC", "VOL"],
                "sheet_name": "Servidores(as)",
                "generator": self.generate_employee_report,
            },
            "trainee": {
                "possession": ["EST"],
                "sheet_name": "Estagiários(as)",
                "generator": self.generate_trainee_report,
            },
        }
        self.task = task
        self.feedback = feedback

    def generate(self):
        newfile_path = self.file_path
        for config in self.configuration:
            self.print_sheet(config)
        self.workbook.save(newfile_path)
        self.feedback("Concluído", 100)
        print(newfile_path)

    def print_sheet(self, type: str):
        config = self.configuration.get(type)
        sheet_name = config.get("sheet_name")
        sheet = self.workbook[sheet_name]
        employees = Servidor.objects.filter(
            type_by_possession__in=config.get("possession"), ativo=True
        ).order_by("pessoa_fisica__nome")
        total_employees = employees.count()
        sheet["A3"] = (
            f"Total de {sheet_name.upper()}  na Unidade Ministerial: {total_employees}"
        )
        sheet["A4"] = f'DATA DA COLETA DOS DADOS: {datetime.now().strftime("%d/%m/%Y")}'
        if self.feedback:
            message_progress = f"Gerando Arquivo de {sheet_name}"
            self.feedback(message_progress, 1)
        line = 0
        for employee in Servidor.objects.filter(
            type_by_possession__in=config.get("possession"), ativo=True
        ).order_by("pessoa_fisica__nome"):
            if self.feedback:
                progress = (100.0 * float(line + 1)) / float(total_employees)
                self.feedback(message_progress, progress)
            name = employee.pessoa_fisica.nome
            cpf = re.sub("[^0-9,]", "", employee.pessoa_fisica.cpf)
            email = f"{employee.user.username}@mpto.mp.br" if employee.user else 0
            gender = "Feminino" if employee.pessoa_fisica.sexo == "F" else "Masculino"
            social_name = self.have_social_name(employee)
            birth_date = employee.pessoa_fisica.data_nascimento.strftime("%d/%m/%Y")
            color_race = self.get_race_color(employee.pessoa_fisica.raca_cor)
            place_of_birth = str(employee.pessoa_fisica.municipio_naturalidade)
            disease = self.get_disease(employee)
            scholarity = self.get_scholarity(employee.pessoa_fisica.grau_instrucao)
            if not scholarity:
                scholarity = self.get_scholarity_by_jobposition(employee)
            marital_status = self.get_marital_status(
                employee.pessoa_fisica.estado_civil
            )
            sons = self.get_sons(employee)
            job_position = self.get_job_position(employee)
            actuation = self.get_actuation(employee)
            exercise_date = self.get_execise_date(employee)
            salary = str(self.get_remuneration(employee))
            commission_or_function = self.have_commissioned_or_function(employee)
            bond = self.bond_type(employee)
            quota = self.get_quota(employee)
            workplace = self.get_workplace(employee)
            ies = self.get_ies(employee)
            course = self.get_course(employee)

            config.get("generator")(
                {
                    "name": name,
                    "cpf": cpf,
                    "email": email,
                    "gender": gender,
                    "social_name": social_name,
                    "birth_date": birth_date,
                    "color_race": color_race,
                    "place_of_birth": place_of_birth,
                    "disease": disease,
                    "scholarity": scholarity,
                    "marital_status": marital_status,
                    "sons": sons,
                    "job_position": job_position,
                    "actuation": actuation,
                    "exercise_date": exercise_date,
                    "salary": salary,
                    "commission_or_function": commission_or_function,
                    "bond": bond,
                    "quota": quota,
                    "workplace": workplace,
                    "ies": ies,
                    "course": course,
                },
                line,
                sheet,
            )
            line += 1

    def generate_trainee_report(self, data: dict, line: int, sheet):
        sheet[f"A{line + self.start_line}"] = data.get("name")
        sheet[f"B{line + self.start_line}"] = data.get("cpf")
        sheet[f"C{line + self.start_line}"] = data.get("email")
        sheet[f"D{line + self.start_line}"] = data.get("gender")
        sheet[f"E{line + self.start_line}"] = data.get("social_name")
        sheet[f"F{line + self.start_line}"] = data.get("birth_date")
        sheet[f"G{line + self.start_line}"] = data.get("color_race")
        sheet[f"H{line + self.start_line}"] = data.get("place_of_birth")
        sheet[f"I{line + self.start_line}"] = data.get("disease")
        sheet[f"J{line + self.start_line}"] = data.get("scholarity")
        sheet[f"K{line + self.start_line}"] = data.get("marital_status")
        sheet[f"L{line + self.start_line}"] = data.get("sons")
        sheet[f"M{line + self.start_line}"] = data.get("job_position")
        sheet[f"N{line + self.start_line}"] = data.get("exercise_date")
        sheet[f"O{line + self.start_line}"] = data.get("salary")
        sheet[f"P{line + self.start_line}"] = data.get("quota")
        sheet[f"Q{line + self.start_line}"] = data.get("workplace")
        sheet[f"R{line + self.start_line}"] = data.get("course")
        sheet[f"S{line + self.start_line}"] = data.get("ies")

    def generate_employee_report(self, data: dict, line: int, sheet):
        sheet[f"A{line + self.start_line}"] = data.get("name")
        sheet[f"B{line + self.start_line}"] = data.get("cpf")
        sheet[f"C{line + self.start_line}"] = data.get("email")
        sheet[f"D{line + self.start_line}"] = data.get("gender")
        sheet[f"E{line + self.start_line}"] = data.get("social_name")
        sheet[f"F{line + self.start_line}"] = data.get("birth_date")
        sheet[f"G{line + self.start_line}"] = data.get("color_race")
        sheet[f"H{line + self.start_line}"] = data.get("place_of_birth")
        sheet[f"I{line + self.start_line}"] = data.get("disease")
        sheet[f"J{line + self.start_line}"] = data.get("scholarity")
        sheet[f"K{line + self.start_line}"] = data.get("marital_status")
        sheet[f"L{line + self.start_line}"] = data.get("sons")
        sheet[f"M{line + self.start_line}"] = data.get("job_position")
        sheet[f"N{line + self.start_line}"] = data.get("actuation")
        sheet[f"O{line + self.start_line}"] = data.get("exercise_date")
        sheet[f"P{line + self.start_line}"] = data.get("salary")
        sheet[f"Q{line + self.start_line}"] = data.get("commission_or_function")
        sheet[f"R{line + self.start_line}"] = data.get("bond")
        sheet[f"S{line + self.start_line}"] = data.get("quota")
        sheet[f"T{line + self.start_line}"] = data.get("workplace")
        sheet[f"U{line + self.start_line}"] = data.get("course")
        sheet[f"V{line + self.start_line}"] = data.get("ies")

    def generate_member_report(self, data: dict, line: int, sheet):
        sheet[f"A{line + self.start_line}"] = data.get("name")
        sheet[f"B{line + self.start_line}"] = data.get("cpf")
        sheet[f"C{line + self.start_line}"] = data.get("email")
        sheet[f"D{line + self.start_line}"] = data.get("gender")
        sheet[f"E{line + self.start_line}"] = data.get("social_name")
        sheet[f"F{line + self.start_line}"] = data.get("birth_date")
        sheet[f"G{line + self.start_line}"] = data.get("color_race")
        sheet[f"H{line + self.start_line}"] = data.get("place_of_birth")
        sheet[f"I{line + self.start_line}"] = data.get("disease")
        sheet[f"J{line + self.start_line}"] = data.get("scholarity")
        sheet[f"K{line + self.start_line}"] = data.get("marital_status")
        sheet[f"L{line + self.start_line}"] = data.get("sons")
        sheet[f"M{line + self.start_line}"] = data.get("job_position")
        sheet[f"N{line + self.start_line}"] = data.get("actuation")
        sheet[f"O{line + self.start_line}"] = data.get("exercise_date")
        sheet[f"P{line + self.start_line}"] = data.get("salary")
        sheet[f"Q{line + self.start_line}"] = data.get("commission_or_function")
        sheet[f"R{line + self.start_line}"] = data.get("quota")
        sheet[f"S{line + self.start_line}"] = data.get("workplace")
        sheet[f"T{line + self.start_line}"] = data.get("ies")

    @classmethod
    def _cache_path(cls):
        cache_path = getattr(settings, "CACHE", {}).get("cnmp_report", None)
        if not cache_path:
            cache_path = getattr(settings, "CACHE_PATH", None)
            if cache_path:
                cache_path = "%s/cnmp_report" % cache_path
        return cache_path

    @classmethod
    def directory_tmp(cls):
        directory_tmp = cls._cache_path()
        if not os.path.exists(directory_tmp):
            os.mkdir(directory_tmp)
        return directory_tmp

    def have_social_name(self, employee: Servidor):
        if (
            employee.pessoa_fisica.social_name != ""
            and employee.pessoa_fisica.social_name != employee.pessoa_fisica.nome
        ):
            return "Sim"
        return "Não"

    def get_race_color(self, race: int):
        if race == 5:
            return 0
        races = dict(Choice.get_choices_for("rh", "TYPE_RACE"))
        return races.get(race).title()

    def get_scholarity(self, scholarity: int):
        scholarities = {
            8: "Nível superior",
            9: "Especialização",
            10: "Mestrado",
            11: "Doutorado",
            4: "Nível fundamental",
            5: "Nível fundamental",
            6: "Nível médio",
            7: "Nível médio",
        }
        return scholarities.get(scholarity, 0)

    def get_marital_status(self, marital_status: int):
        status = {
            1: "Solteiro(a)",
            2: "Casado(a)/união Estável",
            3: "Viúvo(a)",
            4: "Divorciado(a)/Separado(a)",
            5: "Divorciado(a)/Separado(a)",
            6: "Casado(a)/união Estável",
        }
        return status.get(marital_status, 0)

    def get_sons(self, employee: Servidor):
        eighteen_years_ago_date = datetime.now() - relativedelta(years=18)
        sons = employee.dependentes.filter(
            pessoa_fisica__data_nascimento__gte=eighteen_years_ago_date, tipo=3
        )
        if not sons.exists():
            return "Não"
        sons_age = []
        for son in sons:
            if son.dependencias.filter(tipo=6):
                sons_age.append(f"{son.pessoa_fisica.idade} PCD")
            else:
                sons_age.append(f"{son.pessoa_fisica.idade}")

        return ",".join(sons_age)

    def get_member_jobposition(self, employee):
        if employee.posses_ativas.filter(quadro__cargo__codigo="PROCGERALSUB").exists():
            return "Subprocurador(a) geral"
        if employee.is_procurador:
            return "Procurador(a)"
        return "Promotor(a)"

    def get_employee_jobposition(self, employee: Servidor):
        value = 0
        if employee.type_by_possession == "EST":
            if employee.posses_ativas.filter(
                quadro__cargo__configs__active=True,
                quadro__cargo__configs__educational_level=1,
            ).exists():
                return "Estagiário(a) nível médio"
            if employee.posses_ativas.filter(
                quadro__cargo__configs__active=True,
                quadro__cargo__configs__educational_level=2,
            ).exists():
                return "Estagiário(a) nível superior"
            if employee.posses_ativas.filter(
                quadro__cargo__configs__active=True,
                quadro__cargo__configs__educational_level=3,
            ).exists():
                return "Estagiário(a) nível pós-graduação"
            return value
        if employee.posses_ativas.filter(
            quadro__cargo__configs__active=True,
            quadro__cargo__configs__educational_level=1,
        ).exists():
            return "Servidor(a) cargo nível fundamental"
        if employee.posses_ativas.filter(
            quadro__cargo__configs__active=True,
            quadro__cargo__configs__educational_level=2,
        ).exists():
            return "Servidor(a) cargo nível médio"
        if employee.posses_ativas.filter(
            quadro__cargo__configs__active=True,
            quadro__cargo__configs__educational_level=3,
        ).exists():
            return "Servidor(a) cargo nível superior"
        return value

    def get_scholarity_by_jobposition(self, employee: Servidor):
        if employee.type_by_possession == "EST":
            "Nível médio"
        if employee.posses_ativas.filter(
            quadro__cargo__configs__active=True,
            quadro__cargo__configs__educational_level=1,
        ).exists():
            return "Nível fundamental"
        if employee.posses_ativas.filter(
            quadro__cargo__configs__active=True,
            quadro__cargo__configs__educational_level=2,
        ).exists():
            return "Nível médio"
        if employee.posses_ativas.filter(
            quadro__cargo__configs__active=True,
            quadro__cargo__configs__educational_level=3,
        ).exists():
            return "Nível superior"
        return 0

    def get_job_position(self, employee: Servidor):
        if employee.is_member:
            return self.get_member_jobposition(employee)
        return self.get_employee_jobposition(employee)

    def get_member_actuation(self, employee: Servidor):
        actuations = []
        if employee.is_procurador_geral:
            actuations.append("Procurador-geral")
        if employee.posses_ativas.filter(quadro__cargo__codigo="CG-PGJTO").exists():
            actuations.append("Corregedor-Geral")
        if employee.posses_ativas.filter(quadro__cargo__codigo="89C").exists():
            actuations.append("Conselheiro Superior do Ministério Público")
        if employee.posses_ativas.filter(
            quadro__cargo__codigo__in=["72C", "71C"]
        ).exists():
            actuations.append("Assessor(a)")
        if employee.posses_ativas.filter(quadro__cargo__codigo="OMP").exists():
            actuations.append("Ouvidor(a)")
        if employee.posses_ativas.filter(
            quadro__cargo__codigo__in=["100C", "103C", "104", "101C", "102C"]
        ).exists():
            actuations.append("Coordenador(a) de Centro de Apoio Operacional")
        if employee.posses_ativas.filter(
            quadro__cargo__codigo__in=["2C", "70C", "74C"]
        ).exists():
            actuations.append("Outra Chefia de órgão/serviço auxiliar")

        return ",".join(actuations)

    def get_employee_actuation(self, employee: Servidor):
        if employee.posses_ativas.filter(
            quadro__cargo__codigo__in=["1C", "10C"]
        ).exists():
            return "Diretor(a)"
        if employee.posses_ativas.filter(
            quadro__cargo__nome__contains="ASSESSOR"
        ).exists():
            return "Assessor(a)"
        if employee.posses_ativas.filter(
            quadro__cargo__nome__contains="CHEFE"
        ).exists():
            return "Outra Chefia de órgão/serviço auxiliar"
        return ""

    def get_actuation(self, employee: Servidor):
        if employee.is_member:
            return self.get_member_actuation(employee)
        return self.get_employee_actuation(employee)

    def get_remuneration(self, employee: Servidor):
        if employee.is_voluntary() or employee.situacao_funcional_cache in [
            "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP"
        ]:
            return 0
        last_month = datetime.today() - relativedelta(months=1)
        try:
            tipo_folha_id = 101
            if employee.is_trainee():
                tipo_folha_id = 112
            paycheck = (
                self.get_paycheck_employee(employee)
                if not employee.is_trainee()
                else self.get_paycheck_trainee(employee)
            )
            if not paycheck:
                return 0
            return (
                paycheck.lancamentos.filter(evento__tipo="P", evento__lancamento="F")
                .aggregate(salary=Sum("value"))
                .get("salary")
            )
        except:
            return 0

    def get_paycheck_employee(self, employee: Servidor):
        last_month = datetime.today() - relativedelta(months=1)
        return ContraCheque.objects.get(
            servidor=employee,
            folha__tipo_folha__id=101,
            folha__periodo__mes=last_month.month,
            folha__periodo__ano=last_month.year,
            pensioner=None,
            folha__complement=0,
        )

    def get_paycheck_trainee(self, employee: Servidor):
        last_month = datetime.today() - relativedelta(months=1)
        paycheck = ContraCheque.objects.filter(
            servidor=employee,
            folha__tipo_folha__id=101,
            folha__periodo__mes=last_month.month,
            folha__periodo__ano=last_month.year,
            pensioner=None,
            folha__complement=0,
        )
        if paycheck.exists():
            return paycheck.first()

        return ContraCheque.objects.filter(
            servidor=employee,
            folha__tipo_folha__id=112,
            pensioner=None,
            folha__complement=0,
        ).first()

    def have_commissioned_or_function(self, employee):
        if employee.posses_ativas.filter(
            quadro__cargo__tipo_lei_cargo__in=["EL", "CM", "FC"],
            quadro__cargo__remunerated=True,
        ).exists():
            return "Sim"
        return "Não"

    def bond_type(self, employee: Servidor):
        if employee.situacao_funcional_cache in [
            "ATIVO_AFA_OUT_ORG_ONUS_MP",
            "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
        ]:
            return "Cedido para órgãos de fora do Ministério Público"
        if employee.posses_ativas.filter(quadro__cargo__tipo_lei_cargo__in=["AC"]):
            return "Cedido para dentro do Ministério Público"
        if (
            employee.posses_ativas.filter(quadro__cargo__tipo_lei_cargo__in=["VL"])
            or employee.is_voluntary()
        ):
            return "Voluntário(a)"
        if employee.posses_ativas.filter(quadro__cargo__tipo_lei_cargo__in=["EF"]):
            return "Quadro efetivo"
        if employee.posses_ativas.filter(quadro__cargo__tipo_lei_cargo__in=["CM"]):
            return "Comissionado sem vínculo"
        return 0

    def get_execise_date(self, employee: Servidor):
        if (
            (employee.is_efetivo or employee.is_voluntary())
            or (employee.is_comissionado and not employee.is_requested())
            or employee.is_member
            or employee.is_trainee()
        ):
            return employee.data_exercicio.strftime("%d/%m/%Y")
        if employee.is_requested():
            return (
                employee.get_requestmove_at()
                .first()
                .financial_effect_date.strftime("%d/%m/%Y")
            )
        return 0

    def get_workplace(self, employee: Servidor):
        if employee.get_workplace_only().exists():
            return employee.get_workplace_only().first().lotacao.localidade.ibge
        if employee.work_assignment_effective_exercise.exists():
            return (
                employee.work_assignment_effective_exercise.first().lotacao.localidade.ibge
            )
        return 0

    def get_quota(self, employee: Servidor):
        try:
            if employee.pessoa_fisica.deficiencyinformation:
                if employee.pessoa_fisica.deficiencyinformation.quota:
                    return "Cota para PCD"
            return "Não"
        except Exception:
            return "Não"

    def get_disease(self, employee: Servidor):
        if not employee.pessoa_fisica.necessidades_especiais.exists():
            return "Não"
        if employee.pessoa_fisica.necessidades_especiais.filter(
            nome__contains="Deficiência Física"
        ):
            return "Física"
        if employee.pessoa_fisica.necessidades_especiais.filter(
            nome__contains="Deficiência Auditiva"
        ):
            return "Auditiva"
        if employee.pessoa_fisica.necessidades_especiais.filter(
            nome__contains="Deficiência Visual"
        ):
            return "Visual"
        if employee.pessoa_fisica.necessidades_especiais.filter(
            nome__contains="Deficiência Mental - Limitações nas Habilidades Acadêmicas"
        ):
            return "Intelectual"
        if employee.pessoa_fisica.necessidades_especiais.filter(
            nome__contains="Deficiência Mental"
        ):
            return "Psicossocial"
        return "Não"

    def get_course(self, employee: Servidor):
        if employee.type_by_possession == "EST":
            possession = PossessionTrainee.objects.filter(
                servidor=employee, course_cine_brasil__isnull=False
            ).first()
            if possession:
                return possession.course_cine_brasil.code
            return 0
        if employee.graduation.filter(course_cine_brasil__isnull=False):
            return (
                employee.graduation.filter(course_cine_brasil__isnull=False)
                .last()
                .course_cine_brasil.code
            )
        if employee.graduation.filter().exists():
            return employee.graduation.filter().last().course
        return 0

    def get_ies(self, employee: Servidor):
        if employee.type_by_possession == "EST":
            possession = PossessionTrainee.objects.filter(
                servidor=employee, institution_inep__isnull=False
            ).first()
            if possession:
                return possession.institution_inep.code
            possession = PossessionTrainee.objects.filter(
                servidor=employee, educational_institution__isnull=False
            ).first()
            if possession and possession.educational_institution:
                return possession.educational_institution.nome
            return 0
        if employee.graduation.filter(institution_inep__isnull=False):
            return (
                employee.graduation.filter(institution_inep__isnull=False)
                .last()
                .institution_inep.code
            )
        if employee.graduation.filter().exists():
            return employee.graduation.filter().last().institution
        return 0
