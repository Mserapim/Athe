import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { RequestNewVacationsStepperService } from './request-new-vacations-stepper.service';

@Component({
    selector: 'request-new-vacations-stepper',
    templateUrl: './request-new-vacations-stepper.component.html',
    styleUrls: ['./request-new-vacations-stepper.component.scss'],
    standalone: false
})
export class RequestNewVacationsStepperComponent {
    constructor(
        public requestNewRegularVacationsStepperService: RequestNewVacationsStepperService
    ) {}
}
