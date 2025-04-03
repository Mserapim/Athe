import { Component } from '@angular/core';
import { RequestNewElectoralSlackComponent } from '../request-new-electoral-slack/request-new-electoral-slack.component';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack/request-new-electoral-slack.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { RequestNewBloodDonationService } from './request-new-blood-donation.service';

@Component({
    selector: 'request-new-blood-donation',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewBloodDonationComponent extends RequestNewElectoralSlackComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewBloodDonationService
    ) {
        super(router, stepper, service);
    }

    protected configure() {
        this.service.title = 'Doação de Sangue';
        this.service.path = 'doacao-sangue';
        this.service.type_usufruct = TypeUsufructEnum.DOACAO_SANGUE;
        this.title = this.service.title;
    }
}
