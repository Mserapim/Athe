import { Component, Injectable } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';


@Injectable({
    providedIn: 'root'
})
export class RequestNewRegularVacationsStepperService {

    public currentStep: number = 0;

    public setNumberPeriods(quantity: number) {

        this.steps = [this.steps[0], this.steps[1]]

        for (let i = 0; i < quantity; i++)
            this.steps.push(`Informe subtituto - ${i + 1}º Período`)

    }

    public steps = [
        'Periodo aquisitivos',
        'Selecione a combinação e data',
        'Informe o subtituto',
    ];
}
