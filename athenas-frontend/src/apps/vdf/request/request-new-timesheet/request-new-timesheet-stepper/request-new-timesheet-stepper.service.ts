import { Component, Injectable } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';

@Injectable({
    providedIn: 'root',
})
export class RequestNewTimesheetStepperService {
    public currentStep: number = 0;

    public setNumberPeriods(quantity: number) {
        this.steps = [this.steps[0], this.steps[1]];
    }

    public steps = ['Instruções', 'Justificativas'];
}
