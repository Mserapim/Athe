import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { PainelControleServicosService } from './painel-controle-servicos.service';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { PainelControleServicoNovoComponent } from '../painel-controle-servico-novo/painel-controle-servico-novo.component';
import { PainelControleServicoEditarComponent } from '../painel-controle-servico-editar/painel-controle-servico-editar.component';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { apiPainelControleServicoExecutar } from 'api/painel-controle/api-painel-controle-servico-executar.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PainelControleServicoApagarComponent } from '../painel-controle-servico-apagar/painel-controle-servico-apagar.component';
import { Router } from '@angular/router';

const EXECUTADO = [
    { value: 'True', label: 'Executado' },
    { value: 'False', label: 'Não executado' },
];

@Component({
    selector: 'painel-controle-servicos',
    templateUrl: 'painel-controle-servicos.component.html',
    standalone: false
})
export class PainelControleServicosComponent implements OnInit {
    options = {
        executado: EXECUTADO,
    };

    filter = {
        keyword: '',
        executado: [],
    };

    titulo = 'Serviços';

    constructor(
        public service: PainelControleServicosService,
        public dialog: MatDialog,
        public navegacaoAtualService: NavegacaoAtualService,
        private _fuseConfirmationService: FuseConfirmationService,
        protected snackBar: MatSnackBar,
        private _router: Router,
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: true,
            },
            {
                codigo: 'name',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'command',
                titulo: 'Comando',
                visivel: true,
            },
            {
                codigo: 'description',
                titulo: 'Descrição',
                visivel: true,
            },
            {
                codigo: 'classcode_path',
                titulo: 'Classcode',
                visivel: true,
            },
            {
                codigo: 'executado_em',
                titulo: 'Executado em',
                visivel: false,
            },
            {
                codigo: 'executado_por_unicode',
                titulo: 'Executado por',
                visivel: false,
            },
            {
                codigo: 'status_execucao',
                titulo: 'Executado',
                visivel: true,
                tipo: 'EXECUCAO',
            },
            {
                codigo: 'created_at',
                titulo: 'Criado em',
                visivel: false,
            },
            {
                codigo: 'modified_at',
                titulo: 'Modificado em',
                visivel: false,
            },
            {
                codigo: 'created_by_unicode',
                titulo: 'Criado por',
                visivel: false,
            },
            {
                codigo: 'modified_by_unicode',
                titulo: 'Modificado por',
                visivel: false,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        requerPermissao: 'editar',
                        aoClicar: (linha: any) => this.irEditarServico(linha),
                    },
                    {
                        icone: 'delete',
                        titulo: 'Apagar',
                        requerPermissao: 'apagar',
                        aoClicar: (linha: any) => this.irApagarServico(linha),
                    },
                    {
                        icone: 'play_circle_outline',
                        titulo: 'Executar',
                        requerPermissao: 'ativar',
                        aoClicar: (linha: any) => this.irExecutarServico(linha),
                    },
                    {
                        icone: 'history',
                        titulo: 'Visualizar histórico',
                        requerPermissao: 'ler',
                        aoClicar: (linha: any) => this.irVisualizarHistorico(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovoServico() {
        this.dialog.open(PainelControleServicoNovoComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarServico(linha: { id: number }) {
        this.dialog.open(PainelControleServicoEditarComponent, {
            data: {
                servico_id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected irApagarServico(linha: { id: number }) {
        this.dialog.open(PainelControleServicoApagarComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected irExecutarServico(linha: { id: number, em_execucao: boolean }) {

        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja executar o serviço?',
            icon: {
            show: true,
            name: 'heroicons_outline:exclamation',
            color: 'warn'
            },
            actions: {
                confirm: {
                show: true,
                label: 'Executar',
                style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                show: true,
                label: 'Cancelar',
                style: { 'background-color': '#cbd5e1' },
                }
            },
            dismissible: true
        });

        dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                this.exibirMensagem('', 'Job solicitado com sucesso!', 'sucess-snackbar')
                try {
                    setTimeout(() => {
                        this.service.recarregarListagem(); // Recarrega a listagem para exibir o status atualizado: em_execucao
                    }, 1000);

                    result = await apiPainelControleServicoExecutar({
                        id: linha.id
                    });
                    
                    this.exibirMensagem('', result.message, 'sucess-snackbar')

                    this.service.recarregarListagem(); // Recarrega a listagem para exibir o status atualizado: em_execucao
        
                } catch (e: any) {
                    let detalheErro = '';

                    if (e?.response) {
                        detalheErro = e.response.data?.error || e.response.data?.detail || 'Serviço ainda em execução. Por favor, acompanhe pela tela Histórico de serviços!';
                    } else {
                        detalheErro = `Erro inesperado: ${e.message}`;
                    }

                    this.exibirMensagem('Atenção', detalheErro);
                }
            }
        });
    }
    
    protected irVisualizarHistorico(linha: { id: number }) {
        this._router.navigate(['painel-controle/historico-servicos/'], {
            queryParams: { servico_id: linha.id },
        });
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }
}
