import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestNewExercicioCumulativoService } from './request-new-exercicio-cumulativo.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-new-exercicio-cumulativo',
    templateUrl: '../request-new-base/request-new-base.component.html',
    styleUrls: ['../request-new-base/request-new-base.component.scss'],
    standalone: false
})
export class RequestNewExercicioCumulativoComponent extends RequestNewBaseComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewExercicioCumulativoService
    ) {
        super(router, stepper);
        stepper.steps = ['Substituições'];
        this.configure();
    }

    protected configure() {
        this.service.title = 'Exercicio Cumulativo';
        this.service.path = 'exercicio-cumulativo';
        this.title = this.service.title;
    }
}
