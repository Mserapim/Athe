import { Component } from '@angular/core';
import { MpmtStepperService } from './mpmt-stepper.service';

@Component({
    selector: 'mpmt-stepper',
    templateUrl: './mpmt-stepper.component.html',
    styleUrls: ['./mpmt-stepper.component.scss'],
    standalone: false
})
export class MpmtStepperComponent {
    constructor(public mpmtStepperService: MpmtStepperService) {}
}
