import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackStep2Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component';
import { RequestNewMemberRecessService } from '../request-new-member-recess.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-member-recess-step2',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component.html',
    standalone: false
})
export class RequestNewMemberRecessStep2Component extends RequestNewElectoralSlackStep2Component {
    constructor(
        router: Router,
        stepper: RequestStepperService,
        service: RequestNewMemberRecessService
    ) {
        super(stepper, router, service);
    }
}
