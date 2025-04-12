# -*- coding: utf-8 -*-
from contrib.utils import getLogger

from datetime import date, timedelta

from django.db.models import Q, F, Sum
from rh.models import Servidor, MovimentacaoPessoal
from rh.antiguidades.models import ListaAntiguidadeMembros

from rh.const import CANCELED

log = getLogger(__name__)


class ListaAntiguidades:

    def __init__(self):
        self.lista_antiguidades_procuradores = []
        self.lista_antiguidades_promotores = []
        self.lista_antiguidades_promotores_sub = []

    def adicionar_lista(self, antiguidade, lista):

        if lista == "procurador":
            self.lista_antiguidades_procuradores.append(antiguidade)
            self.lista_antiguidades_procuradores.sort(
                key=lambda ant: (
                    ant.tempo_total_instancia,
                    ant.tempo_efetivo_exercicio,
                    ant.data_inicio_carreira,
                    -(ant.servidor.posicao_concurso or 0),
                ),
                reverse=True,
            )
        elif lista == "promotor":
            self.lista_antiguidades_promotores.append(antiguidade)
            self.lista_antiguidades_promotores.sort(
                key=lambda ant: (
                    ant.tempo_total_instancia,
                    ant.tempo_efetivo_exercicio,
                    ant.data_inicio_carreira,
                    -(ant.servidor.posicao_concurso or 0),
                ),
                reverse=True,
            )
        elif lista == "promotor_sub":
            self.lista_antiguidades_promotores_sub.append(antiguidade)
            self.lista_antiguidades_promotores_sub.sort(
                key=lambda ant: (
                    ant.tempo_total_instancia,
                    ant.tempo_efetivo_exercicio,
                    ant.data_inicio_carreira,
                    -(ant.servidor.posicao_concurso or 0),
                ),
                reverse=True,
            )

    def buscar_procuradores_promotores(self):

        TIPO_MEMBRO = ["MBR", "MEL", "MCM", "MEC", "MBR2", "MEL2", "MCM2", "MEC2"]

        CARGOS = [
            "00084",  # PROCURADOR - GERAL DE JUSTICA
            "00056",  # PROCURADOR DE JUSTICA
            "00114",  # PROCURADOR GERAL DE JUSTICA ADJUNTO
            "00055",  # PROMOTOR (A) DE JUSTICA
            "00120",  # PROMOTOR DE JUSTICA - ENTRÂNCIA INICIAL
            "00121",  # PROMOTOR DE JUSTICA - ENTRÂNCIA INTERMEDIÁRIA
            "00085",  # PROMOTOR DE JUSTICA SUBSTITUTO
        ]

        q_servidor = Servidor.objects.filter(
            type_by_possession__in=TIPO_MEMBRO,
            movimentacaopessoal__movimentacaoposse__quadro__cargo__codigo__in=CARGOS,
        ).distinct()

        procuradores = []
        promotores = []
        promotores_sub = []

        for s in q_servidor:
            s_cargo = (
                s.movimentacaopessoal_set.filter(
                    movimentacaoposse__isnull=False,
                    movimentacaoposse__quadro__cargo__tipo_lei_cargo="EF",
                )
                .order_by("pk")
                .last()
                .movimentacaoposse.quadro.cargo
            )

            if s.is_ativo() and (
                s.is_procurador_or_procurador_geral
                or (s_cargo.nome.find("PROCURADOR") != -1)
            ):
                procuradores.append(s)
            elif s.is_ativo() and s.member_substitute:
                promotores_sub.append(s)
            elif s.is_ativo() and s.is_promotor:
                promotores.append(s)

        return (procuradores, promotores, promotores_sub)

    def buscar_tempo_afastamento(self, servidor):

        afastamentos = (
            MovimentacaoPessoal.objects.filter(
                Q(servidor=servidor),
                Q(
                    Q(
                        baselicencaafastamento__afastamento__afastamentosuspensao__isnull=False
                    )
                    | Q(
                        baselicencaafastamento__licenca__licencainteresseparticular__isnull=False
                    )
                ),
            )
            .exclude(baselicencaafastamento__estado=CANCELED)
            .exclude(
                baselicencaafastamento__afastamento__afastamentosuspensao__convertido_multa=True
            )
            .exclude(baselicencaafastamento__desconta_tempo=2)
        )  # baselicencaafastamento__desconta_tempo=2 ,  esta excluindo os registos que estão com 2-Não para desconto de tempo

        afastamentos_total = afastamentos.exclude(
            baselicencaafastamento__total_parcial=1
        ).aggregate(
            dias=Sum(
                F("baselicencaafastamento__data_fim")
                - (F("baselicencaafastamento__data_inicio") - 1)
            )
        )
        dias_afastados_parcial = 0

        for afast in afastamentos:
            if (
                afast.baselicencaafastamento.total_parcial == 1
            ):  # pega da lista de afastamentos/licenças os registros que possuem 1-Sim para total_pacial ,1 para parcial, assim havendo a necessidade de calcupar o numero de dias informado no registro.
                dias_afastados_parcial = (
                    dias_afastados_parcial + afast.baselicencaafastamento.total_desconto
                )

        if afastamentos_total.get("dias"):
            return afastamentos_total["dias"].days + dias_afastados_parcial

        return dias_afastados_parcial

    def buscar_data_inicio_instancia_procurador(self, servidor):

        return (
            servidor.movimentacaopessoal_set.filter(
                movimentacaoposse__quadro__cargo__pk=12939
            )
            .order_by("pk")
            .first()
            .movimentacaoposse.data_exercicio
        )

    def buscar_data_inicio_instancia_promotor(self, servidor):

        mposses = servidor.movimentacaopessoal_set.filter(
            movimentacaoposse__isnull=False,
            movimentacaoposse__quadro__cargo__nome__icontains="PROMOTOR",
            movimentacaoposse__data_inicio_instancia__isnull=False,
        ).order_by("pk")

        if mposses:
            return mposses.first().movimentacaoposse.data_inicio_instancia
        return None

    def buscar_primeiro_provimento(self, servidor):
        return (
            servidor.movimentacaopessoal_set.filter(
                movimentacaoposse__isnull=False,
                movimentacaoposse__quadro__cargo__tipo_lei_cargo="EF",
            )
            .order_by("pk")
            .first()
            .movimentacaoposse
        )

    def atualizar_lista_antiguidades_membros(self, origem):

        log.info("Iniciando o processo de atualizar a lista de antiguidades de membros")

        lista_procuradores, lista_promotores, lista_promotores_sub = (
            self.buscar_procuradores_promotores()
        )

        hoje = date.today() + timedelta(1)

        for procurador in lista_procuradores:

            antiguidade, criado = ListaAntiguidadeMembros.objects.get_or_create(
                servidor=procurador
            )

            primeira_mov_posse = self.buscar_primeiro_provimento(procurador)

            antiguidade.data_inicio_carreira = primeira_mov_posse.data_exercicio
            antiguidade.data_inicio_instancia = (
                self.buscar_data_inicio_instancia_procurador(procurador)
            )
            antiguidade.tempo_afastamento = self.buscar_tempo_afastamento(procurador)
            antiguidade.tempo_total_instancia = (
                hoje - antiguidade.data_inicio_instancia
            ).days
            antiguidade.tempo_total_carreira = (
                hoje - antiguidade.data_inicio_carreira
            ).days
            antiguidade.tempo_efetivo_exercicio = (
                antiguidade.tempo_total_carreira - antiguidade.tempo_afastamento
            )
            antiguidade.origem = origem
            antiguidade.tipo_cargo = 1

            self.adicionar_lista(antiguidade, "procurador")

        for i, antiguidade in enumerate(self.lista_antiguidades_procuradores):
            antiguidade.ordem_antiguidade = i + 1
            antiguidade.save()

        for promotor in lista_promotores:

            antiguidade, criado = ListaAntiguidadeMembros.objects.get_or_create(
                servidor=promotor
            )

            primeira_mov_posse = self.buscar_primeiro_provimento(promotor)

            antiguidade.data_inicio_carreira = primeira_mov_posse.data_exercicio
            antiguidade.data_inicio_instancia = (
                self.buscar_data_inicio_instancia_promotor(promotor)
            )
            antiguidade.tempo_afastamento = self.buscar_tempo_afastamento(promotor)
            if antiguidade.data_inicio_instancia:
                antiguidade.tempo_total_instancia = (
                    hoje - antiguidade.data_inicio_instancia
                ).days
            antiguidade.tempo_total_carreira = (
                hoje - antiguidade.data_inicio_carreira
            ).days
            antiguidade.tempo_efetivo_exercicio = (
                antiguidade.tempo_total_carreira - antiguidade.tempo_afastamento
            )
            antiguidade.origem = origem
            antiguidade.tipo_cargo = 2

            self.adicionar_lista(antiguidade, "promotor")

        for i, antiguidade in enumerate(self.lista_antiguidades_promotores):
            antiguidade.ordem_antiguidade = i + 1
            antiguidade.save()

        for promotor_sub in lista_promotores_sub:

            antiguidade, criado = ListaAntiguidadeMembros.objects.get_or_create(
                servidor=promotor_sub
            )

            primeira_mov_posse = self.buscar_primeiro_provimento(promotor_sub)

            antiguidade.data_inicio_carreira = primeira_mov_posse.data_exercicio
            antiguidade.data_inicio_instancia = (
                self.buscar_data_inicio_instancia_promotor(promotor_sub)
            )
            antiguidade.tempo_afastamento = self.buscar_tempo_afastamento(promotor_sub)
            if antiguidade.data_inicio_instancia:
                antiguidade.tempo_total_instancia = (
                    hoje - antiguidade.data_inicio_instancia
                ).days
            else:
                antiguidade.tempo_total_instancia = (
                    hoje - antiguidade.data_inicio_carreira
                ).days
            antiguidade.tempo_total_carreira = (
                hoje - antiguidade.data_inicio_carreira
            ).days
            antiguidade.tempo_efetivo_exercicio = (
                antiguidade.tempo_total_carreira - antiguidade.tempo_afastamento
            )
            antiguidade.origem = origem
            antiguidade.tipo_cargo = 3

            self.adicionar_lista(antiguidade, "promotor_sub")

        for i, antiguidade in enumerate(self.lista_antiguidades_promotores_sub):
            antiguidade.ordem_antiguidade = i + 1
            antiguidade.save()

        log.info(
            "Finalizando o processo de atualizar a lista de antiguidades de membros"
        )
