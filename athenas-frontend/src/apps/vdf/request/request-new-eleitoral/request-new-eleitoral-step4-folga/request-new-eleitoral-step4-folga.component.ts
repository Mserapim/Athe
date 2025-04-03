import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewEleitoralService } from '../request-new-eleitoral.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-eleitoral-step4-folga',
    templateUrl: './request-new-eleitoral-step4-folga.component.html',
    standalone: false
})
export class RequestNewEleitoralStep4FolgaComponent {
    isLoading = false;

    constructor(
        protected stepper: RequestStepperService,
        protected router: Router,
        protected service: RequestNewEleitoralService
    ) {
        this.stepper.currentStep = 3;
    }

    ngOnInit() {}

    async goConfirm() {
        try {
            this.isLoading = true;
            this.service.message = '';
            await this.service.confirm();
            this.router.navigate(['vdf/solicitacoes']);
        } catch (e) {
            this.service.message = e?.response?.data?.message;
            console.log(e);
        } finally {
            this.isLoading = false;
        }
    }

    goBack() {
        this.router.navigate([
            'vdf/solicitacoes/novo/' + this.service.path,
            'step3',
        ]);
    }
}
