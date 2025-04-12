from rh.gfp.models import Evento, NatureEvent
from esocial.models import ItemTable


def run():
    events = Evento.objects.filter(active=True).values("pk", "nature_of_event__code")

    for e in events:
        print(e)
        nat = e["nature_of_event__code"]
        print(nat)
        if nat:
            item = ItemTable.objects.by_code_table(nat, "3")
            print(item)
            Evento.objects.filter(pk=e["pk"]).update(nature_event=item)
