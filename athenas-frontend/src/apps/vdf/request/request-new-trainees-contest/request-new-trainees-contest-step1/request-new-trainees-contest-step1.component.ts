import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackStep1Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewTraineesContextService } from '../request-new-trainees-contest.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-trainees-contest-step1',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component.html',
    standalone: false
})
export class RequestNewTraineesContextStep1Component extends RequestNewElectoralSlackStep1Component {
    constructor(
        protected service: RequestNewTraineesContextService,
        protected stepper: RequestStepperService,
        protected router: Router
    ) {
        super(service, stepper, router);

        service.title = 'Concurso de Estagiários';
        service.path = 'concurso-estagiario';
        service.type_usufruct = TypeUsufructEnum.CONCURSO_ESTAGIARIO;
    }
}
