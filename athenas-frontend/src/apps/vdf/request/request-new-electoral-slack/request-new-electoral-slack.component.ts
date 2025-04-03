import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestNewElectoralSlackService } from './request-new-electoral-slack.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-electoral-slack',
    templateUrl: '../request-new-base/request-new-base.component.html',
    styleUrls: ['../request-new-base/request-new-base.component.scss'],
    standalone: false
})
export class RequestNewElectoralSlackComponent extends RequestNewBaseComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewElectoralSlackService
    ) {
        super(router, stepper);
        stepper.steps = ['Saldos', 'Usufrutos', 'Substitutos'];
        this.configure();
    }

    protected configure() {
        this.service.title = 'Dispensa eleitoral';
        this.service.path = 'dispensa-eleitoral';
        this.service.type_usufruct = TypeUsufructEnum.FOLGA_ELEITORAL;
        this.title = this.service.title;
    }
}
