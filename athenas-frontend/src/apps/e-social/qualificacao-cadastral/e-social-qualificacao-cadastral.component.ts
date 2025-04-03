import {Component, OnInit} from "@angular/core";
import {ESocialQualificacaoCadastralService} from "./e-social-qualificacao-cadastral.service";
import moment from "moment/moment";
import {MatSnackBar} from "@angular/material/snack-bar";
import {FuseConfirmationService} from "../../../@fuse/services/confirmation";
import {MatDialog} from "@angular/material/dialog";
import {MpmtListagem2Linha} from "../../../components/mpmt-listagem2/mpmt-listagem2.interface";
import {
    apiESocialListarCategoriasTiposPessoas
} from "../../../api/esocial/config/api-esocial-listar-categorias-tipos-pessoas.service";
import {apiESocialListarStatus} from "../../../api/esocial/config/api-esocial-listar-status.service";
import {apiESocialListarOrientacaoCPF} from "../../../api/esocial/config/api-esocial-listar-orientacao-cpf.service";
import {apiESocialListarOrientacaoNIS} from "../../../api/esocial/config/api-esocial-listar-orientacao-nis.service";
import {
    QualificacaoCadastralGerarArquivoDialogComponent
} from "./components/qualificacao-cadastral-gerar-arquivo-dialog/qualificacao-cadastral-gerar-arquivo-dialog.component";
import {
    apiESocialQualificacaoCadastralAtualizarLista
} from "../../../api/esocial/qualificacao-cadastral/api-esocial-qualificacao-cadastral-atualizar-lista.service";
import {CoresPadraoEnum} from "../../../enums/CoresPadraoEnum";
import {
    QualificacaoCadastralConfirmarQualificacaoDialogComponent
} from "./components/qualificacao-cadastral-confirmar-qualificacao-dialog/qualificacao-cadastral-confirmar-qualificacao-dialog.component";
import {NavegacaoAtualService} from "../../../core/navegacao-atual/navegacao-atual.service";

@Component({
    selector: 'e-social-itens-tabela',
    templateUrl: 'e-social-qualificacao-cadastral.component.html',
    standalone: false
})
export class ESocialQualificacaoCadastralComponent implements OnInit {

    categoriasTiposPessoas: any[] = []
    status: any[] = []
    orientacoesNis: any[] = []
    orientacaoCpf: any[] = []


    constructor(public service: ESocialQualificacaoCadastralService,
                protected snackBar: MatSnackBar,
                private _fuseConfirmationService: FuseConfirmationService,
                public navegacaoAtualService: NavegacaoAtualService,
                private dialog: MatDialog) {

    }
    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();

        apiESocialListarCategoriasTiposPessoas().then(response => {
            this.categoriasTiposPessoas = response.results
            this.service.filtros.controls["categoria[]"].setValue(response.results.map(result => result.valor))
        })

        apiESocialListarStatus().then(response => {
            this.status = response.results
            this.service.filtros.controls["status[]"].setValue(response.results.map(result => result.valor))
        })

        apiESocialListarOrientacaoCPF().then(response => {
            this.orientacaoCpf = response.results
            this.service.filtros.controls["orientacao_cpf[]"].setValue(response.results.map(result => result.valor))
        })

        apiESocialListarOrientacaoNIS().then(response => {
            this.orientacoesNis = response.results
            this.service.filtros.controls["orientacao_nis[]"].setValue(response.results.map(result => result.valor))
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
                codigo: 'tipo_pessoa_display',
                titulo: '',
                tipo: 'ICONE',
                transformarValor: (linha: any) => this.buscarIcone(linha),
                tooltip: (linha: any) => this.buscarTooltip(linha),
                visivel: true,
            },
            {
                codigo: 'status_display',
                titulo: 'Status',
                visivel: true,
            },
            {
                codigo: 'nome',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'cpf',
                titulo: 'CPF',
                visivel: true,
            },
            {
                codigo: 'nis',
                titulo: 'NIS',
                visivel: true,
            },
            {
                codigo: 'data_nascimento',
                titulo: 'Data nascimento',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'servidor',
                titulo: 'Servidor',
                visivel: false,
            },
            {
                codigo: 'cod_cpf_inv',
                titulo: 'cod_cpf_inv',
                visivel: false,
            },
            {
                codigo: 'cod_nis_inv',
                titulo: 'cod_nis_inv',
                visivel: false,
            },
            {
                codigo: 'cod_nome_inv',
                titulo: 'cod_nome_inv',
                visivel: false,
            },
            {
                codigo: 'cod_dn_inv',
                titulo: 'cod_dn_inv',
                visivel: false,
            },
            {
                codigo: 'cod_cnis_nis',
                titulo: 'cod_cnis_nis',
                visivel: false,
            },
            {
                codigo: 'cod_cnis_dn',
                titulo: 'cod_cnis_dn',
                visivel: false,
            },
            {
                codigo: 'cod_cnis_obito',
                titulo: 'cod_cnis_obito',
                visivel: false,
            },
            {
                codigo: 'cod_cnis_cpf',
                titulo: 'cod_cnis_cpf',
                visivel: false,
            },
            {
                codigo: 'cod_cnis_cpf_nao_inf',
                titulo: 'cod_cnis_cpf_nao_inf',
                visivel: false,
            },
            {
                codigo: 'cod_cpf_nao_consta',
                titulo: 'cod_cpf_nao_consta',
                visivel: false,
            },
            {
                codigo: 'cod_cpf_nulo',
                titulo: 'cod_cpf_nulo',
                visivel: false,
            },
            {
                codigo: 'cod_cpf_cancelado',
                titulo: 'cod_cpf_cancelado',
                visivel: false,
            },
            {
                codigo: 'cod_cpf_suspenso',
                titulo: 'cod_cpf_suspenso',
                visivel: false,
            },
            {
                codigo: 'cod_cpf_dn',
                titulo: 'cod_cpf_dn',
                visivel: false,
            },
            {
                codigo: 'cod_cpf_nome',
                titulo: 'cod_cpf_nome',
                visivel: false,
            },
            {
                codigo: 'cod_orientacao_cpf',
                titulo: 'cod_orientacao_cpf',
                visivel: false,
            },
            {
                codigo: 'cod_orientacao_nis',
                titulo: 'cod_orientacao_nis',
                visivel: false,
            },
            {
                codigo: 'ultima_qualificacao',
                titulo: 'Qualificado em',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'ultima_qualificacao_por',
                titulo: 'Qualificado por',
                visivel: true,
            },
            {
                codigo: 'ultima_mofificacao',
                titulo: 'ultima_mofificacao',
                tipo: 'DATA',
                visivel: false,
            },
            {
                codigo: 'ultima_mofificacao_por',
                titulo: 'ultima_mofificacao_por',
                visivel: false,
            },
            {
                codigo: 'qualificado',
                titulo: 'qualificado',
                visivel: false,
            },
            {
                codigo: 'tipo_ultima_qualificacao',
                titulo: 'tipo_ultima_qualificacao',
                visivel: false,
            },
            {
                codigo: 'tipo_ultima_qualificacao_display',
                titulo: 'tipo_ultima_qualificacao_display',
                visivel: false,
            },
            {
                codigo: 'info',
                titulo: 'info',
                visivel: false,
            }
        ]);
    }

    getData(data: string) {
        return moment(data).format('DD/MM/YY');
    }
    getDataHora(data: string) {
        return moment(data).format('DD/MM/YY HH:mm:ss');
    }

    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    buscarIcone(linha: MpmtListagem2Linha) {
        let tipoPessoa = linha['tipo_pessoa']
        switch (tipoPessoa) {
            case 1 :
                return 'person'
            case 2 :
                return 'person_off'
            case 3 :
                return 'family_restroom'
            case 4 :
                return 'cookie'
            case 5 :
                return 'school'
            case 6 :
                return 'gavel'
            case 7 :
                return 'no_accounts'
        }
    }

    private buscarTooltip(linha: any) {
        return linha['tipo_pessoa_display'];
    }

    gerarArquivo() {
        const dialogRef = this.dialog.open(QualificacaoCadastralGerarArquivoDialogComponent, {
            width: '30%',
            height: '28%',
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


    atualizarLista() {
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Deseja confirmar a atualização da lista de pessoas qualificáveis?',
            icon: {
                show: true,
                name: 'heroicons_outline:exclamation',
                color: 'warn'
            },
            actions: {
                confirm: {
                    show: true,
                    label: 'Salvar',
                    style: { 'background-color': CoresPadraoEnum.verde },
                },
                cancel: {
                    show: true,
                    label: 'Fechar',
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
                    await apiESocialQualificacaoCadastralAtualizarLista();

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

    confirmarQualificacao() {
        const dialogRef = this.dialog.open(QualificacaoCadastralConfirmarQualificacaoDialogComponent, {
            width: '35%',
            height: '50%',
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
}
