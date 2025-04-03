import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiAnotacoesPessoais } from 'api/anotacoes-pessoais/api-anotacoes-pessoais.service';
import { apiAnotacaoPessoalTiposAnotacao } from 'api/anotacoes-pessoais/api-anotacoes-pessoal-minhas-anotacoes.service';
import { MpmtListagem2Paginacao } from 'components/mpmt-listagem2/mpmt-listagem2.interface';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class AnotacoesPessoaisListagemService extends MpmtListagem2Service {
    public loading: boolean = false;

    tipos_documento: { label: string; value: number }[] = [];
    tipos_anotacao: { label: string; value: number }[] = [];


    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        palavra_chave: new FormControl<string>('', []),
        servidor_ids: new FormControl<any[] | null>(null, []),
        tipos_anotacao: new FormControl<any[]>(null, []),
        tipos_documento: new FormControl<any[]>(null, []),
    });

    constructor() {
        super();

        this.filtros.valueChanges.subscribe((x) => {
            this.paginacao.page = 1;
            this.recarregarListagem();
        });
    }

    public async obterDados(filtros: any) {
        this.loading = true;
        const dados = await apiAnotacoesPessoais(filtros);
        this.loading = false;
        return dados;
    }

    protected async obterFiltros() {
    var filtros = { ...this.filtros.value };
    
    var servidor_ids = null
    var tipos_anotacao = null
    var tipos_documento = null

    if (filtros?.servidor_ids) {
        servidor_ids = filtros.servidor_ids.map(servidor => servidor.pk);
    }

    if (filtros?.tipos_documento) {
        tipos_documento = filtros.tipos_documento.map(tipo => tipo.value);
    }

    if (filtros?.tipos_anotacao) {
        tipos_anotacao = filtros.tipos_anotacao.map(tipo => tipo.value);
    }

    return {  
        order_by: filtros?.order_by,
        palavra_chave: filtros?.palavra_chave,
        servidor_ids: servidor_ids,
        tipos_anotacao: tipos_anotacao,
        tipos_documento: tipos_documento, 
    };
}

    protected get downloadCsvSincrono() {
        return false;
    }

    public async carregarTiposDocumento() {
        try {
            this.tipos_documento = (await apiAnotacoesPessoaisTiposDocumentos({})).results;
        } catch (error) {
            console.error('Erro ao carregar os tipos de documento:', error);
        }
    }

    public async carregarTiposAntotacao() {
        try {
            this.tipos_anotacao = (await apiAnotacaoPessoalTiposAnotacao({})).results;
        } catch (error) {
            console.error('Erro ao carregar os tipos de anotação:', error);
        }
    }
}
