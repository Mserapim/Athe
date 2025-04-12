from django.http import JsonResponse
from rh.models import MovimentacaoPosse, Servidor, ServidorLotacao
from django.db.models import (
    Count,
    Value,
    Q,
    F,
    ExpressionWrapper,
    IntegerField,
    OuterRef,
    Exists,
    CharField,
    Case,
    When,
    Subquery,
    DateTimeField,
    CharField,
)
from django.db.models.functions import (
    Coalesce,
    LPad,
    ExtractDay,
    ExtractMonth,
    ExtractYear,
    Concat,
    Cast,
)
from django.http import HttpResponse
from standard.models import Choice
from django.http import FileResponse
import pandas as pd
from rh.gfp.febrabam.bb import File
import io


def formatar_data_por_query(campo):
    consulta = {f"{campo}__isnull": False}
    data_formatada = Case(
        When(
            Q(**consulta),
            then=(
                Concat(
                    LPad(
                        Cast(
                            ExtractDay(F(campo), output_field=CharField()),
                            output_field=CharField(),
                        ),
                        2,
                        Value("0"),
                    ),
                    Value("/"),
                    LPad(
                        Cast(
                            ExtractMonth(F(campo), output_field=CharField()),
                            output_field=CharField(),
                        ),
                        2,
                        Value("0"),
                    ),
                    Value("/"),
                    ExtractYear(campo, output_field=CharField()),
                )
            ),
        ),
        default=Value(""),
    )
    return data_formatada


def get_label(campo, opcoes):
    for item in opcoes:
        if campo == item.get("cvalue"):
            return item.get("label")
    return campo


def get_annotation():
    posses = MovimentacaoPosse.objects.filter(
        servidor=OuterRef("pk"),
    ).order_by("-data_desligamento")
    data_desligamento = Subquery(
        posses.values("data_desligamento")[:1],
        output_field=DateTimeField(),
    )
    data_desligamento_for = formatar_data_por_query("data_desligamento")

    annotate = {
        "data_desligamento": data_desligamento,
        "data_desligamento_for": data_desligamento_for,
        "servidor": F("pessoa_fisica__nome"),
        "categoria_funcional": F("type_by_possession"),
    }
    return annotate


def relatorio_inconsistencia_lotacao_designacao(request):
    lista = (
        Servidor.objects.filter(
            ativo=False,
            servidor_lotacao__ativo=True,
        )
        .order_by("type_by_possession")
        .distinct()
    )

    categorias = Choice.objects.get_options("rh", "CLASSIF_EMPLOYEE_BY_POSSESSION")

    valores = lista.annotate(**get_annotation()).values(
        "pk",
        "matricula",
        "servidor",
        "categoria_funcional",
        "data_desligamento_for",
    )

    for valor in valores:
        valor["categoria_funcional"] = get_label(
            valor["categoria_funcional"], categorias
        )

        lotacoes_q = ServidorLotacao.objects.filter(
            servidor=valor.get("pk"), ativo=True, designacao=False
        )

        designacoes_q = ServidorLotacao.objects.filter(
            servidor=valor.get("pk"), ativo=True, designacao=True
        )

        valor["lotacoes"] = "/ ".join([str(lotacao) for lotacao in lotacoes_q])
        valor["designacoes"] = "/ ".join(
            [str(designacao) for designacao in designacoes_q]
        )

        valor.pop("pk")

    buffer = io.StringIO()

    df = pd.DataFrame(valores)
    df.to_csv(buffer, index=True, sep=";", encoding="utf-8")
    buffer.seek(0)

    return FileResponse(
        buffer.getvalue(),
        as_attachment=True,
        filename="relatorio_inconsistencia_lotacao_designacao_est_res_vol.csv",
    )
