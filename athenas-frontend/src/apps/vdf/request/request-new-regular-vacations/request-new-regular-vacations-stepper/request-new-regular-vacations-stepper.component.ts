import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { RequestNewRegularVacationsStepperService } from './request-new-regular-vacations-stepper.service';

@Component({
    selector: 'request-new-regular-vacations-stepper',
    templateUrl: './request-new-regular-vacations-stepper.component.html',
    styleUrls: ['./request-new-regular-vacations-stepper.component.scss'],
    standalone: false
})
export class RequestNewRegularVacationsStepperComponent {
    constructor(
        public requestNewRegularVacationsStepperService: RequestNewRegularVacationsStepperService,
    ) {

    }

}
