import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { apiRhListaAntiguidades } from 'api/rh/api-rh-lista-antiguidades.service';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { apiRhListaAntiguidadesAtualizar } from 'api/rh/api-rh-lista-antiguidades-atualizar.service';
import moment from 'moment';
import { MovimentacaoCarreiraListaAntiguidadesService } from './movimentacao-carreira-lista-antiguidades.service';

@Component({
    selector: 'movimentacao-carreira-lista-antiguidades',
    templateUrl: 'movimentacao-carreira-lista-antiguidades.component.html',
    standalone: false
})
export class MovimentacaoCarreiraListaAntiguidadesComponent implements OnInit {
    // filtros = new FormGroup({
    //     order_by: new FormControl<string>(null, []),
    //     palavra_chave: new FormControl<string>('', []),
    //     tipo_membro: new FormControl<number>(0, []),
    // });

    constructor(
        public service: MovimentacaoCarreiraListaAntiguidadesService,
        public dialog: MatDialog
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }
    // protected obterTitulo() {
    //     return 'Lista de Antiguidades';
    // }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'ordem_antiguidade',
                titulo: 'Ordem Antiguidade',
                visivel: true,
            },
            {
                codigo: 'matricula',
                titulo: 'Matricula',
                visivel: true,
            },
            {
                codigo: 'nome',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'get_tipo_cargo_display',
                titulo: 'Tipo Membro',
                visivel: true,
            },

            {
                codigo: 'data_inicio_instancia',
                titulo: 'Data Inicio Instancia',
                visivel: true,
            },
            {
                codigo: 'data_inicio_carreira',
                titulo: 'Data Inicio Carreira',
                visivel: true,
            },

            {
                codigo: 'tempo_afastamento_formatado',
                titulo: 'Tempo Afastamento',
                visivel: true,
            },

            {
                codigo: 'total_instancia_formatado',
                titulo: 'Tempo total de Instancia',
                visivel: true,
            },

            {
                codigo: 'efetivo_exercicio_formatado',
                titulo: 'Tempo Efetivo',
                visivel: true,
            },

            {
                codigo: 'total_carreira_formatado',
                titulo: 'Tempo total de Carreira',
                visivel: true,
            },

            {
                codigo: 'get_origem_display',
                titulo: 'Origem',
                visivel: true,
            },

            {
                codigo: 'posicao_concurso',
                titulo: 'Posição Concurso',
                visivel: true,
            },
            {
                codigo: 'modified_at',
                titulo: 'Processado em',
                visivel: true,
            },

            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                // acoes: [
                //     {
                //         icone: 'edit',
                //         titulo: 'Editar',
                //         aoClicar: (linha: any) => this.irEditarGrupo(linha),
                //     },
                // ],
            },
        ]);
    }

    // protected async obterColunas() {
    //     return {
    //         ordem_antiguidade: 'Ordem Antiguidade',
    //         matricula: 'Matricula',
    //         nome: 'Nome',
    //         get_tipo_cargo_display: 'Tipo Membro',
    //         data_inicio_instancia: 'Data Inicio Instancia',
    //         data_inicio_carreira: 'Data Inicio Carreira',
    //         tempo_afastamento_formatado: 'Tempo Afastamento',
    //         total_instancia_formatado: 'Tempo total de Instancia',
    //         efetivo_exercicio_formatado: 'Tempo Efetivo',
    //         total_carreira_formatado: 'Tempo total de Carreira',
    //         get_origem_display: 'Origem',
    //         posicao_concurso: 'Posição Concurso',
    //         modified_at: "Processado em"
    //     };
    // }

    // protected async obterDados(filtros: any) {
    //     return await apiRhListaAntiguidades(filtros);
    // }

    // protected async obterFiltros() {
    //     return {
    //         ...this.filtros.value,
    //         page: (this.paginator?.pageIndex || 0) + 1,
    //         per_page: this.paginator?.pageSize || 10,
    //     };
    // }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    protected atualizarAntiguidades() {        
        try {
            apiRhListaAntiguidadesAtualizar({});
            // this.aplicarFiltros();
            this.service.recarregarListagem();
        } catch (e: any) {
            console.log(e);
        }
    }

    tipos_membros = [
        { valor: 0, nome: 'Todos' },
        { valor: 1, nome: 'Procuradores' },
        { valor: 2, nome: 'Promotores' },
        { valor: 3, nome: 'Promotores Substitutos' },
    ];

    getData(data: string) {
        return moment(data).format('DD/MM/YY');
    }
    getDataHora(data: string) {
        return moment(data).format('DD/MM/YY HH:mm:ss');
    }
}