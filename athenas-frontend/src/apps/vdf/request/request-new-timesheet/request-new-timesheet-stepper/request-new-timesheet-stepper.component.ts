import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { RequestNewTimesheetStepperService } from './request-new-timesheet-stepper.service';

@Component({
    selector: 'request-new-timesheet-stepper',
    templateUrl: './request-new-timesheet-stepper.component.html',
    styleUrls: ['./request-new-timesheet-stepper.component.scss'],
    standalone: false
})
export class RequestNewTimesheetStepperComponent {
    constructor(
        public RequestNewTimesheetStepperService: RequestNewTimesheetStepperService
    ) {}
}
