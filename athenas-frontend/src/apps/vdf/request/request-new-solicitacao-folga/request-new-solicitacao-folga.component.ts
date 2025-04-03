import { Component } from '@angular/core';
import {  Router } from '@angular/router';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-base',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestSolicitacaoFolgaComponent extends RequestNewBaseComponent {
    title = 'Solicitacao de Crédito de Folga';
    description = ''

    constructor(public router: Router, stepper: RequestStepperService) {
        super(router, stepper);
        stepper.steps = ['Solicitação'];
    }

    ngOnInit() {}
}
