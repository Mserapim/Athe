import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RhPvfapiRhPvfVendaSubstituicoesDataSource } from 'datasources/rh-pvf-venda-subtituicoes.datasource';
import { SelectionModel } from '@angular/cdk/collections';
import { printDate } from 'utils/print-date';
import { apiRhPvfRequestsVendaExerciciosCumulativos } from 'api/rh/api-rh-pvf-requests-venda-exercicios-cumulativos.service';

@Component({
    selector: 'request-new-exercicio-cumulativo-step1',
    templateUrl: './request-new-exercicio-cumulativo-step1.component.html',
    standalone: false
})
export class RequestNewExercicioCumulativoStep1Component {
    dataSource = new RhPvfapiRhPvfVendaSubstituicoesDataSource();
    message: string = '';
    selection = new SelectionModel<any>(true, []);
    observation: string = '';
    total: number = 0;
    results: any[] = [];
    printDate = printDate;
    isLoading: boolean = false;
    selectedItems: Set<number> = new Set();

    displayedColumns = [
        'select',
        'cumulativa',
        'serv_substituto',
        'serv_substituido',
        'data_inicio',
        'data_fim',
    ];

    constructor(
        protected stepper: RequestStepperService,
        protected router: Router
    ) {
        stepper.currentStep = 0;
    }

    async ngOnInit() {
        this.load();
        this.watchTotal();
        this.watchResults();
    }

    async load() {
        this.dataSource.load({});
    }

    watchTotal() {
        this.dataSource.total$.subscribe((value) => {
            this.total = value;
        });
    }

    watchResults() {
        this.dataSource.results$.subscribe((value) => {
            this.results = value;
            this.selection.select(...value);
        });
    }

    get selected() {
        if (!this.selection.selected) return [];
        return this.selection.selected?.map((x) => x.id);
    }

    async goConfirm() {
        this.message = '';
        try {
            this.isLoading = true;
            const response = await apiRhPvfRequestsVendaExerciciosCumulativos({
                observacao: this.observation,
                substituicoes_ids: this.selected,
            });
            this.goRequests();
        } catch (e: any) {
            this.message = e?.response?.data?.message;
        } finally {
            this.isLoading = false;
        }
    }

    public goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }

    get isValid() {
        return this.selected?.length > 0;
    }

    isAllSelected() {
        const numSelected = this.selection.selected.length;
        const numRows = this.total;
        return numSelected === numRows;
    }

    /** Selects all rows if they are not all selected; otherwise clear selection. */
    toggleAllRows() {
        if (this.isAllSelected()) {
            this.selection.clear();
            return;
        }

        this.selection.select(...this.results);
    }
}
