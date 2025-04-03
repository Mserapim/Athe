import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DiariasConfigFluxosService } from './diarias-config-fluxos.service';
import { DiariasConfigFluxoNovoComponent } from '../diarias-config-fluxo-novo/diarias-config-fluxo-novo.component';
import { apiDiariasConfigFluxoApagar } from 'api/diarias/config/api-diarias-config-fluxo-apagar.service';
import { FuseConfirmationDialogComponent } from '@fuse/services/confirmation/dialog/dialog.component';
import { DiariasConfigFluxoEditarComponent } from '../diarias-config-fluxo-editar/diarias-config-fluxo-editar.component';
import { DiariasConfigFluxoGerenciarDestinatariosComponent } from '../diarias-config-fluxo-gerenciar-destinatarios/diarias-config-fluxo-gerenciar-destinatarios.component';


@Component({
    selector: 'diarias-config-fluxos',
    templateUrl: 'diarias-config-fluxos.component.html',
    standalone: false
})
export class DiariasConfigFluxosComponent implements OnInit {
    titulo = 'Fluxo de aprovação de diárias';

    constructor(
        public service: DiariasConfigFluxosService,
        public dialog: MatDialog,
        private snackBar: MatSnackBar
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'ordem',
                titulo: 'Ordem',
                visivel: true,
            },            
            {
                codigo: 'etapa_display',
                titulo: 'Etapa',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'situacao_display',
                titulo: 'Situação',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'condicionais_descricao',
                titulo: 'Condicionais',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'notificar_solicitante',
                titulo: 'Notificar solicitante',
                ordenavel: false,
                visivel: true,
                tipo: 'BOLEANO'
            },
            {
                codigo: 'calcular',
                titulo: 'Calcular',
                ordenavel: false,
                visivel: true,
                tipo: 'BOLEANO'
            },
            {
                codigo: 'deferir_todos_beneficiarios',
                titulo: 'Deferir todos beneficiários',
                ordenavel: false,
                visivel: true,
                tipo: 'BOLEANO'
            },
            {
                codigo: 'id',
                titulo: 'ID',
                visivel: false,
            },
            {
                codigo: 'criado_por_username',
                titulo: 'Criado por',
                visivel: false,
            },            
            {
                codigo: 'created_at',
                titulo: 'Criado em',
                visivel: false,
                tipo: 'DATA_HORA'
            },
            {
                codigo: 'modificado_por_username',
                titulo: 'Modificado por',
                visivel: false,
            }, 
            {
                codigo: 'modified_at',
                titulo: 'Modificado em',
                visivel: false,
                tipo: 'DATA_HORA'
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        titulo: 'Editar',
                        icone: 'edit',
                        aoClicar: (linha: any) => this.irEditarFluxo(linha),
                    },
                    {
                        titulo: 'Gerenciar destinatários',
                        icone: 'contact_mail',
                        aoClicar: (linha: any) => this.irGerenciarDestinatarios(linha),
                    },
                    {
                        titulo: 'Apagar',
                        icone: 'delete',
                        aoClicar: (linha: any) => this.irApagarFluxo(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovoFluxo() {
        this.dialog.open(DiariasConfigFluxoNovoComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarFluxo(linha: { id: number }) {
        this.dialog.open(DiariasConfigFluxoEditarComponent, {
            data: { 
                pk: linha.id,
                onClose: () => this.service.recarregarListagem() 
            },
        });
    }

    protected irApagarFluxo(linha: { id: number }) {
        const dialogData = {
            title: 'Confirmação de exclusão',
            message: 'Tem certeza que deseja apagar esta etapa do fluxo?',
            icon: { name: 'warning', color: 'warn' },
            actions: {
                cancel: {
                    show: true,
                    label: 'Cancelar'
                },
                confirm: {
                    show: true,
                    label: 'Apagar',
                    useStyle: true,
                    style: {
                        backgroundColor: '#dc2626',
                        color: 'white',
                        border: 'none'
                    }
                }
            }
        };
    
        const dialogRef = this.dialog.open(FuseConfirmationDialogComponent, {
            width: '400px',
            data: dialogData
        });
    
        dialogRef.afterClosed().subscribe(result => {
            if (result === 'confirmed') {
                apiDiariasConfigFluxoApagar({ id: linha.id })
                    .then(() => {
                        this.snackBar.open('Etapa apagada com sucesso!', '', { duration: 3000 });
                        this.service.recarregarListagem();
                    })
                    .catch(error => {
                        console.error('Erro ao apagar a etapa:', error);
                        this.snackBar.open('Erro ao apagar a etapa!', '', { duration: 3000 });
                    });
            }
        });
    }

    protected irGerenciarDestinatarios(linha: { id: number }){
        this.dialog.open(DiariasConfigFluxoGerenciarDestinatariosComponent, {
            data: { 
                pk: linha.id,
                onClose: () => this.service.recarregarListagem() 
            },
        });
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }
}
