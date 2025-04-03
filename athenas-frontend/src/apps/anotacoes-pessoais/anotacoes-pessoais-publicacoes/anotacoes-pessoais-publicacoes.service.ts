import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiRhPublicacoes } from 'api/rh/api-rh-publicacoes.service';
import { MpmtListagem2Paginacao } from 'components/mpmt-listagem2/mpmt-listagem2.interface';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { debounceTime, distinctUntilChanged } from 'rxjs';

@Injectable()
export class AnotacoesPessoaisPublicacoesService extends MpmtListagem2Service {
    public loading: boolean = false;

    lista_status = [
        { id: 1, descricao: 'Em aberto' },
        { id: 2, descricao: 'Públicação solicitada' },
        { id: 3, descricao: 'Públicação realizada' },
        { id: 4, descricao: 'Públicação cancelada' },
        { id: 5, descricao: 'Publicação solicitada ao expediente' },
    ];

    tipos: { label: string; value: number }[] = [];


    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        keyword: new FormControl<string>('', []),
        tipo: new FormControl<number[]>(null, []),
        status: new FormControl<number[]>(null, []),
    });

    constructor() {
        super();

        this.filtros.valueChanges
            .pipe(debounceTime(1000), distinctUntilChanged())

            .subscribe((x) => {
                this.paginacao.page = 1;
                this.recarregarListagem();
            });
    }

    public async obterDados(filtros: any) {
        this.loading = true;
        const dados = await apiRhPublicacoes(filtros);
        this.loading = false;
        return dados;
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

    protected get downloadCsvSincrono() {
        return false;
    }

    public async carregarTiposPublicacao() {
        try {
            this.tipos = (await apiAnotacoesPessoaisTiposDocumentos({})).results;
        } catch (error) {
            console.error('Erro ao carregar os tipos de publicação:', error);
        }
    }
}
