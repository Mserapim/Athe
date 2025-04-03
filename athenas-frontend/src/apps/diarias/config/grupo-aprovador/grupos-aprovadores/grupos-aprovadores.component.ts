import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DiariasGruposAprovadoresService } from './grupos-aprovadores.service';
import { DiariasGrupoAprovadorNovoComponent } from '../grupo-aprovador-criar/grupo-aprovador-novo.component';
import { DiariasGrupoAprovadorEditarComponent } from '../grupo-aprovador-editar/grupo-aprovador-editar.component';
import { FuseConfirmationDialogComponent } from '@fuse/services/confirmation/dialog/dialog.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasGrupoAprovadorApagar } from 'api/diarias/config/grupo-aprovador/api-grupo-aprovador-apagar';
import { DiariasGrupoAprovadorEditarUsuariosComponent, DiariasGrupoAprovadorEditarUsuariosComponentData } from '../grupo-aprovador-editar-usuarios/grupo-aprovador-editar-usuarios.component';

@Component({
    selector: 'diarias-grupos-aprovadores',
    templateUrl: 'grupos-aprovadores.component.html',
    standalone: false
})
export class DiariasGruposAprovadoresComponent implements OnInit {
    titulo = 'Grupo de Aprovadores de Viagens';

    constructor(
        public service: DiariasGruposAprovadoresService,
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
                codigo: 'nome',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'quantidade_grupos',
                titulo: 'Grupos',
                ordenavel: false,
                visivel: true,
                tipo: 'VALOR_E_ACAO',
                acoes:[
                    {
                        titulo: 'Ver itens',
                        aoClicar: (linha:any) => this.irEditarGrupo(linha),
                    },
                ]
            },
            {
                codigo: 'quantidade_servidores',
                titulo: 'Servidores',
                ordenavel: false,
                visivel: true,
                tipo: 'VALOR_E_ACAO',
                acoes:[
                    {
                        titulo: 'Ver itens',
                        aoClicar: (linha:any) => this.irEditarServidores(linha),
                    },
                ]
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
                        titulo: 'Editar grupo',
                        aoClicar: (linha: any) => this.irEditarGrupo(linha),
                    },
                    {
                        icone: 'person_add',
                        titulo: 'Editar servidores',
                        aoClicar: (linha: any) => this.irEditarServidores(linha),
                    },
                    {
                        titulo: 'Apagar',
                        icone: 'delete',
                        aoClicar: (linha: any) => this.irApagarGrupo(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovoGrupo() {
        this.dialog.open(DiariasGrupoAprovadorNovoComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarGrupo(linha: { id: number }) {
        this.dialog.open(DiariasGrupoAprovadorEditarComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected irEditarServidores(linha: { id: number }) {
        this.dialog.open(DiariasGrupoAprovadorEditarUsuariosComponent, {
            data: <DiariasGrupoAprovadorEditarUsuariosComponentData>{
                id: linha.id,
                grupo:linha,
                onClose: () => this.service.recarregarListagem(),
            },
            width: '80%',
        });
    }

    protected irApagarGrupo(linha: { id: number }) {
        const dialogData = {
            title: 'Confirmação de exclusão',
            message: 'Tem certeza que deseja apagar este grupo de aprovadores?',
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
                apiDiariasGrupoAprovadorApagar({ id: linha.id })
                    .then(() => {
                        this.snackBar.open('Grupo excluído com sucesso!', '', { duration: 3000 });
                        this.service.recarregarListagem();
                    })
                    .catch(error => {
                        console.error('Erro ao excluir o grupo:', error);
                        this.snackBar.open('Erro ao excluir o grupo!', '', { duration: 3000 });
                    });
            }
        });
    }
}
