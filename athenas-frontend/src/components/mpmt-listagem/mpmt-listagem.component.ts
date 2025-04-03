import {
    Component,
    Input,
    OnChanges,
    OnInit,
    SimpleChanges,
    ViewChild,
} from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MatPaginator } from '@angular/material/paginator';
import { BehaviorSubject, Observable, map, switchMap, tap } from 'rxjs';
import { pvfRequestsService } from 'services/pvf-requests.service';

@Component({
    selector: 'mpmt-listagem',
    templateUrl: './mpmt-listagem.component.html',
    standalone: false
})
export class MpmtListagemComponent implements OnInit, OnChanges {
    @ViewChild(MatPaginator) paginator: MatPaginator;

    public filtros: FormGroup = new FormGroup({});

    private colunasSubject = new BehaviorSubject<{ [key: string]: string }>({});
    private listagemSubject = new BehaviorSubject<any[]>([]);
    private loadingSubject = new BehaviorSubject<boolean>(false);
    private totalSubject = new BehaviorSubject<number>(0);
    private perPageSubject = new BehaviorSubject<number>(10);

    public colunas$ = this.colunasSubject.asObservable();
    public colunaTitulos$ = this.colunasSubject.asObservable();
    public listagem$ = this.listagemSubject.asObservable();
    public loading$ = this.loadingSubject.asObservable();
    public total$ = this.totalSubject.asObservable();
    public perPage$ = this.perPageSubject.asObservable();

    constructor() {}

    ngOnInit() {
        this.configurarColunas();
        this.configurarDados();
    }

    ngAfterViewInit() {
        if (this.paginator)
            this.paginator.page
                .pipe(tap(() => this.configurarDados()))
                .subscribe();
    }

    ngOnChanges(changes: SimpleChanges) {
        this.aplicarFiltros();
    }

    protected async configurarColunas() {
        this.colunasSubject.next(await this.obterColunas());
    }

    protected async configurarDados() {
        const filtros = await this.obterFiltros();
        const response = await this.obterDados(filtros);

        this.listagemSubject.next(response.results);
        this.totalSubject.next(response.total);
        this.perPageSubject.next(response.per_page);
    }

    protected async aplicarFiltros() {
        this.loadingSubject.next(true);
        await this.configurarDados();
        this.loadingSubject.next(false);
    }

    protected async obterColunas(): Promise<{ [key: string]: string }> {
        return {};
    }

    protected obterTitulo() {
        return 'Listagem';
    }

    protected async obterDados(filtros: any): Promise<{
        total?: number;
        page?: number;
        per_page?: number;
        results: any[];
    }> {
        const response = await pvfRequestsService(filtros);
        return response;
    }

    protected async obterFiltros(): Promise<{ [key: string]: any }> {
        return {
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 10,
        };
    }

    protected alterarOrdenacao($event: {
        active: string;
        direction: 'asc' | 'desc';
    }) {
        const { active, direction } = $event;
        this.filtros.patchValue({
            order_by: direction == 'asc' ? active : `-${active}`,
        });
        this.aplicarFiltros();
    }

    protected get colunasVisiveis() {
        return this.colunas$.pipe(map((value) => Object.keys(value)));
    }

    protected get colunasVisiveisComAcao() {
        return this.colunasVisiveis.pipe(
            map((x) => {
                return [...x, 'acao'];
            })
        );
    }
}
