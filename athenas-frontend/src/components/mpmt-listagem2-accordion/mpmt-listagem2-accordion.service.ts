import { ListPaginated } from 'api/@base/list-paginated';
import { BehaviorSubject, firstValueFrom, map, tap } from 'rxjs';
import {
    MpmtListagem2Coluna,
    MpmtListagem2Linha,
    MpmtListagem2Ordenacao,
    MpmtListagem2Paginacao,
} from './mpmt-listagem2-accordion.interface';

export abstract class MpmtListagem2AccordionService<T extends any = any> {
    public ordenacao: MpmtListagem2Ordenacao = {
        order_by: undefined,
    };

    public paginacao: MpmtListagem2Paginacao = {
        page: 1,
        per_page: 10,
    };

    private colunasSubject = new BehaviorSubject<MpmtListagem2Coluna[]>([]);
    private colunasAccordionSubject = new BehaviorSubject<MpmtListagem2Coluna[]>([]);
    private listagemSubject = new BehaviorSubject<MpmtListagem2Linha[]>([]);
    private loadingSubject = new BehaviorSubject<boolean>(false);
    private totalSubject = new BehaviorSubject<number>(0);
    private perPageSubject = new BehaviorSubject<number>(10);

    public colunas$ = this.colunasSubject.asObservable();
    public colunasAccordion$ = this.colunasAccordionSubject.asObservable();
    public listagem$ = this.listagemSubject.asObservable();
    public loading$ = this.loadingSubject.asObservable();
    public total$ = this.totalSubject.asObservable();
    public perPage$ = this.perPageSubject.asObservable();

    constructor() {
        this.aoInicializar();
    }

    /* Events */
    protected aoInicializar() {
        this.configurarColunas([]);
        this.recarregarListagem();
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
    protected async obterPaginacao(): Promise<MpmtListagem2Paginacao> {
        return { ...this.paginacao };
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
    protected async obterOrdenacao(): Promise<MpmtListagem2Ordenacao> {
        return { ...this.ordenacao };
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
        this.recarregarListagem();
    }

    /**
     * Retorna somente as colunas visiveis
     */
    public get colunasVisiveis() {
        return this.colunas$.pipe(
            map((colunas: MpmtListagem2Coluna[]) => {
                return colunas
                    .map((x) => {
                        return {
                            acoes: x.acoes || [],
                            codigo: x.codigo,
                            titulo: x.titulo,
                            ordenavel:
                                x.ordenavel == undefined ? true : x.ordenavel,
                            tipo: x.tipo || 'TEXTO',
                            transformarValor: x.transformarValor || undefined,
                            visivel: x.visivel == undefined ? true : x.visivel,
                        };
                    })
                    .filter((coluna: MpmtListagem2Coluna) => coluna.visivel);
            })
        );
    }

    public get colunaCodigos() {
        return this.colunasVisiveis.pipe(
            map((colunas: MpmtListagem2Coluna[]) => {
                return colunas.map((x) => x.codigo);
            })
        );
    }

    public async configurarColunas(colunas: MpmtListagem2Coluna[]) {
        this.colunasSubject.next(colunas);
    }

    public async configurarColunasAccordion(colunas: MpmtListagem2Coluna[]) {
        this.colunasAccordionSubject.next(colunas);
    }

    public async recarregarListagem() {
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
    }

    atualizarColunasVisiveis(colunas: MpmtListagem2Coluna[]) {
        this.colunasSubject.next(colunas);
    }

    public getTotalItems() {
        return this.totalSubject.getValue();
    }

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

    protected get downloadCsvSincrono() {
        return true;
    }
}
