
import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiRhTelefones } from 'api/rh/telefone/api-rh-telefones-service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { BehaviorSubject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class TelefoneService extends MpmtListagem2Service {
    public loading: boolean = false;


    filtros = new FormGroup({
        pessoa_id: new FormControl<number | null>(null, []),
        orgao_id: new FormControl<number | null>(null, []),
    });


    constructor() {
        super();
    }

    atualizarPessoaId(id: number) {
        this.filtros.get('pessoa_id').setValue(id);
        this.filtros.get('orgao_id').setValue(null);
        this.recarregarListagem();
    }

    atualizarOrgaoId(id: number) {
        this.filtros.get('orgao_id').setValue(id);
        this.filtros.get('pessoa_id').setValue(null);
        this.recarregarListagem();
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

    public async obterDados(filtros: any) {
        this.loading = true;
        const dados = await apiRhTelefones(filtros);
        this.loading = false;
        return dados;
    }

    
}