from datetime import datetime
from django.db.models import Prefetch
from apiv2.baseviews import ListBaseView
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import Servidor
from rh.mov_carreira.apiv2.serializers import (
    MembroProbatorioAfastamentoSerializer,
    MembrosEstagioProbatorioSerializer,
)


class MembrosEstagioProbatorioView(ListBaseView):
    serializer_class = MembrosEstagioProbatorioSerializer
    full_text_index = (
        "pessoa_fisica__nome__unaccent__icontains",
        "matricula__icontains",
    )

    def get_queryset(self):
        """
        Retorna a QuerySet dos Membros em estágio probatório já filtrada e ordenada por `dias_para_fim_estagio`.
        """
        query = Servidor.objects.prefetch_related(Prefetch("pessoa_fisica")).filter(
            type_by_possession__in=[
                "MBR",
                "MEL",
                "MCM",
                "MEC",
                "MBR2",
                "MEL2",
                "MCM2",
                "MEC2",
                "MAP",
            ],
            ativo=True,
        )
        return query.filter(pk__in=self.get_membros_estagio_probatorio(query))

    def get_membros_estagio_probatorio(self, query):
        """
        Retorna uma lista contendo IDs de membros substitutos em estágio probatório.
        """
        return [item.pk for item in query if item.member_substitute]

    def order_queryset(self, queryset):
        """
        Ordena os resultados pelos dias restantes para o fim do estágio probatório,
        pelos dias trabalhados ou pelos dias afastados, conforme o parâmetro `order_by`.

        Se nenhum `order_by` for fornecido, ordena por `dias_para_fim_estagio` do menor para o maior.
        """
        order_by = self.request.query_params.get("order_by")

        if not order_by:
            order_by = "dias_para_fim_estagio"

        ordering_fields = {
            "dias_para_fim_estagio": lambda x: x.days_for_complete_the_probationary_phase()
            or float("inf"),
            "dias_trabalhados": lambda x: x.get_worked_days_if_employee_be_in_probationary_phase
            or 0,
            "dias_afastados": lambda x: x.get_days_departure or 0,
        }

        if order_by.lstrip("-") in ordering_fields:
            reverse = order_by.startswith("-")
            return sorted(
                queryset,
                key=lambda x: ordering_fields[order_by.lstrip("-")](x),
                reverse=reverse,
            )

        return super().order_queryset(queryset)


class MembroProbatorioAfastamentosView(ListBaseView):
    """
    API para listar os afastamentos de um Membro em estágio probatório.
    """

    serializer_class = MembroProbatorioAfastamentoSerializer

    def get_queryset(self):
        """
        Retorna a lista de afastamentos do membro em estágio probatório.
        """
        membro_id = self.request.query_params.get("membroId")
        if not membro_id:
            return BaseLicencaAfastamento.objects.none()
        try:
            membro = Servidor.objects.get(id=membro_id)
        except Servidor.DoesNotExist:
            return BaseLicencaAfastamento.objects.none()

        return membro.departures(
            start_date=membro.first_possession_date,
            end_date=datetime.now().date(),
        )
