import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-timesheet',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewTimesheetComponent extends RequestNewBaseComponent {
    title = 'Solicitação de entrega de Folha ponto';
    description = `
    <div class="flex flex-col ">
        <li>1. Baixe a folha ponto para visualizar e conferir;</li>
        <li>
            2. Caso tenha ausências clique no botão “Novo” para
            adicionar justificativa;
        </li>
        <li>
            3. Envie ao aprovador somente após conferir a folha
            ponto e preencher todas as justificativas necessárias;
        </li>
        <li>
            * 4. Quem participa do programa de teletrabalho ATO
            1058/2021 ou ATO 862/2019 deve utilizar formulário
            próprio;
        </li>
    </div>
`;

    constructor(public router: Router, stepper: RequestStepperService) {
        super(router, stepper);
        stepper.steps = ['Instruções', 'Justificativas'];
    }

    ngOnInit() {}
}
