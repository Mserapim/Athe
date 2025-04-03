import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class PainelControleModulosService extends MpmtListagem2Service {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('ATIVO', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiPainelControleControleAcessoModulos(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}
