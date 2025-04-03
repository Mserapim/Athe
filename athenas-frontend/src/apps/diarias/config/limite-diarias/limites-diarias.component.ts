import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { LimitesDiariasService } from './limites-diarias.service';
import { LimitesDiariasNovoComponent } from './limite-diarias-criar/limite-diarias-novo.component';
import { LimiteDiariasEditarComponent } from './limite-diarias-editar/limite-diarias-editar.component';
import { apiLimiteDiariasApagar } from 'api/diarias/config/limite-diarias/api-limite-diarias-apagar';
import { FuseConfirmationDialogComponent } from '@fuse/services/confirmation/dialog/dialog.component';

@Component({
    selector: 'limites-diarias',
    templateUrl: 'limites-diarias.component.html',
    standalone: false
})
export class LimitesDiariasComponent implements OnInit {
    titulo = 'Limites de diárias';

    constructor(
        public service: LimitesDiariasService,
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
                codigo: 'tipo_display',
                titulo: 'Tipo',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'referencia_display',
                titulo: 'Referência',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'motivos_viagem_display',
                titulo: 'Motivos da viagem',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'limite',
                titulo: 'Limite',
                visivel: true,
                transformarValor: (linha: any) => this.formatarLimite(linha.limite)
            },
            {
                codigo: 'dt_inicio_vigencia',
                titulo: 'Data de início de vigência',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'id',
                titulo: 'ID',
                visivel: false,
            },
            {
                codigo: 'criado_por_username',
                titulo: 'Criado por',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'created_at',
                titulo: 'Criado em',
                tipo: 'DATA_HORA',
                visivel: false,
            },
            {
                codigo: 'modificado_por_username',
                titulo: 'Modificado por',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'modified_at',
                titulo: 'Modificado em',
                tipo: 'DATA_HORA',
                visivel: false,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar limite',
                        aoClicar: (linha: any) => this.irEditarLimite(linha),
                    },
                    {
                        titulo: 'Apagar',
                        icone: 'delete',
                        aoClicar: (linha: any) => this.irApagarLimite(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovoLimite() {
        this.dialog.open(LimitesDiariasNovoComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarLimite(linha: { id: number }) {
        this.dialog.open(LimiteDiariasEditarComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }


    protected irApagarLimite(linha: { id: number }) {
        const dialogData = {
            title: 'Confirmação de exclusão',
            message: 'Tem certeza que deseja apagar este limite de diárias?',
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
                apiLimiteDiariasApagar({ id: linha.id })
                    .then(() => {
                        this.snackBar.open('Limite excluído com sucesso!', '', { duration: 3000 });
                        this.service.recarregarListagem();
                    })
                    .catch(error => {
                        let errorMessage = error?.response?.data?.detail || 'Erro desconhecido ao excluir o limite.';
                        console.error('Erro ao excluir o limite:', error);
                        this.snackBar.open(`Erro ao excluir o limite: ${errorMessage}`, '', { duration: 5000 });
                    });
            }
        });
    }

    private formatarLimite(limite: number | null): string {
        return limite === null ? 'Ilimitado' : `${limite}`;
    }
}
