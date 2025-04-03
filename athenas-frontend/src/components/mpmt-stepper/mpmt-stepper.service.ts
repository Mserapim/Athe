import { Component, Injectable } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';

@Injectable({
    providedIn: 'root',
})
export class MpmtStepperService {
    public currentStep: number = 1;

    public steps = [
        'Início',
    ];
}
