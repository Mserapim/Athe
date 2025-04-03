import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-horizontal-progressions',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewHorizontalProgressionsComponent extends RequestNewBaseComponent {
    title = 'Solicitação de progressão horizontal';
    description = `
        Informações importantes e relevantes sobre como relacionar ou solicitar o
        cancelamentos, contatos e emails para tirar dúvidas
    `;

    constructor(public router: Router, stepper: RequestStepperService) {
        super(router, stepper);
        stepper.steps = ['Classe a progredir', 'Documentos comprobatórios'];
    }

    ngOnInit() {}
}
