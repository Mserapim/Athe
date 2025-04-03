import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasPagamentos } from 'api/diarias/pagamentos/api-diarias-pagamentos.service';
import { MpmtPaginacao } from 'components/mpmt-celula/mpmt-celula.interface';
import { MpmtListagemService } from 'components/mpmt-listagens/mpmt-listagem.service';
import { formatDate } from 'utils/format-date';

@Injectable()
export class DiariasGestaoPagamentosService extends MpmtListagemService {

    status_pagamento = [
        { id: 'aguardando', descricao: 'Aguardando - ordem pendente' },
        { id: 'cnab_criado', descricao: 'Cnab Criado - Aguardando pagamento' },
        { id: 'pago', descricao: 'Pago' },
    ];

    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        status: new FormControl<any[]>([this.status_pagamento[0]], []),
        data_pgto_inicio: new FormControl<Date>(null, []),
        data_pgto_fim: new FormControl<Date>(null, []),
        servidores: new FormControl<any[]>(null, []),
    });

    constructor() {
        super();
        this.filtros.valueChanges.subscribe(()=>this.recarregarListagem())
    }

    public async obterDados(filtros: any) {
        const dados = await apiDiariasPagamentos(filtros);
        dados.results = dados.results.map(item => ({
            ...item,
            checkboxDesativado: item.status === 'pago' || item.status === 'cnab_criado' || item.valor_liquido_deferido_viagem <= 0,
            ocultarAcoes: item.status === 'pago' || item.valor_liquido_deferido_viagem <= 0
        }));

        return dados;
    }

    protected async obterFiltros() {
        const data_pgto_inicio_value = this.filtros.get('data_pgto_inicio')?.value;
        const data_pgto_fim_value = this.filtros.get('data_pgto_fim')?.value;
        const status_value = this.filtros.get('status')?.value;
        const data_pgto_inicio = formatDate(data_pgto_inicio_value);
        const data_pgto_fim = formatDate(data_pgto_fim_value);

        let status = null;
        if (status_value){
            status = status_value.map(status => status.id);
        }

        const servidores_valor = this.filtros.get('servidores')?.value;
        let servidores = null;
        if (servidores_valor){
            servidores = servidores_valor.map(servidor => servidor.pk);
        }

        return { ...this.filtros.value , data_pgto_inicio: data_pgto_inicio, data_pgto_fim:data_pgto_fim, status:status, servidores:servidores};
    }

    protected async obterPaginacao(): Promise<MpmtPaginacao> {
        const status_value = this.filtros?.get('status')?.value || [];
        let status = null;
        if (status_value){
            status = status_value.map(status => status.id);
        }
        if (status.includes('pago') || status.length === 0 || status.includes('cnab_criado')) {
            this.paginacao.per_page = 10;
        } else {
            this.paginacao.per_page = null;
        }
        return { ...this.paginacao };
    }
}
