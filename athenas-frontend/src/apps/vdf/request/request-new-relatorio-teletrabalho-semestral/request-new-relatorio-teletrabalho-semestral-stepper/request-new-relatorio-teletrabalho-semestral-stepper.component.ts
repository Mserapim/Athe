import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { RequestNewRelatorioTeletrabalhoSemestralStepperService } from './request-new-relatorio-teletrabalho-semestral-stepper.service';

@Component({
    selector: 'request-new-relatorio-teletrabalho-semestral-stepper',
    templateUrl: './request-new-relatorio-teletrabalho-semestral-stepper.component.html',
    standalone: false
})
export class RequestNewRelatorioTeletrabalhoSemestralStepperComponent {
    constructor(
        public RequestNewRelatorioTeletrabalhoSemestralStepperService: RequestNewRelatorioTeletrabalhoSemestralStepperService
    ) {}
}
