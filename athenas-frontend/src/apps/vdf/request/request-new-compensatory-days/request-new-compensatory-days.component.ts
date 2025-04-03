import { Component } from '@angular/core';
import { RequestNewElectoralSlackComponent } from '../request-new-electoral-slack/request-new-electoral-slack.component';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { apiRhPvfRequestsUsufructsCompensatoryDaysService } from 'api/rh/api-rh-pvf-requests-usufructs-compensatory-days.service';
import { RequestNewCompensatoryDaysService } from './request-new-compensatory-days.service';

@Component({
    selector: 'request-new-compensatory-days',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewCompensatoryDaysComponent extends RequestNewElectoralSlackComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewCompensatoryDaysService
    ) {
        super(router, stepper, service);
    }

    protected configure() {
        this.service.title = 'Folga compensatórias';
        this.service.path = 'folga-compensatoria';
        this.service.apiService =
            apiRhPvfRequestsUsufructsCompensatoryDaysService;
        this.service.type_usufruct =
            TypeUsufructEnum.FOLGA_COMPENSATORIAS_DE_MEMBROS;
        this.title = this.service.title;
    }
}
