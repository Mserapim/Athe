import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { DiariaStepperService } from '../../stepper/diaria-stepper.service';
import { apiDiariasDestinos } from 'api/diarias/api-diarias-destinos.service';
import { MpmtAccordionService } from 'components/mpmt-accordion/mpmt-accordion.service';




@Injectable()
export class NovaDiariaStep3Service extends MpmtAccordionService {

   

    constructor(
        private stepperService: DiariaStepperService,
    ) {
        super();
    }




    public async obterDadosItem(filtros: any) {
        return apiDiariasBeneficiarios({viagem_id:this.stepperService.id_viagem});
    }

    public async obterDadosSubItem(id: number) {
        return apiDiariasDestinos({beneficiario:id});
    }


}
