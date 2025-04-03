import { Component, Injectable } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';

@Injectable({
    providedIn: 'root',
})
export class RequestStepperService {
    public currentStep: number = 1;

    public steps = [
        'Periodo aquisitivos',
        'Selecione a combinação e data',
        'Informe o subtituto',
    ];
}
