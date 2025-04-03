import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-electoral-slack-step3',
    templateUrl: './request-new-electoral-slack-step3.component.html',
    standalone: false
})
export class RequestNewElectoralSlackStep3Component {
    isLoading = false;

    constructor(
        protected stepper: RequestStepperService,
        protected router: Router,
        protected service: RequestNewElectoralSlackService
    ) {
        this.stepper.currentStep = 2;
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
            'step2',
        ]);
    }
}
