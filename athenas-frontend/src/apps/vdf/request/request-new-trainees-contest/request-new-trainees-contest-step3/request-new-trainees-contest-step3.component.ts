import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewTraineesContextService } from '../request-new-trainees-contest.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewElectoralSlackStep3Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step3/request-new-electoral-slack-step3.component';

@Component({
    selector: 'request-new-trainees-contest-step3',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step3/request-new-electoral-slack-step3.component.html',
    standalone: false
})
export class RequestNewTraineesContextStep3Component extends RequestNewElectoralSlackStep3Component {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewTraineesContextService
    ) {
        super(stepper, router, service);
    }
}
