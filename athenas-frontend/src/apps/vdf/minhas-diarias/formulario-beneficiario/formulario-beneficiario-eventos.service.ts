import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { DiariaStepperService } from '../stepper/diaria-stepper.service';
import { MpmtListagemService } from 'components/mpmt-listagens/mpmt-listagem.service';
import { apiDiariasEventos } from 'api/diarias/api-diarias-eventos.service';
import { MpmtPaginacao } from 'components/mpmt-celula/mpmt-celula.interface';


@Injectable()
export class FormularioEventoService extends MpmtListagemService {

    constructor(
    ) {
        super();
    }

    beneficiario_id: number = null;
    
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        beneficiario: new FormControl<number>(this.beneficiario_id,[]),
    });

    public async obterDados(filtros: any) {
        return apiDiariasEventos(filtros);
    }

    protected async obterFiltros() {

        this.filtros.get('beneficiario')?.setValue(this.beneficiario_id)
        return { ...this.filtros.value };
    }

    protected async obterPaginacao(): Promise<MpmtPaginacao> {

        this.paginacao.per_page = null;
        
        return { ...this.paginacao };
    }
}
