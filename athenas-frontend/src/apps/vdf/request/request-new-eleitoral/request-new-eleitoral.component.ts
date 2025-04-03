import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestNewEleitoralService } from './request-new-eleitoral.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-eleitoral',
    templateUrl: 'request-new-eleitoral.component.html',
    standalone: false
})
export class RequestNewEleitoralComponent extends RequestNewBaseComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewEleitoralService
    ) {
        super(router, stepper);
        stepper.steps = ['Tipo de solicitação'];
        this.configure();
    }

    protected configure() {
        this.service.title = 'Dispensa Eleitoral - TRE';
        this.service.path = 'dispensa-eleitoral';
        this.service.type_usufruct = TypeUsufructEnum.FOLGA_ELEITORAL;
        this.title = this.service.title;
    }
}
