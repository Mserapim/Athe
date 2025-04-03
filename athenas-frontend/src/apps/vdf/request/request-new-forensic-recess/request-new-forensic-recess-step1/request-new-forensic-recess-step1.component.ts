import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackStep1Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewForensicRecessService } from '../request-new-forensic-recess.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-forensic-recess-step1',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component.html',
    standalone: false
})
export class RequestNewForensicRecessStep1Component extends RequestNewElectoralSlackStep1Component {
    constructor(
        protected service: RequestNewForensicRecessService,
        protected stepper: RequestStepperService,
        protected router: Router
    ) {
        super(service, stepper, router);
    }
}
