import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../request/components/request-stepper/request-stepper.service';
import { RequestNewBaseComponent } from '../request/request-new-base/request-new-base.component';

@Component({
    selector: 'vdf-solicitacao-teletrabalho-desbloqueio-criar',
    templateUrl: '../request/request-new-base/request-new-base.component.html',
    standalone: false
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioCriarComponent extends RequestNewBaseComponent {
    title = 'Solicitação Desbloqueio Teletrabalho';
    description = `
    <div class="flex flex-col ">
    </div>
`;

    constructor(public router: Router, stepper: RequestStepperService) {
        super(router, stepper);
        stepper.currentStep = 0;
        stepper.steps = ['Solicitação', 'Envio'];
    }

    ngOnInit() {}
}
