# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.classcodes.salaryprogression.base import SalaryProgressionBase
from standard.models import RunCodeManager

log = getLogger(__name__)


@RunCodeManager.register("mpto-salaryprogression")
class MPTOSalaryProgression(SalaryProgressionBase):
    typeof = "PROGRESSION"
    title = "Código de validações para MPTO"
    description = ""

    def requirements(self, *args, **kwargs):
        """ """
        # if not hasattr(self, '_requirements'):
        salaryprogression = self.salaryprogression
        self._requirements = {"wait": [], "unfit": [], "block": []}

        # Requisitos de faltas (Lei Art. 16 I)
        cute_absences = 5 if salaryprogression.referencia_nivel2d.ordem > 1 else 45
        if salaryprogression.period_absences > cute_absences:
            self._requirements["unfit"].append(
                "Possui mais de %d faltas no período. (Art. 16 inciso I)"
                % cute_absences
            )

        # # Requisitos de suspensão do serviço público. (Lei Art. 16 II) -------------------------------------------
        # dr_suspensions = NewDateRange()
        # for sa in AfastamentoSuspensao.objects.filter(servidor=self.servidor):
        #     dr_suspensions += NewDateRange(sa.data_inicio, sa.data_fim)
        # dr_progression = NewDateRange(self.data_inicio_vigencia, self.expected_date)
        # dr_suspension = dr_suspensions.intersect(dr_progression)
        # if dr_suspension.days > 0:
        #     self._requirements['unfit'].append('Possui punição de suspensão no período. (Art. 16 inciso II)')
        # # --------------------------------------------------------------------------------------------------------

        if salaryprogression.referencia_nivel2d.ordem == 1:
            # Requisitos de aprovação no estágio probatório
            if hasattr(salaryprogression.movimentacao_posse, "estagio_probatorio"):
                eps = salaryprogression.movimentacao_posse.estagio_probatorio
                if eps.is_aprovado() is False:
                    self._requirements["unfit"].append(
                        "Reprovado no estágio probatório."
                    )
                elif eps.is_aprovado() is None:
                    self._requirements["block"].append(
                        "Sem informação do estágio probatório."
                    )
            else:
                self._requirements["block"].append(
                    "Sem informação do estágio probatório."
                )
            # --------------------------------------------------------------------------------------------------------
        else:
            # Requisitos de progressão -------------------------------------------------------------------------------
            self._requirements["wait"].append(
                "Aguardando resultado da APD maior que 60%."
            )
            if (
                salaryprogression.next_reference
                and salaryprogression.referencia_nivel2d.vertical
                == salaryprogression.next_reference.vertical
            ):
                self._requirements["wait"].append(
                    "Aguardando comprovação de qualificação."
                )
            # --------------------------------------------------------------------------------------------------------
        return self._requirements
