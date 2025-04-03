import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService {
    public currentStep: number = 0;

    public setNumberPeriods(quantity: number) {
        this.steps = [this.steps[0], this.steps[1]];
    }

    public steps = ['Instruções', 'Justificativas'];
}
