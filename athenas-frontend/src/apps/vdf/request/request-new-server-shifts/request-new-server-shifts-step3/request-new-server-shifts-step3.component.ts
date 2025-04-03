import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewServerShiftsService } from '../request-new-server-shifts.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewElectoralSlackStep3Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step3/request-new-electoral-slack-step3.component';

@Component({
    selector: 'request-new-server-shifts-step3',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step3/request-new-electoral-slack-step3.component.html',
    standalone: false
})
export class RequestNewServerShiftsStep3Component extends RequestNewElectoralSlackStep3Component {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewServerShiftsService
    ) {
        super(stepper, router, service);
    }
}
