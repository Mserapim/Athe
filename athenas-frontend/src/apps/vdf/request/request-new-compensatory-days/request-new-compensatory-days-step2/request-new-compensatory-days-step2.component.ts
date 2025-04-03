import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackStep2Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component';
import { RequestNewCompensatoryDaysService } from '../request-new-compensatory-days.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-compensatory-days-step2',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component.html',
    standalone: false
})
export class RequestNewCompensatoryDaysStep2Component extends RequestNewElectoralSlackStep2Component {
    constructor(
        router: Router,
        stepper: RequestStepperService,
        service: RequestNewCompensatoryDaysService
    ) {
        super(stepper, router, service);
    }
}
