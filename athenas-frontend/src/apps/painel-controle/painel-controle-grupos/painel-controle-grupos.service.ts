import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleControleAcessoGrupos } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos.service';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class PainelControleGruposService extends MpmtListagem2Service {
    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('ATIVO', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiPainelControleControleAcessoGrupos(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}