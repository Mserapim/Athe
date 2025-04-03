import { Component } from '@angular/core';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService } from './request-new-relatorio-teletrabalho-semestral-criar-stepper.service';

@Component({
    selector: 'request-new-relatorio-teletrabalho-semestral-criar-stepper',
    templateUrl: './request-new-relatorio-teletrabalho-semestral-criar-stepper.component.html',
    standalone: false
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperComponent {
    constructor(
        public vdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService: VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService
    ) {}
}
