from datetime import datetime
from contrib.middleware import set_current_user
from esocial.models import ItemTable

set_current_user(1)
file = "tabelas"


# itens from file
def execute():
    with open(f"esocial/scripts/{file}") as tab:
        for t in tab.readlines():
            code, title, desc, start, end, tabe = t.split("|")
            start = datetime.strptime(start, "%d/%m/%Y") if start != "" else None
            end = datetime.strptime(end, "%d/%m/%Y") if end != "" else None
            tabe = tabe.replace("\n", "")
            print(code, title, desc, start, end, tabe)
            existnat = ItemTable.objects.filter(code=code, esocial_table=tabe)
            if existnat.exists():
                ret = existnat.update(
                    title=title.upper(),
                    description=desc,
                    start_validity=start,
                    end_validity=end,
                    esocial_table=tabe,
                )
                print(f"O registro {existnat} retornou {ret}")
            else:
                new = ItemTable.objects.create(
                    code=code,
                    title=title.upper(),
                    description=desc,
                    start_validity=start,
                    end_validity=end,
                    esocial_table=tabe,
                )
                print(f"Tinha nao, mas criei esse cara {new}")
