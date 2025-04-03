import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleControleAcessoMenuConfigs } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-configs.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class PainelControleGrupoMenuEditarListagemService extends MpmtListagem2Service {
    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        usuario_grupo_id: new FormControl<string>(null, []),
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('ATIVO', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiPainelControleControleAcessoMenuConfigs(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}
