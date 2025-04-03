import { ListPaginated } from 'api/@base/list-paginated';
import { BehaviorSubject, debounceTime, firstValueFrom, map, Subject, takeUntil, tap } from 'rxjs';
import {
    MpmtPaginaListagemAcao,
    MpmtPaginaListagemColuna,
    MpmtPaginaListagemLinha,
    MpmtPaginaListagemOrdenacao,
    MpmtPaginaListagemPaginacao,
} from './mpmt-pagina-listagem.interface';
import {  OnDestroy } from '@angular/core';
import { Injectable,  OnInit } from '@angular/core';

@Injectable()
export abstract class MpmtPaginaListagemService<T extends any = any> implements OnDestroy 
 {
    public ordenacao: MpmtPaginaListagemOrdenacao = {
        order_by: undefined,
    };

    public paginacao: MpmtPaginaListagemPaginacao = {
        page: 1,
        per_page: 10,
        total: 0    
    };

    private colunasSubject = new BehaviorSubject<MpmtPaginaListagemColuna[]>(
        []
    );
    private acoesSubject = new BehaviorSubject<MpmtPaginaListagemAcao[]>(
        []
    );
    public listagemSubject = new BehaviorSubject<MpmtPaginaListagemLinha[]>(
        []
    );
    private carregamentoSubject = new BehaviorSubject<boolean>(false);
    private totalSubject = new BehaviorSubject<number>(0);
    private perPageSubject = new BehaviorSubject<number>(10);
    private recarregarSubject = new BehaviorSubject<number>(0);

    public destroy$ = new Subject<number>();
    public colunas$ = this.colunasSubject.asObservable();
    public acoes$ = this.acoesSubject.asObservable();
    public listagem$ = this.listagemSubject.asObservable();
    public loading$ = this.carregamentoSubject.asObservable();
    public total$ = this.totalSubject.asObservable();
    public perPage$ = this.perPageSubject.asObservable();
    
    constructor() {
        this.aoInicializar();

        this.recarregarSubject                                          
            .pipe(
                takeUntil(this.destroy$),
                debounceTime(300)
            )
            .subscribe(() => this.recarregar());

    }

    /**
     * Ciclo de vida
     */
    protected aoInicializar() {
        this.configurarColunas();
        this.configurarAcoes();
        this.recarregar();
    }

    ngOnDestroy() {
        this.destroy$.next(0);
        this.destroy$.complete();
    }
    
    /**
     * Retorna dados da listagem
     */
    protected async obterDados(filtros: any): Promise<ListPaginated<T>> {
        return {
            page: 1,
            total: 0,
            per_page: 10,
            results: [],
        };
    }

    /**
     * Retorna paginacao
     */
    protected async obterPaginacao(): Promise<MpmtPaginaListagemPaginacao> {
        return { 
            page: this.paginacao.page,
            per_page: this.paginacao.per_page
         };
    }

    /**
     * Retorna os filtros
     */
    protected async obterFiltros(): Promise<{ [key: string]: any }> {
        return {};
    }

    /**
     * Retorna os filtros
     */
    protected async obterOrdenacao(): Promise<MpmtPaginaListagemOrdenacao> {
        return { ...this.ordenacao };
    }

    /**
     * Obter colunas
     */
    protected async obterColunas(): Promise<MpmtPaginaListagemColuna[]> {
        return [];
    }

    /**
     * Obter Acoes
     */
        protected async obterAcoes(): Promise<MpmtPaginaListagemAcao[]> {
            return [];
        }

    /**
     * Alterar a ordenação padrão
     */
    public alterarOrdenacao($event: {
        active: string;
        direction: 'asc' | 'desc';
    }) {
        const { active, direction } = $event;
        this.ordenacao.order_by = direction == 'asc' ? active : `-${active}`;
        this.recarregar();
    }

    /**
     * Retorna somente as colunas visiveis
     */
    public get colunasVisiveis() {
        return this.colunas$.pipe(
            map((colunas: MpmtPaginaListagemColuna[]) => {
                return colunas
                    .map((x) => {
                        return {
                            ...x,
                            visivel: x.visivel == undefined ? true : x.visivel,
                            ordenavel:
                                x.ordenavel == undefined ? false : x.ordenavel,
                            tipo: x.tipo || 'TEXTO',
                        };
                    })
                    .filter(
                        (coluna: MpmtPaginaListagemColuna) => coluna.visivel
                    );
            })
        );
    }

    public get colunaCodigos() {
        return this.colunasVisiveis.pipe(
            map((colunas: MpmtPaginaListagemColuna[]) => {
                return colunas.map((x) => x.codigo);
            })
        );
    }

    public trocarPagina(pagina: number){
        this.paginacao.page = pagina
        this.recarregarUmaVez();
    }

    public async resetar() {
        this.paginacao.page = 1;
        this.listagemSubject.next([]);
        this.totalSubject.next(0);
        this.perPageSubject.next(10);
    }

    public async recarregar() {
        this.iniciarCarregamento();
        const paginacao = await this.obterPaginacao();
        const filtros = await this.obterFiltros();
        const ordenacao = await this.obterOrdenacao();
        const response = await this.obterDados({
            ...ordenacao,
            ...paginacao,
            ...filtros,
        });
        this.listagemSubject.next(response.results);
        this.totalSubject.next(response.total);
        this.perPageSubject.next(response.per_page);
        this.finalizarCarregamento();
    }

    public recarregarUmaVez(): void {
        this.recarregarSubject.next(0);
    }

    public getTotalItems() {
        return this.totalSubject.getValue();
    }

    protected get downloadCsvSincrono() {
        return true;
    }

    protected iniciarCarregamento() {
        this.carregamentoSubject.next(true);
    }

    protected finalizarCarregamento() {
        this.carregamentoSubject.next(false);
    }

    /** Private */
    private async configurarColunas() {
        let colunas = await this.obterColunas();
        colunas.forEach((x) => {
            x.visivel = x.visivel == undefined ? true : x.visivel;
        });
        this.colunasSubject.next(colunas);
    }


    private async configurarAcoes(){
        let acoes = await this.obterAcoes();
        this.acoesSubject.next(acoes);
    }

    /** Public */

    /** 
     * Download em CSV
     */
    public async downloadCsv() {
        const sincrono = this.downloadCsvSincrono;

        const colunas = (await firstValueFrom(this.colunasVisiveis))
            .filter((x) => x.visivel)
            .filter((x) => x.tipo != 'ACOES')
            .map((x) => x.codigo); 

        const csvContent = <string>(<unknown>await this.obterDados({
            ...(await this.obterFiltros()),
            exportar: 'csv',
            colunas,
            page: 1,
            per_page: 10000,
            sincrono,
        }));

        if (sincrono) {
            const csvContent2 = `data:text/csv;charset=utf-8,${csvContent}`;
            var encodedUri = encodeURI(csvContent2);
            window.open(encodedUri);
        } else {
            alert((csvContent as any)?.message);
        }
    }

    public trocarColunaVisibilidade(coluna: MpmtPaginaListagemColuna) {
        coluna.visivel = !coluna.visivel;
    }

    /**
     * method a ser chamado quando o usuario reordenar as linhas
     */
    public aoReordenarLinha: (($event: any) => void) | null | undefined = null
    
}
