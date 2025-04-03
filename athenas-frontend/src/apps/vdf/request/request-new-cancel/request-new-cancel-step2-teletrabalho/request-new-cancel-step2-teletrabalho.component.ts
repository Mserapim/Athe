import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { SelectionModel } from '@angular/cdk/collections';
import { apiRhPvfEnviosTeletabalho } from 'api/rh/api-rh-pvf-config-requests-envios-teletrabalhos.service';
import { apiRhPvfRequestsTeletrabalhoCancelar } from 'api/rh/api-rh-pvf-requests-teletrabalho-cancelar.service';

@Component({
    selector: 'request-new-cancel-step2-teletrabalho',
    templateUrl: './request-new-cancel-step2-teletrabalho.component.html',
    styleUrls: ['./request-new-cancel-step2-teletrabalho.component.scss'],
    standalone: false
})
export class RequestNewCancelStep2TeletrabalhoComponent {
    results = [];
    selection = new SelectionModel<any>(true, []);
    // @ViewChild(MatPaginator) paginator: MatPaginator;
    message: string = '';
    observation: string = '';
    displayedColumns: string[] = [
        'select',
        'id',
        'tipo_solicitacao',
        'date',
        'referencia',
        'status',
        'inicio_plano',
        'fim_plano',
    ];

    constructor(
        private stepper: RequestStepperService,
        private router: Router
    ) {
        stepper.currentStep = 1;
        stepper.steps = ['Selecionar Teletrabalho'];
    }

    ngOnInit() {
        this.load();
    }

    get isValid() {
        return this.selection.selected.length > 0;
    }

    async load() {
        const { results } = await apiRhPvfEnviosTeletabalho({});
        this.results = results;
    }

    selecaoCustomizada(row: any) {
        this.selection.toggle(row);
        for (const item of this.results) {
            const referenciaLista = this.textoToDate(item.referencia);
            const referenciaSelecionada = this.textoToDate(row.referencia);
            if (item !== row)
                if (referenciaLista > referenciaSelecionada) {
                    this.selection.select(item);
                } else {
                    this.selection.deselect(item);
                }
        }
    }

    textoToDate(competencia: string): Date {
        const [mes, ano] = competencia.split('/').map(Number);
        return new Date(ano, mes - 1, 1);
    }

    get selected() {
        if (!this.selection.selected) return [];
        return this.selection.selected?.map((x) => x.id);
    }

    async confirm() {
        const selected = this.selection.selected[0];
        this.message = '';
        try {
            const {} = await apiRhPvfRequestsTeletrabalhoCancelar({
                request_ids: this.selected,
                observation: this.observation,
            });
            this.goRequests();
        } catch (e) {
            this.message = e?.response?.data?.message;
        }
    }

    async goRequests() {
        this.router.navigate([`vdf/solicitacoes/`]);
    }
}
