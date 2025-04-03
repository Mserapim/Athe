import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasDestinos } from 'api/diarias/api-diarias-destinos.service';
import { apiAfastamentosMembrosEstagioProbatorio } from 'api/rh/mov-carreira/api-afastamentos-estagio-probatorio.service';
import { MpmtPaginacao } from 'components/mpmt-celula/mpmt-celula.interface';
import { MpmtListagemService } from 'components/mpmt-listagens/mpmt-listagem.service';
import { BehaviorSubject } from 'rxjs';

@Injectable()
export class AfastamentoService extends MpmtListagemService {
    public membroId: number;

    constructor() {
        super();
    }
    
    async obterDados() {
        const afastamentos = await apiAfastamentosMembrosEstagioProbatorio({
            membroId: this.membroId,
        });
        return afastamentos;
    }

}