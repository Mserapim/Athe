import datetime
from rh.models import *
from rh.gfp.models import *
from standard.models import *


members = ["MBR", "MEL", "MCM", "MEC", "MBR2", "MEL2", "MCM2", "MEC2"]
employees = ["EFE", "ECM", "EFC", "CMS", "REQ", "RCM", "RFC", "VOL"]
trainee = ["EST"]


def have_social_name(employee):
    if (
        employee.pessoa_fisica.social_name != ""
        and employee.pessoa_fisica.social_name != employee.pessoa_fisica.nome
    ):
        return "Sim"
    return "Não"


def get_race_color(race):
    if race == 5:
        return 0
    races = dict(Choice.get_choices_for("rh", "TYPE_RACE"))
    return races.get(race).title()


def get_scholarity(scholarity):
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


def get_marital_status(marital_status):
    status = {
        1: "Solteiro(a)",
        2: "Casado(a)/união Estável",
        3: "Viúvo(a)",
        4: "Divorciado(a)/Separado(a)",
        5: "Divorciado(a)/Separado(a)",
        6: "Casado(a)/união Estável",
    }
    return status.get(marital_status, 0)


def get_sons(employee):
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


def get_member_jobposition(employee):
    if employee.posses_ativas.filter(quadro__cargo__codigo="PROCGERALSUB").exists():
        return "Subprocurador(a) geral"
    if employee.is_procurador:
        return "Procurador(a)"
    return "Promotor(a)"


def get_employee_jobposition(employee):
    if employee.type_by_possession == "EST":
        return "Estagiário(a) nível superior"
    if employee.posses_ativas.filter(
        quadro__cargo__configs__active=True, quadro__cargo__configs__educational_level=1
    ).exists():
        return "Servidor(a) cargo nível fundamental"
    if employee.posses_ativas.filter(
        quadro__cargo__configs__active=True, quadro__cargo__configs__educational_level=2
    ).exists():
        return "Servidor(a) cargo nível médio"
    if employee.posses_ativas.filter(
        quadro__cargo__configs__active=True, quadro__cargo__configs__educational_level=3
    ).exists():
        return "Servidor(a) cargo nível superior"
    return 0


def get_scholarity_by_jobposition(employee):
    if employee.type_by_possession == "EST":
        "Nível médio"
    if employee.posses_ativas.filter(
        quadro__cargo__configs__active=True, quadro__cargo__configs__educational_level=1
    ).exists():
        return "Nível fundamental"
    if employee.posses_ativas.filter(
        quadro__cargo__configs__active=True, quadro__cargo__configs__educational_level=2
    ).exists():
        return "Nível médio"
    if employee.posses_ativas.filter(
        quadro__cargo__configs__active=True, quadro__cargo__configs__educational_level=3
    ).exists():
        return "Nível superior"
    return 0


def get_job_position(employee):
    if employee.is_member:
        return get_member_jobposition(employee)
    return get_employee_jobposition(employee)


def get_member_actuation(employee):
    actuations = []
    if employee.is_procurador_geral:
        actuations.append("Procurador-geral")
    if employee.posses_ativas.filter(quadro__cargo__codigo="CG-PGJTO").exists():
        actuations.append("Corregedor-Geral")
    if employee.posses_ativas.filter(quadro__cargo__codigo="89C").exists():
        actuations.append("Conselheiro Superior do Ministério Público")
    if employee.posses_ativas.filter(quadro__cargo__codigo__in=["72C", "71C"]).exists():
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


def get_employee_actuation(employee):
    if employee.posses_ativas.filter(quadro__cargo__codigo__in=["1C", "10C"]).exists():
        return "Diretor(a)"
    if employee.posses_ativas.filter(quadro__cargo__nome__contains="ASSESSOR").exists():
        return "Assessor(a)"
    if employee.posses_ativas.filter(quadro__cargo__nome__contains="CHEFE").exists():
        return "Outra Chefia de órgão/serviço auxiliar"
    return ""


def get_actuation(employee):
    if employee.is_member:
        return get_member_actuation(employee)
    return get_employee_actuation(employee)


def get_remuneration(employee):
    if employee.is_voluntary() or employee.situacao_funcional_cache in [
        "ATIVO_AFA_OUT_ORG_ONUS_MP",
        "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
    ]:
        return 0
    last_month = datetime.today() - relativedelta(months=1)
    try:
        tipo_folha_id = 101
        if employee.is_trainee():
            tipo_folha_id = 112
        paycheck = (
            get_paycheck_employee(employee)
            if not employee.is_trainee()
            else get_paycheck_trainee(employee)
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


def get_paycheck_employee(employee):
    last_month = datetime.today() - relativedelta(months=1)
    return ContraCheque.objects.get(
        servidor=employee,
        folha__tipo_folha__id=101,
        folha__periodo__mes=last_month.month,
        folha__periodo__ano=last_month.year,
        pensioner=None,
        folha__complement=0,
    )


def get_paycheck_trainee(employee):
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


def have_commissioned_or_function(employee):
    if employee.posses_ativas.filter(
        quadro__cargo__tipo_lei_cargo__in=["EL", "CM", "FC"],
        quadro__cargo__remunerated=True,
    ).exists():
        return "Sim"
    return "Não"


def bond_type(employee):
    if employee.situacao_funcional_cache in [
        "ATIVO_AFA_OUT_ORG_ONUS_MP",
        "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
    ]:
        return "cedido para órgãos de fora do Ministério Público"
    if employee.posses_ativas.filter(quadro__cargo__tipo_lei_cargo__in=["AC"]):
        return "cedido para dentro do Ministério Público"
    if (
        employee.posses_ativas.filter(quadro__cargo__tipo_lei_cargo__in=["VL"])
        or employee.is_voluntary()
    ):
        return "voluntário(a)"
    if employee.posses_ativas.filter(quadro__cargo__tipo_lei_cargo__in=["EF"]):
        return "quadro efetivo"
    if employee.posses_ativas.filter(quadro__cargo__tipo_lei_cargo__in=["CM"]):
        return "comissionado sem vínculo"
    return 0


def get_execise_date(employee):
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


def get_workplace(employee):
    if employee.get_workplace_only().exists():
        return employee.get_workplace_only().first().lotacao.localidade.ibge
    if employee.work_assignment_effective_exercise.exists():
        return (
            employee.work_assignment_effective_exercise.first().lotacao.localidade.ibge
        )
    return 0


def get_quota(employee):
    try:
        if employee.pessoa_fisica.deficiencyinformation:
            if employee.pessoa_fisica.deficiencyinformation.quota:
                return "Cota para PCD"
        return "Não"
    except Exception:
        return "Não"


def get_disease(employee):
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


def get_course(employee):
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


def get_ies(employee):
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


def print_sheet(type_by_possession, type):
    f = open(f"{type}.txt", "w")
    employees = Servidor.objects.filter(
        type_by_possession__in=type_by_possession, ativo=True
    ).order_by("pessoa_fisica__nome")
    print(f"Total: {employees.count()}")
    for employee in Servidor.objects.filter(
        type_by_possession__in=type_by_possession, ativo=True
    ).order_by("pessoa_fisica__nome"):
        name = employee.pessoa_fisica.nome
        cpf = re.sub("[^0-9,]", "", employee.pessoa_fisica.cpf)
        email = f"{employee.user.username}@mpto.mp.br" if employee.user else 0
        gender = "Feminino" if employee.pessoa_fisica.sexo == "F" else "Masculino"
        social_name = have_social_name(employee)
        birth_date = employee.pessoa_fisica.data_nascimento.strftime("%d/%m/%Y")
        color_race = get_race_color(employee.pessoa_fisica.raca_cor)
        place_of_birth = str(employee.pessoa_fisica.municipio_naturalidade)
        disease = get_disease(employee)
        scholarity = get_scholarity(employee.pessoa_fisica.grau_instrucao)
        if not scholarity:
            scholarity = get_scholarity_by_jobposition(employee)
        marital_status = get_marital_status(employee.pessoa_fisica.estado_civil)
        sons = get_sons(employee)
        job_position = get_job_position(employee)
        actuation = get_actuation(employee)
        exercise_date = get_execise_date(employee)
        salary = get_remuneration(employee)
        commission_or_function = have_commissioned_or_function(employee)
        bond = str(bond_type(employee)).capitalize()
        quota = get_quota(employee)
        workplace = get_workplace(employee)
        ies = get_ies(employee)
        course = get_course(employee)

        if type == "EST":
            f.write(
                f"{name};{cpf};{email};{gender};{social_name};{birth_date};{color_race};{place_of_birth};{disease};{scholarity};{marital_status};{sons};{job_position};{exercise_date};{salary};{quota};{workplace};{course};{ies}\n"
            )
        elif type == "SER":
            f.write(
                f"{name};{cpf};{email};{gender};{social_name};{birth_date};{color_race};{place_of_birth};{disease};{scholarity};{marital_status};{sons};{job_position};{actuation};{exercise_date};{salary};{commission_or_function};{bond};{quota};{workplace};{course};{ies};\n"
            )
        elif type == "MEM":
            f.write(
                f"{name};{cpf};{email};{gender};{social_name};{birth_date};{color_race};{place_of_birth};{disease};{scholarity};{marital_status};{sons};{job_position};{actuation};{exercise_date};{salary};{commission_or_function};{quota};{workplace};{ies}\n"
            )
