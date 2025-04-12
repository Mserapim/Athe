# -*- coding: utf-8 -*-

STATE_ENTRADA_CHOICES = (
    (1, "Nota Aberta"),
    (2, "Nota Finalizada"),
    (3, "Nota Cancelada"),
)

STATE_BAIXA_CHOICES = (
    (1, "Nota Aberta"),
    (2, "Nota Finalizada"),
    (3, "Nota Cancelada"),
)

STATE_WORKFLOW = {
    1: tuple([2, 3]),
    2: tuple([]),
    3: tuple([1]),
}

CONSERVACAO_CHOICES = ((1, "Novo"), (2, "Bom"), (3, "Regular"), (4, "Inservivel"))

MOVIMENTO_STATUS = (
    (1, "Aberto"),
    (2, "Aguardando recebimento"),
    (3, "Recebido"),
    (4, "Ciência"),
    (5, "Cancelado"),
    (6, "Autorizado"),
)

MOVIMENTO_STATUS_PERMISSION = {
    1: ("ORIGEM", "ADMIN", "DESTINO"),
    2: ("ORIGEM", "ADMIN"),
    3: ("DESTINO", "ADMIN"),
    4: ("ADMIN",),
    5: ("ORIGEM", "DESTINO", "ADMIN", "HAS_DG", "HAS_CGPGJ", "HAS_PGJ"),
    6: ("HAS_DG", "HAS_CGPGJ", "HAS_PGJ"),
}

CRITICA_STATE = ((1, "Aberto"), (2, "Deferido"), (3, "Indeferido"))
