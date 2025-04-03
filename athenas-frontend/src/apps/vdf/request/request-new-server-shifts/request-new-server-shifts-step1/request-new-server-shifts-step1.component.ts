import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackStep1Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewServerShiftsService } from '../request-new-server-shifts.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-server-shifts-step1',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component.html',
    standalone: false
})
export class RequestNewServerShiftsStep1Component extends RequestNewElectoralSlackStep1Component {
    constructor(
        protected service: RequestNewServerShiftsService,
        protected stepper: RequestStepperService,
        protected router: Router
    ) {
        super(service, stepper, router);

        service.title = 'Recesso Forense';
        service.path = 'plantao-servidor';
        service.type_usufruct = TypeUsufructEnum.PLANTAO_SERVIDORES;
    }
}
