# -*- coding: utf-8 -*-
print("ATHENAS LOAD")
from rh.models import *
from contrib.middleware import get_current_user, set_current_user, StartupLoader
import codecs
import json
from judicial.models import *
from judicial.management.commands.load_infra_conf import *


def scritp_gd_transition_judicial():

    try:
        file_employee = codecs.open(
            "%s/employee_chief_imediate.csv" % settings.CACHE_PATH, "w", "utf-8"
        )
        buf = ""
        employees = Servidor.objects.filter(ativo=True)
        for employee in employees:
            buf1 = "%s|%s\n" % (
                employee.matricula,
                employee.chefe_imediato.matricula if employee.chefe_imediato else None,
            )
            # print buf1
            buf += buf1
        file_employee.write(buf)
        file_employee.close()
    except Exception as err:
        print(str(err))

    conf_ejud()
    align_substitute_to_responsability()
    workplace_change_reponsible_from_substitution()
    show_members()

    try:
        print(
            "\n--------Servidores que mudaram de chefe imediato a pós os SCRIPTS---------------\n"
        )
        count = 0
        file_employee = codecs.open(
            "%s/employee_chief_imediate.csv" % settings.CACHE_PATH, "r"
        )
        for line in file_employee.readlines():
            employees = line.split("|")
            employee = Servidor.objects.get(matricula=employees[0])
            employee_chief_imediate_old = employees[1].replace("\n", "")
            employee_chief_imediate_old = int(employees[1].replace("None", "0"))
            employee_chief_imediate_new = (
                employee.chefe_imediato.matricula
                if employee.chefe_imediato and employee.chefe_imediato.matricula
                else 0
            )
            if employee_chief_imediate_old != employee_chief_imediate_new:
                print("Servidor: %s" % employee)
                for location in employee.work_locations:
                    print(location.__str__responsible__())
                print(
                    "Chefe anterior: %s"
                    % Servidor.objects.get(matricula=employee_chief_imediate_old)
                )
                print(
                    "Chefe novo: %s"
                    % Servidor.objects.get(matricula=employee_chief_imediate_new)
                )
                count += 1
                print("-----------------------")
        print(count)
    except Exception as err:
        print(str(err))


def conf_ejud():
    print("""Configurações EJUD""")

    manager = Manager(verbose=True)

    manager.set_workplace_configurations()

    manager.load_workplace_responsible_from_file_gen()

    manager.load_responsible_from_file_gen()

    manager.load_responsible_from_substitution_member()

    manager.load_responsible_from_inativation_member()

    manager.call_update_situation_employee_workplace()

    manager.set_work_assignment_to_substitution()

    # PARA colocar apenas exercicio pleno em produção não deve realizar o comando abaixo
    # manager.call_update_substitution_member()

    # manager.call_update_situation_employee_workplace()


def align_substitute_to_responsability():
    """
    A partir da substituição.
    """
    count = 0
    today = datetime.now().date()
    query = Q(data_inicio__lte=today) & Q(Q(data_fim__gte=today) | Q(data_fim=None))
    movs = MovimentacaoSubstituicaoMembro.objects.filter(query)
    for substitution in movs:
        print("--------------------------------")
        print(substitution)
        workplace = None
        job_position = Cargo.objects.filter(
            cargo_arquimedes=substitution.cargo_arquimedes
        )
        if job_position.exists():
            workplace = job_position.latest("pk").lotacao_responsavel
            if workplace:
                print("Substituído:", substitution.servidor_substituido)
                print("Substituto:", substitution.servidor)
                print("workplace:", workplace)
                if workplace.responsavel != substitution.servidor:
                    # Lotacao.objects.filter(pk=workplace).update(responsavel=substitution.servidor, responsible_substituted=substitution.servidor_substituido)
                    workplace.update_responsible(responsible_new=substitution.servidor)
                    Lotacao.objects.filter(pk=workplace).update(
                        responsible_substituted=substitution.servidor_substituido
                    )
                    workplace = Lotacao.objects.get(pk=workplace)
                    print(
                        "Novo Responsável",
                        workplace.responsavel,
                        "-> Responsável substituído",
                        workplace.responsible_substituted,
                    )
                    count += 1
    print("\nSubstituições ativas:", movs.count())
    print("\nSubstituições que mudaram o chefe:", count)


def workplace_change_reponsible_from_substitution():
    """
    A partir da lotação, descobrindo se existe movimentacao para
    aquele período ou se o substituto deve ser o servidor de posse do local.
    """
    today = datetime.now().date()
    for workplace in Lotacao.objects.filter(~Q(responsible_substituted=None)):
        substitute = None
        job_position = (
            workplace.cargo_responsavel.latest("pk")
            if workplace.cargo_responsavel.exists()
            else None
        )
        substitutions = None
        if job_position:
            substitutions = MovimentacaoSubstituicaoMembro.objects.filter(
                servidor_substituido=workplace.responsible_substituted,
                cargo_arquimedes=job_position.cargo_arquimedes,
            ).filter(
                Q(data_inicio__lte=today) & (Q(data_fim__gte=today) | Q(data_fim=None))
            )
            substitute = (
                substitutions.latest("pk").servidor if substitutions.exists() else None
            )
        # print workplace, "==", workplace.responsavel, "==", workplace.responsible_substituted
        may_change = False
        if substitutions and substitutions.exists():
            if substitute != workplace.responsavel:
                may_change = True
                print(
                    workplace,
                    "==",
                    workplace.responsavel,
                    "==",
                    workplace.responsible_substituted,
                )
                print("-->SUBSTITUTE:", substitute)
        else:
            may_change = True
        if may_change:
            if substitute:
                print("DEVE MUDAR O RESPONSAVEL")
                print(
                    workplace,
                    "==",
                    workplace.responsavel,
                    "==",
                    workplace.responsible_substituted,
                )
                print("1 - MUDARÁ PARA:", substitute)
                workplace.update_responsible(responsible_new=substitute)
                break
            print("DEVE MUDAR O RESPONSAVEL")
            print(
                workplace,
                "==",
                workplace.responsavel,
                "==",
                workplace.responsible_substituted,
            )
            print(workplace.cargo_responsavel.filter())
            if workplace.cargo_responsavel.exists():
                possession = MovimentacaoPosse.objects.filter(
                    servidor=workplace.responsible_substituted,
                    quadro__cargo=workplace.cargo_responsavel.latest("pk"),
                    ativo=True,
                )
                if possession.exists():
                    print(
                        possession.latest("pk"),
                        " - ESTÁ ATIVO? ",
                        possession.latest("pk").servidor.afastamento_ativo(),
                    )
                    if not possession.latest("pk").servidor.afastamento_ativo():
                        print("2 - MUDARÁ PARA:", possession.latest("pk").servidor)
                        workplace.update_responsible(
                            responsible_new=possession.latest("pk").servidor
                        )
                else:
                    possession = MovimentacaoPosse.objects.filter(
                        quadro__cargo=workplace.cargo_responsavel.latest("pk"),
                        ativo=True,
                    )
                    if possession.exists():
                        print(
                            possession.latest("pk"),
                            " - ESTÁ ATIVO? ",
                            possession.latest("pk").servidor.afastamento_ativo(),
                        )
                        if not possession.latest("pk").servidor.afastamento_ativo():
                            print("3 - MUDARÁ PARA:", possession.latest("pk").servidor)
                            workplace.update_responsible(
                                responsible_new=possession.latest("pk").servidor
                            )
            print("------------------------------------------------")
    set_workplace_responsible_substituted_to_none()


def set_workplace_responsible_substituted_to_none():
    for workplace in Lotacao.objects.filter(~Q(responsible_substituted=None)):
        if workplace.responsavel == workplace.responsible_substituted:
            Lotacao.objects.filter(pk=workplace.pk).update(responsible_substituted=None)


def show_members():
    today = datetime.now().date()
    print("--------------------MEMBERS-SHOW----------------------------")
    movs = MovimentacaoSubstituicaoMembro.objects.filter().filter(
        Q(data_inicio__lte=today) & (Q(data_fim__gte=today) | Q(data_fim=None))
    )
    for m in movs:
        print(m.pk, " - ", m.servidor_substituido, "{{ %s }}" % m, "---->", m.servidor)
        if m.cargo_arquimedes != 0:
            job_position = Cargo.objects.filter(cargo_arquimedes=m.cargo_arquimedes)
            if job_position.exists():
                workplace = job_position.latest("pk").lotacao_responsavel
                print(
                    workplace,
                    "== RESPONSAVEL:",
                    workplace.responsavel,
                    "== SUBSTITUIDO:",
                    workplace.responsible_substituted,
                )
        else:
            print("Não possui cargo arquimedes!")
        print("------------------------------------")
    set_workplace_responsible_substituted_to_none()


scritp_gd_transition_judicial()
