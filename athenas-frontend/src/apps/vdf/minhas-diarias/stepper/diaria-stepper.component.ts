import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import {DiariaStepperService } from './diaria-stepper.service';

@Component({
    selector: 'diaria-stepper',
    templateUrl: './diaria-stepper.component.html',
    styleUrls: ['./diaria-stepper.component.scss'],
    standalone: false
})
export class DiariaStepperComponent {
    constructor(
        public novaDiariaStepperService: DiariaStepperService,
    ) {}

}
