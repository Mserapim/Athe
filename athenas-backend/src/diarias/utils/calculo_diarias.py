from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q

from diarias.models import ValorDiarias, CalculoConsolidado
from rh.gfp.models import ExtraPaymentPeriod, Periodo, ConfigEvent

from diarias.utils.fluxo_condicionais import (
    benef_servidor,
    membro_solicitou_veiculo_daa,
    benef_acomp_autoridade,
)
from diarias.utils.excedentes import verificar_excedentes, criar_excedente

from contrib.utils import getLogger

log = getLogger()


class CalcularConsolidarDiarias(object):
    """
    Classe com métodos e lógicas para ralizar os cálculos de diárias.

    O método a ser chamado para executar toda a lógica é o 'calcular_consolidar_diarias'.
    """

    def __init__(self, *args, **kwargs):
        self.beneficiario = kwargs.get("beneficiario")
        self.destinos = self.beneficiario.destinos.order_by("data")
        self.viagem = self.beneficiario.viagem

        self.membro_com_veiculo_daa = (
            True if membro_solicitou_veiculo_daa(self.beneficiario) else False
        )

        if (
            benef_servidor(self.beneficiario)
            and benef_acomp_autoridade(self.beneficiario)
            and self.beneficiario.acomp_autoridade_deferimento
        ):
            self.servidor_acomp_aut = True
        else:
            self.servidor_acomp_aut = False

        self.dentro_estado_mt = True if self.viagem.tipo_viagem == "ESTADUAL" else False

        self.consolidado = {
            "beneficiario": self.beneficiario,
            "qtd_total_diarias_calculadas": Decimal(0),
            "qtd_total_diarias": Decimal(0),
            "qtd_total_excedente": Decimal(0),
            "qtd_total_diarias_dentro_uf": Decimal(0),
            "qtd_total_diarias_fora_uf": Decimal(0),
            # 'qtd_total_diarias_deferido': Decimal(0),
            "valor_base_diaria": Decimal(0),
            "valor_base_subsidio": Decimal(0),
            "valor_base_desc_transporte": Decimal(0),
            "valor_desc_transporte": Decimal(0),
            "valor_base_desc_alimentacao": Decimal(0),
            "valor_desc_alimentacao": Decimal(0),
            "valor_total_diarias_dentro_estado": Decimal(0),
            "valor_total_diarias_fora_estado": Decimal(0),
            "valor_total_veiculo_mp": Decimal(0),
            "valor_total_desconto": Decimal(0),
            "valor_total_bruto": Decimal(0),
            "valor_total_liquido": Decimal(0),
            "valor_total_liquido_deferido": Decimal(0),
        }

    def calcular_consolidar_diarias(self):
        """
        Método responsável sobre executar o método de cálculo de a cordo com o tipo, se Membro ou não, e execução do método
        para consolidar essas informações.
        """

        (
            self.calcular_diarias_membro()
            if self.beneficiario.servidor.tipo == "M"
            else self.calcular_diarias_servidor()
        )
        self.consolidar_calculos()

        return self.consolidado

    def consolidar_calculos(self):
        """
        Método responsável por gravar as informações consolidadas no modelo CalculoConsolidado
        """

        q_calculo_consolidado = CalculoConsolidado.objects.filter(
            beneficiario=self.consolidado["beneficiario"]
        )
        if q_calculo_consolidado.exists():
            q_calculo_consolidado.update(**self.consolidado)
        else:
            CalculoConsolidado.objects.create(**self.consolidado)

        self.verificar_calcular_excedentes()

        return self.consolidado

    def verificar_calcular_excedentes(self):

        if (
            self.beneficiario.fluxo.id != 2
        ):  # testa se o fluxo é diferente do rascunho, e caso seja ele não deixa refazer o calculo de excedentes
            return None

        if self.beneficiario.viagem.excedente:
            return None

        qtd_dirias = self.consolidado["qtd_total_diarias_calculadas"]
        qtd_limite, qtd_saldo, qtd_uso, qtd_total_excendentes, qtd_excedentes = (
            verificar_excedentes(self.beneficiario, qtd_dirias)
        )

        if qtd_excedentes > 0:

            self.consolidado["qtd_total_excedente"] = qtd_excedentes

            (
                self.calcular_diarias_membro()
                if self.beneficiario.servidor.tipo == "M"
                else self.calcular_diarias_servidor()
            )

            q_calculo_consolidado = CalculoConsolidado.objects.filter(
                beneficiario=self.consolidado["beneficiario"]
            )
            if q_calculo_consolidado.exists():
                q_calculo_consolidado.update(**self.consolidado)
            else:
                CalculoConsolidado.objects.create(**self.consolidado)

            criar_excedente(self.beneficiario, qtd_excedentes)

    def qtd_diarias_transp_alim(self):
        return Decimal(self.consolidado["qtd_total_diarias"] + Decimal(0.5))

    def verificar_recebimento_verba_alimentacao(self):
        """
        Método responsável por verificar se o beneficiário recebe a Verba Ind. de Alimentação (06700) dentro
        do período dos últimos 3 meses a partir da data do cálculo de diárias.
        """

        data_ref = datetime.today().date() - relativedelta(months=3)

        return self.beneficiario.servidor.entries.filter(
            evento__numero="06700",
            contracheque__folha__periodo__ano__gte=data_ref.year,
            contracheque__folha__periodo__mes__gte=data_ref.month,
        ).exists()

    def buscar_valor_base_verba_alimentacao(self):
        """
        Método responsável por buscar o valor base de Indenização de Alimentação do beneficiário.

        Deve-se buscar o valor em verbas extras (VERBA IND. DE ALIMENTAÇÃO -  AUXILIO-ALIMENTACAO).
        """

        data_hoje = datetime.today().date()
        q_verba_extra = ExtraPaymentPeriod.objects.filter(
            extra_payment__slug="AUXILIO-ALIMENTACAO",
        ).filter(
            Q(start_validity__lte=data_hoje, end_validity__gte=data_hoje)
            | Q(end_validity__isnull=True)
        )
        q_verba_extra_benef = q_verba_extra.filter(employee=self.beneficiario.servidor)

        if q_verba_extra_benef.exists():
            return q_verba_extra_benef.first().value
        else:
            q_verba_extra = q_verba_extra.filter(
                employee__isnull=True,
                start_validity__lte=data_hoje,
                end_validity__isnull=True,
            )
            return q_verba_extra.first().value

    def calcular_desconto_alimentacao(self):
        """
        Método responsável por realizar o cálculo do valor a ser descontado do beneficiário sobre Verba Ind. de Alimentação (06700).

        Regra para verificar se é para descontar sobre alimentação:
        Se houver pagamento da verba dentro dos últimos 3 meses a partir da data do cálculo de diárias, então deve-se
        considerar que recebe a verba e gerar o desconto no valor total de diárias.

        A fórmula para desconto é 1/30 avos do valor base multiplicado pela quantidade total de diárias.

        Para buscar o valor base de cálculo de Alimentação, deve-se buscar o valor em verbas extras
        (VERBA IND. DE ALIMENTAÇÃO -  AUXILIO-ALIMENTACAO).
        """

        if self.verificar_recebimento_verba_alimentacao():
            valor_base = self.buscar_valor_base_verba_alimentacao()
            self.consolidado["valor_base_desc_alimentacao"] = Decimal(valor_base)
            self.consolidado["valor_desc_alimentacao"] = Decimal(
                (valor_base / 30) * self.qtd_diarias_transp_alim()
            )
            self.consolidado["valor_total_desconto"] += Decimal(
                self.consolidado["valor_desc_alimentacao"]
            )

    def verificar_recebimento_verba_transporte(self):
        """
        Método responsável por verificar se o beneficiário recebe a verba Ajuda de Custo para Transporte (07600) dentro
        do período dos últimos 3 meses a partir da data do cálculo de diárias.
        """

        data_ref = datetime.today().date() - relativedelta(months=3)

        return self.beneficiario.servidor.entries.filter(
            evento__numero="07600",
            contracheque__folha__periodo__ano__gte=data_ref.year,
            contracheque__folha__periodo__mes__gte=data_ref.month,
        ).exists()

    def buscar_porc_vigente_verba_transporte(self):
        """
        Método responsável por buscar a porcentagem vigente de cálculo da verba de Ajuda de Custo para Transporte (07600).
        """

        data_hoje = datetime.today().date()
        evento_config = (
            ConfigEvent.objects.filter(
                event__numero="07600",
            )
            .filter(
                Q(start_validity__lte=data_hoje, end_validity__gte=data_hoje)
                | Q(start_validity__lte=data_hoje, end_validity__isnull=True)
            )
            .first()
        )

        return evento_config.percentage * Decimal(0.01)

    def buscar_valor_base_verba_transporte(self):
        """
        Método responsável por buscar o valor base para cálculo de desconto de transporte.

        Deve-se buscar o valor vigente nas configurações de tetos no model rh.gfp.Periodo retornando a configuração de salario_teto_memebro.
        """

        valor_teto = (
            Periodo.objects.order_by("-ano", "-mes").first().salario_teto_membros
        )
        porc_verba = self.buscar_porc_vigente_verba_transporte()

        return valor_teto * porc_verba

    def calcular_desconto_transporte(self):
        """
        Método responsável por realizar o cálculo do valor a ser descontado do beneficiário sobre Ajuda de Custo para Transporte (07600).

        Regra para verificar se é para descontar sobre transporte:
        Se houver pagamento da verba dentro dos últimos 3 meses a partir da data do cálculo de diárias, então deve-se
        considerar que recebe a verba e gerar o desconto no valor total de diárias.

        A fórmula para desconto é: (((valor base * porcentagem vigente) / 30) * quantidade total de diárias).

        Para buscar o valor base de cálculo de Alimentação, deve-se buscar o valor vigente nas configurações dos tetos, no model
        rh.gfp.Periodo retornando a configuração de salario_teto_memebro.
        """

        if self.verificar_recebimento_verba_transporte():
            valor_base = self.buscar_valor_base_verba_transporte()

            self.consolidado["valor_base_desc_transporte"] = Decimal(valor_base)
            self.consolidado["valor_desc_transporte"] = Decimal(
                (valor_base / 30) * self.qtd_diarias_transp_alim()
            )
            self.consolidado["valor_total_desconto"] += Decimal(
                self.consolidado["valor_desc_transporte"]
            )

    def calcular_qtd_diarias(self):
        qtd = Decimal(0)

        if self.viagem.excedente:
            beneficiario_original = self.viagem.viagem_origem.beneficiarios.get(
                servidor=self.beneficiario.servidor
            )
            calc_original = beneficiario_original.calculos_diarias_consolidados
            self.consolidado["qtd_total_diarias_calculadas"] = (
                calc_original.qtd_total_diarias_calculadas
            )
            qtd = calc_original.qtd_total_excedente
        else:

            for i, destino in enumerate(self.destinos):
                data = destino.data_daa or destino.data
                data_proxima = (
                    (self.destinos[i + 1].data_daa or self.destinos[i + 1].data)
                    if i < len(self.destinos) - 1
                    else None
                )
                if (i == (len(self.destinos) - 1)) or self.viagem.hospedagem_anfitriao:
                    qtd += Decimal(0.5)
                else:
                    qtd += Decimal((data_proxima - data).days)

            self.consolidado["qtd_total_diarias_calculadas"] = Decimal(qtd)
            if self.consolidado["qtd_total_excedente"] > 0:
                qtd -= self.consolidado["qtd_total_excedente"]

        return qtd if qtd > 0 else 0

    def calcular_valor_diarias(
        self, valor_diaria_dentro_estado_mt, valor_diaria_fora_estado_mt
    ):

        if self.dentro_estado_mt:
            if self.servidor_acomp_aut:
                valor_diaria = valor_diaria_dentro_estado_mt + (
                    valor_diaria_dentro_estado_mt * 0.5
                )
            else:
                valor_diaria = valor_diaria_dentro_estado_mt
        else:
            if self.servidor_acomp_aut:
                valor_diaria = valor_diaria_fora_estado_mt + (
                    valor_diaria_fora_estado_mt * 0.32
                )
            else:
                valor_diaria = valor_diaria_fora_estado_mt

        return valor_diaria

    def calcular_diarias(
        self,
        valor_diaria_dentro_estado_mt,
        valor_diaria_fora_estado_mt,
        valor_com_motorista=None,
    ):
        """
        Método responsável por realizar o cálculo de diárias e consolidar as informações de valores totais e quantitativos.
        """

        qtd_diarias = self.calcular_qtd_diarias()
        valor_diaria = self.calcular_valor_diarias(
            valor_diaria_dentro_estado_mt, valor_diaria_fora_estado_mt
        )

        if self.membro_com_veiculo_daa:
            self.consolidado["valor_total_veiculo_mp"] = Decimal(
                valor_com_motorista * qtd_diarias
            )

        if self.dentro_estado_mt:
            self.consolidado["valor_total_diarias_dentro_estado"] = Decimal(
                valor_diaria * qtd_diarias
            )
            self.consolidado["qtd_total_diarias_dentro_uf"] += Decimal(
                qtd_diarias + self.consolidado["qtd_total_excedente"]
            )
        else:
            self.consolidado["qtd_total_diarias_fora_uf"] = Decimal(
                qtd_diarias + self.consolidado["qtd_total_excedente"]
            )
            self.consolidado["valor_total_diarias_fora_estado"] = Decimal(
                valor_diaria * qtd_diarias
            )

        self.consolidado["qtd_total_diarias"] = Decimal(qtd_diarias)
        self.consolidado["valor_base_diaria"] = valor_diaria
        self.consolidado["valor_total_bruto"] = Decimal(valor_diaria * qtd_diarias)

        self.calcular_desconto_alimentacao()
        self.calcular_desconto_transporte()

        self.consolidado["valor_total_liquido"] = Decimal(
            self.consolidado["valor_total_bruto"]
            - self.consolidado["valor_total_desconto"]
        )
        self.consolidado["valor_total_liquido_deferido"] = self.consolidado[
            "valor_total_liquido"
        ]

        # self.consolidado['qtd_total_diarias_calculadas'] = Decimal(self.consolidado['qtd_total_diarias'] + self.consolidado['qtd_total_excedente'])

        return self.consolidado

    def calcular_diarias_membro(self):
        """
        Método responsável por coletar as informações necessárias para realizar o cálculo de diárias de um beneficiário
        do tipo Membro.

        O valor de referência da diária para Membros deve ser 1/30 avos do atual subsídio (verba 00100) e considerar as situações:
        - se o trecho tiver destino dentro do MT, será o valor de 1/30 avos.
        - se o trecho tiver destino fora do MT, será o valor de 1/30 avos mais 10%.
        - se o trecho tiver origem e destino dentro do MT e tiver com carro do MP, será o valor de 1/30 avos menos 10%.

        Obs.: o valor de referência para o Procurar-Geral de Justiça deve ser o mesmo que para os Procuradores
        """

        folha_evento_subsidio = (
            self.beneficiario.servidor.entries.filter(evento__numero="00100")
            .order_by(
                "-contracheque__folha__periodo__ano",
                "-contracheque__folha__periodo__mes",
            )
            .first()
        )

        self.consolidado["valor_base_subsidio"] = Decimal(
            folha_evento_subsidio.valor_base
        )

        valor_dentro_estado = Decimal(self.consolidado["valor_base_subsidio"] / 30)
        valor_fora_estado = Decimal(valor_dentro_estado) + (
            valor_dentro_estado * Decimal(0.1)
        )
        valor_com_motorista = Decimal(valor_dentro_estado) - (
            valor_dentro_estado * Decimal(0.1)
        )

        self.calcular_diarias(
            valor_dentro_estado, valor_fora_estado, valor_com_motorista
        )

        return self.consolidado

    def calcular_diarias_servidor(self):
        """
        Método responsável por coletar as informações necessárias para realizar o cálculo de diárias de um beneficiário
        do tipo Servidor (que não seja Membro).

        Os valores de referência para pagamentos de Servidor devem ser buscados no modelo ValorDiarias, utilizando o método 'buscar_valor_vigente'.
        """

        valor_vigente = ValorDiarias().buscar_valor_vigente()
        self.calcular_diarias(
            valor_vigente.valor_estado, valor_vigente.valor_fora_estado
        )

        return self.consolidado

    def recalcular_diarias_deferidas(self, qtd_diarias_def):
        """
        Função para recalcular os valores de diárias com base na quantidade de diárias deferidas.
        """

        qtd_diarias_deferidas = Decimal(qtd_diarias_def)

        calculo_consolidado = CalculoConsolidado.objects.filter(
            beneficiario=self.consolidado["beneficiario"]
        ).first()

        valor_base_diaria = calculo_consolidado.valor_base_diaria
        valor_base_alimentacao = calculo_consolidado.valor_base_desc_alimentacao
        valor_base_transporte = calculo_consolidado.valor_base_desc_transporte

        calculo_consolidado.valor_desc_alimentacao = Decimal(0)
        calculo_consolidado.valor_desc_transporte = Decimal(0)
        calculo_consolidado.valor_total_veiculo_mp = Decimal(0)
        calculo_consolidado.valor_total_desconto = Decimal(0)
        calculo_consolidado.valor_total_bruto = Decimal(0)
        calculo_consolidado.valor_total_liquido = Decimal(0)
        calculo_consolidado.valor_total_liquido_deferido = Decimal(0)

        # 1. Recalcular o valor relacionado ao veículo do MP
        membro_com_veiculo_daa = membro_solicitou_veiculo_daa(self.beneficiario)
        if membro_com_veiculo_daa:
            calculo_consolidado.valor_total_veiculo_mp = Decimal(
                valor_base_diaria * qtd_diarias_deferidas
            )

        # 2. Recalcular os descontos de alimentação e transporte
        if qtd_diarias_deferidas % 1 == 0.5:
            qtd_diarias_desconto = Decimal((qtd_diarias_def) + 0.5)
        else:
            qtd_diarias_desconto = qtd_diarias_deferidas

        if valor_base_alimentacao:
            calculo_consolidado.valor_desc_alimentacao = Decimal(
                (valor_base_alimentacao / 30) * qtd_diarias_desconto
            )
            calculo_consolidado.valor_total_desconto += Decimal(
                calculo_consolidado.valor_desc_alimentacao
            )

        if valor_base_transporte:
            calculo_consolidado.valor_desc_transporte = Decimal(
                (valor_base_transporte / 30) * qtd_diarias_desconto
            )
            calculo_consolidado.valor_total_desconto += Decimal(
                calculo_consolidado.valor_desc_transporte
            )

        # 3. Recalcular o valor total bruto e líquido
        valor_total_bruto = Decimal(valor_base_diaria * qtd_diarias_deferidas)
        calculo_consolidado.valor_total_bruto = valor_total_bruto

        # 4. Calcular o valor líquido
        calculo_consolidado.valor_total_liquido = Decimal(
            valor_total_bruto - calculo_consolidado.valor_total_desconto
        )

        # 5. Atualizar o valor líquido deferido
        calculo_consolidado.valor_total_liquido_deferido = (
            calculo_consolidado.valor_total_liquido
        )

        # 6. Salvar os valores recalculados no modelo CalculoConsolidado
        calculo_consolidado.save()

        return calculo_consolidado

    def recalcular_diarias(self):
        """
        Função para recalcular os valores de diárias com base na quantidade de diárias deferidas.
        """

        calculo_consolidado = CalculoConsolidado.objects.filter(
            beneficiario=self.consolidado["beneficiario"]
        ).first()

        qtd_diarias_def = Decimal(
            calculo_consolidado.qtd_total_diarias_deferido
        ) or Decimal(calculo_consolidado.qtd_total_diarias)

        valor_base_diaria = calculo_consolidado.valor_base_diaria
        valor_base_alimentacao = calculo_consolidado.valor_base_desc_alimentacao
        valor_base_transporte = calculo_consolidado.valor_base_desc_transporte

        calculo_consolidado.valor_desc_alimentacao = Decimal(0)
        calculo_consolidado.valor_desc_transporte = Decimal(0)
        calculo_consolidado.valor_total_veiculo_mp = Decimal(0)
        calculo_consolidado.valor_total_desconto = Decimal(0)
        calculo_consolidado.valor_total_bruto = Decimal(0)
        calculo_consolidado.valor_total_liquido = Decimal(0)
        calculo_consolidado.valor_total_liquido_deferido = Decimal(0)

        # 1. Recalcular o valor relacionado ao veículo do MP
        membro_com_veiculo_daa = membro_solicitou_veiculo_daa(self.beneficiario)
        if membro_com_veiculo_daa:
            calculo_consolidado.valor_total_veiculo_mp = Decimal(
                valor_base_diaria * calculo_consolidado.qtd_total_diarias_deferido
            )

        # 2. Recalcular os descontos de alimentação e transporte
        if calculo_consolidado.qtd_total_diarias_deferido % 1 == 0.5:
            qtd_diarias_desconto = Decimal((qtd_diarias_def) + Decimal(0.5))
        else:
            qtd_diarias_desconto = calculo_consolidado.qtd_total_diarias_deferido

        if valor_base_alimentacao:
            calculo_consolidado.valor_desc_alimentacao = Decimal(
                (valor_base_alimentacao / 30) * qtd_diarias_desconto
            )
            calculo_consolidado.valor_total_desconto += Decimal(
                calculo_consolidado.valor_desc_alimentacao
            )

        if valor_base_transporte:
            calculo_consolidado.valor_desc_transporte = Decimal(
                (valor_base_transporte / 30) * qtd_diarias_desconto
            )
            calculo_consolidado.valor_total_desconto += Decimal(
                calculo_consolidado.valor_desc_transporte
            )

        # 3. Recalcular o valor total bruto e líquido
        valor_total_bruto = Decimal(
            valor_base_diaria * calculo_consolidado.qtd_total_diarias_deferido
        )
        calculo_consolidado.valor_total_bruto = valor_total_bruto

        # 4. Calcular o valor líquido
        calculo_consolidado.valor_total_liquido = Decimal(
            valor_total_bruto - calculo_consolidado.valor_total_desconto
        )

        # 5. Atualizar o valor líquido deferido
        calculo_consolidado.valor_total_liquido_deferido = (
            calculo_consolidado.valor_total_liquido
        )

        # 6. Salvar os valores recalculados no modelo CalculoConsolidado
        calculo_consolidado.save()

        return calculo_consolidado
