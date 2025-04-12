from edocs.protocolo.api.manage import *
from edocs.protocolo.models import *
from django.contrib.auth.models import *
from edocs.protocolo.utils import EDOCBoxQuery
import csv


def new_extract_box(employee):
    from django.db import connection, reset_queries
    import time

    work_locations_effective_exercise = employee.work_locations_effective_exercise
    box_params = {
        "servidor": employee,
        "lotacoes": [
            row.get("pk") for row in work_locations_effective_exercise.values("pk")
        ],
    }

    if work_locations_effective_exercise.filter(acesso_protocolo_geral=True).exists():
        box_params.update(
            lotacoes_protocolo_geral=work_locations_effective_exercise.filter(
                acesso_protocolo_geral=True
            )
        )

    box = EDOCBoxQuery(**box_params)
    box = (
        box.get_caixa_entrada()
        .filter(data_finalizado=None, protocolo__data_finalizado=None)
        .order_by("-data_encaminhamento")
    )

    manage = EDOCManage(None, None)

    start_time = time.time()
    if box.exists():
        manage.box_to_dict(box, 0, 30)
    end_time = time.time()
    total_time = round(end_time - start_time, 3)
    connections = len(connection.queries)
    reset_queries()
    return connections, total_time


def old_extract_box(employee):
    from django.db import connection, reset_queries
    import time

    work_locations_effective_exercise = employee.work_locations_effective_exercise
    box_params = {
        "servidor": employee,
        "lotacoes": [
            row.get("pk") for row in work_locations_effective_exercise.values("pk")
        ],
    }

    if work_locations_effective_exercise.filter(acesso_protocolo_geral=True).exists():
        box_params.update(
            lotacoes_protocolo_geral=work_locations_effective_exercise.filter(
                acesso_protocolo_geral=True
            )
        )

    box = EDOCBoxQuery(**box_params)
    box = (
        box.get_caixa_entrada()
        .filter(data_finalizado=None, protocolo__data_finalizado=None)
        .order_by("-data_encaminhamento")
    )

    manage = EDOCManage(None, None)

    start_time = time.time()
    [manage.model_to_dict(inst) for inst in manage.page_box(box, 0, 30)]
    end_time = time.time()
    total_time = round(end_time - start_time, 3)
    connections = len(connection.queries)
    reset_queries()
    return connections, total_time


def old_avg(qtd_box=1000):
    users = User.objects.filter(is_active=True, is_staff=True)
    header = ["User", "Connectoions", "time", "Connections", "time"]
    avg_conn = []
    avg_time = []
    total = 0
    with open("new_metodo.csv", "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for user in users[:qtd_box]:
            employee = employee_from_user(user)
            if employee:
                conn, time = old_extract_box(employee)

                avg_conn.append(conn)
                avg_time.append(time)

                print("====================================")
                print("      USER       | CONNECTION | TIME")
                print("------------------------------------")
                print(
                    f'{user.username[:16].ljust(16, " ")} |    {f"{conn}".rjust(4, "0")}    | {time}'
                )
                print("------------------------------------")
                writer.writerow([user.username, conn, time])
    print("")
    print("")
    print("")
    print("******MÉDIA DE CONEXÕES E TEMPO MODELO ANTIGO******")
    print(f"AVG CONNECTIONS: {round(sum(avg_conn) / len(avg_conn), 1)}")
    print(f"AVG TIME:        {round(sum(avg_time) / len(avg_time), 3)}")


def new_avg(qtd_box=1000):
    users = User.objects.filter(is_active=True, is_staff=True)
    header = ["User", "Connectoions", "time", "Connections", "time"]
    avg_conn = []
    avg_time = []
    total = 0
    with open("new_metodo.csv", "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for user in users[:qtd_box]:
            employee = employee_from_user(user)
            if employee:
                conn, time = new_extract_box(employee)

                avg_conn.append(conn)
                avg_time.append(time)

                print("====================================")
                print("      USER       | CONNECTION | TIME")
                print("------------------------------------")
                print(
                    f'{user.username[:16].ljust(16, " ")} |    {f"{conn}".rjust(4, "0")}    | {time}'
                )
                print("------------------------------------")
                writer.writerow([user.username, conn, time])
    print("")
    print("")
    print("")
    print("******MÉDIA DE CONEXÕES E TEMPO NOVO MODELO******")
    print(f"AVG CONNECTIONS: {round(sum(avg_conn) / len(avg_conn), 1)}")
    print(f"AVG TIME:        {round(sum(avg_time) / len(avg_time), 3)}")
