from django.db.models import Q, Count
from datetime import datetime
from rh.models import MovimentacaoPosse

TIPOS_POSSE_SEM_VINCULO = [
    "EST",
    "RES",
    "REC",
    "RCM",
    "TCR",
    "VOL",
    "CTR",
    "EXT",
    "RFC",
    "JCA",
    "REX",
]
TIPOS_POSSE_MEMBRO = ["MBR", "MEL", "MEC", "MCM"]


def get_cargo_posse_stats(cargos):
    """Retorna um dicionário com as contagens de posses por cargo."""
    date = datetime.now().date()
    posses = MovimentacaoPosse.objects.filter(
        Q(quadro__cargo__in=cargos)
        & Q(data_exercicio__lte=date)  # Filtra apenas os cargos da requisição
        & (  # Exercício já iniciado
            Q(data_desligamento__gt=date) | Q(data_desligamento__isnull=True)
        )  # Ainda em posse
    ).exclude(benefitmovement__isnull=False)
    stats = posses.values("quadro__cargo").annotate(
        qtd_vagas_ocupadas=Count("id", distinct=True),
        qtd_vagas_efetivo=Count(
            "id", filter=Q(servidor__type_by_possession__in=["EFE"]), distinct=True
        ),
        qtd_vagas_membro=Count(
            "id",
            filter=Q(servidor__type_by_possession__in=TIPOS_POSSE_MEMBRO),
            distinct=True,
        ),
        qtd_vagas_comissionado=Count(
            "id", filter=Q(servidor__type_by_possession__in=["CMS"]), distinct=True
        ),
        qtd_vagas_efetivo_funcao=Count(
            "id", filter=Q(servidor__type_by_possession__in=["EFC"]), distinct=True
        ),
        qtd_vagas_efetivo_comissao=Count(
            "id", filter=Q(servidor__type_by_possession__in=["ECM"]), distinct=True
        ),
        qtd_vagas_sem_vinculo=Count(
            "id",
            filter=Q(servidor__type_by_possession__in=TIPOS_POSSE_SEM_VINCULO),
            distinct=True,
        ),
    )

    return {stat["quadro__cargo"]: stat for stat in stats}
