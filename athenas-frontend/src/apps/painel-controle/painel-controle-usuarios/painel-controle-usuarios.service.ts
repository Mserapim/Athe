import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleControleAcessoGrupos } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos.service';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { apiPainelControleControleAcessoUsuarios } from 'api/painel-controle/api-painel-controle-controle-acesso-usuarios.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class PainelControleUsuariosService extends MpmtListagem2Service {
    public loading: boolean = false;

    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('Todos', []),
        cat_func: new FormControl<string>(null, []),
        lotacao: new FormControl<string>(null, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        this.loading = true;
        const dados = await apiPainelControleControleAcessoUsuarios(filtros);
        this.loading = false;
        return dados;
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

    protected get downloadCsvSincrono() {
        return false;
    }
}
