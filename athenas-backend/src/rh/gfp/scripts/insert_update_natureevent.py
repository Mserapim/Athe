from rh.gfp.models import NatureEvent

with open("rh/gfp/fixtures/tabela_esocial_3.txt") as tab:
    for t in tab.readlines():
        code, title, desc, act = t.split("|")
        print(code)
        act = True if act.replace("\n", "") == "S" else False
        existnat = NatureEvent.objects.filter(code=code)
        if existnat.exists():
            ret = existnat.update(title=title.upper(), description=desc, active=act)
            print(f"O registro {existnat} retornou {ret}")
        else:
            new = NatureEvent.objects.create(
                code=code, title=title.upper(), description=desc, active=act
            )
            print(f"Tinha nao, mas criei esse cara {new}")
