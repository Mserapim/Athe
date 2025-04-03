import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ApprovalShowComponent } from '../approval/approval-show/approval-show.component';
import { ActivatedRoute } from '@angular/router';
import { VdfFolhaPontoService } from './vdf-folha-ponto.service';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { apiFolhaPontoServidores } from 'api/folha-ponto/api-folha-ponto-servidores.service';
import { apiFolhaPontoLotacoes } from 'api/folha-ponto/api-folha-ponto-lotacoes.service';
import {
    apiFolhaPontoTiposDias,
    ApiFolhaPontoTiposDiasItem,
} from 'api/folha-ponto/api-folha-ponto-tipos-dias.service';
import { ApiFolhaPontoMarcacoesItem } from 'api/folha-ponto/api-folha-ponto-marcacoes.service';
import { ViewEncapsulation } from '@angular/core';

// Depending on whether rollup is used, moment needs to be imported differently.
// Since Moment.js doesn't have a default export, we normally need to import using the `* as`
// syntax. However, rollup creates a synthetic default module and we thus need to import it using
// the `default as` syntax.
import _moment from 'moment';
// tslint:disable-next-line:no-duplicate-imports
import { default as _rollupMoment } from 'moment';
import { VdfFolhaPontoJustificativasComponent } from './vdf-folha-ponto-justificativas/vdf-folha-ponto-justificativas.component';
import { VdfFolhaPontoMarcacaoEditarComponent } from './vdf-folha-ponto-marcacao-editar/vdf-folha-ponto-marcacao-editar.component';
import { apiReportRhPvfPointSheet } from 'api/report/api-report-rh-pvf-point-sheet.service';
import { useDownload } from 'api/@base/use-download';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { formatDate } from 'utils/format-date';
import { apiReportRhPvfFolhaPonto } from 'api/report/api-report-rh-pvf-folha-ponto.service';
import { apiFolhaPontoJustificativasPermissao } from 'api/folha-ponto/api-folha-ponto-justificativas-permissao';

const moment = _rollupMoment || _moment;

// See the Moment.js docs for the meaning of these formats:
// https://momentjs.com/docs/#/displaying/format/
export const MY_FORMATS = {
    parse: {
        dateInput: 'MM/YYYY',
    },
    display: {
        dateInput: 'MM/YYYY',
        monthYearLabel: 'MMM YYYY',
        dateA11yLabel: 'LL',
        monthYearA11yLabel: 'MMMM YYYY',
    },
};

@Component({
    selector: 'vdf-folha-ponto',
    templateUrl: 'vdf-folha-ponto.component.html',
    styleUrls: ['vdf-folha-ponto.component.scss'],
    encapsulation: ViewEncapsulation.None,
    standalone: false,
})
export class VdfFolhaPontoComponent implements OnInit {
    tipoDias: ApiFolhaPontoTiposDiasItem[];
    total: number = 0;
    podeAdicionarJustificativa: boolean = false;

    constructor(
        public service: VdfFolhaPontoService,
        public dialog: MatDialog,
        private mpPdfPreviewComponent: MpPdfPreviewComponent,
        private route: ActivatedRoute
    ) {
        const filtros = this.route.snapshot.data?.filtros;

        if (filtros) {
            this.service.filtros.patchValue({
                ...filtros,
            });
        } 

        const normalizedMonthAndYear = moment();
        this.service.filtros.patchValue({
            competencia: normalizedMonthAndYear,
            mes: normalizedMonthAndYear.month(),
            ano: normalizedMonthAndYear.year(),
        });
    }

    ngOnInit() {
        this.loadFolhaPontoJustificativasPermissao();
        this.loadTipoDias();
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    temMarcacao(linha: ApiFolhaPontoMarcacoesItem) {
        return !(
            !linha.marcacoes ||
            !linha.marcacoes?.length ||
            linha.marcacoes?.length <= 0
        );
    }

    pegarMarcacao(linha: ApiFolhaPontoMarcacoesItem, index: number) {
        if (
            !linha.marcacoes ||
            !linha.marcacoes?.length ||
            linha.marcacoes?.length <= 0
        )
            return '';
        const marcacoesValidas =
            linha.marcacoes?.filter((marcacao) => marcacao.marcacao_valida) ||
            [];
        if (marcacoesValidas.length < index) return '';
        return marcacoesValidas[index - 1].marcacao_hora;
    }

    marcacaoImpar(linha: ApiFolhaPontoMarcacoesItem) {
        if (
            !linha.marcacoes ||
            !linha.marcacoes?.length ||
            linha.marcacoes?.length <= 0
        )
            return false;
        const marcacoesValidas = linha.marcacoes.filter(
            (marcacao) => marcacao.marcacao_valida
        );
        return marcacoesValidas.length % 2 == 1;
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                titulo: 'Data',
                codigo: 'data',
                visivel: true,
            },
            {
                titulo: 'Dia',
                codigo: 'dia',
                visivel: true,
            },
            {
                titulo: 'Tipo dia',
                codigo: 'tipo_texto',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) => {
                    return (linha.tipo_texto && typeof linha.tipo_texto === 'string')
                        ? linha.tipo_texto.toUpperCase()
                        : '';
                },
                construirEstilo: (linha: ApiFolhaPontoMarcacoesItem) => {
                    if (linha.tipo_texto && linha.tipo_texto.toUpperCase() === 'FALTA') {
                        return 'text-red-500';
                    }
                    return '';
                },
                visivel: true,
            },
            {
                titulo: 'Marcação 1',
                codigo: 'marcacao1',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) =>
                    this.pegarMarcacao(linha, 1),
                visivel: true,
                ordenavel: false,
            },
            {
                titulo: 'Marcação 2',
                codigo: 'marcacao2',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) =>
                    this.pegarMarcacao(linha, 2),
                visivel: true,
                ordenavel: false,
            },
            {
                titulo: 'Marcação 3',
                codigo: 'marcacao3',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) =>
                    this.pegarMarcacao(linha, 3),
                visivel: true,
                ordenavel: false,
            },
            {
                titulo: 'Marcação 4',
                codigo: 'marcacao4',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) =>
                    this.pegarMarcacao(linha, 4),
                visivel: true,
                ordenavel: false,
            },

            {
                titulo: 'Marcação 5',
                codigo: 'marcacao5',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) =>
                    this.pegarMarcacao(linha, 5),
                visivel: false,
                ordenavel: false,
            },

            {
                titulo: 'Marcação 6',
                codigo: 'marcacao6',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) =>
                    this.pegarMarcacao(linha, 6),
                visivel: false,
                ordenavel: false,
            },

            {
                titulo: 'Total dia',
                codigo: 'total_dia',
                visivel: true,
            },

            {
                titulo: 'Saldo dia',
                codigo: 'saldo_dia',
                visivel: true,
            },

            {
                titulo: '',
                codigo: 'alert',
                tipo: 'ICONE',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) =>
                    'warning',
                construirEstilo: (linha: ApiFolhaPontoMarcacoesItem) =>
                    'cursor-pointer text-yellow-500',
                exibirSe: (linha: ApiFolhaPontoMarcacoesItem) =>
                    linha.afastamento_pendente != null ||
                    this.marcacaoImpar(linha),
                width: '10px',
                visivel: true,
            },
            {
                titulo: '',
                codigo: 'responsavel',
                tipo: 'ICONE',
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) => {
                    const marcacaoEditada = linha.marcacoes?.find(
                        (m) => m.editado_por === 'servidor' || m.editado_por === 'chefia' || m.editado_por === 'DGP'
                    );
    
                    if (marcacaoEditada?.editado_por === 'servidor') {
                        return 'person';
                    } else if (marcacaoEditada?.editado_por === 'chefia') {
                        return 'manage_accounts'; 
                    } else if (marcacaoEditada?.editado_por === 'DGP') {
                        return 'manage_accounts'; 
                    }
                    return null;
                },
                construirEstilo: (linha: ApiFolhaPontoMarcacoesItem) => {
                    const marcacaoEditada = linha.marcacoes?.find(
                        (m) => m.editado_por === 'servidor' || m.editado_por === 'chefia'
                    );
            
                    if (marcacaoEditada?.editado_por === 'servidor') {
                        return 'text-blue-500';
                    } else if (marcacaoEditada?.editado_por === 'chefia') {
                        return 'text-green-500';
                    }
                    return '';
                },
                tooltip: (linha: ApiFolhaPontoMarcacoesItem) => {
                    const marcacaoEditada = linha.marcacoes?.find(
                        (m) => m.editado_por === 'servidor' || m.editado_por === 'chefia' || m.editado_por === 'DGP'
                    );
                    if (marcacaoEditada?.editado_por === 'servidor') {
                        return 'Alteração em marcação feita pelo servidor';
                    } else if (marcacaoEditada?.editado_por === 'chefia') {
                        return 'Alteração em marcação feita pela chefia';
                    } else if (marcacaoEditada?.editado_por === 'DGP') {
                        return 'Alteração em marcação feita pelo DGP';
                    }
                    return '';
                },
                exibirSe: (linha: ApiFolhaPontoMarcacoesItem) =>
                    linha.marcacoes?.some(
                        (m) => m.editado_por === 'servidor' || m.editado_por === 'chefia' || m.editado_por === 'DGP'
                    ),
                width: '10px',
                visivel: true,
            },
            {
                codigo: 'editar',
                titulo: '',
                visivel: true,
                tipo: 'ICONE',
                width: '10px',
                exibirSe: (linha: ApiFolhaPontoMarcacoesItem) =>
                    this.temMarcacao(linha),
                transformarValor: (linha: ApiFolhaPontoMarcacoesItem) => 'edit',
                aoClicar: (linha: any) => this.editarBatida(linha),
                construirEstilo: (linha: ApiFolhaPontoMarcacoesItem) =>
                    'cursor-pointer',
            },
        ]);
    }

    protected irJustificativas() {
        this.dialog.open(VdfFolhaPontoJustificativasComponent, {
            data: {
                filtros: {
                    ...this.service.filtros.value,
                    mes: this.service.filtros.value.mes !== null &&
                        this.service.filtros.value.mes !== undefined
                        ? this.service.filtros.value.mes + 1
                        : undefined,
                    inicio: this.service.periodo.value.inicio,
                    fim: this.service.periodo.value.fim,
                },
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    public editarBatida(element: any) {
        const { pk: requestId, portal_request_type, status } = element;

        const dialogRef = this.dialog.open(
            VdfFolhaPontoMarcacaoEditarComponent,
            {
                // width: '98%',
                // maxWidth: '98vw',
                // maxHeight: '98vh',
                data: {
                    marcacao: element,
                    close: () => {
                        dialogRef.close;
                    },
                },
            }
        );

        dialogRef.afterClosed().subscribe((result) => {
            this.service.recarregarListagem();
        });
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];

    public async loadTipoDias() {
        const { results } = await apiFolhaPontoTiposDias({});
        this.tipoDias = results;
    }

    public async loadFolhaPontoJustificativasPermissao() {
        const { pode_adicionar_justificativa } =
            await apiFolhaPontoJustificativasPermissao({});
        this.podeAdicionarJustificativa = pode_adicionar_justificativa;
    }

    selecaoServidores: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiFolhaPontoServidores,
        obterValor: 'id',
        obterTitulo: async (payload) => {
            return payload.ativo
                ? `<span class="text-black">${payload.servidor} </span>`
                : `<span class="line-through text-red-400">${payload.servidor} <b>(INATIVO)</b></span>`;
        },
        obterFiltros: (payload) => {
            return {
                ...payload,
                lotacao_id:
                    this.service?.filtros?.value?.lotacao_id || undefined,
                per_page: 10,
            };
        },
    };

    selecaoLotacoes: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiFolhaPontoLotacoes,
        obterValor: 'id',
        obterTitulo: 'lotacao_display',
        obterFiltros: (payload) => {
            return {
                ...payload,
                per_page: 10,
            };
        },
    };

    selecaoTiposDias: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiFolhaPontoTiposDias,
        obterValor: 'cod',
        obterTitulo: 'descricao',
        obterFiltros: (payload) => {
            return {
                ...payload,
                per_page: 10,
            };
        },
    };

    public isLoading = false;

    async download() {
        this.isLoading = true;
        try {
            const inicioDate = this.service.periodo.value?.inicio || undefined;
            const fimDate = this.service.periodo.value?.fim || undefined;

            const tipoFiltro = this.service.filtros?.value.tipo_filtro;

            const inicio =
                tipoFiltro == 'PERIODO' ? formatDate(inicioDate) : undefined;
            const fim =
                tipoFiltro == 'PERIODO' ? formatDate(fimDate) : undefined;

            const competencia =
                tipoFiltro == 'COMPETENCIA'
                    ? this.service.filtros.value.competencia
                    : undefined;
            const mes = competencia?.month() + 1 || undefined;
            const ano = competencia?.year() || undefined;

            const servidor_id = this.service.filtros.value.servidor_id;
            const tipos_dia = this.service.filtros.value.tipos_dia;

            const { uuid } = await apiReportRhPvfFolhaPonto({
                year: ano,
                month: mes,
                employee_id: servidor_id,
                tipos_dia,
                inicio,
                fim,
            });

            const link = await useDownload(uuid, 0, 30, {
                automaticDownload: false,
            });
            this.mpPdfPreviewComponent.open(link);
        } finally {
            this.isLoading = false;
        }
    }
}
