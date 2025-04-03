import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewCompensatoryDaysService } from '../request-new-compensatory-days.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewElectoralSlackStep3Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step3/request-new-electoral-slack-step3.component';

@Component({
    selector: 'request-new-compensatory-days-step3',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step3/request-new-electoral-slack-step3.component.html',
    standalone: false
})
export class RequestNewCompensatoryDaysStep3Component extends RequestNewElectoralSlackStep3Component {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewCompensatoryDaysService
    ) {
        super(stepper, router, service);
    }
}
