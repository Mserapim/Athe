import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { apiRhPvfConfigRequestsCancelUsufructs } from 'api/rh/api-rh-pvf-config-requests-cancel-usufructs.service';
import { SelectionModel } from '@angular/cdk/collections';
import { apiRhPvfRequestsSchedulesCancel } from 'api/rh/api-rh-pvf-requests-schedules-cancel.service';

@Component({
    selector: 'request-new-cancel-step2-usufrutos',
    templateUrl: './request-new-cancel-step2-usufrutos.component.html',
    styleUrls: ['./request-new-cancel-step2-usufrutos.component.scss'],
    standalone: false
})
export class RequestNewCancelStep2UsufrutosComponent {
    results = [];
    selection = new SelectionModel<any>(true, []);
    // @ViewChild(MatPaginator) paginator: MatPaginator;
    message: string = '';
    observation: string = '';
    displayedColumns: string[] = [
        'select',
        'type_usufruct',
        'start_date',
        'end_date',
        'days',
        'type_activity',
        'start_date_acquisition',
    ];

    constructor(
        private stepper: RequestStepperService,
        private router: Router
    ) {
        stepper.currentStep = 1;
        stepper.steps = ['Selecionar Usufruto'];
    }

    ngOnInit() {
        this.loadConfigRequestsCanceables();
    }

    get isValid() {
        return this.selection.selected.length > 0;
    }

    async loadConfigRequestsCanceables() {
        const { results } = await apiRhPvfConfigRequestsCancelUsufructs({});
        this.results = results;
    }

    async confirm() {
        const selected = this.selection.selected[0];
        this.message = '';
        try {
            const {} = await apiRhPvfRequestsSchedulesCancel({
                usufruct_id: selected.pk,
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
