import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-relatorio-teletrabalho-semestral',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewRelatorioTeletrabalhoSemestralComponent extends RequestNewBaseComponent {
    title = 'Solicitação de entrega de Relatório Teletrabalho Semestral';
    description = `
    <div class="flex flex-col ">
    </div>
`;

    constructor(public router: Router, stepper: RequestStepperService) {
        super(router, stepper);
        stepper.steps = ['Resumo', 'Formulário'];
    }

    ngOnInit() {}
}
