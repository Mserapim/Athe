import { Component } from '@angular/core';
import { RequestNewElectoralSlackComponent } from '../request-new-electoral-slack/request-new-electoral-slack.component';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { apiRhPvfRequestsUsufructsCompensatoryDaysService } from 'api/rh/api-rh-pvf-requests-usufructs-compensatory-days.service';
import { RequestNewSubstitutePromotersService } from './request-new-substitute-promoters.service';
import { apiRhPvfRequestsUsufructsMemberRecessService } from 'api/rh/api-rh-pvf-requests-usufructs-member-recess.service';
import { apiRhPvfRequestsUsufructsSubstitutePromotersService } from 'api/rh/api-rh-pvf-requests-usufructs-substitute-promoters.service';

@Component({
    selector: 'request-new-substitute-promoters',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewSubstitutePromotersComponent extends RequestNewElectoralSlackComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewSubstitutePromotersService
    ) {
        super(router, stepper, service);
    }

    protected configure() {
        this.service.title = 'Concurso de promotor substituto';
        this.service.path = 'concurso-promotor-substituto';
        this.service.apiService =
            apiRhPvfRequestsUsufructsSubstitutePromotersService;
        this.service.type_usufruct =
            TypeUsufructEnum.CONCURSO_PROMOTOR_SUBSTITUTO;
        this.title = this.service.title;
    }
}
