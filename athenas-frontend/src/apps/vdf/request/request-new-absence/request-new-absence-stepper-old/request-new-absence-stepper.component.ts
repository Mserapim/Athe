import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-absence-stepper',
    templateUrl: './request-new-absence-stepper.component.html',
    styleUrls: ['./request-new-absence-stepper.component.scss'],
    standalone: false
})
export class RequestNewAbsenceStepperComponent {
    constructor(public requesStepperService: RequestStepperService) {
        this.requesStepperService.steps = [
            'Tipo de afastamento',
            'Dados do afastamento',
            'Informe o subtituto',
        ];
    }
}
