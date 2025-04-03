import { Component } from '@angular/core';
import { RequestStepperService } from './request-stepper.service';

@Component({
    selector: 'request-stepper',
    templateUrl: './request-stepper.component.html',
    styleUrls: ['./request-stepper.component.scss'],
    standalone: false
})
export class RequestStepperComponent {
    constructor(public requestStepperService: RequestStepperService) {}
}
