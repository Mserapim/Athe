import {Component, OnInit} from "@angular/core";
import {ESocialItensTabelaService} from "./e-social-itens-tabela.service";
import moment from "moment/moment";
import {apiESocialListarTabelas} from "../../../api/esocial/api-esocial-listar-tabelas.service";
import {MatSnackBar} from "@angular/material/snack-bar";
import {FuseConfirmationService} from "../../../@fuse/services/confirmation";
import {apiESocialApagarItemTabela} from "../../../api/esocial/api-esocial-apagar-item-tabela.service";
import {MatDialog} from "@angular/material/dialog";
import {ItemTabelaCriarDialogComponent} from "./components/item-tabela-criar-dialog/item-tabela-criar-dialog.component";
import {
    ItemTabelaEditarDialogComponent
} from "./components/item-tabela-editar-dialog/item-tabela-editar-dialog.component";
import {DateTime} from "luxon";
import {NavegacaoAtualService} from "../../../core/navegacao-atual/navegacao-atual.service";

class OpcoesDetalhe {
    id: number;
    titulo: string;
    valor: string;
}

class ItemTabela {
    id: number;
    titulo: string;
    codigo: string;
    info: string;
    descricao: string;
    tabela_esocial: string;
    inicio_vigencia: Date;
    fim_vigencia: Date;
    criado_em: DateTime;
    modificado_em: DateTime;
    criado_por: string;
    modificado_por: string;
    choice_filtro: string;
    opcoes_detalhes: OpcoesDetalhe[];
}

@Component({
    selector: 'e-social-itens-tabela',
    templateUrl: 'e-social-itens-tabela.component.html',
    standalone: false
})
export class ESocialItensTabelaComponent implements OnInit {

    tabelasFiltro: any[] = []

    constructor(public service: ESocialItensTabelaService,
                protected snackBar: MatSnackBar,
                private _fuseConfirmationService: FuseConfirmationService,
                public navegacaoAtualService: NavegacaoAtualService,
                private dialog: MatDialog) {

    }
    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();

        apiESocialListarTabelas().then(response => {
            this.tabelasFiltro = response.results
        })
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Chave',
                visivel: false,
            },
            {
                codigo: 'codigo',
                titulo: 'Codígo',
                visivel: true,
            },
            {
                codigo: 'info',
                titulo: 'Info',
                visivel: false,
            },
            {
                codigo: 'titulo',
                titulo: 'Título',
                visivel: true,
            },
            // {
            //     codigo: 'descricao',
            //     titulo: 'Descrição',
            //     visivel: true,
            // },
            {
                codigo: 'tabela_esocial',
                titulo: 'Tabela',
                visivel: true,
            },
            // {
            //     codigo: 'opcoes_detalhes',
            //     titulo: 'Opcoes',
            //     visivel: true,
            // },
            {
                codigo: 'inicio_vigencia',
                titulo: 'Inicio Vigência',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'fim_vigencia',
                titulo: 'Fim Vigência',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'modificado_em',
                titulo: 'Modificado Em',
                visivel: false,
            },
            {
                codigo: 'modificado_por',
                titulo: 'Modificado Por',
                visivel: false,
            },
            {
                codigo: 'criado_em',
                titulo: 'Criado Em',
                visivel: false,
            },
            {
                codigo: 'criado_por',
                titulo: 'Criado Por',
                visivel: false,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        titulo: 'Excluir',
                        icone: 'cancel',
                        requerPermissao: 'apagar',
                        aoClicar: (linha: any) => this.excluir(linha),
                    },
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        requerPermissao: 'editar',
                        aoClicar: (linha: any) => this.editar(linha),
                    }
                ]
            }
        ]);

        this.service.configurarColunasAccordion([
            {
                codigo: 'descricao',
                titulo: 'Descrição',
                tipo: 'TEXTO'
            },
            {
                codigo: 'opcoes_detalhes',
                titulo: 'Opções correspondentes',
                lista: true,
                transformarValor: (linha: any) => this.formatarListaOpcoes(linha),
                tipo: 'LISTA'
            }
        ])
    }

    getData(data: string) {
        return moment(data).format('DD/MM/YY');
    }
    getDataHora(data: string) {
        return moment(data).format('DD/MM/YY HH:mm:ss');
    }

    criar() {
        const dialogRef = this.dialog.open(ItemTabelaCriarDialogComponent, {
            width: '65%',
            maxWidth: '98vw',
            maxHeight: '98vh',
            data: {
                close: () => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.service.recarregarListagem();
        });
    }

    excluir(linha: any) {
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja apagar o item de tabela '+ linha.titulo + ' ?',
            icon: {
                show: true,
                name: 'heroicons_outline:exclamation',
                color: 'warn'
            },
            actions: {
                confirm: {
                    show: true,
                    label: 'Apagar',
                    style: { 'background-color': '#dc2626' },
                },
                cancel: {
                    show: true,
                    label: 'Cancelar',
                    style: { 'background-color': '#cbd5e1' },
                    useClass: true,
                    class: 'text-black'
                }
            },
            dismissible: true
        });

        dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                try {

                    result = await apiESocialApagarItemTabela({
                        id: linha.id
                    });

                    this.exibirMensagem('', result.datail)

                    this.service.recarregarListagem();


                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
        });
    }

    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    private editar(linha: any) {
        const dialogRef = this.dialog.open(ItemTabelaEditarDialogComponent, {
            width: '65%',
            maxWidth: '98vw',
            maxHeight: '98vh',
            data: {
                id: linha.id,
                close: () => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.service.recarregarListagem();
        });
    }

    private formatarListaOpcoes(linha: ItemTabela) {
        let opcoes = linha.opcoes_detalhes.map(opcaoDetalhe => opcaoDetalhe.titulo);

        return opcoes;
    }
}
