import { Component } from '@angular/core';
import { RequestNewElectoralSlackComponent } from '../request-new-electoral-slack/request-new-electoral-slack.component';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestNewForensicRecessService } from './request-new-forensic-recess.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-forensic-recess',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewForensicRecessComponent extends RequestNewElectoralSlackComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewForensicRecessService
    ) {
        super(router, stepper, service);
    }

    protected configure() {
        this.service.title = 'Recesso Forense';
        this.service.path = 'recesso-forense';
        this.service.type_usufruct = TypeUsufructEnum.RECESSO_FORENSE;
        this.title = this.service.title;
    }
}
