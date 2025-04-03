import {Component, OnInit} from "@angular/core";
import {ESocialConfiguracoesService} from "./e-social-configuracoes.service";
import moment from "moment/moment";
import {MatSnackBar} from "@angular/material/snack-bar";
import {FuseConfirmationService} from "../../../@fuse/services/confirmation";
import {MatDialog} from "@angular/material/dialog";
import {
    ConfiguracaoCriarDialogComponent
} from "./components/configuracao-criar-dialog/configuracao-criar-dialog.component";
import {apiESocialApagarConfiguracao} from "../../../api/esocial/api-esocial-apagar-configuracao.service";
import {
    ItemTabelaEditarDialogComponent
} from "../itens-tabela/components/item-tabela-editar-dialog/item-tabela-editar-dialog.component";
import {
    ConfiguracaoEditarDialogComponent
} from "./components/configuracao-editar-dialog/configuracao-editar-dialog.component";
import {
    AtualizarCertificadoDialogComponent
} from "./components/atualizar-certificado-dialog/atualizar-certificado-dialog.component";
import {NavegacaoAtualService} from "../../../core/navegacao-atual/navegacao-atual.service";

@Component({
    selector: 'e-social-configuracoes',
    templateUrl: 'e-social-configuracoes.component.html',
    standalone: false
})
export class ESocialConfiguracoesComponent implements OnInit {

    status: any[] = []


    constructor(public service: ESocialConfiguracoesService,
                protected snackBar: MatSnackBar,
                private _fuseConfirmationService: FuseConfirmationService,
                public navegacaoAtualService: NavegacaoAtualService,
                private dialog: MatDialog) {

    }
    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Chave',
                visivel: false,
            },
            {
                codigo: 'ambiente_display',
                titulo: 'Ambiente',
                width: 'w-18',
                visivel: true,
            },
            {
                codigo: 'layout_versao',
                titulo: 'Layout',
                width: 'w-5',
                visivel: true,
            },
            {
                codigo: 'webservice_envio',
                titulo: 'WS-Envio',
                width: 'w-70',
                visivel: true,
                quebrarPalavra: true
            },
            {
                codigo: 'webservice_consulta',
                titulo: 'WS-Consulta',
                width: 'w-70',
                visivel: true,
                quebrarPalavra: true
            },
            {
                codigo: 'tabela_iniciais',
                titulo: 'Tabelas iniciais',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'periodicos',
                titulo: 'Periódicos',
                visivel: false,
            },
            {
                codigo: 'nao_periodicos',
                titulo: 'Não periódicos',
                visivel: false,
            },
            {
                codigo: 'sst',
                titulo: 'SST',
                visivel: false,
            },
            {
                codigo: 'inicio_vigencia',
                titulo: 'Início vigência',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'fim_vigencia',
                titulo: 'Fim vigência',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'data_corte_s2231',
                titulo: 'Corte de s2231',
                tipo: 'DATA',
                visivel: false,
            },
            {
                codigo: 'envio_fila',
                titulo: 'Envio em fila',
                visivel: false,
            },
            {
                codigo: 'criado_por',
                titulo: 'Criado por',
                visivel: false,
            },
            {
                codigo: 'criado_em',
                titulo: 'Criado em',
                tipo: 'DATA',
                visivel: false,
            },
            {
                codigo: 'modificado_por',
                titulo: 'Modificado por',
                visivel: false,
            },
            {
                codigo: 'modificado_em',
                titulo: 'Modificado em',
                tipo: 'DATA',
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
    }

    getData(data: string) {
        return moment(data).format('DD/MM/YY');
    }

    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    excluir(linha: any) {
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja apagar essa configuração?',
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

                    result = await apiESocialApagarConfiguracao({
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

    criar() {
        const dialogRef = this.dialog.open(ConfiguracaoCriarDialogComponent, {
            width: '90%',
            height: '80%',
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

    private editar(linha: any) {
        const dialogRef = this.dialog.open(ConfiguracaoEditarDialogComponent, {
            width: '90%',
            height: '80%',
            data: {
                configuracao: linha,
                close: () => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.service.recarregarListagem();
        });
    }

    atualizarCertificado() {
        const dialogRef = this.dialog.open(AtualizarCertificadoDialogComponent, {
            width: '65%',
            maxWidth: '48vw',
            maxHeight: '78vh',
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
}
