# -*- coding: utf-8 -*-

from contrib.middleware import set_current_user
from django.contrib.auth.models import User
from rh.gfp.models import Folha, Evento, ContraCheque

set_current_user(User.objects.get(username="athenas"))

f = Folha.objects.get(pk=605)  # MARÇO DE 2013 - BASE
f_ = Folha.objects.get(pk=653)  # FEVEREIRO 2014 - PAGAMENTO

print("DELETING EVENT 5076...")
f_.lancamentos.filter(evento__numero="5076").delete()
print("OK")

for fe in f.lancamentos.filter(evento__numero="0001").order_by("servidor"):
    if fe.servidor.tipo == "S" and fe.servidor.is_efetivo:
        print(fe.servidor)
        fe_prev = f.lancamentos.get(
            evento__numero__in=["5540", "5544"], servidor=fe.servidor
        )
        print(
            ":%s:%s:%s:%s:%s:%s:%s"
            % (
                fe.qnt / 30.0,
                fe.valor,
                fe_prev.valor_base,
                1,
                1,
                round(float(fe_prev.valor_base) / float(fe.qnt), 2),
                "REF. 2013",
            )
        )
        try:
            cc = f_.paychecks.get(servidor__pessoa_fisica=fe.servidor.pessoa_fisica)
        except ContraCheque.DoesNotExist:
            print("NE")
        else:
            ev = Evento.objects.get(numero="5076")
            fe_, created_or_updated = cc.add_evento(
                True,
                True,
                **{
                    "evento": ev,
                    "qnt": 1,
                    "prazo": 1,
                    "valor": round(float(fe_prev.valor_base) / float(fe.qnt), 2),
                    "valor_base": fe_prev.valor_base,
                    "info": "REF. 2013",
                }
            )
            print("OK")
