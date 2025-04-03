import { ListPaginated } from 'api/@base/list-paginated';
import { BehaviorSubject, firstValueFrom, map, tap } from 'rxjs';
import {
    MpmtColuna,
    MpmtLinha,
    MpmtOrdenacao,
    MpmtPaginacao,
} from '../mpmt-celula/mpmt-celula.interface';


export interface MpmtAccordionInterface {
    item: any;
    subItem?: any[];
}


export abstract class MpmtAccordionService<T extends any = any> {

    public ordenacaoSubItem: MpmtOrdenacao = {
        order_by: undefined,
    };

    public paginacao: MpmtPaginacao = {
        page: 1,
        per_page: 100,
    };


    private listagemSubject = new BehaviorSubject<MpmtAccordionInterface[]>([]);
    private loadingSubject = new BehaviorSubject<boolean>(false);
    private totalSubject = new BehaviorSubject<number>(0);

    private colunasItemSubject = new BehaviorSubject<MpmtColuna[]>([]);
    private colunasSubItemSubject = new BehaviorSubject<MpmtColuna[]>([]);


    public listagem$ = this.listagemSubject.asObservable();
    public loading$ = this.loadingSubject.asObservable();
    public total$ = this.totalSubject.asObservable();

    public colunasItem$ = this.colunasItemSubject.asObservable();
    public colunasSubItem$ = this.colunasSubItemSubject.asObservable();



    constructor() {
        this.aoInicializar();
    }

    /* Events */
    protected aoInicializar() {
        this.configurarColunasItem([]);
        this.configurarColunasSubItem([]);
        this.recarregarListagem();
    }

    /**
   * Retorna dados dos itens
   */
    protected async obterDadosItem(filtros: any): Promise<ListPaginated<any>> {
        return {
            page: 1,
            total: 0,
            per_page: 10,
            results: [],
        };
    }


    /**
   * Retorna dados dos sub itens
   */
    public async obterDadosSubItem(id_item: number): Promise<ListPaginated<T>> {
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
    protected async obterPaginacao(): Promise<MpmtPaginacao> {
        return { ...this.paginacao };
    }

    /**
     * Retorna os filtros
     */
    protected async obterFiltrosItem(): Promise<{ [key: string]: any }> {
        return {};
    }

    /**
     * Retorna os filtros
     */
    protected async obterFiltrosSubItem(): Promise<{ [key: string]: any }> {
        return {};
    }

    /**
     * Retorna os filtros
     */
    protected async obterOrdenacaoSubItem(): Promise<MpmtOrdenacao> {
        return { ...this.ordenacaoSubItem };
    }

    /**
     * Alterar a ordenação padrão
     */
    public alterarOrdenacaoSubItem($event: {
        active: string;
        direction: 'asc' | 'desc';
    }) {
        const { active, direction } = $event;
        this.ordenacaoSubItem.order_by = direction == 'asc' ? active : `-${active}`;
        this.recarregarListagem();
    }

    /**
     * Retorna somente as colunas visiveis
     */
    public get colunasVisiveisItem() {
        return this.colunasItem$.pipe(
            map((colunas: MpmtColuna[]) => {
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
                    .filter((coluna: MpmtColuna) => coluna.visivel);
            })
        );
    }


    /**
     * Retorna somente as colunas visiveis
     */
    public get colunasVisiveisSubItem() {
        return this.colunasSubItem$.pipe(
            map((colunas: MpmtColuna[]) => {
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
                    .filter((coluna: MpmtColuna) => coluna.visivel);
            })
        );
    }


    public get colunaCodigosItem() {
        return this.colunasVisiveisItem.pipe(
            map((colunas: MpmtColuna[]) => {
                return colunas.map((x) => x.codigo);
            })
        );
    }

    public get colunaCodigosSubItem() {
        return this.colunasVisiveisSubItem.pipe(
            map((colunas: MpmtColuna[]) => {
                return colunas.map((x) => x.codigo);
            })
        );
    }



    public async configurarColunasItem(colunas: MpmtColuna[]) {
        this.colunasItemSubject.next(colunas);
    }

    public async configurarColunasSubItem(colunas: MpmtColuna[]) {
        this.colunasSubItemSubject.next(colunas);
    }



    public async recarregarListagem() {
        const paginacao = await this.obterPaginacao();
        const filtros = await this.obterFiltrosItem();
        const response_item = await this.obterDadosItem({
            ...paginacao,
            ...filtros,
        });

        const resultado: MpmtAccordionInterface[] = await Promise.all(
            response_item.results.map(async (item) => {
                const response_subItem = await this.obterDadosSubItem(
                    item.id,
                );

                return {
                    item,
                    subItem: response_subItem.results
                };
            })
        );

        this.listagemSubject.next(resultado);
        this.totalSubject.next(response_item.total);

    }



    atualizarColunasVisiveisItem(colunas: MpmtColuna[]) {
        this.colunasItemSubject.next(colunas);
    }

    atualizarColunasVisiveisSubItem(colunas: MpmtColuna[]) {
        this.colunasSubItemSubject.next(colunas);
    }


    public getTotalItems() {
        return this.totalSubject.getValue();
    }


    public pegarValorItem(item: any, coluna: MpmtColuna) {

        const valor = item[coluna.codigo];

        if (!coluna.transformarValor) return valor;
        return coluna.transformarValor(valor);
    }

}
