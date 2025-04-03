import { Component } from '@angular/core';
import { RequestNewElectoralSlackComponent } from '../request-new-electoral-slack/request-new-electoral-slack.component';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { apiRhPvfRequestsUsufructsCompensatoryDaysService } from 'api/rh/api-rh-pvf-requests-usufructs-compensatory-days.service';
import { RequestNewMemberRecessService } from './request-new-member-recess.service';
import { apiRhPvfRequestsUsufructsMemberRecessService } from 'api/rh/api-rh-pvf-requests-usufructs-member-recess.service';

@Component({
    selector: 'request-new-member-recess',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewMemberRecessComponent extends RequestNewElectoralSlackComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewMemberRecessService
    ) {
        super(router, stepper, service);
    }

    protected configure() {
        this.service.title = 'Recesso Forense de Membros';
        this.service.path = 'recesso-forense-de-membros';
        this.service.apiService = apiRhPvfRequestsUsufructsMemberRecessService;
        this.service.type_usufruct =
            TypeUsufructEnum.PLANTAO_RECESSO_FORENSE_MEMBROS;
        this.title = this.service.title;
    }
}
