import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { PrestacoesContasService } from './prestacoes-contas.service';
import { PrestacaoContasComponent } from './modal-prestacao-contas/modal-prestacao-contas.component';
import { apiDiariasPrestacaoContasNotificar } from 'api/diarias/prestacao-contas/api-diarias-prestacao-contas-notificar.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiReportDiariasPrestacaoContas } from 'api/report/api-report-diarias-prestacao-contas.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { apiDiariasPrestacaoContasCancelar } from 'api/diarias/prestacao-contas/api-diarias-prestacao-contas-cancelar.service';
import { apiDiariasPrestacaoContasReceber } from 'api/diarias/prestacao-contas/api-diarias-prestacao-contas-receber.service';



@Component({
    selector: 'prestacoes-contas',
    templateUrl: 'prestacoes-contas.component.html',
    standalone: false
})
export class PrestacoesContasComponent implements OnInit {
    titulo = 'Prestação de Contas';
    
    constructor(
        protected currentUserService: CurrentUserService,
        private _fuseConfirmationService: FuseConfirmationService,
        public service: PrestacoesContasService,
        public dialog: MatDialog,
        protected snackBar: MatSnackBar,
        private router: Router,
    ) {}
    
    ngOnInit() {
        this.currentUserService.load().then(() => {
            this.service.carregarPerfilAprovador(this.currentUserService?.currentUser?.id)
                .then(() => {
                    this.configurarColunas();
                });
        });
        // this.configurarColunas();
        this.service.recarregarListagem();
    }
    
    private configurarColunas() {
        this.service.configurarColunas([
            
            {
                codigo: 'status_servidor',
                titulo: 'Status servidor',
                visivel: true,
                tipo:'BOLEANO_ICONE',
                ordenavel: false,
            },
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: false,
            },
            {
                codigo: 'status_display',
                titulo: 'Status',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'assinado_em',
                titulo: 'Data de prestação de contas',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'beneficiario_matricula',
                titulo: 'Matrícula',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'beneficiario_nome',
                titulo: 'Nome',
                visivel: true,
                ordenavel: false,

            },
            {
                codigo: 'beneficiario_situcacao',
                titulo: 'Situação',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'avaliador_nome',
                titulo: 'Avaliador',
                visivel: true,
                ordenavel: false,

            },
            {
                codigo: 'data_validacao',
                titulo: 'Data de validação',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        titulo: 'Detalhes',
                        icone: 'assignment',
                        aoClicar: (linha: any) => {
                            this.dialog.open(PrestacaoContasComponent, {
                                data: {
                                    width: '50%',
                                    height: '80%',
                                    prestacao_contas_id: linha.id,
                                    visualizacao: true,
                                    analise: true,
                                    onClose: () => {}, 
                                },
                            });
                        },
                        
                    },
                    {
                        titulo: 'Avaliar',
                        icone: 'assignment_turned_in',
                        aoClicar: (linha: any) => {
                            this.dialog.open(PrestacaoContasComponent, {
                                data: {
                                    width: '50%',
                                    height: '80%',
                                    prestacao_contas_id: linha.id,
                                    avaliar: true,
                                    onClose: () => {this.service.recarregarListagem()}, 
                                },
                            });
                        },
                        exibirSe: (linha: any) => {
                            return linha.status == 'entregue'
                        }
                    },
                    {
                        titulo: 'Cancelar',
                        icone: 'cancel',
                        aoClicar: (linha: any) => {
                            this.irCancelarPrestacaoContas(linha);
                        },
                        exibirSe: (linha: any) => (this.service.perfil.grupos.includes('ADMIN')),
                    },
                    {
                        titulo: 'Prestar contas',
                        icone: 'edit',
                        aoClicar: (linha: any) => {
                            this.dialog.open(PrestacaoContasComponent, {
                                data: {
                                    width: '50%',
                                    height: '80%',
                                    prestacao_contas_id: linha.id,
                                    avaliar: true,
                                    onClose: () => {this.service.recarregarListagem()}, 
                                },
                            });
                        },
                        exibirSe: (linha: any) => {
                            return linha.status == 'aguardando' || linha.status == 'atrasado'
                        }
                    },
                    {
                        titulo: 'Reenviar Email',
                        icone: 'email',
                        aoClicar: async (linha: any) => {
                        
                            try {
                                const result = await apiDiariasPrestacaoContasNotificar({
                                    id: linha.id
                                });
                    
                                this.exibirMensagem('', result.message, 'sucess-snackbar')
                                
                            } catch (e: any) {
                                console.error(e);
                                this.exibirErro(e);
                            }
                        },
                        exibirSe: (linha: any) => {
                            return (!['aprovado'].includes(linha.status))
                        }
                    },
                    {
                        titulo: 'Exportar Prestação de Contas',
                        icone: 'print',
                        aoClicar: async (linha: any) => {
                            try {
                                const result =
                                    await apiReportDiariasPrestacaoContas({
                                        id_prestacao: linha.id,
                                    });
                    
                                this.exibirMensagem('', result.message, 'sucess-snackbar');
                            } catch (e: any) {
                                console.error(e);
                                this.exibirErro(e);
                            }
                        },
                    },
                    {
                        titulo: 'Receber Prestação de Contas',
                        icone: 'analytics',
                        aoClicar: async (linha: any) => {
                            try {
                                const result =
                                    await apiDiariasPrestacaoContasReceber({
                                        id: linha.id,
                                    });
                    
                                this.exibirMensagem('', result.message, 'sucess-snackbar');
                            } catch (e: any) {
                                console.error(e);
                                this.exibirErro(e);
                            }
                            this.service.recarregarListagem()
                        },
                        exibirSe: (linha: any) => (this.service.perfil.etapas_aprovador.includes(18) && linha.avaliador == null),
                    },
                ],
                
            },
        ]);
    }


    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected exibirErro(e: any) {
        const detalheErro = e?.response?.data?.message || '';
        const texto = `Ocorreu um erro inesperado ao salvar. ${detalheErro}`;
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }

    protected irCancelarPrestacaoContas(linha: any) {

        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja cancelar a prestação de contas selecionada ?',
            icon: {
                show: true,
                name: 'heroicons_outline:exclamation',
                color: 'warn'
            },
            actions: {
                confirm: {
                    show: true,
                    label: 'Cancelar',
                    style: { 'background-color': '#dc2626' },
                },
                cancel: {
                    show: true,
                    label: 'Fechar',
                    style: { 'background-color': '#cbd5e1' },
                }
            },
            dismissible: true
        });

        dialogRef.afterClosed().subscribe(async result => {
            if (result === 'confirmed') {
                try {

                    result = await apiDiariasPrestacaoContasCancelar({
                        id: linha.id
                    });

                    this.exibirMensagem('', result.message)

                    this.service.recarregarListagem();


                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' || e?.response?.data?.message;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
        });

    }
}
