import { Component, Inject } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewEleitoralService } from '../request-new-eleitoral.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-electoral-slack-step2',
    templateUrl: './request-new-eleitoral-step3-folga.component.html',
    standalone: false
})
export class RequestNewEleitoralStep3FolgaComponent {
    constructor(
        stepper: RequestStepperService,
        protected router: Router,
        protected service: RequestNewEleitoralService
    ) {
        stepper.currentStep = 2;
    }

    goBack() {
        this.router.navigate([
            `vdf/solicitacoes/novo/${this.service.path}`,
            'step2',
        ]);
    }

    async goNext() {
        try {
            this.service.message = '';
            if (this.service.hasStep3) return this.goStep3();

            await this.service.confirm();
            this.router.navigate(['vdf/solicitacoes']);
        } catch (e) {
            this.service.message = e?.response?.data?.message;
            console.log(e);
        }
    }

    goStep3() {
        this.router.navigate([
            `vdf/solicitacoes/novo/${this.service.path}`,
            'step4',
        ]);
    }
}
