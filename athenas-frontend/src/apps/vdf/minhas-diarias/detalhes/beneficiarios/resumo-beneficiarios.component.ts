import { Component, Inject, Optional } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { apiReceberBeneficiarios } from 'api/diarias/analise-beneficiario/api-receber-beneficiarios.service';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { apiDiariasViagem } from 'api/diarias/api-diarias-viagem.service';
import { apiDiariasPagamentos } from 'api/diarias/pagamentos/api-diarias-pagamentos.service';
import { CienciaCancelamentoComponent } from 'apps/diarias/gestao/viagem/ver-diaria-aprovador/ciencia-cancelamento-diarias/ciencia-cancelamento-diarias.component';
import { VerDiariaService } from 'apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { Subscription } from 'rxjs';

class ResumoBeneficiariosDiariasComponentData {
    id: number;
}

@Component({
    selector: 'resumo-beneficiarios',
    templateUrl: './resumo-beneficiarios.component.html',
    standalone: false
})
export class ResumoBeneficiariosDiarias extends MpmtFormularioComponent<ResumoBeneficiariosDiariasComponentData> {
    beneficiarios: any = [];
    viagem: any = {};
    tituloViagem: string = '';
    acordeaoAbertoIndex: number | null = null;
    podeGerarCnab: boolean = false;
    private refreshSubscription: Subscription;
    darCienciaCancelamentoDEPLAN: boolean = false;
    darCienciaCancelamentoDAA: boolean = false;
    darCienciaCancelamentoDG: boolean = false;

    fluxoAguardandoNota: number = 13;
    fluxoNotaAndamento: number = 47;
    fluxoOrdemAndamento: number = 51;
    
    fluxoAguardandoEmpenho: number = 10;
    fluxoAguardandoOrdem: number = 14;
    fluxoEmpenhoAndamento: number[] = [50, 49];

    constructor(
        @Inject(MAT_DIALOG_DATA) protected data: ResumoBeneficiariosDiariasComponentData,
        @Optional() protected dialogRef: MatDialogRef<ResumoBeneficiariosDiariasComponentData>,
        protected snackBar: MatSnackBar,
        private verDiariaService: VerDiariaService,
        private router: Router,
        public dialog: MatDialog,

    ) {
        super(data, snackBar, dialogRef);
    }
    
    ngOnInit() {
        this.carregarDados();

        this.refreshSubscription = this.verDiariaService.refresh$.subscribe(() => {
            this.carregarDados();
        });
    }

    ngOnDestroy() {
        if (this.refreshSubscription) {
            this.refreshSubscription.unsubscribe();
        }
    }

    async carregarDados() {
        await this.carregarBeneficiarios();
        await this.carregarDadosViagem();
    }
    
    async carregarBeneficiarios() {
        const viagem_id = this.data && this.data.id ? this.data.id : this.verDiariaService.viagemId;
        const telaChefeImediato = this.verDiariaService.telaChefeImediato;
        try {
            const beneficiarios = await apiDiariasBeneficiarios({ 
                viagem_id: viagem_id,
                telaChefeImediato: telaChefeImediato
             });
            this.beneficiarios = beneficiarios.results.map(beneficiario => {
                let titulo = beneficiario.servidor_unicode;
                if (beneficiario.qtd_total_diarias_deferido) {
                    titulo = `${beneficiario.servidor_unicode} - ${beneficiario.qtd_total_diarias_deferido} DIÁRIAS`;
                } else if (beneficiario.qtd_total_diarias) {
                    titulo = `${beneficiario.servidor_unicode} - ${beneficiario.qtd_total_diarias} DIÁRIAS`;
                }
    
                return {
                    ...beneficiario,
                    titulo
                };
            });

            await this.verificarPodeGerarCnab();
            await this.verificarCienciaCancelamento()

        } catch (e: any) {
        console.error('Erro ao buscar dados', e);
        }
    }

    async carregarDadosViagem() {
        const id = this.data && this.data.id ? this.data.id : this.verDiariaService.viagemId;
        if (id != null) {
            try {
                const viagem = await apiDiariasViagem({ id: id });
                this.viagem = viagem

                if (this.viagem.data_inicio_viagem) {
                    const [year, month, day] = this.viagem.data_inicio_viagem.split('-').map(Number);
                    this.verDiariaService.dataInicio = new Date(year, month - 1, day);
                }
                if (this.viagem.data_fim_viagem) {
                    const [year, month, day] = this.viagem.data_fim_viagem.split('-').map(Number);
                    this.verDiariaService.dataFim = new Date(year, month - 1, day);
                }
                if (this.viagem.situacao_etapa_atual) {
                    this.verDiariaService.fluxoViagem = this.viagem.situacao_etapa_atual;
                }
                if (this.viagem.situacao_solicitacao_display) {
                    this.verDiariaService.situacaoSolicitacao = this.viagem.situacao_solicitacao_display;
                }
                if (this.viagem.etapa_solicitacao_display) {
                    this.verDiariaService.etapaSolicitacao = this.viagem.etapa_solicitacao_display;
                } 
                if (this.viagem.excedente !== undefined) {
                    this.verDiariaService.excedente = this.viagem.excedente;
                }
                if (this.viagem.possui_excedente !== undefined) {
                    this.verDiariaService.possuiExcedente = this.viagem.possui_excedente;
                }
                if ([71, 72, 73].includes(this.viagem.finalidade_viagem)) {
                    this.verDiariaService.finalidadeAcompanhamento = true;
                }
            } catch (e: any) {
                const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
                this.exibirMensagem('Erro', detalheErro);
            }
        }
    }

    alternarAcordeao(index: number): void {
        if (this.acordeaoAbertoIndex === index) {
            this.acordeaoAbertoIndex = null;
        } else {
            this.acordeaoAbertoIndex = index;
        }
    }

    async verificarPodeGerarCnab() {
        if (!this.verDiariaService.viagemId) {
            this.podeGerarCnab = false;
            return;
        }

        const beneficiarioIds = this.beneficiarios.map(b => b.id);
        try {
            const pagamentos = await apiDiariasPagamentos({ status: ['aguardando'] });
            const pagamentosIds = pagamentos.results.map(p => p.beneficiario);
            this.podeGerarCnab = beneficiarioIds.every(id => pagamentosIds.includes(id));
        } catch (e: any) {
            console.error('Erro ao verificar pagamentos', e);
            this.podeGerarCnab = false;
        }
    }

    gerarCnabParaPagamento(): void {
        const beneficiarioIds = this.beneficiarios.map((b: any) => b.id);
        this.router.navigate(['/diarias/gestao/pagamentos'], {
            queryParams: { beneficiarios: beneficiarioIds.join(',') }
        });
    }

    async verificarCienciaCancelamento() {
        this.darCienciaCancelamentoDAA = false;
        this.darCienciaCancelamentoDEPLAN = false;
        this.darCienciaCancelamentoDG = false;

        if (!this.verDiariaService.viagemId) {
            return false

        } else if (this.beneficiarios.some(beneficiario =>beneficiario.fluxo === 34)) {
            this.darCienciaCancelamentoDAA = true;
            //fluxo_id = 34: Aguardando ciência de cancelamento - DAA
            return true;

        } else if (this.beneficiarios.some(beneficiario => beneficiario.fluxo === 35)) {
            this.darCienciaCancelamentoDEPLAN = true;
            //fluxo_id = 35: Aguardando ciência de cancelamento - DEPLAN - Executor
            return true
        } else if (this.beneficiarios.some(beneficiario =>beneficiario.fluxo === 52)) {
            this.darCienciaCancelamentoDG = true;
            //fluxo_id = 52: Aguardando ciência de cancelamento - DG
            return true;
        }
        return false;
    }

    protected async darCienciaCancelamento() {
        let tituloModal: string;
        let fluxoID: number;

        if (this.darCienciaCancelamentoDAA) {
            tituloModal = "Ciência de cancelamento de diária - DAA";
            fluxoID = 34;
        } else if (this.darCienciaCancelamentoDEPLAN) {
            tituloModal = "Ciência de cancelamento de diária - DEPLAN";
            fluxoID = 35;
        } else if (this.darCienciaCancelamentoDG) {
            tituloModal = "Ciência de cancelamento de diária - DG";
            fluxoID = 52;
        } 

        const dialogRef = this.dialog.open(CienciaCancelamentoComponent, {
            data: {
                fluxoID: fluxoID,
                viagemID: this.verDiariaService.viagemId,
                titulo: tituloModal,
                onClose: () => {
                    this.carregarDados();
                },
            },
        });

        dialogRef.afterClosed().subscribe(() => {
            this.carregarDados();
        });
    }

    protected exibirReceber() {
        if (
            this.verDiariaService.telaAprovador &&
            this.verDiariaService.etapasAprovador.includes(this.viagem.etapa_fluxo) &&
            (
                (this.viagem.fluxo === this.fluxoAguardandoNota) ||
                (this.viagem.fluxo === this.fluxoAguardandoEmpenho) ||
                (this.viagem.fluxo === this.fluxoAguardandoOrdem)
            )
        ) {
            return true;
        }
        return false;
    }
    
    protected async irReceber() {
        try {
            await apiReceberBeneficiarios({
                viagem: this.viagem.id,
            });

            await this.carregarDados();

        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao receber os beneficiários. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    protected exibirServidorResponsavel () {
        if (this.viagem.fluxo === this.fluxoNotaAndamento ||
            this.fluxoEmpenhoAndamento.includes(this.viagem.fluxo) ||
            this.viagem.fluxo === this.fluxoOrdemAndamento
        ) {
            return true;
        }
        return false;
    }

}