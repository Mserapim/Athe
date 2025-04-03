import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewVactionsService } from '../../request-new-vacations/request-new-vacations.service';
import { RequestNewRetificationService } from '../request-new-retification.service';
import { RequestNewElectoralSlackComponent } from '../../request-new-electoral-slack/request-new-electoral-slack.component';
import { RequestNewElectoralSlackStep2Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component';
import { RequestNewElectoralSlackService } from '../../request-new-electoral-slack/request-new-electoral-slack.service';

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

@Component({
    selector: 'request-new-retification-step2-dayoff',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component.html',
    standalone: false
})
export class RequestNewRetificationStep2DayoffComponent extends RequestNewElectoralSlackStep2Component {
    constructor(
        protected stepper: RequestStepperService,
        protected router: Router,
        protected service: RequestNewElectoralSlackService,
        protected requestNewRetificationService: RequestNewRetificationService
    ) {
        super(stepper, router, service);
        stepper.currentStep = 1;

        if (this.requestNewRetificationService.usufructs_ids?.length <= 0) {
            this.goBack();
        }
    }

    protected get total_days() {
        return this.requestNewRetificationService.total_days_to_retification;
    }

    // goBack() {
    //     this.router.navigate([
    //         `vdf/solicitacoes/novo/${this.service.path}`,
    //         'step1',
    //     ]);
    // }

    async goNext() {
        try {
            this.service.message = '';
            if (this.service.hasStep3) return this.goStep3();

            this.service.confirm();
            this.router.navigate(['vdf/solicitacoes']);
        } catch (e) {
            this.service.message = e?.response?.data?.message;
            console.log(e);
        }
    }

    goStep3() {
        this.router.navigate([
            `vdf/solicitacoes/novo/${this.service.path}`,
            'step3',
        ]);
    }

    // goNext() {
    //     this.requestNewRetificationService.usufructs_in = Object.values(
    //         this.dates
    //     ).map((x) => {
    //         return {
    //             start_date: x.start,
    //             end_date: x.end,
    //             days: x.days,
    //             sale_usufruct: 0,
    //             parcel_number: 1,
    //         };
    //     });

    //     const hasSell = this.selectedConfig.indemnity?.length > 0;
    //     if (hasSell) {
    //         const sellDay = this.selectedConfig.indemnity[0];
    //         this.requestNewRetificationService.usufructs_in.push({
    //             start_date: null,
    //             end_date: null,
    //             days: 0,
    //             sale_usufruct: sellDay,
    //             parcel_number: 1,
    //         });
    //     }
    //     if (this.currentUserService.isSubstitutable) {
    //         this.router.navigate(['vdf/solicitacoes/retificacoes', 'step3']);
    //     } else {
    //         this.goConfirm();
    //     }
    // }

    // async goConfirm() {
    //     try {
    //         const response = await this.requestNewRetificationService.confirm();
    //         this.goRequests();
    //     } catch (e) {
    //         this.message = e?.response?.data?.message;
    //     }
    // }

    goBack() {
        this.router.navigate(['vdf/solicitacoes/retificacoes', 'step1']);
    }
}
