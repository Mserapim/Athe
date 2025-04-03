import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestNewAuxilioCrecheIrService } from './request-new-auxilio-creche-ir.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-auxilio-creche-ir',
    templateUrl: '../request-new-base/request-new-base.component.html',
    styleUrls: ['../request-new-base/request-new-base.component.scss'],
    standalone: false
})
export class RequestNewAuxilioCrecheIrComponent extends RequestNewBaseComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewAuxilioCrecheIrService
    ) {
        super(router, stepper);
        stepper.steps = ['Solicitação'];
        this.configure();
    }

    protected configure() {
        this.service.title = 'Auxílio creche e/ou dependente de IRRF';
        this.service.path = 'auxilio-creche-ir';
        this.title = this.service.title;
    }
}
