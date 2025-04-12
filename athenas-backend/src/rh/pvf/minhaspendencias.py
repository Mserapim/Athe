from rh.pvf.apiv2.utils.approval import filtro_tipo_servidor, group_list
from rh.pvf.approvalflow import (
    REQUEST_TYPE_DESBLOQUEIO_TELETRABALHO,
    STS_WAI_APPROVER,
    STS_WAI_EFFECTIVENESS,
)
from rh.pvf.models import PortalRequest
from datetime import datetime
from rh.pvf.const import (
    STS_CANCELED_APPLICANT,
    STS_CANCELED_DGP,
    STS_EFFECTIVE,
    STS_REJECTED,
)
from rh.pvf.utils.chefe_imediato import get_aprovador
from rh.registerpoint.models import MarkPoint
from rh.pvf.apiv2.utils.telework import (
    aprovador_semestral,
    is_workplan,
    referencias_pendentes,
)
from django.db.models.query_utils import Q

from rh.teletrabalho.models import ConfigPeriodoEnvioRelatoriosSemestrais

from contrib.utils import getLogger
from diarias.models import PrestacaoContas
from diarias.const import (
    FLUXOS_PAGAMENTO,
    FLUXOS_PRESTACAO_CONTAS,
    FLUXO_FINALIZADO,
    FLUXOS_CANCELADOS,
)

log = getLogger(__name__)


class MinhasPendencias(object):

    def pendencias(self, employee):
        data = []
        self.get_aprovacoes_pendentes(data, employee)
        self.get_pendencias_ponto(data, employee)
        self.get_pendencia_envio_relatorio_semestral(data, employee)
        self.get_pendencia_envio_prestacao_contas_diarias(data, employee)
        self.get_pendencia_aprovadores_diarias(data, employee)
        self.get_pendencias_teletrabalho(data, employee)
        self.get_pendencia_ciencia_chefe_imediato(data, employee)
        self.get_pendencias_desbloqueio_teletrabalho(data, employee)
        return data

    def get_aprovacoes_pendentes(self, data, employee):
        etapas = group_list(employee)
        query = PortalRequest.objects.filter(
            Q(approver=employee) | Q(step_current__in=etapas)
        ).exclude(
            status__in=[
                STS_EFFECTIVE,
                STS_REJECTED,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
            ]
        )

        tipo_servidor = filtro_tipo_servidor(employee)
        if tipo_servidor:
            query = query.filter(employee__type_by_possession__in=tipo_servidor)
        qtd_pendencias = query.count()

        if qtd_pendencias >= 1:
            msg = f"{qtd_pendencias} solicitação(es) aguardando aprovação"
            data.append(
                {
                    "type": "APROVACOES_PENDENTES",
                    "title": "Minhas Aprovações",
                    "message": msg,
                    "value": None,
                }
            )

    def get_pendencias_ponto(self, data, employee):
        if (
            employee.type_by_possession not in ["MBR", "MEL", "MEC"]
            and not is_workplan(employee)
            and not employee.servidor_lotacao.filter(
                movimentacao_posse__quadro__cargo__chefia=True
            ).exists()
        ):
            qtd_marcacao_ponto = MarkPoint.objects.filter(
                employee=employee, day=datetime.today().date()
            )
            if not qtd_marcacao_ponto:
                data.append(
                    {
                        "type": "REGISTRO_PONTO_ENTRADA",
                        "title": "Folha Ponto",
                        "message": "Registre o ponto de entrada",
                        "value": None,
                    }
                )

    def get_pendencia_envio_relatorio_semestral(self, data, employee):
        """
        Função que adiciona a lista as pendencias de envio do relatório semestral
        args:
            data: lista de pendências
            servidor (objeto): instancia do servidor.
        """
        data_atual = datetime.today().date()
        periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.last()
        if aprovador_semestral(employee, data_atual):
            data.append(
                {
                    "type": "RELATORIO_SEMESTRAL_PENDENTE",
                    "title": "Relatório Semestral do teletrabalho",
                    "message": f"Envio pendente referente ao período {periodo.data_inicio_periodo_analisado} a {periodo.data_fim_periodo_analisado}.",
                    "value": None,
                }
            )

    def get_pendencia_envio_prestacao_contas_diarias(self, data, servidor):
        q_prestacoes = PrestacaoContas.objects.filter(
            beneficiario__servidor=servidor, status="aguardando"
        )

        if q_prestacoes.exists():
            data.append(
                {
                    "type": "PRESTACAO_CONTAS_DIARIAS",
                    "title": "Diárias",
                    "message": "Prestação de Contas de Diária",
                    "value": q_prestacoes.first().id,
                }
            )

    def get_pendencias_teletrabalho(self, data, employee):
        """
        Função que adiciona a lista as pendencias de envio do relatório mensal
        args:
            data: lista de pendências
            servidor (objeto): instancia do servidor.
        """
        referencias = referencias_pendentes(employee)
        if len(referencias) > 0 and not employee.is_teletrabalho_bloqueado:
            texto = ""
            for ref in referencias:
                if texto == "":
                    texto = f"{ref}"
                else:
                    texto = f"{texto}, {ref}"
            data.append(
                {
                    "type": "ENVIO_TELETRABALHO_PENDENTE",
                    "title": "Envio do teletrabalho",
                    "message": f"Envio pendente referente ao(s) período(s): {texto}.",
                    "value": None,
                }
            )

    def get_pendencia_ciencia_chefe_imediato(self, data, employee):
        """
        Função que adiciona à lista as pendencias as solicitações de diárias que
        dependem da ciência do chefe imediato
        args:
            data: lista de pendências
            servidor (objeto): instancia do servidor.
        """

        from diarias.models import Viagem

        pendencias = (
            Viagem.objects.filter(beneficiarios__fluxo_id=20)  # Fluxo "Chefe Imediato"
            .filter(beneficiarios__chefe_imediato=employee)
            .exclude(importada=True)
        )

        beneficiarios_sem_chefe = (
            Viagem.objects.filter(beneficiarios__fluxo_id=20)  # Fluxo "Chefe Imediato"
            .filter(beneficiarios__chefe_imediato__isnull=True)
            .exclude(importada=True)
        )

        viagem_ids = []

        for viagem in beneficiarios_sem_chefe:
            for beneficiario in viagem.beneficiarios.all():
                chefe_imediato = get_aprovador(beneficiario.servidor)
                if chefe_imediato and chefe_imediato == employee:
                    viagem_ids.append(viagem.id)

        if viagem_ids:
            pendencias = pendencias | Viagem.objects.filter(id__in=viagem_ids)

        qtd_pendencias = pendencias.distinct().count()

        if qtd_pendencias >= 1:
            msg = f"{qtd_pendencias} solicitação(es) de diárias aguardando aprovação"
            data.append(
                {
                    "type": "APROVACOES_DIARIAS_PENDENTES",
                    "title": "Minhas Aprovações",
                    "message": msg,
                    "value": None,
                }
            )

    def get_pendencias_desbloqueio_teletrabalho(self, data, employee):
        sol_desbloqueio_tele = PortalRequest.objects.filter(
            employee=employee,
            request_type=REQUEST_TYPE_DESBLOQUEIO_TELETRABALHO,
            status__in=[STS_WAI_APPROVER, STS_WAI_EFFECTIVENESS],
        ).exists()
        if employee.is_teletrabalho_bloqueado and not sol_desbloqueio_tele:
            data.append(
                {
                    "type": "DESBLOQUEIO_TELETRABALHO",
                    "title": "Desbloqueio Teletrabalho",
                    "message": "Realize o desbloqueio do teletrabalho",
                    "value": None,
                }
            )

    def get_pendencia_aprovadores_diarias(self, data, servidor):

        from diarias.models import GrupoAprovador, Beneficiario

        grupos = GrupoAprovador.objects.filter(servidores__id=servidor.id)

        lista_etapas = set()

        for grupo in grupos:

            lista_etapas.update(grupo.grupos)

        beneficiarios = (
            Beneficiario.objects.filter(fluxo__etapa__in=lista_etapas)
            .exclude(fluxo__id=FLUXO_FINALIZADO)
            .exclude(fluxo__id__in=FLUXOS_CANCELADOS)
            .exclude(viagem__importada=True)
        )

        if beneficiarios.exists():

            valor = "diarias"

            beneficiarios_q = beneficiarios.exclude(
                fluxo__in=[*FLUXOS_PRESTACAO_CONTAS, *FLUXOS_PAGAMENTO]
            )

            if not beneficiarios_q.exists():

                if beneficiarios.filter(fluxo__in=FLUXOS_PRESTACAO_CONTAS).exists():
                    valor = "prestacao"

                if beneficiarios.filter(fluxo__in=FLUXOS_PAGAMENTO).exists():
                    valor = "pagamento"

            data.append(
                {
                    "type": "AVALIACOES_PENDENTES_DIARIAS",
                    "title": "Diárias",
                    "message": f"{beneficiarios.count()} Avaliações Pendentes",
                    "value": valor,
                }
            )
