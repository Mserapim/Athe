import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewEleitoralService } from '../request-new-eleitoral.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-electoral-slack-step1',
    templateUrl: './request-new-eleitoral-step2-folga.component.html',
    standalone: false
})
export class RequestNewEleitoralStep2FolgaComponent {
    title = '';
    subtitle = '';
    displayedColumns = [
        'group_period_name',
        'start_date_acquisition',
        'end_date_acquisition',
        'balance_available',
        'status_name',
    ];

    constructor(
        protected service: RequestNewEleitoralService,
        protected stepper: RequestStepperService,
        protected router: Router
    ) {
        stepper.currentStep = 1;
    }

    async ngOnInit() {
        await this.service.loadRights();
    }

    get isValid() {
        return this.service.hasBalance;
    }

    goNext() {
        this.router.navigate([
            `vdf/solicitacoes/novo/${this.service.path}`,
            'step3',
        ]);
    }
}
