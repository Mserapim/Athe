import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DiariasGestaoPagamentosService } from './diaria-pagamentos.service';
import { PagamentoCnabCriarComponent } from './pagamentos-cnab/cnab-individual-criar.component';
import { PagamentoCnabEmMassaCriarComponent } from './pagamentos-cnab/cnab-multiplos-beneficiarios-criar.component';
import { ActivatedRoute, Router } from '@angular/router';
import { ManutencaoDadosBancariosComponent } from './manutencao-dados-bancarios/manutencao-dados-bancarios.component';

@Component({
    selector: 'diarias-gestao-pagamentos',
    templateUrl: 'diaria-pagamentos.component.html',
    standalone: false
})
export class DiariasGestaoPagamentosComponent implements OnInit {
    titulo = 'Pagamentos de diárias';
    beneficiarios: any[] = [];

    constructor(
        public service: DiariasGestaoPagamentosService,
        public dialog: MatDialog,
        private snackBar: MatSnackBar,
        private route: ActivatedRoute, 
        private router: Router
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();

        this.route.queryParams.subscribe(params => {
            const beneficiarios = params['beneficiarios'];
            if (beneficiarios) {
                const beneficiarioIds = beneficiarios.split(',').map((id: string) => parseInt(id, 10));
                this.carregarBeneficiarios(beneficiarioIds);
            }
        });
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'checkbox',
                titulo: '',
                visivel: true,
                tipo: 'CHECKBOX',
                ordenavel: false,
            },
            {
                codigo: 'data_inicio_viagem',
                titulo: 'Data de início da viagem',
                visivel: true,
            },
            {
                codigo: 'servidor',
                titulo: 'Beneficiário',
                visivel: true,
            },
            {
                codigo: 'status_display',
                titulo: 'Status',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'valor_liquido_deferido_viagem',
                titulo: 'Valor líquido da viagem',
                tipo: 'MOEDA',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'info_conta_bancaria',
                titulo: 'Conta bancária',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'data_pgto',
                titulo: 'Data de pagamento',
                visivel: true,
            },
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: false,
            },
            {
                codigo: 'cnab',
                titulo: 'CNAB',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'assinado_por',
                titulo: 'Assinado por',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'assinado_em',
                titulo: 'Assinado em',
                visivel: false,
            },
            {
                codigo: 'criado_por',
                titulo: 'Criado por',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'created_at',
                titulo: 'Criado em',
                tipo:'DATA_HORA',
                visivel: false,
            },
            {
                codigo: 'modificado_por',
                titulo: 'Modificado por',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'modified_at',
                titulo: 'Modificado em',
                tipo:'DATA_HORA',
                visivel: false,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        icone: 'payments',
                        titulo: 'Gerar CNAB para pagamento',
                        aoClicar: (linha: any) => this.irGerarCnabIndividual(linha, 'Gerar CNAB para pagamento'),
                        exibirSe: (linha: any) => linha.status === 'aguardando',
                    },
                    {
                        icone: 'autorenew',
                        titulo: 'Regerar CNAB para pagamento',
                        aoClicar: (linha: any) => this.irGerarCnabIndividual(linha, 'Regerar CNAB para pagamento'),
                        exibirSe: (linha: any) => linha.status === 'cnab_criado',
                    },
                    {
                        icone: 'account_balance_wallet',
                        titulo: 'Manutenção de dados bancários',
                        aoClicar: (linha: any) => this.irEditarDadosBancarios(linha),
                        exibirSe: (linha: any) => linha.status === 'aguardando',
                    },

                ],
            },
        ]);
    }

    protected irGerarCnab() {
        const linhasSelecionadas = this.service.obterItensSelecionados();

        if (linhasSelecionadas.length === 0) {
            this.snackBar.open('Por favor, selecione pelo menos um beneficiário.', '', {
                duration: 3000,
                horizontalPosition: 'center',
                verticalPosition: 'top',
                panelClass: ['custom-snackbar'],
            });
            return;
        }

        const dados = linhasSelecionadas.map(linha => ({
            id: linha.id,
            servidor: linha.servidor,
            valor_liquido_deferido_viagem: linha.valor_liquido_deferido_viagem,
            info_conta_bancaria: linha.info_conta_bancaria,
        }));

        this.dialog.open(PagamentoCnabEmMassaCriarComponent, {
            data: {
                titulo: 'Gerar CNAB em massa',
                dados: dados,
                onClose: () => {
                    this.service.limparItensSelecionados();
                    this.service.recarregarListagem();
                },
            },
        });
    }

    protected irGerarCnabIndividual(linha: any, titulo: string) {
        this.dialog.open(PagamentoCnabCriarComponent, {
            data: {
                titulo: titulo,
                beneficiario_id: linha.id,
                servidor: linha.servidor,
                valor_liquido_deferido_viagem: linha.valor_liquido_deferido_viagem,
                info_conta_bancaria: linha.info_conta_bancaria,
                onClose: () => {
                    this.service.limparItensSelecionados();
                    this.service.recarregarListagem();
                },
            },
        });
    }

    protected irEditarDadosBancarios(linha: any) {
        this.dialog.open(ManutencaoDadosBancariosComponent, {
            data: {
                beneficiario_id: linha.beneficiario,
                servidor_id: linha.servidor_id,
                onClose: () => {
                    this.service.recarregarListagem();
                },
            },
        });
    }

    private carregarBeneficiarios(beneficiarioIds: number[]) {
        this.service.listagem$.subscribe(listagem => {
            const beneficiariosSelecionados = listagem.filter(item => beneficiarioIds.includes(item.beneficiario));
            if (beneficiariosSelecionados.length > 0){
                this.abrirPagamentoCnabEmMassaModal(beneficiariosSelecionados);
            }
        });
    }

    protected abrirPagamentoCnabEmMassaModal(beneficiarios: any[]) {
        const dados = beneficiarios.map(b => ({
            id: b.id,
            servidor: b.servidor,
            valor_liquido_deferido_viagem: b.valor_liquido_deferido_viagem,
            info_conta_bancaria: b.info_conta_bancaria,
        }));
        if (dados) {
            const dialogRef = this.dialog.open(PagamentoCnabEmMassaCriarComponent, {
                data: {
                    titulo: 'Gerar CNAB em massa',
                    dados: dados,
                    onClose: () => {
                        this.service.limparItensSelecionados();
                        this.service.recarregarListagem();
                    },
                },
            });

            dialogRef.afterClosed().subscribe(() => {
                this.router.navigate([], {
                    relativeTo: this.route,
                    queryParams: { beneficiarios: null },
                    queryParamsHandling: 'merge',
                });
            });
        }
    }
}
