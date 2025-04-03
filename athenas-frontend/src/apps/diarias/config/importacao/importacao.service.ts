import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasConfigCargos } from 'api/diarias/config/api-diarias-config-cargos.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class DiariasConfigImportacaoService extends MpmtListagem2Service {
    filtros = new FormGroup({
        servidor: new FormControl<number>(null, []),
        ano_inicio: new FormControl<number>(null, []),
        ano_fim: new FormControl<number>(null, []),
    });

    public lista_anos: number[] = []

    constructor() {
        super();
        this.carregarAnos();
    }

    public async obterDados(filtros: any) {
        return apiDiariasConfigCargos(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

    protected carregarAnos(): void {
        const inicio: number = 2005;
        const fim: number = 2025;
        const anos: number[] = [];
        
        for (let ano = inicio; ano <= fim; ano++) {
            anos.push(ano);
        }
        
        this.lista_anos = anos;
    }
}
