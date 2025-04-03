import {
    Component,
    EventEmitter,
    Inject,
    Input,
    OnInit,
    Output,
} from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { PainelControleGrupoMenuEditarListagemService } from './painel-controle-grupo-menu-editar-listagem.service';
import { apiPainelControleControleAcessoMenuConfigApagar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-config-apagar.service ';

export class PainelControleGrupoMenuEditarListagemComponentData {
    usuarioGrupoId: string;
}
@Component({
    selector: 'painel-controle-grupo-menu-editar-listagem',
    templateUrl: 'painel-controle-grupo-menu-editar-listagem.component.html',
    standalone: false
})
export class PainelControleGrupoMenuEditarListagemComponent implements OnInit {
    @Input() usuarioGrupoId: string;
    @Output() readonly irNovo: EventEmitter<null> = new EventEmitter<null>();
    @Output() readonly irEditar: EventEmitter<any> = new EventEmitter<any>();

    isLoading: boolean = true;

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleGrupoMenuEditarListagemComponentData,
        public service: PainelControleGrupoMenuEditarListagemService,
        public dialog: MatDialog
    ) {}

    ngOnInit() {}

    ngOnChanges(changes: any) {
        this.service.filtros.patchValue({
            usuario_grupo_id: this.usuarioGrupoId,
        });
        if (this.usuarioGrupoId == null) return;
        this.configurarColunas();
        this.service.recarregarListagem().then(() => this.isLoading = false);
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'modulo_nome',
                titulo: 'Módulo',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'nome_menu',
                titulo: 'Nome do menu',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'acoes',
                titulo: 'Permissões',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'actions',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        icone: 'heroicons_outline:trash',
                        titulo: 'Excluir',
                        aoClicar: (linha: any) =>
                            this.irApagarMenuConfig(linha),
                    },
                ],
            },
        ]);
    }

    public recarregarListagem() {
        this.service.recarregarListagem().then(() => this.isLoading = false);
    }

    async irApagarMenuConfig(row: any) {
        try {
            await apiPainelControleControleAcessoMenuConfigApagar({
                id: row.id,
            });
            this.service.recarregarListagem().then(() => this.isLoading = false);
        } catch (e) {
            console.error(e);
        }
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];
}
