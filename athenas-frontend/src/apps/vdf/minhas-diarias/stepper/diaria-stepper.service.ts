import { Component, Injectable } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';


@Injectable({
    providedIn: 'root'
})
export class DiariaStepperService {

    public currentStep: number = 1;

    public id_viagem: number = null;

    public getTituloStep(){
        return this.steps[this.currentStep]
    }

    public steps = [
        'Dados da Viagem',
        'Beneficiarios',
        'Trechos de Destino',
    ];
}
