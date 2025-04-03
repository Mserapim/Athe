import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { DiariaStepperService } from '../../stepper/diaria-stepper.service';
import { MpmtListagemService } from 'components/mpmt-listagens/mpmt-listagem.service';


@Injectable()
export class NovaDiariaStep2Service extends MpmtListagemService {

    constructor(
        private stepperService: DiariaStepperService,
    ) {
        super();
    }
    
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        viagem_id: new FormControl<number>(this.stepperService.id_viagem,[]),
    });

    public async obterDados(filtros: any) {
        return apiDiariasBeneficiarios(filtros);
    }

    protected async obterFiltros() {

        this.filtros.get('viagem_id')?.setValue(this.stepperService.id_viagem)
        return { ...this.filtros.value };
    }
}
