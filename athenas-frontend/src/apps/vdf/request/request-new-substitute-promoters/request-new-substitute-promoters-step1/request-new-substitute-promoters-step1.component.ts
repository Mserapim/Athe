import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackStep1Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewSubstitutePromotersService } from '../request-new-substitute-promoters.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-substitute-promoters-step1',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component.html',
    standalone: false
})
export class RequestNewSubstitutePromotersStep1Component extends RequestNewElectoralSlackStep1Component {
    constructor(
        protected service: RequestNewSubstitutePromotersService,
        protected stepper: RequestStepperService,
        protected router: Router
    ) {
        super(service, stepper, router);
    }
}
