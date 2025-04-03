import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackStep1Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewBloodDonationService } from '../request-new-blood-donation.service';

@Component({
    selector: 'request-new-blood-donation-step1',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component.html',
    standalone: false
})
export class RequestNewBloodDonationStep1Component extends RequestNewElectoralSlackStep1Component {
    constructor(
        protected service: RequestNewBloodDonationService,
        protected stepper: RequestStepperService,
        protected router: Router
    ) {
        super(service, stepper, router);
    }
}
