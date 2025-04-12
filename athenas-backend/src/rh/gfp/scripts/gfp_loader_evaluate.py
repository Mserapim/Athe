import csv
from rh.gfp.models import Folha

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YLW = "\033[0;33m"
NC = "\033[0m"  # No Color


def update_consigfacil(filename, year, month, complement=0, only_errors=False):
    f = Folha.objects.filter(
        periodo__ano=year, periodo__mes=month, complement=complement
    ).first()
    print(f)

    with open(filename, newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=";")
        for row in spamreader:
            error = False
            # print(row)
            if len(row) > 10:
                fes = f.lancamentos.filter(
                    servidor__matricula=row[1], evento__numero=row[2], valor=row[6]
                )
                if row[0] == "E":
                    if fes.count() > 1:
                        ret = f"{RED}ERRO > 1{NC}"
                        error = True
                    elif fes.count() == 0:
                        ret = f"{GREEN}OK {row[10]}{NC}"
                    else:
                        error = True
                        ups = fes.update(info=row[10])
                        ret = f"{YLW}ERRO UP {fes[0].info} >> {row[10]} ({ups}){NC}"
                else:
                    if fes.count() > 1:
                        error = True
                        ret = f"{RED}ERRO > 1{NC}"
                    elif fes.count() == 0:
                        ret = f"{RED}ERRO DNE{NC}"
                        error = True
                    else:
                        ret = f"{GREEN}OK {fes[0].info}/{row[10]}{NC}"
                if error:
                    print(row, end="")
                    print(ret)
