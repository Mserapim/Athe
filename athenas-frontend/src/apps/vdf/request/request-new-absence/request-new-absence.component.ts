import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';

@Component({
    selector: 'request-new-absence',
    templateUrl: '../request-new-base/request-new-base.component.html',
    styleUrls: ['../request-new-base/request-new-base.component.scss'],
    standalone: false
})
export class RequestNewAbsenceComponent extends RequestNewBaseComponent {
    title = 'Solicitação de Afastamentos';
    description = `
    Informações importantes e relevantes sobre como relacionar ou solicitar o
    cancelamentos, contatos e emails para tirar dúvidas
    Informações importantes e relevantes sobre como relacionar ou solicitar o
    cancelamentos, contatos e emails para tirar dúvidas
`;

    constructor(public router: Router, stepper: RequestStepperService) {
        super(router, stepper);
        stepper.steps = [
            'Tipo de afastamento',
            'Dados do afastamento',
            'Informe o subtituto',
        ];
    }

    ngOnInit() {}
}
